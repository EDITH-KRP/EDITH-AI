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

# Translation dictionaries for regional languages
TRANSLATION_DICT = {
    'hi': {  # Hindi
        'जोड़ो': 'add', 'एड': 'add', 'डालो': 'add',
        'अपडेट': 'update', 'बदलो': 'update', 'चेंज': 'update',
        'हटाओ': 'remove', 'निकालो': 'remove',
        'डिलीट': 'delete', 'मिटाओ': 'delete',
        'लिस्ट': 'list', 'दिखाओ': 'list', 'बताओ': 'list',
        'किलो': 'kg', 'केजी': 'kg',
        'रुपये': 'rupees', 'रुपया': 'rupees',
        'टमाटर': 'tomato', 'प्याज': 'onion', 'केला': 'banana',
        'आलू': 'potato', 'गाजर': 'carrot', 'चावल': 'rice',
        'दाल': 'dal', 'दूध': 'milk', 'चीनी': 'sugar',
        'कीमत': 'price', 'दाम': 'price', 'रेट': 'rate'
    },
    'kn': {  # Kannada
        'ಸೇರಿಸಿ': 'add', 'ಹಾಕಿ': 'add', 'ಸೇರಿಸು': 'add',
        'ಅಪ್ಡೇಟ್': 'update', 'ಬದಲಾಯಿಸಿ': 'update',
        'ತೆಗೆದುಹಾಕಿ': 'remove', 'ತೆಗೆ': 'remove',
        'ಅಳಿಸಿ': 'delete', 'ಡಿಲೀಟ್': 'delete',
        'ಲಿಸ್ಟ್': 'list', 'ತೋರಿಸಿ': 'list',
        'ಕಿಲೋ': 'kg', 'ಕೆಜಿ': 'kg',
        'ರೂಪಾಯಿ': 'rupees', 'ರೂಪಾಯಿಗಳು': 'rupees',
        'ಟೊಮೇಟೊ': 'tomato', 'ಈರುಳ್ಳಿ': 'onion', 'ಬಾಳೆಹಣ್ಣು': 'banana',
        'ಆಲೂಗಡ್ಡೆ': 'potato', 'ಅಕ್ಕಿ': 'rice', 'ಹಾಲು': 'milk',
        'ಬೆಲೆ': 'price', 'ದರ': 'rate'
    },
    'ta': {  # Tamil
        'சேர்': 'add', 'போடு': 'add', 'சேர்க்க': 'add',
        'மாற்று': 'update', 'அப்டேட்': 'update',
        'எடு': 'remove', 'நீக்கு': 'remove',
        'நீக்கு': 'delete', 'அழி': 'delete',
        'பட்டியல்': 'list', 'காட்டு': 'list',
        'கிலோ': 'kg', 'கேஜி': 'kg',
        'ரூபாய்': 'rupees', 'ரூபா': 'rupees',
        'தக்காளி': 'tomato', 'வெங்காயம்': 'onion', 'வாழைப்பழம்': 'banana',
        'உருளைக்கிழங்கு': 'potato', 'அரிசி': 'rice', 'பால்': 'milk',
        'விலை': 'price', 'ரேட்': 'rate'
    },
    'te': {  # Telugu
        'చేర్చు': 'add', 'పెట్టు': 'add', 'యాడ్': 'add',
        'అప్డేట్': 'update', 'మార్చు': 'update',
        'తీసివేయి': 'remove', 'తీసేయి': 'remove',
        'తొలగించు': 'delete', 'డిలీట్': 'delete',
        'లిస్ట్': 'list', 'చూపించు': 'list',
        'కిలో': 'kg', 'కేజీ': 'kg',
        'రూపాయలు': 'rupees', 'రూపాయి': 'rupees',
        'టమాట': 'tomato', 'ఉల్లిపాయ': 'onion', 'అరటిపండు': 'banana',
        'బంగాళాదుంప': 'potato', 'అన్నం': 'rice', 'పాలు': 'milk',
        'ధర': 'price', 'రేట్': 'rate'
    }
}

