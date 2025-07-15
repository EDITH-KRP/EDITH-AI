from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from motor.motor_asyncio import AsyncIOMotorClient
import uuid
from datetime import datetime
import re
import math

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = AsyncIOMotorClient(MONGO_URL)
db = client.voice_catalog

# Pydantic models
class Product(BaseModel):
    id: str
    name: str
    quantity: float  # in kg
    price_per_kg: float  # price per kg
    description: Optional[str] = ""
    category: Optional[str] = "General"
    tags: List[str] = []
    created_at: datetime
    updated_at: datetime

class ProductCreate(BaseModel):
    name: str
    quantity: float
    price_per_kg: float
    description: Optional[str] = ""
    category: Optional[str] = "General"

class ProductUpdate(BaseModel):
    quantity: Optional[float] = None
    price_per_kg: Optional[float] = None
    description: Optional[str] = None

class VoiceCommand(BaseModel):
    command: str
    language: Optional[str] = "en"

# Helper functions
def calculate_price_breakdown(price_per_kg: float):
    """Calculate price breakdown for different quantities"""
    breakdown = {
        "1kg": price_per_kg,
        "half_kg": math.ceil(price_per_kg / 2),
        "quarter_kg": math.ceil(price_per_kg / 4)
    }
    return breakdown

def is_low_stock(quantity: float) -> bool:
    """Check if product is low in stock"""
    return quantity <= 2.0

def parse_voice_command(command: str):
    """Parse voice command and extract action, product, quantity, price"""
    command = command.lower().strip()
    
    # Add product: "add 5 kg tomato at ₹50" or "add 5 kg tomato 50 rupees"
    add_patterns = [
        r"add (\d+(?:\.\d+)?)\s*kg\s+(.+?)\s+(?:at\s+)?₹?(\d+(?:\.\d+)?)",
        r"add (\d+(?:\.\d+)?)\s*kg\s+(.+?)\s+(\d+(?:\.\d+)?)\s*rupees?",
        r"add (\d+(?:\.\d+)?)\s*(?:kg\s+)?(.+?)\s+(?:at\s+)?₹?(\d+(?:\.\d+)?)"
    ]
    
    for pattern in add_patterns:
        match = re.search(pattern, command)
        if match:
            quantity = float(match.group(1))
            product_name = match.group(2).strip()
            price = float(match.group(3))
            return {
                "action": "add",
                "product": product_name,
                "quantity": quantity,
                "price": price
            }
    
    # Update price: "update tomato price to ₹60"
    update_price_patterns = [
        r"update\s+(.+?)\s+price\s+to\s+₹?(\d+(?:\.\d+)?)",
        r"change\s+(.+?)\s+price\s+to\s+₹?(\d+(?:\.\d+)?)"
    ]
    
    for pattern in update_price_patterns:
        match = re.search(pattern, command)
        if match:
            product_name = match.group(1).strip()
            price = float(match.group(2))
            return {
                "action": "update_price",
                "product": product_name,
                "price": price
            }
    
    # Remove quantity: "remove 2 kg onions"
    remove_patterns = [
        r"remove\s+(\d+(?:\.\d+)?)\s*kg\s+(.+)",
        r"take\s+out\s+(\d+(?:\.\d+)?)\s*kg\s+(.+)"
    ]
    
    for pattern in remove_patterns:
        match = re.search(pattern, command)
        if match:
            quantity = float(match.group(1))
            product_name = match.group(2).strip()
            return {
                "action": "remove",
                "product": product_name,
                "quantity": quantity
            }
    
    # Delete product: "delete banana"
    delete_patterns = [
        r"delete\s+(.+)",
        r"remove\s+(.+)\s+completely"
    ]
    
    for pattern in delete_patterns:
        match = re.search(pattern, command)
        if match:
            product_name = match.group(1).strip()
            return {
                "action": "delete",
                "product": product_name
            }
    
    # List products: "list all products"
    if re.search(r"list\s+(?:all\s+)?products?", command):
        return {"action": "list"}
    
    return {"action": "unknown", "command": command}

