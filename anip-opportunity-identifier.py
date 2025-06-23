import os
import json
import base64
import random
from datetime import datetime
from flask import Flask, request, jsonify
from google.cloud import storage
import google.generativeai as genai

# Initialize Flask app
app = Flask(__name__)

# Add favicon route to prevent 404 errors
@app.route('/favicon.ico')
def favicon():
    # Return 204 No Content - standard way to handle missing favicons
    return '', 204

# Initialize GCP clients
try:
    storage_client = storage.Client()
    # Configure Gemini API (using API key approach for simplicity)
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key:
        genai.configure(api_key=api_key)
    else:
        print("Warning: GEMINI_API_KEY not found, using simulated responses")
except Exception as e:
    print(f"Error initializing GCP clients: {e}")

# Get environment variables
GCS_BUCKET_NAME = os.environ.get("GCS_BUCKET_NAME", "windsurf-anipe-data")

# --- Helper Function: Perform Web Search ---
def perform_web_search(query: str, num_results: int = 5) -> list:
    """
    Performs a web search to find trending questions.
    In production, replace this with an actual search API integration.
    """
    print(f"Performing web search for: '{query}'")
    
    # Simulated results for demonstration purposes
    simulated_results = {
        "AI in Healthcare challenges": [
            {"title": "How is AI transforming patient diagnostics?", "snippet": "AI algorithms are improving accuracy in medical imaging analysis.", "link": "https://example.com/ai-diagnostics"},
            {"title": "What are the ethical implications of AI in medicine?", "snippet": "Concerns about bias and accountability in AI healthcare decisions.", "link": "https://example.com/ai-ethics"},
            {"title": "Can AI personalize treatment plans?", "snippet": "AI analyzes patient data to suggest tailored therapies.", "link": "https://example.com/ai-personalization"}
        ],
        "Sustainable Technology trends": [
            {"title": "What is the role of AI in renewable energy optimization?", "snippet": "AI predicts energy demand and optimizes grid management.", "link": "https://example.com/renewable-ai"},
            {"title": "How can blockchain support supply chain sustainability?", "snippet": "Blockchain provides transparency and traceability for ethical sourcing.", "link": "https://example.com/blockchain-sustainability"},
            {"title": "Emerging green technologies for smart cities", "snippet": "Innovations in waste management and energy-efficient infrastructure.", "link": "https://example.com/green-cities"}
        ],
        "Future of Work predictions": [
            {"title": "How will AI impact job displacement and creation?", "snippet": "Automation may replace some jobs but create new roles requiring different skills.", "link": "https://example.com/ai-jobs"},
            {"title": "What are the best strategies for upskilling in the AI era?", "snippet": "Lifelong learning and adaptability are key for future workforce.", "link": "https://example.com/upskilling-ai"},
            {"title": "The rise of the gig economy and AI's influence", "snippet": "AI platforms are connecting freelancers with opportunities globally.", "link": "https://example.com/gig-economy-ai"}
        ],
        "Personal Finance automation": [
            {"title": "How can AI optimize personal investment strategies?", "snippet": "AI-driven robo-advisors analyze market trends for personalized investment recommendations.", "link": "https://example.com/ai-investing"},
            {"title": "What are the best AI tools for budget management?", "snippet": "Smart algorithms categorize expenses and predict future spending patterns.", "link": "https://example.com/budget-ai"},
            {"title": "AI-powered fraud detection for personal banking", "snippet": "Machine learning models identify unusual transaction patterns to prevent fraud.", "link": "https://example.com/ai-fraud-prevention"}
        ],
        "Digital Marketing ROI": [
            {"title": "How to measure AI's impact on marketing campaigns?", "snippet": "Advanced analytics track customer journey and attribute conversions more accurately.", "link": "https://example.com/ai-marketing-analytics"},
            {"title": "Which AI tools provide the best ROI for small business marketing?", "snippet": "Cost-effective AI solutions for content creation and audience targeting.", "link": "https://example.com/small-business-ai"},
            {"title": "Predictive analytics for marketing budget optimization", "snippet": "AI forecasts campaign performance to allocate resources more efficiently.", "link": "https://example.com/predictive-marketing"}
        ]
    }
    
    # Randomly pick a broad topic
    broad_topic = random.choice(list(simulated_results.keys()))
    print(f"Selected broad topic: {broad_topic}")
    return simulated_results.get(broad_topic, [])

