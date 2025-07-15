from fastapi import FastAPI, HTTPException, Depends, File, UploadFile, Form, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import os
import json
import uuid
from motor.motor_asyncio import AsyncIOMotorClient
import bcrypt
import jwt
from emergentintegrations.llm.chat import LlmChat, UserMessage
from emergentintegrations.llm.gemeni.image_generation import GeminiImageGeneration
import asyncio
import base64
import io
from PIL import Image
import qrcode

# Initialize FastAPI app
app = FastAPI(title="AI Catalog Assistant", version="1.0.0")

# Environment variables
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyBlfljbTfiUyY3CnPr9rmCNEKqHJTnyliE")
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-here")
DATABASE_NAME = os.getenv("DATABASE_NAME", "ai_catalog_db")

# Database connection
client = AsyncIOMotorClient(MONGO_URL)
db = client[DATABASE_NAME]

# Security
security = HTTPBearer()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class UserSignup(BaseModel):
    username: str
    email: str
    password: str
    role: str = "seller"  # seller or consumer
    language: str = "en"  # primary language

class UserLogin(BaseModel):
    email: str
    password: str

class Product(BaseModel):
    name: str
    quantity: float
    unit: str = "kg"
    price_per_unit: float
    description: Optional[str] = None
    image_base64: Optional[str] = None
    tags: List[str] = []
    seller_id: str
    language: str = "en"

class VoiceCommand(BaseModel):
    command: str
    language: str = "en"
    seller_id: str

class Order(BaseModel):
    product_id: str
    quantity: float
    consumer_id: str
    seller_id: str
    total_price: float
    status: str = "pending"

class AIResponse(BaseModel):
    message: str
    language: str
    action: Optional[str] = None
    data: Optional[Dict[str, Any]] = None

# Initialize AI services
async def get_ai_chat(session_id: str, system_message: str):
    chat = LlmChat(
        api_key=GEMINI_API_KEY,
        session_id=session_id,
        system_message=system_message
    )
    return chat.with_model("gemini", "gemini-2.0-flash")

async def get_image_generator():
    return GeminiImageGeneration(api_key=GEMINI_API_KEY)

