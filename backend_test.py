import requests
import unittest
import json
from datetime import datetime, timedelta

# Use the public endpoint for testing
BACKEND_URL = "https://cd87bbbe-f3e6-4246-83d8-829e2326a985.preview.emergentagent.com/api"

class AIMarketingAssistantAPITest(unittest.TestCase):
    """Test suite for the AI Marketing Assistant API"""

    def test_01_health_check(self):
        """Test the health check endpoint"""
        response = requests.get(f"{BACKEND_URL}/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "healthy")
        self.assertIn("timestamp", data)
        print("✅ Health check endpoint is working")

    def test_02_available_models(self):
        """Test the available models endpoint"""
        response = requests.get(f"{BACKEND_URL}/available-models")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Check that all providers are present
        self.assertIn("openai", data)
        self.assertIn("anthropic", data)
        self.assertIn("gemini", data)
        self.assertIn("groq", data)
        
        # Check that each provider has models
        self.assertTrue(len(data["openai"]) > 0)
        self.assertTrue(len(data["anthropic"]) > 0)
        self.assertTrue(len(data["gemini"]) > 0)
        self.assertTrue(len(data["groq"]) > 0)
        
        print("✅ Available models endpoint is working")
        print(f"  - OpenAI models: {len(data['openai'])}")
        print(f"  - Anthropic models: {len(data['anthropic'])}")
        print(f"  - Gemini models: {len(data['gemini'])}")
        print(f"  - Groq models: {len(data['groq'])}")

    def test_03_get_config(self):
        """Test getting the API configuration"""
        response = requests.get(f"{BACKEND_URL}/config")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Check that the config has the expected fields
        self.assertIn("id", data)
        self.assertIn("user_id", data)
        self.assertIn("openai_api_key", data)
        self.assertIn("anthropic_api_key", data)
        self.assertIn("gemini_api_key", data)
        self.assertIn("groq_api_key", data)
        self.assertIn("unsplash_api_key", data)
        
        print("✅ Get config endpoint is working")

    def test_04_update_config(self):
        """Test updating the API configuration"""
        # Create a test configuration
        test_config = {
            "openai_api_key": "test_openai_key",
            "anthropic_api_key": "test_anthropic_key",
            "gemini_api_key": "test_gemini_key",
            "groq_api_key": "test_groq_key",
            "unsplash_api_key": "test_unsplash_key"
        }
        
        response = requests.post(f"{BACKEND_URL}/config", json=test_config)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Check that the config was updated
        self.assertEqual(data["openai_api_key"], "test_openai_key")
        self.assertEqual(data["anthropic_api_key"], "test_anthropic_key")
        self.assertEqual(data["gemini_api_key"], "test_gemini_key")
        self.assertEqual(data["groq_api_key"], "test_groq_key")
        self.assertEqual(data["unsplash_api_key"], "test_unsplash_key")
        
        print("✅ Update config endpoint is working")

    def test_05_generate_posts_error_handling(self):
        """Test error handling for post generation without API keys"""
        request_data = {
            "platforms": ["facebook", "twitter"],
            "post_type": "General Update",
            "product_description": "Our new product is amazing!",
            "tone_style": "Professional",
            "include_hashtags": True,
            "include_emojis": True,
            "variants_count": 1,
            "ai_provider": "openai",
            "ai_model": "gpt-4o-mini"
        }
        
        response = requests.post(f"{BACKEND_URL}/generate-posts", json=request_data)
        
        # Since we're using test API keys, we expect an error
        # Either 400 (API key not configured) or 500 (API error)
        self.assertTrue(response.status_code in [400, 500])
        
        if response.status_code == 400:
            self.assertIn("API key", response.json().get("detail", ""))
            print("✅ Generate posts endpoint correctly returns 400 when API key is not configured")
        else:
            print("✅ Generate posts endpoint returns 500 when there's an API error")

    def test_06_rewrite_content_error_handling(self):
        """Test error handling for content rewriting without API keys"""
        request_data = {
            "original_content": "This is a test post.",
            "tone_style": "Professional",
            "platform": "facebook",
            "ai_provider": "openai",
            "ai_model": "gpt-4o-mini"
        }
        
        response = requests.post(f"{BACKEND_URL}/rewrite-content", json=request_data)
        
        # Since we're using test API keys, we expect an error
        # Either 400 (API key not configured) or 500 (API error)
        self.assertTrue(response.status_code in [400, 500])
        
        if response.status_code == 400:
            self.assertIn("API key", response.json().get("detail", ""))
            print("✅ Rewrite content endpoint correctly returns 400 when API key is not configured")
        else:
            print("✅ Rewrite content endpoint returns 500 when there's an API error")

    def test_07_analyze_post_error_handling(self):
        """Test error handling for post analysis without API keys"""
        request_data = {
            "content": "This is a test post.",
            "platform": "facebook",
            "ai_provider": "openai",
            "ai_model": "gpt-4o-mini"
        }
        
        response = requests.post(f"{BACKEND_URL}/analyze-post", json=request_data)
        
        # Since we're using test API keys, we expect an error
        # Either 400 (API key not configured) or 500 (API error)
        self.assertTrue(response.status_code in [400, 500])
        
        if response.status_code == 400:
            self.assertIn("API key", response.json().get("detail", ""))
            print("✅ Analyze post endpoint correctly returns 400 when API key is not configured")
        else:
            print("✅ Analyze post endpoint returns 500 when there's an API error")

    def test_08_schedule_post(self):
        """Test scheduling a post"""
        scheduled_date = (datetime.utcnow() + timedelta(hours=1)).isoformat()
        
        request_data = {
            "platform": "facebook",
            "content": "This is a scheduled test post.",
            "hashtags": ["test", "marketing"],
            "scheduled_date": scheduled_date
        }
        
        response = requests.post(f"{BACKEND_URL}/schedule-post", json=request_data)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Check that the post was scheduled
        self.assertIn("id", data)
        self.assertEqual(data["platform"], "facebook")
        self.assertEqual(data["content"], "This is a scheduled test post.")
        self.assertEqual(data["hashtags"], ["test", "marketing"])
        self.assertEqual(data["status"], "scheduled")
        
        # Save the post ID for the next test
        self.post_id = data["id"]
        
        print("✅ Schedule post endpoint is working")

    def test_09_get_scheduled_posts(self):
        """Test getting scheduled posts"""
        response = requests.get(f"{BACKEND_URL}/scheduled-posts")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Check that we got a list of posts
        self.assertIsInstance(data, list)
        
        # Check if our previously scheduled post is in the list
        if hasattr(self, 'post_id'):
            post_found = False
            for post in data:
                if post["id"] == self.post_id:
                    post_found = True
                    break
            
            self.assertTrue(post_found, "Previously scheduled post not found")
        
        print(f"✅ Get scheduled posts endpoint is working, found {len(data)} posts")

    def test_10_delete_scheduled_post(self):
        """Test deleting a scheduled post"""
        if not hasattr(self, 'post_id'):
            self.skipTest("No post ID from previous test")
        
        response = requests.delete(f"{BACKEND_URL}/scheduled-posts/{self.post_id}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Check that the post was deleted
        self.assertIn("message", data)
        self.assertIn("deleted", data["message"])
        
        print("✅ Delete scheduled post endpoint is working")

    def test_11_export_posts_error_handling(self):
        """Test error handling for exporting posts with invalid IDs"""
        response = requests.get(f"{BACKEND_URL}/export-posts/csv", params={"post_ids": ["invalid_id"]})
        
        # We expect a 404 since the post doesn't exist
        self.assertEqual(response.status_code, 404)
        
        print("✅ Export posts endpoint correctly returns 404 for invalid post IDs")

if __name__ == "__main__":
    unittest.main(verbosity=2)
