import requests
import unittest
import json
import re
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
        
        # Store the API keys for later tests
        self.api_keys = {
            "openai": data.get("openai_api_key"),
            "anthropic": data.get("anthropic_api_key"),
            "gemini": data.get("gemini_api_key"),
            "groq": data.get("groq_api_key")
        }
        
        # Check if we have at least one valid API key
        has_valid_key = any(key for key in self.api_keys.values() if key)
        print(f"✅ Get config endpoint is working (Has valid API keys: {has_valid_key})")

    def test_04_update_config(self):
        """Test updating the API configuration"""
        # First get the current configuration
        response = requests.get(f"{BACKEND_URL}/config")
        self.assertEqual(response.status_code, 200)
        current_config = response.json()
        
        # Create a test configuration (preserving any existing API keys)
        test_config = {
            "openai_api_key": current_config.get("openai_api_key") or "test_openai_key",
            "anthropic_api_key": current_config.get("anthropic_api_key") or "test_anthropic_key",
            "gemini_api_key": current_config.get("gemini_api_key") or "test_gemini_key",
            "groq_api_key": current_config.get("groq_api_key") or "test_groq_key",
            "unsplash_api_key": current_config.get("unsplash_api_key") or "test_unsplash_key"
        }
        
        response = requests.post(f"{BACKEND_URL}/config", json=test_config)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Check that the config was updated
        for key, value in test_config.items():
            self.assertEqual(data[key], value)
        
        # Verify persistence by getting the config again
        response = requests.get(f"{BACKEND_URL}/config")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        for key, value in test_config.items():
            self.assertEqual(data[key], value)
        
        print("✅ Update config endpoint is working and persists changes")

    def test_05_rewrite_content_with_different_providers(self):
        """Test content rewriting with different AI providers"""
        sample_content = "Our new product is amazing and everyone should buy it now"
        
        # Get available API keys
        response = requests.get(f"{BACKEND_URL}/config")
        self.assertEqual(response.status_code, 200)
        config = response.json()
        
        providers_to_test = []
        if config.get("openai_api_key"):
            providers_to_test.append("openai")
        if config.get("anthropic_api_key"):
            providers_to_test.append("anthropic")
        if config.get("gemini_api_key"):
            providers_to_test.append("gemini")
        if config.get("groq_api_key"):
            providers_to_test.append("groq")
        
        if not providers_to_test:
            self.skipTest("No API keys configured for testing")
        
        results = {}
        
        for provider in providers_to_test:
            request_data = {
                "original_content": sample_content,
                "tone_style": "Professional",
                "platform": "facebook",
                "ai_provider": provider,
                "ai_model": self.get_default_model(provider)
            }
            
            response = requests.post(f"{BACKEND_URL}/rewrite-content", json=request_data)
            
            if response.status_code == 200:
                rewritten = response.json().get("rewritten_content", "")
                
                # Check that the response doesn't contain meta-commentary
                self.assertFalse(
                    any(phrase in rewritten.lower() for phrase in [
                        "here's a rewritten", "i've rewritten", "here is a", 
                        "here's how", "i would rewrite", "rewritten version"
                    ]),
                    f"Rewritten content contains meta-commentary: {rewritten}"
                )
                
                # Check that the content is different from the original
                self.assertNotEqual(sample_content, rewritten)
                
                # Store the result for comparison
                results[provider] = rewritten
                print(f"✅ Rewrite with {provider} successful")
                print(f"  Original: {sample_content}")
                print(f"  Rewritten: {rewritten[:100]}...")
            else:
                print(f"❌ Rewrite with {provider} failed: {response.status_code}")
                if response.headers.get('content-type') == 'application/json':
                    print(f"  Error: {response.json().get('detail', 'Unknown error')}")
        
        # If we have results from multiple providers, check they're different
        if len(results) > 1:
            providers_list = list(results.keys())
            for i in range(len(providers_list)):
                for j in range(i+1, len(providers_list)):
                    provider1 = providers_list[i]
                    provider2 = providers_list[j]
                    self.assertNotEqual(
                        results[provider1], 
                        results[provider2],
                        f"Results from {provider1} and {provider2} are identical"
                    )
                    print(f"✅ Results from {provider1} and {provider2} are different")

    def test_06_analyze_post_with_different_content(self):
        """Test post analysis with different content samples"""
        # Sample contents with expected relative scores
        samples = [
            {
                "content": "Buy now! Limited time offer! Don't miss out!!!",
                "platform": "linkedin",
                "expected_lower_scores": True  # We expect lower scores for this content
            },
            {
                "content": "We're excited to share insights about sustainable business practices that can help companies reduce their environmental impact while maintaining profitability.",
                "platform": "linkedin",
                "expected_lower_scores": False  # We expect higher scores for this content
            }
        ]
        
        # Get available API keys
        response = requests.get(f"{BACKEND_URL}/config")
        self.assertEqual(response.status_code, 200)
        config = response.json()
        
        # Choose a provider that has an API key
        provider = None
        for p in ["openai", "anthropic", "gemini", "groq"]:
            if config.get(f"{p}_api_key"):
                provider = p
                break
        
        if not provider:
            self.skipTest("No API keys configured for testing")
        
        results = []
        
        for sample in samples:
            request_data = {
                "content": sample["content"],
                "platform": sample["platform"],
                "ai_provider": provider,
                "ai_model": self.get_default_model(provider)
            }
            
            response = requests.post(f"{BACKEND_URL}/analyze-post", json=request_data)
            
            if response.status_code == 200:
                analysis = response.json()
                
                # Check that we have all the expected score fields
                self.assertIn("engagement_score", analysis)
                self.assertIn("readability_score", analysis)
                self.assertIn("tone_consistency_score", analysis)
                self.assertIn("platform_best_practices_score", analysis)
                self.assertIn("overall_score", analysis)
                
                # Check that scores are within expected range
                for score_field in ["engagement_score", "readability_score", 
                                   "tone_consistency_score", "platform_best_practices_score", 
                                   "overall_score"]:
                    score = analysis[score_field]
                    self.assertIsInstance(score, int)
                    self.assertGreaterEqual(score, 0)
                    self.assertLessEqual(score, 100)
                
                # Check that we have improvement tips
                self.assertIn("improvement_tips", analysis)
                self.assertIsInstance(analysis["improvement_tips"], list)
                self.assertGreater(len(analysis["improvement_tips"]), 0)
                
                # Store the result
                results.append({
                    "content": sample["content"][:50] + "...",
                    "expected_lower_scores": sample["expected_lower_scores"],
                    "scores": {
                        "engagement": analysis["engagement_score"],
                        "readability": analysis["readability_score"],
                        "tone": analysis["tone_consistency_score"],
                        "platform": analysis["platform_best_practices_score"],
                        "overall": analysis["overall_score"]
                    }
                })
                
                print(f"✅ Analysis successful for: {sample['content'][:50]}...")
                print(f"  Scores: Engagement={analysis['engagement_score']}, " +
                      f"Readability={analysis['readability_score']}, " +
                      f"Tone={analysis['tone_consistency_score']}, " +
                      f"Platform={analysis['platform_best_practices_score']}, " +
                      f"Overall={analysis['overall_score']}")
            else:
                print(f"❌ Analysis failed: {response.status_code}")
                if response.headers.get('content-type') == 'application/json':
                    print(f"  Error: {response.json().get('detail', 'Unknown error')}")
        
        # If we have results for both samples, compare them
        if len(results) == 2:
            # The promotional content should have lower scores than the professional content
            promotional = results[0] if results[0]["expected_lower_scores"] else results[1]
            professional = results[1] if results[0]["expected_lower_scores"] else results[0]
            
            # Check if at least one score is different
            scores_are_different = False
            for score_type in ["overall", "platform", "tone"]:
                if promotional["scores"][score_type] != professional["scores"][score_type]:
                    scores_are_different = True
                    break
            
            self.assertTrue(scores_are_different, "Scores should be different for different content")
            print("✅ Analysis produces different scores for different content")
            
            # Check if the professional content has higher scores in at least one category
            has_higher_score = False
            for score_type in ["overall", "platform", "tone"]:
                if professional["scores"][score_type] > promotional["scores"][score_type]:
                    has_higher_score = True
                    print(f"  Professional content has higher {score_type} score " +
                          f"({professional['scores'][score_type]} vs {promotional['scores'][score_type]})")
                    break
            
            self.assertTrue(has_higher_score, "Professional content should have higher scores")

    def test_07_config_persistence(self):
        """Test that API configuration persists across requests"""
        # First, get the current configuration
        response = requests.get(f"{BACKEND_URL}/config")
        self.assertEqual(response.status_code, 200)
        initial_config = response.json()
        
        # Update with a unique test value
        test_value = f"test_value_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        update_data = {
            "openai_api_key": test_value
        }
        
        response = requests.post(f"{BACKEND_URL}/config", json=update_data)
        self.assertEqual(response.status_code, 200)
        
        # Verify the update was successful
        response = requests.get(f"{BACKEND_URL}/config")
        self.assertEqual(response.status_code, 200)
        updated_config = response.json()
        self.assertEqual(updated_config["openai_api_key"], test_value)
        
        # Restore the original value
        restore_data = {
            "openai_api_key": initial_config["openai_api_key"] or ""
        }
        
        response = requests.post(f"{BACKEND_URL}/config", json=restore_data)
        self.assertEqual(response.status_code, 200)
        
        print("✅ API configuration persists across requests")

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

    def get_default_model(self, provider):
        """Get a default model for the given provider"""
        models = {
            "openai": "gpt-4o-mini",
            "anthropic": "claude-3-5-haiku-20241022",
            "gemini": "gemini-1.5-flash",
            "groq": "llama-3.1-8b-instant"
        }
        return models.get(provider, "gpt-4o-mini")

if __name__ == "__main__":
    unittest.main(verbosity=2)
