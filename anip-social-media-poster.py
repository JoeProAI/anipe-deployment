#!/usr/bin/env python3
"""
ANIPE Social Media Poster Service
Automatically creates and posts promotional content for new products
"""

import os
import json
import requests
from datetime import datetime
from flask import Flask, request, jsonify
from google.cloud import storage
import google.generativeai as genai

app = Flask(__name__)

# Initialize GCP clients
try:
    storage_client = storage.Client()
    # Configure Gemini API
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key:
        genai.configure(api_key=api_key)
    else:
        print("Warning: GEMINI_API_KEY not found, using simulated responses")
except Exception as e:
    print(f"Error initializing GCP clients: {e}")

# Get environment variables
GCS_BUCKET_NAME = os.environ.get("GCS_BUCKET_NAME", "windsurf-anipe-data")
TWITTER_BEARER_TOKEN = os.environ.get("TWITTER_BEARER_TOKEN")
LINKEDIN_ACCESS_TOKEN = os.environ.get("LINKEDIN_ACCESS_TOKEN")

def generate_social_media_content(product_data: dict, sales_page_url: str) -> dict:
    """
    Generate engaging social media posts for the product using AI
    """
    niche_topic = product_data.get("niche_topic", "Business Intelligence")
    target_audience = product_data.get("target_audience", "professionals")
    
    prompt = f"""
    Create engaging social media content to promote this AI-generated product:

    Product Topic: {niche_topic}
    Target Audience: {target_audience}
    Sales Page: {sales_page_url}

    Create 3 different promotional posts:
    
    1. TWITTER POST (280 characters max):
    - Hook with pain point or benefit
    - Include trending hashtags
    - Call to action
    - Professional but engaging tone
    
    2. LINKEDIN POST (longer form):
    - Professional tone for business audience
    - Focus on ROI and business value
    - Include industry insights
    - Call to action for the report
    
    3. FACEBOOK POST (casual but valuable):
    - More conversational tone
    - Focus on transformation/results
    - Include emojis appropriately
    - Clear call to action

    Format as JSON with keys: twitter, linkedin, facebook
    Each should be ready to post directly.
    Include relevant hashtags for each platform.
    """

    try:
        if not api_key:
            raise Exception("No API key configured")
            
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        
        # Try to extract JSON from response
        content = response.text.strip()
        if content.startswith('```json'):
            content = content[7:-3]
        elif content.startswith('```'):
            content = content[3:-3]
            
        social_content = json.loads(content)
        return {
            "status": "success",
            "content": social_content,
            "debug_info": "Generated with Gemini AI"
        }
        
    except Exception as e:
        print(f"AI generation failed: {e}")
        # Fallback content
        return {
            "status": "success",
            "content": {
                "twitter": f"🚀 New AI Report: {niche_topic} insights that could change everything! Get the data-driven strategies top companies use. Limited time access ⏰ {sales_page_url} #AI #Business #Strategy #DataDriven",
                "linkedin": f"📊 Just released: Comprehensive {niche_topic} analysis that reveals market insights typically reserved for enterprise consultants.\n\nThis AI-generated report provides:\n✅ Data-driven market analysis\n✅ Actionable strategic recommendations\n✅ Competitive intelligence insights\n\nPerfect for {target_audience} looking to gain a competitive edge.\n\nAccess the full report: {sales_page_url}\n\n#BusinessIntelligence #MarketAnalysis #Strategy #AI",
                "facebook": f"🎯 Something exciting just dropped!\n\nWe've generated an in-depth {niche_topic} report using advanced AI analysis. The insights are incredible and could seriously impact how {target_audience} approach their strategy.\n\n💡 What's inside:\n- Market trends you won't find elsewhere\n- Actionable recommendations\n- Professional-grade analysis\n\nCheck it out here: {sales_page_url}\n\nLet me know what you think! 👇\n\n#AI #BusinessStrategy #MarketInsights"
            },
            "debug_info": f"Fallback content used - AI error: {e}"
        }