def format_product_response(product: dict, language: str = "en"):
    """Format product response with breakdown"""
    breakdown = calculate_price_breakdown(product["price_per_kg"])
    
    response = {
        "product": product["name"],
        "quantity": product["quantity"],
        "price_per_kg": product["price_per_kg"],
        "breakdown": breakdown,
        "description": product.get("description", ""),
        "category": product.get("category", "General"),
        "tags": product.get("tags", []),
        "low_stock": is_low_stock(product["quantity"])
    }
    
    # Add language-specific formatting
    if language == "kn":  # Kannada
        response["message_kn"] = f"ನಿಮಗೆ {product['name']} {product['quantity']} ಕೆ.ಜಿ ₹{product['price_per_kg']} ದರದಲ್ಲಿ ಸೇರಿಸಲಾಗಿದೆ. 1 ಕೆ.ಜಿ = ₹{breakdown['1kg']}, ಅರ್ಧ = ₹{breakdown['half_kg']}, ತ್ರೈಮಾಸಿಕ = ₹{breakdown['quarter_kg']}."
    elif language == "hi":  # Hindi
        response["message_hi"] = f"आपके लिए {product['name']} {product['quantity']} किलो ₹{product['price_per_kg']} दर से जोड़ा गया है। 1 किलो = ₹{breakdown['1kg']}, आधा = ₹{breakdown['half_kg']}, चौथाई = ₹{breakdown['quarter_kg']}।"
    
    return response

# API Routes
@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "voice_catalog"}

@app.post("/api/products")
async def create_product(product: ProductCreate):
    """Add a new product to inventory"""
    try:
        # Check if product already exists
        existing = await db.products.find_one({"name": product.name.lower()})
        if existing:
            raise HTTPException(status_code=400, detail="Product already exists")
        
        product_data = {
            "id": str(uuid.uuid4()),
            "name": product.name.lower(),
            "display_name": product.name,
            "quantity": product.quantity,
            "price_per_kg": product.price_per_kg,
            "description": product.description,
            "category": product.category,
            "tags": [product.name.lower(), product.category.lower()],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        await db.products.insert_one(product_data)
        return format_product_response(product_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/products")
async def list_products():
    """List all products with stock alerts"""
    try:
        products = []
        async for product in db.products.find({}):
            product_response = format_product_response(product)
            products.append(product_response)
        
        # Add stock alerts
        low_stock_products = [p for p in products if p["low_stock"]]
        
        return {
            "products": products,
            "total_products": len(products),
            "low_stock_alerts": low_stock_products
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/products/{product_name}")
async def update_product(product_name: str, update: ProductUpdate):
    """Update product quantity or price"""
    try:
        product = await db.products.find_one({"name": product_name.lower()})
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        update_data = {"updated_at": datetime.utcnow()}
        if update.quantity is not None:
            update_data["quantity"] = update.quantity
        if update.price_per_kg is not None:
            update_data["price_per_kg"] = update.price_per_kg
        if update.description is not None:
            update_data["description"] = update.description
        
        await db.products.update_one(
            {"name": product_name.lower()},
            {"$set": update_data}
        )
        
        updated_product = await db.products.find_one({"name": product_name.lower()})
        return format_product_response(updated_product)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/products/{product_name}")
async def delete_product(product_name: str):
    """Delete a product from inventory"""
    try:
        result = await db.products.delete_one({"name": product_name.lower()})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Product not found")
        return {"message": f"Product '{product_name}' deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/voice-command")
async def process_voice_command(command: VoiceCommand):
    """Process voice command and execute corresponding action"""
    try:
        parsed = parse_voice_command(command.command)
        
        if parsed["action"] == "add":
            product_data = ProductCreate(
                name=parsed["product"],
                quantity=parsed["quantity"],
                price_per_kg=parsed["price"],
                description=f"Fresh {parsed['product']} perfect for cooking.",
                category="Grocery"
            )
            return await create_product(product_data)
        
        elif parsed["action"] == "update_price":
            update_data = ProductUpdate(price_per_kg=parsed["price"])
            return await update_product(parsed["product"], update_data)
        
        elif parsed["action"] == "remove":
            product = await db.products.find_one({"name": parsed["product"].lower()})
            if not product:
                raise HTTPException(status_code=404, detail="Product not found")
            
            new_quantity = max(0, product["quantity"] - parsed["quantity"])
            update_data = ProductUpdate(quantity=new_quantity)
            return await update_product(parsed["product"], update_data)
        
        elif parsed["action"] == "delete":
            return await delete_product(parsed["product"])
        
        elif parsed["action"] == "list":
            return await list_products()
        
        else:
            return {
                "error": "Command not understood",
                "parsed_command": parsed,
                "suggestion": "Try commands like 'add 5 kg tomato at ₹50' or 'list all products'"
            }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)