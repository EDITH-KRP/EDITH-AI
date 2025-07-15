import requests
import sys
import json
from datetime import datetime

class VoiceCatalogAPITester:
    def __init__(self, base_url="https://289abe84-7de6-45db-899e-23de90da1f2f.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.test_products = []

    def run_test(self, name, method, endpoint, expected_status, data=None, params=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"   Response: {json.dumps(response_data, indent=2)[:200]}...")
                    return True, response_data
                except:
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_health_check(self):
        """Test health check endpoint"""
        success, response = self.run_test(
            "Health Check",
            "GET",
            "api/health",
            200
        )
        return success and response.get('status') == 'healthy'

    def test_create_product(self, name, quantity, price_per_kg, description="Test product"):
        """Test creating a product"""
        product_data = {
            "name": name,
            "quantity": quantity,
            "price_per_kg": price_per_kg,
            "description": description,
            "category": "Test"
        }
        
        success, response = self.run_test(
            f"Create Product - {name}",
            "POST",
            "api/products",
            200,
            data=product_data
        )
        
        if success:
            self.test_products.append(name.lower())
            # Verify response structure
            expected_fields = ['product', 'quantity', 'price_per_kg', 'breakdown', 'low_stock']
            for field in expected_fields:
                if field not in response:
                    print(f"⚠️  Missing field in response: {field}")
                    return False
            
            # Verify price breakdown
            breakdown = response.get('breakdown', {})
            if not all(key in breakdown for key in ['1kg', 'half_kg', 'quarter_kg']):
                print(f"⚠️  Invalid price breakdown: {breakdown}")
                return False
                
            print(f"   Price breakdown: 1kg=₹{breakdown['1kg']}, ½kg=₹{breakdown['half_kg']}, ¼kg=₹{breakdown['quarter_kg']}")
            
            # Check stock alert logic
            if quantity <= 2.0 and not response.get('low_stock'):
                print(f"⚠️  Low stock alert not triggered for quantity {quantity}")
            elif quantity > 2.0 and response.get('low_stock'):
                print(f"⚠️  Low stock alert incorrectly triggered for quantity {quantity}")
                
        return success

    def test_list_products(self):
        """Test listing all products"""
        success, response = self.run_test(
            "List Products",
            "GET",
            "api/products",
            200
        )
        
        if success:
            # Verify response structure
            expected_fields = ['products', 'total_products', 'low_stock_alerts']
            for field in expected_fields:
                if field not in response:
                    print(f"⚠️  Missing field in response: {field}")
                    return False
            
            products = response.get('products', [])
            total = response.get('total_products', 0)
            alerts = response.get('low_stock_alerts', [])
            
            print(f"   Found {total} products, {len(alerts)} low stock alerts")
            
            # Verify each product has required fields
            for product in products:
                required_fields = ['product', 'quantity', 'price_per_kg', 'breakdown', 'low_stock']
                for field in required_fields:
                    if field not in product:
                        print(f"⚠️  Product missing field: {field}")
                        return False
        
        return success

    def test_update_product(self, product_name, quantity=None, price_per_kg=None):
        """Test updating a product"""
        update_data = {}
        if quantity is not None:
            update_data['quantity'] = quantity
        if price_per_kg is not None:
            update_data['price_per_kg'] = price_per_kg
            
        success, response = self.run_test(
            f"Update Product - {product_name}",
            "PUT",
            f"api/products/{product_name}",
            200,
            data=update_data
        )
        
        if success:
            # Verify updated values
            if quantity is not None and response.get('quantity') != quantity:
                print(f"⚠️  Quantity not updated correctly: expected {quantity}, got {response.get('quantity')}")
                return False
            if price_per_kg is not None and response.get('price_per_kg') != price_per_kg:
                print(f"⚠️  Price not updated correctly: expected {price_per_kg}, got {response.get('price_per_kg')}")
                return False
                
        return success

    def test_delete_product(self, product_name):
        """Test deleting a product"""
        success, response = self.run_test(
            f"Delete Product - {product_name}",
            "DELETE",
            f"api/products/{product_name}",
            200
        )
        
        if success and product_name.lower() in self.test_products:
            self.test_products.remove(product_name.lower())
            
        return success

    def test_voice_command(self, command, language="en", expected_action=None):
        """Test voice command processing"""
        command_data = {
            "command": command,
            "language": language
        }
        
        success, response = self.run_test(
            f"Voice Command ({language.upper()}) - {command[:30]}...",
            "POST",
            "api/voice-command",
            200,
            data=command_data
        )
        
        if success:
            print(f"   Command processed successfully")
            if 'error' in response:
                print(f"⚠️  Command returned error: {response['error']}")
                return False
            
            # Check if response has expected language
            if response.get('language') != language:
                print(f"⚠️  Response language mismatch: expected {language}, got {response.get('language')}")
                
        return success

    def test_voice_commands_comprehensive(self):
        """Test various voice commands"""
        commands = [
            ("Add 5 kg tomato at ₹50", "en", "add"),
            ("Update tomato price to ₹60", "en", "update_price"),
            ("Remove 2 kg tomato", "en", "remove"),
            ("List all products", "en", "list"),
            ("Delete tomato", "en", "delete")
        ]
        
        all_passed = True
        for command, language, expected_action in commands:
            if not self.test_voice_command(command, language, expected_action):
                all_passed = False
                
        return all_passed

    def test_multilanguage_voice_commands(self):
        """Test voice commands in different languages"""
        print(f"\n🌍 Testing Multi-Language Voice Commands...")
        
        # Test commands in different languages
        multilang_commands = [
            # English
            ("Add 5 kg tomato at ₹50", "en"),
            ("Add 3 kg onion at ₹30", "en"),
            
            # Hindi
            ("5 किलो टमाटर 50 रुपये जोड़ो", "hi"),
            ("3 किलो प्याज 30 रुपये जोड़ो", "hi"),
            ("टमाटर कीमत 60 रुपये अपडेट करो", "hi"),
            
            # Kannada
            ("5 ಕಿಲೋ ಟೊಮೇಟೊ 50 ರೂಪಾಯಿ ಸೇರಿಸಿ", "kn"),
            ("3 ಕಿಲೋ ಈರುಳ್ಳಿ 30 ರೂಪಾಯಿ ಸೇರಿಸಿ", "kn"),
            
            # Tamil
            ("5 கிலோ தக்காளி 50 ரூபாய் சேர்", "ta"),
            ("3 கிலோ வெங்காயம் 30 ரூபாய் சேர்", "ta"),
            
            # Telugu
            ("5 కిలో టమాట 50 రూపాయలు చేర్చు", "te"),
            ("3 కிలో ఉల్లిపాయ 30 రూపాయలు చేర్చు", "te"),
        ]
        
        all_passed = True
        for command, language in multilang_commands:
            if not self.test_voice_command(command, language):
                all_passed = False
                
        return all_passed

    def test_translation_functionality(self):
        """Test regional language translation to English"""
        print(f"\n🔤 Testing Translation Functionality...")
        
        # Test translation by comparing similar commands in different languages
        translation_tests = [
            # Hindi to English equivalents
            ("5 किलो टमाटर 50 रुपये जोड़ो", "hi", "Add 5 kg tomato at ₹50", "en"),
            ("प्याज कीमत 40 रुपये अपडेट करो", "hi", "Update onion price to ₹40", "en"),
            
            # Kannada to English equivalents  
            ("5 ಕಿಲೋ ಟೊಮೇಟೊ 50 ರೂಪಾಯಿ ಸೇರಿಸಿ", "kn", "Add 5 kg tomato at ₹50", "en"),
            
            # Tamil to English equivalents
            ("5 கிலோ தக்காளி 50 ரூபாய் சேர்", "ta", "Add 5 kg tomato at ₹50", "en"),
            
            # Telugu to English equivalents
            ("5 కిలో టమాట 50 రూపాయలు చేర్చు", "te", "Add 5 kg tomato at ₹50", "en"),
        ]
        
        all_passed = True
        for regional_cmd, regional_lang, english_cmd, english_lang in translation_tests:
            print(f"\n   Testing translation: {regional_lang.upper()} -> {english_lang.upper()}")
            print(f"   Regional: {regional_cmd}")
            print(f"   English:  {english_cmd}")
            
            # Test regional command
            success1, response1 = self.test_voice_command(regional_cmd, regional_lang)
            
            # Clean up any created products before testing English equivalent
            if success1 and 'product' in response1:
                self.test_delete_product(response1['product'])
            
            # Test English equivalent
            success2, response2 = self.test_voice_command(english_cmd, english_lang)
            
            if success1 and success2:
                print(f"   ✅ Both commands processed successfully")
            else:
                print(f"   ❌ Translation test failed")
                all_passed = False
                
        return all_passed

    def test_error_handling(self):
        """Test error handling scenarios"""
        print(f"\n🔍 Testing Error Handling...")
        
        # Test creating duplicate product
        success, _ = self.run_test(
            "Create Duplicate Product",
            "POST",
            "api/products",
            400,  # Should return 400 for duplicate
            data={"name": "tomato", "quantity": 5, "price_per_kg": 50}
        )
        
        # Test updating non-existent product
        success2, _ = self.run_test(
            "Update Non-existent Product",
            "PUT",
            "api/products/nonexistent",
            404,  # Should return 404
            data={"quantity": 10}
        )
        
        # Test deleting non-existent product
        success3, _ = self.run_test(
            "Delete Non-existent Product",
            "DELETE",
            "api/products/nonexistent",
            404  # Should return 404
        )
        
        return success and success2 and success3

def main():
    print("🚀 Starting Voice Catalog API Tests...")
    print("=" * 60)
    
    tester = VoiceCatalogAPITester()
    
    # Test sequence
    tests = [
        ("Health Check", tester.test_health_check),
        ("Create Product - Apple", lambda: tester.test_create_product("apple", 10, 100)),
        ("Create Product - Banana (Low Stock)", lambda: tester.test_create_product("banana", 1.5, 80)),
        ("List Products", tester.test_list_products),
        ("Update Apple Price", lambda: tester.test_update_product("apple", price_per_kg=120)),
        ("Update Banana Quantity", lambda: tester.test_update_product("banana", quantity=5)),
        ("Voice Commands", tester.test_voice_commands_comprehensive),
        ("Error Handling", tester.test_error_handling),
        ("Delete Apple", lambda: tester.test_delete_product("apple")),
        ("Delete Banana", lambda: tester.test_delete_product("banana")),
    ]
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            if not result:
                print(f"❌ {test_name} failed")
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {str(e)}")
    
    # Final results
    print(f"\n{'='*60}")
    print(f"📊 FINAL RESULTS")
    print(f"{'='*60}")
    print(f"Tests passed: {tester.tests_passed}/{tester.tests_run}")
    print(f"Success rate: {(tester.tests_passed/tester.tests_run)*100:.1f}%")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())