# Response messages in different languages
RESPONSE_MESSAGES = {
    'en': {
        'product_added': 'Product {product} {quantity} kg added at ₹{price} per kg',
        'price_updated': 'Price updated for {product} to ₹{price} per kg',
        'quantity_removed': 'Removed {quantity} kg of {product}',
        'product_deleted': 'Product {product} deleted',
        'low_stock': 'Low stock alert',
        'products_listed': 'You have {count} products in inventory'
    },
    'hi': {
        'product_added': '{product} {quantity} किलो ₹{price} दर से जोड़ा गया',
        'price_updated': '{product} की कीमत ₹{price} अपडेट की गई',
        'quantity_removed': '{product} से {quantity} किलो हटाया गया',
        'product_deleted': '{product} डिलीट किया गया',
        'low_stock': 'कम स्टॉक अलर्ट',
        'products_listed': 'आपके पास {count} उत्पाद हैं'
    },
    'kn': {
        'product_added': '{product} {quantity} ಕಿಲೋ ₹{price} ದರದಲ್ಲಿ ಸೇರಿಸಲಾಗಿದೆ',
        'price_updated': '{product} ಬೆಲೆ ₹{price} ಅಪ್ಡೇಟ್ ಮಾಡಲಾಗಿದೆ',
        'quantity_removed': '{product} ನಿಂದ {quantity} ಕಿಲೋ ತೆಗೆದುಹಾಕಲಾಗಿದೆ',
        'product_deleted': '{product} ಅಳಿಸಲಾಗಿದೆ',
        'low_stock': 'ಕಡಿಮೆ ಸ್ಟಾಕ್ ಎಚ್ಚರಿಕೆ',
        'products_listed': 'ನಿಮ್ಮ ಬಳಿ {count} ಉತ್ಪಾದನೆಗಳಿವೆ'
    },
    'ta': {
        'product_added': '{product} {quantity} கிலோ ₹{price} விலையில் சேர்க்கப்பட்டது',
        'price_updated': '{product} விலை ₹{price} அப்டேட் செய்யப்பட்டது',
        'quantity_removed': '{product} இல் இருந்து {quantity} கிலோ எடுக்கப்பட்டது',
        'product_deleted': '{product} நீக்கப்பட்டது',
        'low_stock': 'குறைந்த பங்கு எச்சரிக்கை',
        'products_listed': 'உங்களிடம் {count} பொருட்கள் உள்ளன'
    },
    'te': {
        'product_added': '{product} {quantity} కిలో ₹{price} రేటుతో చేర్చబడింది',
        'price_updated': '{product} ధర ₹{price} అప్డేట్ చేయబడింది',
        'quantity_removed': '{product} నుండి {quantity} కిలో తీసివేయబడింది',
        'product_deleted': '{product} తొలగించబడింది',
        'low_stock': 'తక్కువ స్టాక్ హెచ్చరిక',
        'products_listed': 'మీకు {count} ఉత్పత్తులు ఉన్నాయి'
    }
}

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
def translate_regional_to_english(text: str, language: str) -> str:
    """Translate regional language text to English using dictionary"""
    if language == 'en' or language not in TRANSLATION_DICT:
        return text
    
    translation_dict = TRANSLATION_DICT[language]
    translated_text = text.lower()
    
    # Replace each regional word with English equivalent
    for regional_word, english_word in translation_dict.items():
        translated_text = translated_text.replace(regional_word, english_word)
    
    print(f"Translation: {text} ({language}) -> {translated_text}")
    return translated_text

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