# Utility functions
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_jwt_token(user_id: str, role: str) -> str:
    payload = {
        "user_id": user_id,
        "role": role,
        "exp": datetime.utcnow() + timedelta(days=7)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

def verify_jwt_token(token: str) -> Dict[str, Any]:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    payload = verify_jwt_token(credentials.credentials)
    user = await db.users.find_one({"_id": payload["user_id"]})
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

def generate_qr_code(data: str) -> str:
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return img_str

# Language detection and AI processing
async def process_voice_command(command: str, seller_id: str, language: str = "en"):
    system_message = f"""You are a multilingual AI assistant for rural vendors in India. 
    You help with catalog management, pricing suggestions, and inventory tracking.
    
    Current language: {language}
    
    Extract information from voice commands and respond appropriately.
    
    For commands like "Add 5 kg tomatoes at ₹40", extract:
    - Product name
    - Quantity and unit
    - Price per unit
    - Calculate breakdown (1kg, 1/2kg, 1/4kg prices)
    
    Always respond in the same language as the input.
    Provide helpful suggestions for better pricing or descriptions.
    """
    
    chat = await get_ai_chat(f"seller_{seller_id}", system_message)
    user_message = UserMessage(text=command)
    response = await chat.send_message(user_message)
    
    return response

# Auth endpoints
@app.post("/api/auth/signup")
async def signup(user_data: UserSignup):
    # Check if user exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user
    user_id = str(uuid.uuid4())
    user_doc = {
        "_id": user_id,
        "username": user_data.username,
        "email": user_data.email,
        "password": hash_password(user_data.password),
        "role": user_data.role,
        "language": user_data.language,
        "created_at": datetime.utcnow()
    }
    
    await db.users.insert_one(user_doc)
    
    # Generate JWT token
    token = create_jwt_token(user_id, user_data.role)
    
    return {
        "message": "User created successfully",
        "token": token,
        "user": {
            "id": user_id,
            "username": user_data.username,
            "email": user_data.email,
            "role": user_data.role,
            "language": user_data.language
        }
    }

@app.post("/api/auth/login")
async def login(login_data: UserLogin):
    user = await db.users.find_one({"email": login_data.email})
    if not user or not verify_password(login_data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_jwt_token(user["_id"], user["role"])
    
    return {
        "message": "Login successful",
        "token": token,
        "user": {
            "id": user["_id"],
            "username": user["username"],
            "email": user["email"],
            "role": user["role"],
            "language": user["language"]
        }
    }

# Voice processing endpoints
@app.post("/api/voice/process")
async def process_voice(voice_command: VoiceCommand, current_user: dict = Depends(get_current_user)):
    try:
        # Process the voice command with AI
        ai_response = await process_voice_command(
            voice_command.command,
            current_user["_id"],
            voice_command.language
        )
        
        # Parse the AI response to extract product information
        # This is a simplified version - in production you'd need more sophisticated parsing
        response_text = ai_response.lower()
        
        # Try to extract product information
        action = None
        data = None
        
        if "add" in response_text or "सेट" in response_text or "ಸೇರಿಸಿ" in response_text:
            action = "add_product"
            # Extract product details (simplified)
            data = {
                "suggestion": "Product extracted from voice command",
                "parsed_command": voice_command.command
            }
        elif "update" in response_text or "बदलें" in response_text or "ಬದಲಾಯಿಸಿ" in response_text:
            action = "update_product"
            data = {"suggestion": "Update product details"}
        elif "delete" in response_text or "हटाएं" in response_text or "ಅಳಿಸಿ" in response_text:
            action = "delete_product"
            data = {"suggestion": "Delete product"}
        elif "stock" in response_text or "स्टॉक" in response_text or "ಸ್ಟಾಕ್" in response_text:
            action = "check_stock"
            data = {"suggestion": "Check current inventory"}
        
        return AIResponse(
            message=ai_response,
            language=voice_command.language,
            action=action,
            data=data
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Voice processing failed: {str(e)}")

# Product management endpoints
@app.post("/api/products")
async def create_product(product: Product, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "seller":
        raise HTTPException(status_code=403, detail="Only sellers can create products")
    
    try:
        # Generate product image using AI
        image_generator = await get_image_generator()
        image_prompt = f"Fresh {product.name} vegetables for Indian market, high quality, vibrant colors"
        
        try:
            images = await image_generator.generate_images(
                prompt=image_prompt,
                number_of_images=1
            )
            
            if images and len(images) > 0:
                product.image_base64 = base64.b64encode(images[0]).decode('utf-8')
        except Exception as e:
            print(f"Image generation failed: {e}")
            product.image_base64 = None
        
        # Create product document
        product_id = str(uuid.uuid4())
        product_doc = {
            "_id": product_id,
            "name": product.name,
            "quantity": product.quantity,
            "unit": product.unit,
            "price_per_unit": product.price_per_unit,
            "description": product.description,
            "image_base64": product.image_base64,
            "tags": product.tags,
            "seller_id": current_user["_id"],
            "language": product.language,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        await db.products.insert_one(product_doc)
        
        # Generate QR code for product
        qr_data = f"Product: {product.name}, Price: ₹{product.price_per_unit}/{product.unit}, ID: {product_id}"
        qr_code = generate_qr_code(qr_data)
        
        # Calculate price breakdown
        price_breakdown = {
            "1_kg": product.price_per_unit,
            "half_kg": round(product.price_per_unit / 2, 2),
            "quarter_kg": round(product.price_per_unit / 4, 2)
        }
        
        return {
            "message": "Product created successfully",
            "product_id": product_id,
            "price_breakdown": price_breakdown,
            "qr_code": qr_code
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Product creation failed: {str(e)}")

@app.get("/api/products")
async def get_products(current_user: dict = Depends(get_current_user)):
    if current_user["role"] == "seller":
        # Sellers see their own products
        products = await db.products.find({"seller_id": current_user["_id"]}).to_list(100)
    else:
        # Consumers see all available products
        products = await db.products.find({"quantity": {"$gt": 0}}).to_list(100)
    
    return {"products": products}

@app.get("/api/products/{product_id}")
async def get_product(product_id: str, current_user: dict = Depends(get_current_user)):
    product = await db.products.find_one({"_id": product_id})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return product

@app.put("/api/products/{product_id}")
async def update_product(product_id: str, product: Product, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "seller":
        raise HTTPException(status_code=403, detail="Only sellers can update products")
    
    existing_product = await db.products.find_one({"_id": product_id, "seller_id": current_user["_id"]})
    if not existing_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    update_data = {
        "name": product.name,
        "quantity": product.quantity,
        "unit": product.unit,
        "price_per_unit": product.price_per_unit,
        "description": product.description,
        "tags": product.tags,
        "updated_at": datetime.utcnow()
    }
    
    await db.products.update_one({"_id": product_id}, {"$set": update_data})
    
    return {"message": "Product updated successfully"}

@app.delete("/api/products/{product_id}")
async def delete_product(product_id: str, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "seller":
        raise HTTPException(status_code=403, detail="Only sellers can delete products")
    
    result = await db.products.delete_one({"_id": product_id, "seller_id": current_user["_id"]})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return {"message": "Product deleted successfully"}

# Order management endpoints
@app.post("/api/orders")
async def create_order(order: Order, current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "consumer":
        raise HTTPException(status_code=403, detail="Only consumers can create orders")
    
    # Check product availability
    product = await db.products.find_one({"_id": order.product_id})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if product["quantity"] < order.quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock")
    
    # Create order
    order_id = str(uuid.uuid4())
    order_doc = {
        "_id": order_id,
        "product_id": order.product_id,
        "quantity": order.quantity,
        "consumer_id": current_user["_id"],
        "seller_id": order.seller_id,
        "total_price": order.total_price,
        "status": "pending",
        "created_at": datetime.utcnow()
    }
    
    await db.orders.insert_one(order_doc)
    
    # Update product quantity
    new_quantity = product["quantity"] - order.quantity
    await db.products.update_one(
        {"_id": order.product_id},
        {"$set": {"quantity": new_quantity, "updated_at": datetime.utcnow()}}
    )
    
    return {"message": "Order created successfully", "order_id": order_id}

@app.get("/api/orders")
async def get_orders(current_user: dict = Depends(get_current_user)):
    if current_user["role"] == "seller":
        orders = await db.orders.find({"seller_id": current_user["_id"]}).to_list(100)
    else:
        orders = await db.orders.find({"consumer_id": current_user["_id"]}).to_list(100)
    
    return {"orders": orders}

# AI suggestions endpoint
@app.get("/api/suggestions")
async def get_ai_suggestions(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != "seller":
        raise HTTPException(status_code=403, detail="Only sellers can get suggestions")
    
    # Get seller's products
    products = await db.products.find({"seller_id": current_user["_id"]}).to_list(100)
    
    # Generate AI suggestions
    system_message = f"""You are an AI assistant for rural vendors in India. 
    Provide helpful suggestions for improving sales, pricing, and inventory management.
    Language: {current_user.get('language', 'en')}
    
    Based on the current inventory, suggest:
    1. Optimal pricing strategies
    2. Product bundling opportunities
    3. Inventory management tips
    4. Marketing suggestions
    """
    
    chat = await get_ai_chat(f"suggestions_{current_user['_id']}", system_message)
    
    products_summary = f"Current inventory: {len(products)} products. "
    for product in products[:5]:  # Limit to first 5 products
        products_summary += f"{product['name']}: {product['quantity']} {product['unit']} at ₹{product['price_per_unit']}/{product['unit']}. "
    
    user_message = UserMessage(text=f"Provide suggestions for: {products_summary}")
    suggestions = await chat.send_message(user_message)
    
    return {"suggestions": suggestions, "language": current_user.get('language', 'en')}

# WebSocket for real-time updates
@app.websocket("/api/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await websocket.accept()
    try:
        while True:
            # Keep connection alive and handle real-time updates
            await websocket.receive_text()
            
            # Send real-time updates about inventory changes
            await websocket.send_text(json.dumps({
                "type": "inventory_update",
                "message": "Inventory updated",
                "timestamp": datetime.utcnow().isoformat()
            }))
            
    except WebSocketDisconnect:
        print(f"Client {user_id} disconnected")

# Health check
@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)