# --- Helper Function: Use AI for Niche Identification ---
def identify_niche_opportunity(search_results: list) -> dict:
    """
    Uses Gemini AI to analyze search results and identify a specific, actionable niche opportunity.
    Falls back to simulated responses if AI is unavailable.
    """
    if not search_results:
        return {"status": "no_opportunity", "message": "No relevant search results found."}

    prompt = f"""
    CRITICAL INSTRUCTIONS: You are an expert niche market researcher tasked with finding HIGHLY SPECIFIC, UNIQUE micro-opportunities that are NOT obvious or generic.

    FORBIDDEN TOPICS (DO NOT suggest anything related to):
    - Generic "communication" or "productivity"
    - Basic "time management" or "organization"  
    - Broad "marketing" or "social media"
    - Generic "wellness" or "fitness"
    - Common "leadership" or "team building"
    - Overused "AI tools" or "automation"

    REQUIREMENTS FOR A VALID OPPORTUNITY:
    1. Must be HYPER-SPECIFIC (not broad categories)
    2. Must target a clear, defined audience with money to spend
    3. Must solve a real, painful problem people pay to fix
    4. Must be something that can generate $5K+ monthly revenue
    5. Must be based on emerging trends or underserved segments
    6. Must be actionable and not theoretical

    Search Results to Analyze:
    {json.dumps(search_results, indent=2)}

    EXAMPLES of the specificity level required:
    GOOD: "AI-powered inventory optimization for artisanal food producers selling at farmers markets"
    GOOD: "Automated compliance reporting system for cryptocurrency tax accountants"
    GOOD: "Voice-to-text transcription service specialized for medical professionals treating ADHD patients"
    
    BAD: "Communication tools"
    BAD: "Productivity software"
    BAD: "AI-powered insights"

    Based on the search results, identify ONE unique micro-niche that meets ALL requirements above.

    Respond ONLY in valid JSON format:
    {{
        "niche_topic": "Ultra-specific 8-12 word description targeting exact audience and use case",
        "problem_statement": "Specific pain point that costs this audience time/money/stress",
        "target_audience": "Precise demographic with purchasing power (job title, industry, situation)",
        "product_idea": "Concrete digital solution (report, tool, course, template) they'd pay $50-500 for",
        "keywords": ["specific", "niche", "terms", "not", "generic"],
        "revenue_potential": "Realistic monthly revenue estimate with reasoning",
        "market_validation": "Why this audience would actually pay for this solution",
        "confidence_score": 0.85
    }}
    """
    
    # Start with complete default data to guarantee all required keys
    # Use timestamp to ensure uniqueness even in fallback mode
    timestamp_suffix = datetime.now().strftime("%H%M")
    
    default_opportunity = {
        "niche_topic": f"AI-powered patent analysis for renewable energy startups targeting Series A funding ({timestamp_suffix})",
        "problem_statement": "Renewable energy startups spend 40+ hours manually analyzing patent landscapes before investor meetings, often missing critical IP conflicts", 
        "target_audience": "Renewable energy startup founders preparing for Series A funding rounds ($2M+ raises)", 
        "product_idea": "Weekly AI-generated patent landscape reports with competitive analysis and IP risk assessment for specific renewable energy sectors",
        "keywords": ["patent analysis", "renewable energy", "IP due diligence", "startup funding", "Series A"],
        "revenue_potential": "$15,000/month from 30 startups paying $500/month for weekly reports",
        "market_validation": "Series A startups have budget for IP due diligence and investors require thorough patent analysis before funding decisions",
        "confidence_score": 0.85,
        "ai_powered": False,
        "status": "success"
    }
    
    # Try to use Gemini AI and merge with defaults
    try:
        if os.environ.get("GEMINI_API_KEY"):
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Extract JSON from response text
            if response_text.startswith("```json"):
                response_text = response_text[7:]
                if response_text.endswith("```"):
                    response_text = response_text[:-3]
            
            ai_opportunity = json.loads(response_text)
            
            # Merge AI response with defaults (AI data takes precedence)
            default_opportunity.update(ai_opportunity)
            default_opportunity["ai_powered"] = True
            
            print(f"AI generation successful: {default_opportunity.get('niche_topic', 'N/A')}")
            return default_opportunity
        else:
            raise Exception("No API key available")
            
    except Exception as e:
        error_msg = f"AI generation failed: {str(e)}"
        print(error_msg)
        
        # Add error details for debugging but keep all required keys
        default_opportunity["debug_error"] = error_msg
        
        return default_opportunity

# --- API Endpoint ---
@app.route('/identify', methods=['POST'])
def identify_opportunity():
    """API endpoint to identify a niche opportunity."""
    try:
        # Get request data (optional parameters)
        data = request.get_json(silent=True) or {}
        query = data.get('query', None)
        
        # Define broad search queries if not provided
        if not query:
            broad_queries = [
                "AI in Healthcare challenges",
                "Sustainable Technology trends",
                "Future of Work predictions",
                "Personal Finance automation questions",
                "Digital Marketing ROI challenges"
            ]
            query = random.choice(broad_queries)
        
        # Perform web search
        search_results = perform_web_search(query)
        
        # Identify niche opportunity using simulated AI response
        opportunity = identify_niche_opportunity(search_results)

        if opportunity["status"] == "success":
            print(f"Identified Niche Opportunity: {opportunity['niche_topic']}")
            
            # Store the identified opportunity in GCS
            bucket = storage_client.bucket(GCS_BUCKET_NAME)
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            blob_name = f"opportunities/opportunity_{timestamp}.json"
            blob = bucket.blob(blob_name)
            blob.upload_from_string(json.dumps(opportunity, indent=2), content_type="application/json")
            
            # Return success response
            response = {
                "status": "success", 
                "message": "Opportunity identified and saved.", 
                "opportunity": opportunity, 
                "gcs_path": f"gs://{GCS_BUCKET_NAME}/{blob_name}"
            }
            return jsonify(response), 200
        else:
            return jsonify({"status": "error", "message": opportunity["message"]}), 500
            
    except Exception as e:
        print(f"Error in identify_opportunity: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for Cloud Run."""
    return jsonify({"status": "healthy", "service": "anip-opportunity-identifier"}), 200

# Store results endpoint - accepts final workflow results and stores in GCS
@app.route('/store', methods=['POST'])
def store_results():
    """API endpoint to store final ANIPE workflow results in GCS."""
    try:
        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "message": "No data provided"}), 400
        
        # Store the complete results in GCS
        bucket = storage_client.bucket(GCS_BUCKET_NAME)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        blob_name = f"results/anipe_complete_{timestamp}.json"
        blob = bucket.blob(blob_name)
        blob.upload_from_string(json.dumps(data, indent=2), content_type="application/json")
        
        print(f"Successfully stored results in GCS: {blob_name}")
        
        # Return success response
        response = {
            "status": "success", 
            "message": "Results stored successfully.", 
            "gcs_path": f"gs://{GCS_BUCKET_NAME}/{blob_name}",
            "timestamp": timestamp
        }
        return jsonify(response), 200
        
    except Exception as e:
        print(f"Error in store_results: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

# Main entry point
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)
