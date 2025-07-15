#!/usr/bin/env python3
"""
Comprehensive Backend Testing for AI Catalog Assistant
Tests all backend functionality including authentication, products, voice commands, AI features, and orders.
"""

import requests
import json
import time
import asyncio
import websockets
from datetime import datetime
import base64

# Configuration
BASE_URL = "https://037d5400-7702-4ee0-b730-79f440f43271.preview.emergentagent.com/api"
WS_URL = "wss://037d5400-7702-4ee0-b730-79f440f43271.preview.emergentagent.com/api/ws"

class BackendTester:
    def __init__(self):
        self.base_url = BASE_URL
        self.ws_url = WS_URL
        self.seller_token = None
        self.consumer_token = None
        self.seller_id = None
        self.consumer_id = None
        self.test_product_id = None
        self.test_order_id = None
        
    def log(self, message, status="INFO"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{status}] {message}")
        
    def test_health_check(self):
        """Test basic health check endpoint"""
        self.log("Testing health check endpoint...")
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.log(f"Health check passed: {data}", "SUCCESS")
                return True
            else:
                self.log(f"Health check failed with status {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"Health check failed: {str(e)}", "ERROR")
            return False
    
    def test_user_signup(self):
        """Test user signup for both seller and consumer"""
        self.log("Testing user signup...")
        
        # Test seller signup
        seller_data = {
            "username": "राज पटेल",
            "email": "raj.patel@example.com", 
            "password": "securepass123",
            "role": "seller",
            "language": "hi"
        }
        
        try:
            response = requests.post(f"{self.base_url}/auth/signup", json=seller_data, timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.seller_token = data["token"]
                self.seller_id = data["user"]["id"]
                self.log(f"Seller signup successful: {data['user']['username']}", "SUCCESS")
                seller_success = True
            else:
                self.log(f"Seller signup failed: {response.status_code} - {response.text}", "ERROR")
                seller_success = False
        except Exception as e:
            self.log(f"Seller signup failed: {str(e)}", "ERROR")
            seller_success = False
        
        # Test consumer signup
        consumer_data = {
            "username": "प्रिया शर्मा",
            "email": "priya.sharma@example.com",
            "password": "securepass456", 
            "role": "consumer",
            "language": "hi"
        }
        
        try:
            response = requests.post(f"{self.base_url}/auth/signup", json=consumer_data, timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.consumer_token = data["token"]
                self.consumer_id = data["user"]["id"]
                self.log(f"Consumer signup successful: {data['user']['username']}", "SUCCESS")
                consumer_success = True
            else:
                self.log(f"Consumer signup failed: {response.status_code} - {response.text}", "ERROR")
                consumer_success = False
        except Exception as e:
            self.log(f"Consumer signup failed: {str(e)}", "ERROR")
            consumer_success = False
            
        return seller_success and consumer_success
    
    def test_user_login(self):
        """Test user login functionality"""
        self.log("Testing user login...")
        
        login_data = {
            "email": "raj.patel@example.com",
            "password": "securepass123"
        }
        
        try:
            response = requests.post(f"{self.base_url}/auth/login", json=login_data, timeout=10)
            if response.status_code == 200:
                data = response.json()
                token = data["token"]
                self.log(f"Login successful for user: {data['user']['username']}", "SUCCESS")
                
                # Verify token works
                headers = {"Authorization": f"Bearer {token}"}
                test_response = requests.get(f"{self.base_url}/products", headers=headers, timeout=10)
                if test_response.status_code in [200, 403]:  # 403 is ok for role-based access
                    self.log("JWT token validation successful", "SUCCESS")
                    return True
                else:
                    self.log(f"JWT token validation failed: {test_response.status_code}", "ERROR")
                    return False
            else:
                self.log(f"Login failed: {response.status_code} - {response.text}", "ERROR")
                return False
        except Exception as e:
            self.log(f"Login failed: {str(e)}", "ERROR")
            return False
    
    def test_product_creation(self):
        """Test product creation with AI image generation"""
        self.log("Testing product creation...")
        
        if not self.seller_token:
            self.log("No seller token available for product creation", "ERROR")
            return False
        
        product_data = {
            "name": "टमाटर",
            "quantity": 50.0,
            "unit": "kg",
            "price_per_unit": 40.0,
            "description": "ताजे लाल टमाटर, स्थानीय खेत से",
            "tags": ["vegetables", "fresh", "tomatoes"],
            "seller_id": self.seller_id,
            "language": "hi"
        }
        
        headers = {"Authorization": f"Bearer {self.seller_token}"}
        
        try:
            response = requests.post(f"{self.base_url}/products", json=product_data, headers=headers, timeout=30)
            if response.status_code == 200:
                data = response.json()
                self.test_product_id = data["product_id"]
                self.log(f"Product created successfully: {self.test_product_id}", "SUCCESS")
                
                # Verify price breakdown calculation
                if "price_breakdown" in data:
                    breakdown = data["price_breakdown"]
                    expected_half = round(40.0 / 2, 2)
                    expected_quarter = round(40.0 / 4, 2)
                    
                    if (breakdown["1_kg"] == 40.0 and 
                        breakdown["half_kg"] == expected_half and 
                        breakdown["quarter_kg"] == expected_quarter):
                        self.log("Price breakdown calculation correct", "SUCCESS")
                    else:
                        self.log(f"Price breakdown incorrect: {breakdown}", "ERROR")
                        return False
                
                # Verify QR code generation
                if "qr_code" in data and data["qr_code"]:
                    self.log("QR code generated successfully", "SUCCESS")
                else:
                    self.log("QR code generation failed", "ERROR")
                    return False
                    
                return True
            else:
                self.log(f"Product creation failed: {response.status_code} - {response.text}", "ERROR")
                return False
        except Exception as e:
            self.log(f"Product creation failed: {str(e)}", "ERROR")
            return False
    
    def test_product_management(self):
        """Test product CRUD operations"""
        self.log("Testing product management operations...")
        
        if not self.seller_token or not self.test_product_id:
            self.log("Prerequisites not met for product management test", "ERROR")
            return False
        
        headers = {"Authorization": f"Bearer {self.seller_token}"}
        
        # Test GET products
        try:
            response = requests.get(f"{self.base_url}/products", headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                products = data.get("products", [])
                self.log(f"Retrieved {len(products)} products", "SUCCESS")
                
                # Find our test product
                test_product = None
                for product in products:
                    if product["_id"] == self.test_product_id:
                        test_product = product
                        break
                
                if not test_product:
                    self.log("Test product not found in product list", "ERROR")
                    return False
            else:
                self.log(f"Get products failed: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"Get products failed: {str(e)}", "ERROR")
            return False
        
        # Test GET single product
        try:
            response = requests.get(f"{self.base_url}/products/{self.test_product_id}", headers=headers, timeout=10)
            if response.status_code == 200:
                product = response.json()
                self.log(f"Retrieved single product: {product['name']}", "SUCCESS")
            else:
                self.log(f"Get single product failed: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"Get single product failed: {str(e)}", "ERROR")
            return False
        
        # Test UPDATE product
        update_data = {
            "name": "टमाटर - प्रीमियम",
            "quantity": 45.0,
            "unit": "kg", 
            "price_per_unit": 45.0,
            "description": "प्रीमियम गुणवत्ता के ताजे टमाटर",
            "tags": ["vegetables", "fresh", "tomatoes", "premium"],
            "seller_id": self.seller_id,
            "language": "hi"
        }
        
        try:
            response = requests.put(f"{self.base_url}/products/{self.test_product_id}", 
                                  json=update_data, headers=headers, timeout=10)
            if response.status_code == 200:
                self.log("Product updated successfully", "SUCCESS")
            else:
                self.log(f"Product update failed: {response.status_code} - {response.text}", "ERROR")
                return False
        except Exception as e:
            self.log(f"Product update failed: {str(e)}", "ERROR")
            return False
        
        return True
    
    def test_voice_command_processing(self):
        """Test voice command processing with AI"""
        self.log("Testing voice command processing...")
        
        if not self.seller_token:
            self.log("No seller token available for voice command test", "ERROR")
            return False
        
        voice_commands = [
            {
                "command": "5 किलो टमाटर ₹40 में जोड़ें",
                "language": "hi",
                "seller_id": self.seller_id
            },
            {
                "command": "Add 3 kg onions at ₹30 per kg",
                "language": "en", 
                "seller_id": self.seller_id
            },
            {
                "command": "स्टॉक चेक करें",
                "language": "hi",
                "seller_id": self.seller_id
            }
        ]
        
        headers = {"Authorization": f"Bearer {self.seller_token}"}
        
        for i, voice_cmd in enumerate(voice_commands):
            try:
                response = requests.post(f"{self.base_url}/voice/process", 
                                       json=voice_cmd, headers=headers, timeout=20)
                if response.status_code == 200:
                    data = response.json()
                    self.log(f"Voice command {i+1} processed successfully", "SUCCESS")
                    self.log(f"AI Response: {data.get('message', 'No message')[:100]}...", "INFO")
                    
                    # Check if action was detected
                    if data.get("action"):
                        self.log(f"Action detected: {data['action']}", "SUCCESS")
                    
                    # Check language consistency
                    if data.get("language") == voice_cmd["language"]:
                        self.log("Language consistency maintained", "SUCCESS")
                    else:
                        self.log(f"Language mismatch: expected {voice_cmd['language']}, got {data.get('language')}", "ERROR")
                        
                else:
                    self.log(f"Voice command {i+1} failed: {response.status_code} - {response.text}", "ERROR")
                    return False
            except Exception as e:
                self.log(f"Voice command {i+1} failed: {str(e)}", "ERROR")
                return False
        
        return True
    
    def test_order_management(self):
        """Test order creation and management"""
        self.log("Testing order management...")
        
        if not self.consumer_token or not self.test_product_id:
            self.log("Prerequisites not met for order management test", "ERROR")
            return False
        
        # Create order
        order_data = {
            "product_id": self.test_product_id,
            "quantity": 2.0,
            "consumer_id": self.consumer_id,
            "seller_id": self.seller_id,
            "total_price": 90.0,  # 2kg * 45/kg
            "status": "pending"
        }
        
        headers = {"Authorization": f"Bearer {self.consumer_token}"}
        
        try:
            response = requests.post(f"{self.base_url}/orders", json=order_data, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.test_order_id = data["order_id"]
                self.log(f"Order created successfully: {self.test_order_id}", "SUCCESS")
            else:
                self.log(f"Order creation failed: {response.status_code} - {response.text}", "ERROR")
                return False
        except Exception as e:
            self.log(f"Order creation failed: {str(e)}", "ERROR")
            return False
        
        # Test order history for consumer
        try:
            response = requests.get(f"{self.base_url}/orders", headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                orders = data.get("orders", [])
                self.log(f"Consumer retrieved {len(orders)} orders", "SUCCESS")
                
                # Find our test order
                test_order = None
                for order in orders:
                    if order["_id"] == self.test_order_id:
                        test_order = order
                        break
                
                if test_order:
                    self.log("Test order found in consumer order history", "SUCCESS")
                else:
                    self.log("Test order not found in consumer order history", "ERROR")
                    return False
            else:
                self.log(f"Get consumer orders failed: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"Get consumer orders failed: {str(e)}", "ERROR")
            return False
        
        # Test order history for seller
        seller_headers = {"Authorization": f"Bearer {self.seller_token}"}
        try:
            response = requests.get(f"{self.base_url}/orders", headers=seller_headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                orders = data.get("orders", [])
                self.log(f"Seller retrieved {len(orders)} orders", "SUCCESS")
                
                # Find our test order
                test_order = None
                for order in orders:
                    if order["_id"] == self.test_order_id:
                        test_order = order
                        break
                
                if test_order:
                    self.log("Test order found in seller order history", "SUCCESS")
                else:
                    self.log("Test order not found in seller order history", "ERROR")
                    return False
            else:
                self.log(f"Get seller orders failed: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"Get seller orders failed: {str(e)}", "ERROR")
            return False
        
        return True
    
    def test_ai_suggestions(self):
        """Test AI suggestions for sellers"""
        self.log("Testing AI suggestions...")
        
        if not self.seller_token:
            self.log("No seller token available for AI suggestions test", "ERROR")
            return False
        
        headers = {"Authorization": f"Bearer {self.seller_token}"}
        
        try:
            response = requests.get(f"{self.base_url}/suggestions", headers=headers, timeout=20)
            if response.status_code == 200:
                data = response.json()
                suggestions = data.get("suggestions", "")
                language = data.get("language", "")
                
                if suggestions and len(suggestions) > 50:  # Reasonable suggestion length
                    self.log("AI suggestions generated successfully", "SUCCESS")
                    self.log(f"Suggestion preview: {suggestions[:100]}...", "INFO")
                    self.log(f"Response language: {language}", "INFO")
                    return True
                else:
                    self.log("AI suggestions too short or empty", "ERROR")
                    return False
            else:
                self.log(f"AI suggestions failed: {response.status_code} - {response.text}", "ERROR")
                return False
        except Exception as e:
            self.log(f"AI suggestions failed: {str(e)}", "ERROR")
            return False
    
    def test_websocket_connection(self):
        """Test WebSocket real-time updates"""
        self.log("Testing WebSocket connection...")
        
        if not self.seller_id:
            self.log("No seller ID available for WebSocket test", "ERROR")
            return False
        
        async def test_ws():
            try:
                uri = f"{self.ws_url}/{self.seller_id}"
                async with websockets.connect(uri, timeout=10) as websocket:
                    self.log("WebSocket connection established", "SUCCESS")
                    
                    # Send a test message
                    await websocket.send("test message")
                    
                    # Wait for response
                    try:
                        response = await asyncio.wait_for(websocket.recv(), timeout=5)
                        data = json.loads(response)
                        
                        if data.get("type") == "inventory_update":
                            self.log("WebSocket real-time update received", "SUCCESS")
                            return True
                        else:
                            self.log(f"Unexpected WebSocket response: {data}", "ERROR")
                            return False
                    except asyncio.TimeoutError:
                        self.log("WebSocket response timeout", "ERROR")
                        return False
                        
            except Exception as e:
                self.log(f"WebSocket connection failed: {str(e)}", "ERROR")
                return False
        
        try:
            return asyncio.run(test_ws())
        except Exception as e:
            self.log(f"WebSocket test failed: {str(e)}", "ERROR")
            return False
    
    def test_product_deletion(self):
        """Test product deletion (cleanup)"""
        self.log("Testing product deletion...")
        
        if not self.seller_token or not self.test_product_id:
            self.log("Prerequisites not met for product deletion test", "ERROR")
            return False
        
        headers = {"Authorization": f"Bearer {self.seller_token}"}
        
        try:
            response = requests.delete(f"{self.base_url}/products/{self.test_product_id}", 
                                     headers=headers, timeout=10)
            if response.status_code == 200:
                self.log("Product deleted successfully", "SUCCESS")
                return True
            else:
                self.log(f"Product deletion failed: {response.status_code} - {response.text}", "ERROR")
                return False
        except Exception as e:
            self.log(f"Product deletion failed: {str(e)}", "ERROR")
            return False
    
    def run_all_tests(self):
        """Run all backend tests"""
        self.log("Starting comprehensive backend testing...", "INFO")
        self.log("="*60, "INFO")
        
        test_results = {}
        
        # Test sequence
        tests = [
            ("Health Check", self.test_health_check),
            ("User Signup", self.test_user_signup),
            ("User Login", self.test_user_login),
            ("Product Creation", self.test_product_creation),
            ("Product Management", self.test_product_management),
            ("Voice Command Processing", self.test_voice_command_processing),
            ("Order Management", self.test_order_management),
            ("AI Suggestions", self.test_ai_suggestions),
            ("WebSocket Connection", self.test_websocket_connection),
            ("Product Deletion", self.test_product_deletion)
        ]
        
        for test_name, test_func in tests:
            self.log(f"\n--- Running {test_name} Test ---", "INFO")
            try:
                result = test_func()
                test_results[test_name] = result
                status = "PASSED" if result else "FAILED"
                self.log(f"{test_name}: {status}", status if result else "ERROR")
            except Exception as e:
                test_results[test_name] = False
                self.log(f"{test_name}: FAILED - {str(e)}", "ERROR")
            
            time.sleep(1)  # Brief pause between tests
        
        # Summary
        self.log("\n" + "="*60, "INFO")
        self.log("TEST SUMMARY", "INFO")
        self.log("="*60, "INFO")
        
        passed = sum(1 for result in test_results.values() if result)
        total = len(test_results)
        
        for test_name, result in test_results.items():
            status = "✅ PASSED" if result else "❌ FAILED"
            self.log(f"{test_name}: {status}", "INFO")
        
        self.log(f"\nOverall: {passed}/{total} tests passed", "INFO")
        
        if passed == total:
            self.log("🎉 ALL TESTS PASSED! Backend is working correctly.", "SUCCESS")
        else:
            self.log(f"⚠️  {total - passed} tests failed. Backend needs attention.", "ERROR")
        
        return test_results

if __name__ == "__main__":
    tester = BackendTester()
    results = tester.run_all_tests()