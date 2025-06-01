import requests
import unittest
import json
import sys
from pprint import pprint

# Use the public endpoint from frontend/.env
BACKEND_URL = "https://100fbc48-303d-4006-89db-8f09d429a74e.preview.emergentagent.com"
API_URL = f"{BACKEND_URL}/api"

class BibleAPITester(unittest.TestCase):
    """Test suite for the Multilingual Bible API"""
    
    def setUp(self):
        """Setup for each test"""
        self.api_url = API_URL
        
    def test_01_health_check(self):
        """Test API health check endpoint"""
        print("\n🔍 Testing API health check...")
        response = requests.get(f"{self.api_url}/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("message", data)
        print(f"✅ API health check passed: {data['message']}")
        
    def test_02_get_books(self):
        """Test getting all Bible books"""
        print("\n🔍 Testing get all books...")
        response = requests.get(f"{self.api_url}/books")
        self.assertEqual(response.status_code, 200)
        books = response.json()
        self.assertIsInstance(books, list)
        self.assertGreater(len(books), 0)
        
        # Verify book structure
        sample_book = books[0]
        self.assertIn("id", sample_book)
        self.assertIn("name", sample_book)
        self.assertIn("english", sample_book["name"])
        self.assertIn("hindi", sample_book["name"])
        self.assertIn("hebrew", sample_book["name"])
        self.assertIn("greek", sample_book["name"])
        self.assertIn("testament", sample_book)
        self.assertIn("chapters", sample_book)
        
        print(f"✅ Get books passed: Found {len(books)} books")
        print(f"   Sample book: {sample_book['name']['english']}")
        
    def test_03_get_chapter(self):
        """Test getting verses from a specific chapter"""
        print("\n🔍 Testing get chapter verses...")
        book_name = "Genesis"
        chapter = 1
        
        response = requests.get(f"{self.api_url}/books/{book_name}/chapters/{chapter}")
        self.assertEqual(response.status_code, 200)
        verses = response.json()
        self.assertIsInstance(verses, list)
        self.assertGreater(len(verses), 0)
        
        # Verify verse structure
        sample_verse = verses[0]
        self.assertIn("id", sample_verse)
        self.assertIn("book", sample_verse)
        self.assertIn("chapter", sample_verse)
        self.assertIn("verse", sample_verse)
        self.assertIn("text", sample_verse)
        
        # Verify multilingual content
        self.assertIn("english", sample_verse["text"])
        self.assertIn("hindi", sample_verse["text"])
        self.assertIn("hebrew", sample_verse["text"])
        self.assertIn("greek", sample_verse["text"])
        
        print(f"✅ Get chapter passed: Found {len(verses)} verses in {book_name} {chapter}")
        print(f"   Sample verse: {sample_verse['book']} {sample_verse['chapter']}:{sample_verse['verse']}")
        
    def test_04_get_specific_verse(self):
        """Test getting a specific verse by ID"""
        print("\n🔍 Testing get specific verse...")
        verse_id = "gen-1-1"
        
        response = requests.get(f"{self.api_url}/verses/{verse_id}")
        self.assertEqual(response.status_code, 200)
        verse = response.json()
        
        # Verify verse structure
        self.assertEqual(verse["id"], verse_id)
        self.assertIn("book", verse)
        self.assertIn("chapter", verse)
        self.assertIn("verse", verse)
        self.assertIn("text", verse)
        self.assertIn("transliteration", verse)
        self.assertIn("cross_references", verse)
        self.assertIn("notes", verse)
        
        print(f"✅ Get specific verse passed: {verse['book']} {verse['chapter']}:{verse['verse']}")
        
    def test_05_search_verses(self):
        """Test searching verses"""
        print("\n🔍 Testing search functionality...")
        
        # Test search in English
        query = "beginning"
        response = requests.get(f"{self.api_url}/search", params={"q": query, "language": "english"})
        self.assertEqual(response.status_code, 200)
        results = response.json()
        self.assertIn("verses", results)
        self.assertIn("total_count", results)
        self.assertGreater(results["total_count"], 0)
        
        print(f"✅ Search in English passed: Found {results['total_count']} results for '{query}'")
        
        # Test search in Hindi
        query = "परमेश्वर"
        response = requests.get(f"{self.api_url}/search", params={"q": query, "language": "hindi"})
        self.assertEqual(response.status_code, 200)
        results = response.json()
        
        print(f"✅ Search in Hindi passed: Found {results['total_count']} results for '{query}'")
        
        # Test search in Hebrew
        query = "בְּרֵאשִׁית"
        response = requests.get(f"{self.api_url}/search", params={"q": query, "language": "hebrew"})
        self.assertEqual(response.status_code, 200)
        results = response.json()
        
        print(f"✅ Search in Hebrew passed: Found {results['total_count']} results for '{query}'")
        
    def test_06_cross_references(self):
        """Test getting cross-references for a verse"""
        print("\n🔍 Testing cross-references functionality...")
        verse_id = "gen-1-1"
        
        response = requests.get(f"{self.api_url}/cross-references/{verse_id}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertIn("original_verse", data)
        self.assertIn("cross_references", data)
        
        original = data["original_verse"]
        cross_refs = data["cross_references"]
        
        self.assertEqual(original["id"], verse_id)
        self.assertIsInstance(cross_refs, list)
        
        print(f"✅ Cross-references passed: Found {len(cross_refs)} cross-references for {original['book']} {original['chapter']}:{original['verse']}")
        
    def test_07_daily_verse(self):
        """Test getting a daily verse"""
        print("\n🔍 Testing daily verse functionality...")
        
        response = requests.get(f"{self.api_url}/daily-verse")
        self.assertEqual(response.status_code, 200)
        verse = response.json()
        
        self.assertIn("id", verse)
        self.assertIn("book", verse)
        self.assertIn("chapter", verse)
        self.assertIn("verse", verse)
        self.assertIn("text", verse)
        
        print(f"✅ Daily verse passed: {verse['book']} {verse['chapter']}:{verse['verse']}")

if __name__ == "__main__":
    print(f"\n🌐 Testing Bible API at: {API_URL}\n")
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
