import os
import json
import random
from datetime import datetime
from flask import Flask, request, jsonify
from google.cloud import storage
from google.cloud import aiplatform

# Initialize Flask app
app = Flask(__name__)

# Initialize GCP clients
try:
    storage_client = storage.Client()
    aiplatform.init(project=os.environ.get("GCP_PROJECT_ID", "windsurf-ai-project"), 
                    location=os.environ.get("GCP_REGION", "us-central1"))
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

# --- Helper Function: Use LLM for Niche Identification ---
def identify_niche_opportunity(search_results: list) -> dict:
    """
    Uses an LLM to analyze search results and identify a specific, actionable niche opportunity.
    """
    if not search_results:
        return {"status": "no_opportunity", "message": "No relevant search results found."}

    prompt = f"""
    Analyze the following web search results and identify a highly specific, commercially viable micro-niche opportunity.
    Focus on a problem or question that AI could help solve or provide unique insights for.
    
    Search Results:
    {json.dumps(search_results, indent=2)}
    
    Provide your analysis in JSON format with the following keys:
    - "niche_topic": A very specific, actionable topic (e.g., "AI-powered personalized nutrition plans for diabetics").
    - "problem_statement": The core problem this niche addresses.
    - "target_audience": Who would pay for a solution/product in this niche.
    - "product_idea": A concrete digital product idea (e.g., "A weekly AI-generated report on emerging sustainable energy patents").
    - "keywords": 3-5 relevant keywords for this niche.
    - "confidence_score": A score from 0.0 to 1.0 indicating confidence in this opportunity.
    """
    
    try:
        # Use Vertex AI's Gemini model
        model = aiplatform.GenerativeModel(model_id="gemini-pro")
        response = model.generate_content(prompt)
        
        # Extract JSON from response text
        response_text = response.text.strip()
        if response_text.startswith("```json"):
            response_text = response_text[7:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
        
        opportunity = json.loads(response_text)
        opportunity["status"] = "success"
        return opportunity
    except Exception as e:
        print(f"Error identifying niche opportunity with LLM: {e}")
        return {"status": "error", "message": f"LLM analysis failed: {e}"}

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
        
        # Identify niche opportunity using LLM
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

# Main entry point
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)
