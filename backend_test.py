#!/usr/bin/env python3
"""
Comprehensive Backend Testing for Digital Catalog Agent
Tests all API endpoints and functionality as specified in test_result.md
"""

import requests
import json
import uuid
import time
from typing import Dict, Any, List

# Backend URL from frontend/.env
BACKEND_URL = "https://8ebecb1a-c376-4089-8457-dbe54a3fbf93.preview.emergentagent.com/api"

class DigitalCatalogTester:
    def __init__(self):
        self.session_id = str(uuid.uuid4())
        self.test_results = {}
        
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log test results"""
        self.test_results[test_name] = {
            "success": success,
            "details": details
        }
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")
        print()

    def test_root_endpoint(self):
        """Test basic API root endpoint"""
        try:
            response = requests.get(f"{BACKEND_URL}/")
            if response.status_code == 200:
                data = response.json()
                if "message" in data:
                    self.log_test("Root endpoint", True, f"Response: {data['message']}")
                else:
                    self.log_test("Root endpoint", False, "Missing message in response")
            else:
                self.log_test("Root endpoint", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_test("Root endpoint", False, f"Exception: {str(e)}")

    def test_languages_endpoint(self):
        """Test /api/languages endpoint"""
        try:
            response = requests.get(f"{BACKEND_URL}/languages")
            if response.status_code == 200:
                data = response.json()
                expected_languages = ["english", "hindi", "kannada", "tamil", "telugu", "malayalam"]
                
                if "languages" in data and "content" in data:
                    languages = data["languages"]
                    content = data["content"]
                    
                    # Check if all expected languages are present
                    missing_languages = [lang for lang in expected_languages if lang not in languages]
                    if not missing_languages:
                        # Check if content has all languages
                        missing_content = [lang for lang in expected_languages if lang not in content]
                        if not missing_content:
                            self.log_test("Languages endpoint", True, f"All 6 languages supported: {languages}")
                        else:
                            self.log_test("Languages endpoint", False, f"Missing content for: {missing_content}")
                    else:
                        self.log_test("Languages endpoint", False, f"Missing languages: {missing_languages}")
                else:
                    self.log_test("Languages endpoint", False, "Missing 'languages' or 'content' in response")
            else:
                self.log_test("Languages endpoint", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_test("Languages endpoint", False, f"Exception: {str(e)}")

    def test_individual_language_endpoints(self):
        """Test /api/language/{language} for each supported language"""
        languages = ["english", "hindi", "kannada", "tamil", "telugu", "malayalam"]
        
        for language in languages:
            try:
                response = requests.get(f"{BACKEND_URL}/language/{language}")
                if response.status_code == 200:
                    data = response.json()
                    if "language" in data and "content" in data:
                        content = data["content"]
                        # Check for essential UI elements
                        essential_keys = ["app_title", "product_name", "quantity", "price", "generate_listing"]
                        missing_keys = [key for key in essential_keys if key not in content]
                        
                        if not missing_keys:
                            self.log_test(f"Language endpoint - {language}", True, f"All essential keys present")
                        else:
                            self.log_test(f"Language endpoint - {language}", False, f"Missing keys: {missing_keys}")
                    else:
                        self.log_test(f"Language endpoint - {language}", False, "Missing 'language' or 'content' in response")
                else:
                    self.log_test(f"Language endpoint - {language}", False, f"Status code: {response.status_code}")
            except Exception as e:
                self.log_test(f"Language endpoint - {language}", False, f"Exception: {str(e)}")

    def test_generate_listing_hindi(self):
        """Test AI-powered product description generation with Hindi input"""
        try:
            # Test with Hindi input as specified in requirements
            product_data = {
                "name": "टमाटर",  # Tomato in Hindi
                "quantity": "1 kg",
                "price": 50.0,
                "language": "hindi",
                "session_id": self.session_id,
                "additional_info": "ताजा और लाल टमाटर"  # Fresh and red tomatoes
            }
            
            response = requests.post(f"{BACKEND_URL}/generate-listing", json=product_data)
            if response.status_code == 200:
                data = response.json()
                required_fields = ["id", "name", "quantity", "price", "price_breakdown", "description", "tags", "category", "language", "session_id"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields:
                    # Check price breakdown calculation
                    price_breakdown = data.get("price_breakdown", {})
                    expected_prices = {
                        "1 kg": 50.0,
                        "½ kg": 25.0,
                        "¼ kg": 12.5
                    }
                    
                    price_correct = True
                    price_details = []
                    for qty, expected_price in expected_prices.items():
                        actual_price = price_breakdown.get(qty)
                        if actual_price is None:
                            price_correct = False
                            price_details.append(f"Missing {qty}")
                        elif abs(actual_price - expected_price) > 0.1:  # Allow small rounding differences
                            price_correct = False
                            price_details.append(f"{qty}: expected {expected_price}, got {actual_price}")
                        else:
                            price_details.append(f"{qty}: ₹{actual_price} ✓")
                    
                    if price_correct:
                        self.log_test("Generate listing - Hindi input", True, 
                                    f"AI generated listing with correct price breakdown: {'; '.join(price_details)}")
                    else:
                        self.log_test("Generate listing - Hindi input", False, 
                                    f"Price breakdown issues: {'; '.join(price_details)}")
                else:
                    self.log_test("Generate listing - Hindi input", False, f"Missing fields: {missing_fields}")
            else:
                self.log_test("Generate listing - Hindi input", False, f"Status code: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_test("Generate listing - Hindi input", False, f"Exception: {str(e)}")

    def test_generate_listing_english(self):
        """Test AI-powered product description generation with English input"""
        try:
            product_data = {
                "name": "Fresh Apples",
                "quantity": "2 kg",
                "price": 120.0,
                "language": "english",
                "session_id": self.session_id,
                "additional_info": "Organic red apples from Kashmir"
            }
            
            response = requests.post(f"{BACKEND_URL}/generate-listing", json=product_data)
            if response.status_code == 200:
                data = response.json()
                
                # Check if AI generated meaningful content
                description = data.get("description", "")
                tags = data.get("tags", [])
                category = data.get("category", "")
                
                if description and len(description) > 10:
                    if tags and len(tags) > 0:
                        if category and len(category) > 0:
                            self.log_test("Generate listing - English input", True, 
                                        f"AI generated: Description ({len(description)} chars), Tags: {tags}, Category: {category}")
                        else:
                            self.log_test("Generate listing - English input", False, "Empty category generated")
                    else:
                        self.log_test("Generate listing - English input", False, "No tags generated")
                else:
                    self.log_test("Generate listing - English input", False, "Poor or empty description generated")
            else:
                self.log_test("Generate listing - English input", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_test("Generate listing - English input", False, f"Exception: {str(e)}")

    def test_price_breakdown_calculations(self):
        """Test price breakdown calculations for different quantities"""
        test_cases = [
            {"quantity": "1 kg", "price": 50.0, "expected": {"1 kg": 50.0, "½ kg": 25.0, "¼ kg": 12.5}},
            {"quantity": "2 kg", "price": 100.0, "expected": {"1 kg": 50.0, "½ kg": 25.0, "¼ kg": 12.5}},
            {"quantity": "5 pieces", "price": 25.0, "expected": {"1 piece": 5.0, "5 pieces": 25.0, "10 pieces": 50.0}}
        ]
        
        for i, test_case in enumerate(test_cases):
            try:
                product_data = {
                    "name": f"Test Product {i+1}",
                    "quantity": test_case["quantity"],
                    "price": test_case["price"],
                    "language": "english",
                    "session_id": self.session_id
                }
                
                response = requests.post(f"{BACKEND_URL}/generate-listing", json=product_data)
                if response.status_code == 200:
                    data = response.json()
                    price_breakdown = data.get("price_breakdown", {})
                    
                    all_correct = True
                    details = []
                    for qty, expected_price in test_case["expected"].items():
                        actual_price = price_breakdown.get(qty)
                        if actual_price is None:
                            all_correct = False
                            details.append(f"Missing {qty}")
                        elif abs(actual_price - expected_price) > 0.1:
                            all_correct = False
                            details.append(f"{qty}: expected {expected_price}, got {actual_price}")
                        else:
                            details.append(f"{qty}: ₹{actual_price} ✓")
                    
                    self.log_test(f"Price breakdown - {test_case['quantity']}", all_correct, "; ".join(details))
                else:
                    self.log_test(f"Price breakdown - {test_case['quantity']}", False, f"Status code: {response.status_code}")
            except Exception as e:
                self.log_test(f"Price breakdown - {test_case['quantity']}", False, f"Exception: {str(e)}")

    def test_listings_retrieval(self):
        """Test GET /api/listings/{session_id}"""
        try:
            response = requests.get(f"{BACKEND_URL}/listings/{self.session_id}")
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    # Should have listings from previous tests
                    if len(data) > 0:
                        # Check if listings have required fields
                        first_listing = data[0]
                        required_fields = ["id", "name", "quantity", "price", "session_id"]
                        missing_fields = [field for field in required_fields if field not in first_listing]
                        
                        if not missing_fields:
                            self.log_test("Listings retrieval", True, f"Retrieved {len(data)} listings successfully")
                        else:
                            self.log_test("Listings retrieval", False, f"Missing fields in listing: {missing_fields}")
                    else:
                        self.log_test("Listings retrieval", True, "No listings found (empty session)")
                else:
                    self.log_test("Listings retrieval", False, "Response is not a list")
            else:
                self.log_test("Listings retrieval", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_test("Listings retrieval", False, f"Exception: {str(e)}")

    def test_listings_deletion(self):
        """Test DELETE /api/listings/{session_id}"""
        try:
            response = requests.delete(f"{BACKEND_URL}/listings/{self.session_id}")
            if response.status_code == 200:
                data = response.json()
                if "deleted_count" in data:
                    deleted_count = data["deleted_count"]
                    
                    # Verify deletion by trying to retrieve
                    verify_response = requests.get(f"{BACKEND_URL}/listings/{self.session_id}")
                    if verify_response.status_code == 200:
                        verify_data = verify_response.json()
                        if isinstance(verify_data, list) and len(verify_data) == 0:
                            self.log_test("Listings deletion", True, f"Deleted {deleted_count} listings, verified empty")
                        else:
                            self.log_test("Listings deletion", False, f"Deletion claimed {deleted_count} but {len(verify_data)} still exist")
                    else:
                        self.log_test("Listings deletion", False, "Could not verify deletion")
                else:
                    self.log_test("Listings deletion", False, "Missing 'deleted_count' in response")
            else:
                self.log_test("Listings deletion", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_test("Listings deletion", False, f"Exception: {str(e)}")

    def test_database_operations(self):
        """Test MongoDB storage and retrieval operations"""
        try:
            # Create a test listing
            product_data = {
                "name": "Database Test Product",
                "quantity": "1 unit",
                "price": 100.0,
                "language": "english",
                "session_id": self.session_id
            }
            
            # Create listing
            create_response = requests.post(f"{BACKEND_URL}/generate-listing", json=product_data)
            if create_response.status_code == 200:
                created_listing = create_response.json()
                listing_id = created_listing.get("id")
                
                if listing_id:
                    # Retrieve and verify
                    retrieve_response = requests.get(f"{BACKEND_URL}/listings/{self.session_id}")
                    if retrieve_response.status_code == 200:
                        listings = retrieve_response.json()
                        found_listing = None
                        for listing in listings:
                            if listing.get("id") == listing_id:
                                found_listing = listing
                                break
                        
                        if found_listing:
                            # Verify data integrity
                            if (found_listing.get("name") == product_data["name"] and
                                found_listing.get("price") == product_data["price"] and
                                found_listing.get("session_id") == product_data["session_id"]):
                                self.log_test("Database operations", True, "Create, store, and retrieve operations successful")
                            else:
                                self.log_test("Database operations", False, "Data integrity issues in stored listing")
                        else:
                            self.log_test("Database operations", False, "Created listing not found in retrieval")
                    else:
                        self.log_test("Database operations", False, "Failed to retrieve listings")
                else:
                    self.log_test("Database operations", False, "No ID returned from creation")
            else:
                self.log_test("Database operations", False, f"Failed to create listing: {create_response.status_code}")
        except Exception as e:
            self.log_test("Database operations", False, f"Exception: {str(e)}")

    def test_translation_endpoint(self):
        """Test translation endpoint (bonus functionality)"""
        try:
            translation_data = {
                "text": "Fresh tomatoes",
                "from_language": "english",
                "to_language": "hindi"
            }
            
            response = requests.post(f"{BACKEND_URL}/translate", json=translation_data)
            if response.status_code == 200:
                data = response.json()
                if "translated_text" in data:
                    translated = data["translated_text"]
                    if translated and len(translated) > 0:
                        self.log_test("Translation endpoint", True, f"Translated 'Fresh tomatoes' to: {translated}")
                    else:
                        self.log_test("Translation endpoint", False, "Empty translation returned")
                else:
                    self.log_test("Translation endpoint", False, "Missing 'translated_text' in response")
            else:
                self.log_test("Translation endpoint", False, f"Status code: {response.status_code}")
        except Exception as e:
            self.log_test("Translation endpoint", False, f"Exception: {str(e)}")

    def run_all_tests(self):
        """Run all backend tests"""
        print("=" * 60)
        print("DIGITAL CATALOG AGENT - BACKEND API TESTING")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Session ID: {self.session_id}")
        print("=" * 60)
        print()
        
        # Run tests in logical order
        self.test_root_endpoint()
        self.test_languages_endpoint()
        self.test_individual_language_endpoints()
        self.test_generate_listing_hindi()
        self.test_generate_listing_english()
        self.test_price_breakdown_calculations()
        self.test_listings_retrieval()
        self.test_database_operations()
        self.test_listings_deletion()
        self.test_translation_endpoint()
        
        # Summary
        print("=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        print()
        
        if failed_tests > 0:
            print("FAILED TESTS:")
            for test_name, result in self.test_results.items():
                if not result["success"]:
                    print(f"❌ {test_name}: {result['details']}")
        
        return self.test_results

if __name__ == "__main__":
    tester = DigitalCatalogTester()
    results = tester.run_all_tests()