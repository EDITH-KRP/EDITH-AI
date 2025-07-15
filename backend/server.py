from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime
import asyncio

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Pydantic Models
class ProductInput(BaseModel):
    name: str
    quantity: str
    price: float
    language: str
    session_id: Optional[str] = None
    additional_info: Optional[str] = None

class ProductListing(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    quantity: str
    price: float
    price_breakdown: Dict[str, float]
    description: str
    tags: List[str]
    category: str
    language: str
    session_id: str
    original_input: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class LanguageContent(BaseModel):
    language: str
    content: Dict[str, Any]

class TranslationRequest(BaseModel):
    text: str
    from_language: str
    to_language: str

# Language content
LANGUAGE_CONTENT = {
    "english": {
        "app_title": "Digital Catalog Agent",
        "subtitle": "Create professional product listings with AI",
        "product_name": "Product Name",
        "quantity": "Quantity",
        "price": "Price (₹)",
        "additional_info": "Additional Info (optional)",
        "generate_listing": "Generate Listing",
        "product_listing": "Product Listing Generated",
        "description": "Description",
        "tags": "Tags",
        "category": "Category",
        "price_breakdown": "Price Breakdown",
        "my_listings": "My Listings",
        "no_listings": "No listings found",
        "clear_all": "Clear All",
        "processing": "Processing...",
        "error_occurred": "An error occurred"
    },
    "hindi": {
        "app_title": "डिजिटल कैटलॉग एजेंट",
        "subtitle": "एआई के साथ पेशेवर उत्पाद लिस्टिंग बनाएं",
        "product_name": "उत्पाद का नाम",
        "quantity": "मात्रा",
        "price": "मूल्य (₹)",
        "additional_info": "अतिरिक्त जानकारी (वैकल्पिक)",
        "generate_listing": "लिस्टिंग जेनरेट करें",
        "product_listing": "उत्पाद लिस्टिंग जेनरेट की गई",
        "description": "विवरण",
        "tags": "टैग",
        "category": "श्रेणी",
        "price_breakdown": "मूल्य विवरण",
        "my_listings": "मेरी लिस्टिंग",
        "no_listings": "कोई लिस्टिंग नहीं मिली",
        "clear_all": "सभी साफ करें",
        "processing": "प्रसंस्करण...",
        "error_occurred": "एक त्रुटि हुई"
    },
    "kannada": {
        "app_title": "ಡಿಜಿಟಲ್ ಕ್ಯಾಟಲಾಗ್ ಏಜೆಂಟ್",
        "subtitle": "AI ಯೊಂದಿಗೆ ವೃತ್ತಿಪರ ಉತ್ಪಾದನಾ ಪಟ್ಟಿಗಳನ್ನು ರಚಿಸಿ",
        "product_name": "ಉತ್ಪಾದನೆಯ ಹೆಸರು",
        "quantity": "ಪ್ರಮಾಣ",
        "price": "ಬೆಲೆ (₹)",
        "additional_info": "ಹೆಚ್ಚುವರಿ ಮಾಹಿತಿ (ಐಚ್ಛಿಕ)",
        "generate_listing": "ಪಟ್ಟಿ ಉತ್ಪಾದಿಸಿ",
        "product_listing": "ಉತ್ಪಾದನಾ ಪಟ್ಟಿ ಉತ್ಪಾದಿಸಲಾಗಿದೆ",
        "description": "ವಿವರಣೆ",
        "tags": "ಟ್ಯಾಗ್‌ಗಳು",
        "category": "ವರ್ಗ",
        "price_breakdown": "ಬೆಲೆ ವಿವರಣೆ",
        "my_listings": "ನನ್ನ ಪಟ್ಟಿಗಳು",
        "no_listings": "ಯಾವುದೇ ಪಟ್ಟಿಗಳು ಕಂಡುಬಂದಿಲ್ಲ",
        "clear_all": "ಎಲ್ಲವನ್ನೂ ಸಾಫ್ ಮಾಡಿ",
        "processing": "ಸಂಸ್ಕರಿಸಲಾಗುತ್ತಿದೆ...",
        "error_occurred": "ದೋಷ ಸಂಭವಿಸಿದೆ"
    },
    "tamil": {
        "app_title": "டிஜிட்டல் கேடலாக் ஏஜென்ட்",
        "subtitle": "AI உடன் தொழில்முறை தயாரிப்பு பட்டியல்களை உருவாக்கவும்",
        "product_name": "தயாரிப்பு பெயர்",
        "quantity": "அளவு",
        "price": "விலை (₹)",
        "additional_info": "கூடுதல் தகவல் (விருப்பம்)",
        "generate_listing": "பட்டியல் உருவாக்கவும்",
        "product_listing": "தயாரிப்பு பட்டியல் உருவாக்கப்பட்டது",
        "description": "விளக்கம்",
        "tags": "குறிச்சொற்கள்",
        "category": "வகை",
        "price_breakdown": "விலை விவரம்",
        "my_listings": "என் பட்டியல்கள்",
        "no_listings": "பட்டியல்கள் எதுவும் கிடைக்கவில்லை",
        "clear_all": "அனைத்தையும் அழிக்கவும்",
        "processing": "செயலாக்கம்...",
        "error_occurred": "ஒரு பிழை நேர்ந்தது"
    },
    "telugu": {
        "app_title": "డిజిటల్ కేటలాగ్ ఏజెంట్",
        "subtitle": "AI తో వృత్తిపరమైన ఉత్పత్తి జాబితాలను సృష్టించండి",
        "product_name": "ఉత్పత్తి పేరు",
        "quantity": "పరిమాణం",
        "price": "ధర (₹)",
        "additional_info": "అదనపు సమాచారం (ఐచ్ఛికం)",
        "generate_listing": "జాబితాను సృష్టించండి",
        "product_listing": "ఉత్పత్తి జాబితా సృష్టించబడింది",
        "description": "వివరణ",
        "tags": "ట్యాగ్‌లు",
        "category": "వర్గం",
        "price_breakdown": "ధర వివరణ",
        "my_listings": "నా జాబితాలు",
        "no_listings": "జాబితాలు కనుగొనబడలేదు",
        "clear_all": "అన్నీ క్లియర్ చేయండి",
        "processing": "ప్రాసెసింగ్...",
        "error_occurred": "ఒక లోపం సంభవించింది"
    },
    "malayalam": {
        "app_title": "ഡിജിറ്റൽ കാറ്റലോഗ് ഏജന്റ്",
        "subtitle": "AI ഉപയോഗിച്ച് പ്രൊഫഷണൽ ഉൽപ്പന്ന ലിസ്റ്റിംഗുകൾ സൃഷ്ടിക്കുക",
        "product_name": "ഉൽപ്പന്ന നാമം",
        "quantity": "അളവ്",
        "price": "വില (₹)",
        "additional_info": "അധിക വിവരങ്ങൾ (ഓപ്ഷണൽ)",
        "generate_listing": "ലിസ്റ്റിംഗ് ജനറേറ്റ് ചെയ്യുക",
        "product_listing": "ഉൽപ്പന്ന ലിസ്റ്റിംഗ് ജനറേറ്റ് ചെയ്തു",
        "description": "വിവരണം",
        "tags": "ടാഗുകൾ",
        "category": "വിഭാഗം",
        "price_breakdown": "വില വിശദീകരണം",
        "my_listings": "എന്റെ ലിസ്റ്റിംഗുകൾ",
        "no_listings": "ലിസ്റ്റിംഗുകളൊന്നും കണ്ടെത്തിയില്ല",
        "clear_all": "എല്ലാം മായ്ക്കുക",
        "processing": "പ്രോസസ്സിംഗ്...",
        "error_occurred": "ഒരു പിശക് സംഭവിച്ചു"
    }
}

# Helper functions
def calculate_price_breakdown(base_price: float, quantity: str) -> Dict[str, float]:
    """Calculate price breakdown for common quantities"""
    breakdown = {}
    
    # Extract numeric value from quantity string
    try:
        if "kg" in quantity.lower():
            base_kg = float(quantity.lower().replace("kg", "").strip())
            breakdown["1 kg"] = round(base_price / base_kg, 2)
            breakdown["½ kg"] = round(breakdown["1 kg"] / 2, 2)
            breakdown["¼ kg"] = round(breakdown["1 kg"] / 4, 2)
        elif "piece" in quantity.lower() or "pcs" in quantity.lower():
            base_pcs = float(quantity.lower().replace("piece", "").replace("pcs", "").strip())
            breakdown["1 piece"] = round(base_price / base_pcs, 2)
            breakdown["5 pieces"] = round(breakdown["1 piece"] * 5, 2)
            breakdown["10 pieces"] = round(breakdown["1 piece"] * 10, 2)
        else:
            breakdown[f"1 {quantity}"] = base_price
    except:
        breakdown[f"1 {quantity}"] = base_price
    
    return breakdown

def extract_product_info(ai_response: str) -> Dict[str, Any]:
    """Extract structured info from AI response"""
    try:
        # Simple parsing - in real app, this would be more sophisticated
        lines = ai_response.split('\n')
        
        description = ""
        tags = []
        category = ""
        
        for line in lines:
            line = line.strip()
            if line.startswith("Description:"):
                description = line.replace("Description:", "").strip()
            elif line.startswith("Tags:"):
                tags_str = line.replace("Tags:", "").strip()
                tags = [tag.strip() for tag in tags_str.split(",")]
            elif line.startswith("Category:"):
                category = line.replace("Category:", "").strip()
        
        return {
            "description": description,
            "tags": tags,
            "category": category
        }
    except:
        return {
            "description": ai_response,
            "tags": [],
            "category": "General"
        }

# Initialize Gemini AI
async def init_gemini():
    """Initialize Gemini AI client"""
    global gemini_chat
    try:
        # Import here to avoid issues if not installed
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        
        gemini_chat = LlmChat(
            api_key=os.environ.get('GEMINI_API_KEY'),
            session_id="catalog-agent",
            system_message="""You are an AI assistant helping rural farmers, artisans, and small shop owners create professional product listings. 

Your task is to:
1. Generate professional product descriptions based on basic input
2. Suggest relevant tags for the product
3. Recommend appropriate categories
4. Handle multiple Indian languages (Hindi, Kannada, Tamil, Telugu, Malayalam)

Input format: Product name, quantity, price, and optional additional information.

Output format:
Description: [Professional product description]
Tags: [comma-separated relevant tags]
Category: [suggested category path like "Grocery > Vegetables" or "Handicrafts > Textiles"]

Keep descriptions concise but appealing, suitable for online marketplaces."""
        ).with_model("gemini", "gemini-2.0-flash")
        
        return True
    except Exception as e:
        print(f"Failed to initialize Gemini: {e}")
        return False

# Global variable for Gemini chat
gemini_chat = None

# API Routes
@api_router.get("/")
async def root():
    return {"message": "Digital Catalog Agent API"}

@api_router.get("/languages")
async def get_languages():
    """Get available languages and their content"""
    return {"languages": list(LANGUAGE_CONTENT.keys()), "content": LANGUAGE_CONTENT}

@api_router.get("/language/{language}")
async def get_language_content(language: str):
    """Get content for a specific language"""
    if language not in LANGUAGE_CONTENT:
        raise HTTPException(status_code=404, detail="Language not found")
    return {"language": language, "content": LANGUAGE_CONTENT[language]}

@api_router.post("/generate-listing")
async def generate_product_listing(product_input: ProductInput):
    """Generate AI-powered product listing"""
    try:
        # Initialize Gemini if not already done
        if gemini_chat is None:
            initialized = await init_gemini()
            if not initialized:
                raise HTTPException(status_code=500, detail="AI service not available")
        
        # Create session ID if not provided
        session_id = product_input.session_id or str(uuid.uuid4())
        
        # Prepare input for AI
        ai_input = f"""
        Product Name: {product_input.name}
        Quantity: {product_input.quantity}
        Price: ₹{product_input.price}
        Language: {product_input.language}
        Additional Info: {product_input.additional_info or 'None'}
        
        Please generate a professional product listing with description, tags, and category.
        """
        
        # Get AI response
        from emergentintegrations.llm.chat import UserMessage
        user_message = UserMessage(text=ai_input)
        ai_response = await gemini_chat.send_message(user_message)
        
        # Extract structured information
        product_info = extract_product_info(ai_response)
        
        # Calculate price breakdown
        price_breakdown = calculate_price_breakdown(product_input.price, product_input.quantity)
        
        # Create product listing
        listing = ProductListing(
            name=product_input.name,
            quantity=product_input.quantity,
            price=product_input.price,
            price_breakdown=price_breakdown,
            description=product_info["description"],
            tags=product_info["tags"],
            category=product_info["category"],
            language=product_input.language,
            session_id=session_id,
            original_input=ai_input
        )
        
        # Save to database
        await db.product_listings.insert_one(listing.dict())
        
        return listing
        
    except Exception as e:
        print(f"Error generating listing: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/listings/{session_id}")
async def get_listings(session_id: str):
    """Get all listings for a session"""
    try:
        listings = await db.product_listings.find({"session_id": session_id}).to_list(100)
        return [ProductListing(**listing) for listing in listings]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.delete("/listings/{session_id}")
async def clear_listings(session_id: str):
    """Clear all listings for a session"""
    try:
        result = await db.product_listings.delete_many({"session_id": session_id})
        return {"deleted_count": result.deleted_count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/translate")
async def translate_text(translation_request: TranslationRequest):
    """Translate text between languages using Gemini"""
    try:
        if gemini_chat is None:
            initialized = await init_gemini()
            if not initialized:
                raise HTTPException(status_code=500, detail="AI service not available")
        
        # Create translation prompt
        prompt = f"""
        Translate the following text from {translation_request.from_language} to {translation_request.to_language}:
        
        Text: {translation_request.text}
        
        Please provide only the translation, no additional text.
        """
        
        from emergentintegrations.llm.chat import UserMessage
        user_message = UserMessage(text=prompt)
        translated_text = await gemini_chat.send_message(user_message)
        
        return {"translated_text": translated_text.strip()}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("Starting Digital Catalog Agent API...")
    await init_gemini()

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()