def parse_voice_command(command: str, language: str = "en"):
    """Parse voice command and extract action, product, quantity, price"""
    # First translate regional language to English
    translated_command = translate_regional_to_english(command, language)
    command_lower = translated_command.lower().strip()
    
    # Enhanced pattern matching for better regional language support
    # Add product patterns - more flexible
    add_patterns = [
        r"add\s+(\d+(?:\.\d+)?)\s*kg\s+(.+?)\s+(?:at\s+)?₹?(\d+(?:\.\d+)?)",
        r"add\s+(\d+(?:\.\d+)?)\s*kg\s+(.+?)\s+(\d+(?:\.\d+)?)\s*rupees?",
        r"add\s+(\d+(?:\.\d+)?)\s*(?:kg\s+)?(.+?)\s+(?:at\s+)?₹?(\d+(?:\.\d+)?)",
        r"(\d+(?:\.\d+)?)\s*kg\s+(.+?)\s+(?:at\s+)?₹?(\d+(?:\.\d+)?)",
        r"(\d+(?:\.\d+)?)\s*kg\s+(.+?)\s+(\d+(?:\.\d+)?)\s*rupees?",
        r"(\d+(?:\.\d+)?)\s+(.+?)\s+(\d+(?:\.\d+)?)\s*rupees?",
        r"(\d+(?:\.\d+)?)\s+(.+?)\s+₹?(\d+(?:\.\d+)?)"
    ]
    
    for pattern in add_patterns:
        match = re.search(pattern, command_lower)
        if match:
            try:
                quantity = float(match.group(1))
                product_name = match.group(2).strip()
                price = float(match.group(3))
                
                # Clean product name - remove common words and extra spaces
                product_name = re.sub(r'\b(?:add|at|rupees?|kg|కిలో|किलो|ಕಿಲೋ|கிலோ|রূপা|ரூபா|రూపాయ|ರೂಪಾಯಿ|रुपये)\b', '', product_name).strip()
                product_name = ' '.join(product_name.split())  # Remove extra spaces
                
                return {
                    "action": "add",
                    "product": product_name,
                    "quantity": quantity,
                    "price": price
                }
            except (ValueError, IndexError):
                continue
    
    # Update price patterns - enhanced
    update_price_patterns = [
        r"update\s+(.+?)\s+price\s+to\s+₹?(\d+(?:\.\d+)?)",
        r"change\s+(.+?)\s+price\s+to\s+₹?(\d+(?:\.\d+)?)",
        r"(.+?)\s+price\s+₹?(\d+(?:\.\d+)?)",
        r"(.+?)\s+rate\s+₹?(\d+(?:\.\d+)?)",
        r"(.+?)\s+₹?(\d+(?:\.\d+)?)\s*rupees?\s+update",
        r"(.+?)\s+₹?(\d+(?:\.\d+)?)\s*update"
    ]
    
    for pattern in update_price_patterns:
        match = re.search(pattern, command_lower)
        if match:
            try:
                product_name = match.group(1).strip()
                price = float(match.group(2))
                
                # Clean product name
                product_name = re.sub(r'\b(?:update|change|price|rate|rupees?)\b', '', product_name).strip()
                
                return {
                    "action": "update_price",
                    "product": product_name,
                    "price": price
                }
            except (ValueError, IndexError):
                continue
    
    # Remove quantity patterns
    remove_patterns = [
        r"remove\s+(\d+(?:\.\d+)?)\s*kg\s+(.+)",
        r"take\s+out\s+(\d+(?:\.\d+)?)\s*kg\s+(.+)",
        r"(\d+(?:\.\d+)?)\s*kg\s+(.+?)\s*remove"
    ]
    
    for pattern in remove_patterns:
        match = re.search(pattern, command_lower)
        if match:
            try:
                quantity = float(match.group(1))
                product_name = match.group(2).strip()
                return {
                    "action": "remove",
                    "product": product_name,
                    "quantity": quantity
                }
            except (ValueError, IndexError):
                continue
    
    # Delete product patterns
    delete_patterns = [
        r"delete\s+(.+)",
        r"remove\s+(.+)\s+completely",
        r"(.+?)\s*delete"
    ]
    
    for pattern in delete_patterns:
        match = re.search(pattern, command_lower)
        if match:
            product_name = match.group(1).strip()
            return {
                "action": "delete",
                "product": product_name
            }
    
    # List products patterns
    if re.search(r"list\s+(?:all\s+)?products?", command_lower):
        return {"action": "list"}
    
    return {
        "action": "unknown", 
        "command": command, 
        "translated": translated_command,
        "language": language
    }

def format_product_response(product: dict, language: str = "en"):
    """Format product response with breakdown and language support"""
    breakdown = calculate_price_breakdown(product["price_per_kg"])
    
    response = {
        "product": product["name"],
        "quantity": product["quantity"],
        "price_per_kg": product["price_per_kg"],
        "breakdown": breakdown,
        "description": product.get("description", ""),
        "category": product.get("category", "General"),
        "tags": product.get("tags", []),
        "low_stock": is_low_stock(product["quantity"]),
        "language": language
    }
    
    # Add language-specific message
    if language in RESPONSE_MESSAGES:
        messages = RESPONSE_MESSAGES[language]
        response["message"] = messages["product_added"].format(
            product=product["name"],
            quantity=product["quantity"],
            price=product["price_per_kg"]
        )
        
        if response["low_stock"]:
            response["message"] += f" - {messages['low_stock']}"
    
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
    except HTTPException:
        raise
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
    except HTTPException:
        raise
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
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/voice-command")
async def process_voice_command(command: VoiceCommand):
    """Process voice command and execute corresponding action"""
    try:
        parsed = parse_voice_command(command.command, command.language)
        
        if parsed["action"] == "add":
            product_data = ProductCreate(
                name=parsed["product"],
                quantity=parsed["quantity"],
                price_per_kg=parsed["price"],
                description=f"Fresh {parsed['product']} perfect for cooking.",
                category="Grocery"
            )
            result = await create_product(product_data)
            result["language"] = command.language
            return result
        
        elif parsed["action"] == "update_price":
            update_data = ProductUpdate(price_per_kg=parsed["price"])
            result = await update_product(parsed["product"], update_data)
            result["language"] = command.language
            return result
        
        elif parsed["action"] == "remove":
            product = await db.products.find_one({"name": parsed["product"].lower()})
            if not product:
                raise HTTPException(status_code=404, detail="Product not found")
            
            new_quantity = max(0, product["quantity"] - parsed["quantity"])
            update_data = ProductUpdate(quantity=new_quantity)
            result = await update_product(parsed["product"], update_data)
            result["language"] = command.language
            return result
        
        elif parsed["action"] == "delete":
            result = await delete_product(parsed["product"])
            result["language"] = command.language
            return result
        
        elif parsed["action"] == "list":
            result = await list_products()
            result["language"] = command.language
            return result
        
        else:
            return {
                "error": "Command not understood",
                "parsed_command": parsed,
                "suggestion": "Try commands like 'add 5 kg tomato at ₹50' or 'list all products'",
                "language": command.language
            }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)