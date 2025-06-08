from fastapi import FastAPI, APIRouter, HTTPException, Query, BackgroundTasks
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
from enum import Enum
import json
import aiofiles
from emergentintegrations.llm.chat import LlmChat, UserMessage
# Temporarily removing Unsplash functionality
# from python_unsplash import PyUnsplash

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI(title="AI Marketing Assistant", version="1.0.0")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Enums
class PostType(str, Enum):
    GENERAL_UPDATE = "General Update"
    PROMOTIONAL = "Promotional"
    PRODUCT_LAUNCH = "Product Launch"
    EVENT_ANNOUNCEMENT = "Event Announcement"
    CUSTOMER_TESTIMONIAL = "Customer Testimonial"
    BEHIND_THE_SCENES = "Behind the Scenes"
    TIPS_TRICKS = "Tips & Tricks"

class ToneStyle(str, Enum):
    PROFESSIONAL = "Professional"
    FRIENDLY = "Friendly"
    PLAYFUL = "Playful"
    URGENCY = "Urgency"
    INSPIRATIONAL = "Inspirational"

class Platform(str, Enum):
    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"
    TWITTER = "twitter"
    LINKEDIN = "linkedin"
    TIKTOK = "tiktok"
    GOOGLE_ADS = "google_ads"

class AIProvider(str, Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GEMINI = "gemini"
    GROQ = "groq"

# Models
class APIConfiguration(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = "default"  # For now using default user
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None
    groq_api_key: Optional[str] = None
    unsplash_api_key: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class APIConfigurationCreate(BaseModel):
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None
    groq_api_key: Optional[str] = None
    unsplash_api_key: Optional[str] = None

class AudienceTarget(BaseModel):
    age_range: Optional[str] = None
    gender: Optional[str] = None
    interests: Optional[str] = None
    location: Optional[str] = None

class PostGenerationRequest(BaseModel):
    platforms: List[Platform]
    post_type: PostType
    product_description: str
    tone_style: ToneStyle
    include_hashtags: bool = False
    include_emojis: bool = False
    include_seo_optimization: bool = False
    seo_keywords: Optional[str] = None
    variants_count: int = 1
    audience_target: Optional[AudienceTarget] = None
    ai_provider: AIProvider = AIProvider.OPENAI
    ai_model: str = "gpt-4o-mini"

class PostContent(BaseModel):
    platform: Platform
    content: str
    hashtags: Optional[List[str]] = None
    meta_description: Optional[str] = None

class GeneratedPost(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = "default"
    original_request: PostGenerationRequest
    post_contents: List[PostContent]
    variant_number: int
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ContentRewriteRequest(BaseModel):
    original_content: str
    tone_style: ToneStyle
    platform: Platform
    ai_provider: AIProvider = AIProvider.OPENAI
    ai_model: str = "gpt-4o-mini"

class PostAnalysisRequest(BaseModel):
    content: str
    platform: Platform
    ai_provider: AIProvider = AIProvider.OPENAI
    ai_model: str = "gpt-4o-mini"

class PostAnalysisResult(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    content: str
    platform: Platform
    engagement_score: int
    readability_score: int
    tone_consistency_score: int
    platform_best_practices_score: int
    overall_score: int
    improvement_tips: List[str]
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ScheduledPost(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = "default"
    platform: Platform
    content: str
    hashtags: Optional[List[str]] = None
    scheduled_date: datetime
    status: str = "scheduled"  # scheduled, published, cancelled
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ScheduledPostCreate(BaseModel):
    platform: Platform
    content: str
    hashtags: Optional[List[str]] = None
    scheduled_date: datetime

class UnsplashImage(BaseModel):
    id: str
    urls: Dict[str, str]
    alt_description: Optional[str]
    description: Optional[str]
    download_url: str

# API Configuration endpoints
@api_router.post("/config", response_model=APIConfiguration)
async def create_or_update_config(config: APIConfigurationCreate):
    """Create or update API configuration"""
    try:
        # Check if config exists for default user
        existing_config = await db.api_configurations.find_one({"user_id": "default"})
        
        if existing_config:
            # Update existing config
            update_data = {k: v for k, v in config.dict().items() if v is not None}
            update_data["updated_at"] = datetime.utcnow()
            
            await db.api_configurations.update_one(
                {"user_id": "default"},
                {"$set": update_data}
            )
            
            updated_config = await db.api_configurations.find_one({"user_id": "default"})
            return APIConfiguration(**updated_config)
        else:
            # Create new config
            config_dict = config.dict()
            config_obj = APIConfiguration(**config_dict)
            await db.api_configurations.insert_one(config_obj.dict())
            return config_obj
            
    except Exception as e:
        logger.error(f"Error creating/updating config: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/config", response_model=APIConfiguration)
async def get_config():
    """Get current API configuration"""
    try:
        config = await db.api_configurations.find_one({"user_id": "default"})
        if not config:
            # Return empty config
            return APIConfiguration()
        return APIConfiguration(**config)
    except Exception as e:
        logger.error(f"Error getting config: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Available models for each provider
@api_router.get("/available-models")
async def get_available_models():
    """Get available models for each AI provider"""
    return {
        "openai": [
            "gpt-4.1",
            "gpt-4.1-mini", 
            "gpt-4.1-nano",
            "o4-mini",
            "o3-mini",
            "o3",
            "o1-mini",
            "gpt-4o-mini"
        ],
        "anthropic": [
            "claude-sonnet-4-20250514",
            "claude-opus-4-20250514",
            "claude-3-7-sonnet-20250219",
            "claude-3-5-haiku-20241022",
            "claude-3-5-sonnet-20241022"
        ],
        "gemini": [
            "gemini-2.5-flash-preview-04-17",
            "gemini-2.5-pro-preview-05-06", 
            "gemini-2.0-flash",
            "gemini-2.0-flash-preview-image-generation",
            "gemini-2.0-flash-lite",
            "gemini-1.5-flash",
            "gemini-1.5-flash-8b",
            "gemini-1.5-pro"
        ],
        "groq": [
            "llama-3.1-70b-versatile",
            "llama-3.1-8b-instant",
            "mixtral-8x7b-32768"
        ]
    }

# AI Chat Helper Function
async def get_ai_response(prompt: str, provider: AIProvider, model: str, api_key: str) -> str:
    """Get response from AI provider"""
    try:
        session_id = str(uuid.uuid4())
        
        chat = LlmChat(
            api_key=api_key,
            session_id=session_id,
            system_message="You are an expert marketing content creator. Generate engaging, platform-optimized content that drives engagement and conversions."
        ).with_model(provider.value, model)
        
        user_message = UserMessage(text=prompt)
        response = await chat.send_message(user_message)
        
        return response
        
    except Exception as e:
        logger.error(f"Error getting AI response: {e}")
        raise HTTPException(status_code=500, detail=f"AI generation failed: {str(e)}")

# Post Generation endpoints
@api_router.post("/generate-posts", response_model=List[GeneratedPost])
async def generate_posts(request: PostGenerationRequest):
    """Generate posts for multiple platforms"""
    try:
        # Get API configuration
        config = await db.api_configurations.find_one({"user_id": "default"})
        if not config:
            raise HTTPException(status_code=400, detail="API configuration not found. Please configure your API keys first.")
        
        # Get appropriate API key
        api_key = None
        if request.ai_provider == AIProvider.OPENAI and config.get("openai_api_key"):
            api_key = config["openai_api_key"]
        elif request.ai_provider == AIProvider.ANTHROPIC and config.get("anthropic_api_key"):
            api_key = config["anthropic_api_key"]
        elif request.ai_provider == AIProvider.GEMINI and config.get("gemini_api_key"):
            api_key = config["gemini_api_key"]
        elif request.ai_provider == AIProvider.GROQ and config.get("groq_api_key"):
            api_key = config["groq_api_key"]
        
        if not api_key:
            raise HTTPException(status_code=400, detail=f"API key for {request.ai_provider.value} not configured.")
        
        generated_posts = []
        
        # Generate variants
        for variant_num in range(1, request.variants_count + 1):
            platform_posts = []
            
            for platform in request.platforms:
                # Build platform-specific prompt
                prompt = f"""
Create a {request.tone_style.value.lower()} {request.post_type.value.lower()} post for {platform.value.upper()} about: {request.product_description}

Platform Requirements:
- {platform.value.upper()}: {get_platform_requirements(platform)}

"""
                
                if request.audience_target:
                    audience_info = []
                    if request.audience_target.age_range:
                        audience_info.append(f"Age: {request.audience_target.age_range}")
                    if request.audience_target.gender:
                        audience_info.append(f"Gender: {request.audience_target.gender}")
                    if request.audience_target.interests:
                        audience_info.append(f"Interests: {request.audience_target.interests}")
                    if request.audience_target.location:
                        audience_info.append(f"Location: {request.audience_target.location}")
                    
                    if audience_info:
                        prompt += f"Target Audience: {', '.join(audience_info)}\n"
                
                if request.include_emojis:
                    prompt += "Include relevant emojis to make the post more engaging.\n"
                
                if request.include_hashtags:
                    prompt += "Include 5-10 relevant hashtags at the end.\n"
                    
                if request.include_seo_optimization and request.seo_keywords:
                    prompt += f"Include these SEO keywords naturally: {request.seo_keywords}\n"
                    prompt += "Also provide a meta description for SEO purposes.\n"
                
                if variant_num > 1:
                    prompt += f"This is variant #{variant_num} - make it different from previous versions while maintaining the same core message.\n"
                
                prompt += """
Please respond in this exact JSON format:
{
    "content": "The main post content here",
    "hashtags": ["hashtag1", "hashtag2", "hashtag3"],
    "meta_description": "SEO meta description if requested"
}

Only return valid JSON, no additional text."""
                
                # Get AI response
                ai_response = await get_ai_response(prompt, request.ai_provider, request.ai_model, api_key)
                
                try:
                    # Parse JSON response
                    response_data = json.loads(ai_response)
                    
                    post_content = PostContent(
                        platform=platform,
                        content=response_data.get("content", ""),
                        hashtags=response_data.get("hashtags") if request.include_hashtags else None,
                        meta_description=response_data.get("meta_description") if request.include_seo_optimization else None
                    )
                    platform_posts.append(post_content)
                    
                except json.JSONDecodeError:
                    # Fallback if JSON parsing fails
                    post_content = PostContent(
                        platform=platform,
                        content=ai_response,
                        hashtags=None,
                        meta_description=None
                    )
                    platform_posts.append(post_content)
            
            # Create generated post object
            generated_post = GeneratedPost(
                original_request=request,
                post_contents=platform_posts,
                variant_number=variant_num
            )
            
            # Save to database
            await db.generated_posts.insert_one(generated_post.dict())
            generated_posts.append(generated_post)
        
        return generated_posts
        
    except Exception as e:
        logger.error(f"Error generating posts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def get_platform_requirements(platform: Platform) -> str:
    """Get platform-specific requirements"""
    requirements = {
        Platform.FACEBOOK: "Longer posts work well (up to 300 words). Include call-to-action. Focus on community building.",
        Platform.INSTAGRAM: "Visual-first content. Keep captions engaging but concise. Stories format works well.",
        Platform.TWITTER: "Keep under 280 characters. Use trending hashtags. Be conversational and timely.",
        Platform.LINKEDIN: "Professional tone. Can be longer (up to 1300 chars). Include industry insights.",
        Platform.TIKTOK: "Short, catchy content. Include trending sounds/challenges. Be creative and fun.",
        Platform.GOOGLE_ADS: "Clear headline, compelling description. Include strong call-to-action. Focus on benefits."
    }
    return requirements.get(platform, "Create engaging content appropriate for the platform.")

# Content Rewriting endpoint
@api_router.post("/rewrite-content")
async def rewrite_content(request: ContentRewriteRequest):
    """Rewrite existing content with new tone/style"""
    try:
        # Get API configuration
        config = await db.api_configurations.find_one({"user_id": "default"})
        if not config:
            raise HTTPException(status_code=400, detail="API configuration not found.")
        
        # Get appropriate API key
        api_key = None
        if request.ai_provider == AIProvider.OPENAI and config.get("openai_api_key"):
            api_key = config["openai_api_key"]
        elif request.ai_provider == AIProvider.ANTHROPIC and config.get("anthropic_api_key"):
            api_key = config["anthropic_api_key"]
        elif request.ai_provider == AIProvider.GEMINI and config.get("gemini_api_key"):
            api_key = config["gemini_api_key"]
        elif request.ai_provider == AIProvider.GROQ and config.get("groq_api_key"):
            api_key = config["groq_api_key"]
        
        if not api_key:
            raise HTTPException(status_code=400, detail=f"API key for {request.ai_provider.value} not configured.")
        
        prompt = f"""
Rewrite the following post to improve engagement, clarity, and match a {request.tone_style.value} tone for {request.platform.value.upper()}:

Original Post: {request.original_content}

Platform Requirements: {get_platform_requirements(request.platform)}

Please make the rewritten content more engaging while maintaining the core message.
"""
        
        rewritten_content = await get_ai_response(prompt, request.ai_provider, request.ai_model, api_key)
        
        return {"rewritten_content": rewritten_content}
        
    except Exception as e:
        logger.error(f"Error rewriting content: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Post Analysis endpoint
@api_router.post("/analyze-post", response_model=PostAnalysisResult)
async def analyze_post(request: PostAnalysisRequest):
    """Analyze a post and provide improvement suggestions"""
    try:
        # Get API configuration
        config = await db.api_configurations.find_one({"user_id": "default"})
        if not config:
            raise HTTPException(status_code=400, detail="API configuration not found.")
        
        # Get appropriate API key
        api_key = None
        if request.ai_provider == AIProvider.OPENAI and config.get("openai_api_key"):
            api_key = config["openai_api_key"]
        elif request.ai_provider == AIProvider.ANTHROPIC and config.get("anthropic_api_key"):
            api_key = config["anthropic_api_key"]
        elif request.ai_provider == AIProvider.GEMINI and config.get("gemini_api_key"):
            api_key = config["gemini_api_key"]
        elif request.ai_provider == AIProvider.GROQ and config.get("groq_api_key"):
            api_key = config["groq_api_key"]
        
        if not api_key:
            raise HTTPException(status_code=400, detail=f"API key for {request.ai_provider.value} not configured.")
        
        prompt = f"""
Analyze the following post for {request.platform.value.upper()} and score it 0-100 for:
1. Engagement potential
2. Readability 
3. Tone consistency
4. Platform best practices

Post Content: {request.content}

Platform Requirements: {get_platform_requirements(request.platform)}

Please respond in this exact JSON format:
{{
    "engagement_score": 85,
    "readability_score": 90,
    "tone_consistency_score": 80,
    "platform_best_practices_score": 75,
    "overall_score": 82,
    "improvement_tips": ["Tip 1", "Tip 2", "Tip 3"]
}}

Only return valid JSON."""
        
        ai_response = await get_ai_response(prompt, request.ai_provider, request.ai_model, api_key)
        
        try:
            analysis_data = json.loads(ai_response)
            
            analysis_result = PostAnalysisResult(
                content=request.content,
                platform=request.platform,
                engagement_score=analysis_data.get("engagement_score", 0),
                readability_score=analysis_data.get("readability_score", 0),
                tone_consistency_score=analysis_data.get("tone_consistency_score", 0),
                platform_best_practices_score=analysis_data.get("platform_best_practices_score", 0),
                overall_score=analysis_data.get("overall_score", 0),
                improvement_tips=analysis_data.get("improvement_tips", [])
            )
            
            # Save to database
            await db.post_analyses.insert_one(analysis_result.dict())
            
            return analysis_result
            
        except json.JSONDecodeError:
            raise HTTPException(status_code=500, detail="Failed to parse AI analysis response")
        
    except Exception as e:
        logger.error(f"Error analyzing post: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Unsplash Image Search endpoints (temporarily disabled)
@api_router.get("/search-images")
async def search_images(query: str, page: int = 1, per_page: int = 15):
    """Search for images on Unsplash"""
    try:
        # Temporarily disabled - need to configure Unsplash API properly
        raise HTTPException(status_code=501, detail="Unsplash integration temporarily disabled")
        
        # # Get API configuration
        # config = await db.api_configurations.find_one({"user_id": "default"})
        # if not config or not config.get("unsplash_api_key"):
        #     raise HTTPException(status_code=400, detail="Unsplash API key not configured.")
        
        # pu = PyUnsplash(api_key=config["unsplash_api_key"])
        # search = pu.search(type_='photos', query=query, page=page, per_page=per_page)
        
        # images = []
        # for photo in search.entries:
        #     images.append({
        #         "id": photo.id,
        #         "urls": {
        #             "raw": photo.link_download_location,
        #             "full": photo.link_download_location,
        #             "regular": photo.body.get('urls', {}).get('regular', ''),
        #             "small": photo.body.get('urls', {}).get('small', ''),
        #             "thumb": photo.body.get('urls', {}).get('thumb', '')
        #         },
        #         "alt_description": photo.body.get('alt_description', ''),
        #         "description": photo.body.get('description', ''),
        #         "download_url": photo.link_download
        #     })
        
        # return {
        #     "results": images,
        #     "total": search.total
        # }
        
    except Exception as e:
        logger.error(f"Error searching images: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Scheduling endpoints
@api_router.post("/schedule-post", response_model=ScheduledPost)
async def schedule_post(post: ScheduledPostCreate):
    """Schedule a post for future publishing"""
    try:
        scheduled_post = ScheduledPost(**post.dict())
        await db.scheduled_posts.insert_one(scheduled_post.dict())
        return scheduled_post
    except Exception as e:
        logger.error(f"Error scheduling post: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/scheduled-posts", response_model=List[ScheduledPost])
async def get_scheduled_posts():
    """Get all scheduled posts"""
    try:
        posts = await db.scheduled_posts.find({"user_id": "default"}).to_list(1000)
        return [ScheduledPost(**post) for post in posts]
    except Exception as e:
        logger.error(f"Error getting scheduled posts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.delete("/scheduled-posts/{post_id}")
async def delete_scheduled_post(post_id: str):
    """Delete a scheduled post"""
    try:
        result = await db.scheduled_posts.delete_one({"id": post_id})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Scheduled post not found")
        return {"message": "Scheduled post deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting scheduled post: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Export endpoints
@api_router.get("/export-posts/{format}")
async def export_posts(format: str, post_ids: List[str] = Query(...)):
    """Export posts in various formats"""
    try:
        if format not in ["csv", "txt", "json"]:
            raise HTTPException(status_code=400, detail="Unsupported export format")
        
        # Get posts from database
        posts = []
        for post_id in post_ids:
            post = await db.generated_posts.find_one({"id": post_id})
            if post:
                posts.append(post)
        
        if not posts:
            raise HTTPException(status_code=404, detail="No posts found")
        
        if format == "csv":
            # Generate CSV content
            csv_content = "Platform,Content,Hashtags,Created At\n"
            for post in posts:
                for content in post["post_contents"]:
                    hashtags = ",".join(content.get("hashtags", [])) if content.get("hashtags") else ""
                    csv_content += f'"{content["platform"]}","{content["content"]}","{hashtags}","{post["created_at"]}"\n'
            
            return {"content": csv_content, "filename": "posts.csv"}
            
        elif format == "json":
            return {"content": json.dumps(posts, default=str, indent=2), "filename": "posts.json"}
            
        elif format == "txt":
            txt_content = ""
            for post in posts:
                txt_content += f"Generated at: {post['created_at']}\n"
                txt_content += f"Variant: {post['variant_number']}\n"
                txt_content += "=" * 50 + "\n"
                for content in post["post_contents"]:
                    txt_content += f"\n{content['platform'].upper()}:\n"
                    txt_content += f"{content['content']}\n"
                    if content.get("hashtags"):
                        txt_content += f"Hashtags: {' '.join(content['hashtags'])}\n"
                txt_content += "\n" + "=" * 50 + "\n\n"
            
            return {"content": txt_content, "filename": "posts.txt"}
        
    except Exception as e:
        logger.error(f"Error exporting posts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Basic health check
@api_router.get("/")
async def root():
    return {"message": "AI Marketing Assistant API is running"}

@api_router.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