def post_to_twitter(content: str) -> dict:
    """
    Post content to Twitter/X using the API
    """
    if not TWITTER_BEARER_TOKEN:
        return {"status": "skipped", "message": "Twitter Bearer Token not configured"}
    
    try:
        # Twitter API v2 endpoint for posting tweets
        url = "https://api.twitter.com/2/tweets"
        headers = {
            "Authorization": f"Bearer {TWITTER_BEARER_TOKEN}",
            "Content-Type": "application/json"
        }
        data = {"text": content}
        
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 201:
            tweet_data = response.json()
            return {
                "status": "success",
                "platform": "twitter",
                "post_id": tweet_data.get("data", {}).get("id"),
                "message": "Posted to Twitter successfully"
            }
        else:
            return {
                "status": "error",
                "platform": "twitter",
                "message": f"Twitter API error: {response.status_code} - {response.text}"
            }
            
    except Exception as e:
        return {
            "status": "error",
            "platform": "twitter",
            "message": f"Error posting to Twitter: {e}"
        }

def post_to_linkedin(content: str) -> dict:
    """
    Post content to LinkedIn using the API
    """
    if not LINKEDIN_ACCESS_TOKEN:
        return {"status": "skipped", "message": "LinkedIn Access Token not configured"}
    
    try:
        # LinkedIn API endpoint for posting
        url = "https://api.linkedin.com/v2/ugcPosts"
        headers = {
            "Authorization": f"Bearer {LINKEDIN_ACCESS_TOKEN}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0"
        }
        
        data = {
            "author": "urn:li:person:YOUR_PERSON_ID",  # This would need to be configured
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": content
                    },
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }
        
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 201:
            return {
                "status": "success",
                "platform": "linkedin",
                "post_id": response.headers.get("x-linkedin-id"),
                "message": "Posted to LinkedIn successfully"
            }
        else:
            return {
                "status": "error",
                "platform": "linkedin",
                "message": f"LinkedIn API error: {response.status_code} - {response.text}"
            }
            
    except Exception as e:
        return {
            "status": "error",
            "platform": "linkedin",
            "message": f"Error posting to LinkedIn: {e}"
        }

@app.route('/promote', methods=['POST'])
def promote_product():
    """
    API endpoint to create and post social media content for a new product
    """
    try:
        # Get product data from request
        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "message": "No data provided"}), 400
        
        product_data = data.get('product_data', {})
        sales_page_url = data.get('sales_page_url')
        
        if not sales_page_url:
            return jsonify({"status": "error", "message": "Sales page URL required"}), 400
        
        print(f"Promoting product: {product_data.get('niche_topic', 'Unknown')}")
        
        # Generate social media content
        content_result = generate_social_media_content(product_data, sales_page_url)
        social_content = content_result.get('content', {})
        
        # Post to each platform
        results = []
        
        # Twitter
        if social_content.get('twitter'):
            twitter_result = post_to_twitter(social_content['twitter'])
            results.append(twitter_result)
        
        # LinkedIn  
        if social_content.get('linkedin'):
            linkedin_result = post_to_linkedin(social_content['linkedin'])
            results.append(linkedin_result)
        
        # Facebook posting would require similar implementation
        # For now, we'll just log the content
        if social_content.get('facebook'):
            results.append({
                "status": "logged",
                "platform": "facebook", 
                "message": "Facebook content generated (posting not implemented yet)",
                "content": social_content['facebook']
            })
        
        # Save promotion record to GCS
        niche_topic = product_data.get('niche_topic', 'unknown')
        safe_niche = niche_topic.replace(' ', '_').replace('/', '-')
        promotion_record = {
            "timestamp": datetime.now().isoformat(),
            "product_data": product_data,
            "sales_page_url": sales_page_url,
            "generated_content": social_content,
            "posting_results": results,
            "debug_info": content_result.get('debug_info')
        }
        
        record_blob_name = f"promotions/{safe_niche}_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
        record_blob = storage_client.bucket(GCS_BUCKET_NAME).blob(record_blob_name)
        record_blob.upload_from_string(json.dumps(promotion_record, indent=2), content_type="application/json")
        
        return jsonify({
            "status": "success",
            "message": "Social media promotion completed",
            "generated_content": social_content,
            "posting_results": results,
            "promotion_record": f"gs://{GCS_BUCKET_NAME}/{record_blob_name}"
        }), 200
        
    except Exception as e:
        print(f"Error in promote_product: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for Cloud Run."""
    return jsonify({"status": "healthy", "service": "anip-social-media-poster"}), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)
