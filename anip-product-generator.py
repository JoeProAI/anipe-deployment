import os
import json
from datetime import datetime
from flask import Flask, request, jsonify
from google.cloud import storage
import google.generativeai as genai

# Initialize Flask app
app = Flask(__name__)

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

# --- Helper Function: Generate Product Content with AI ---
def generate_product_content(opportunity: dict) -> str:
    """
    Uses Gemini AI to generate content for the digital product based on the identified opportunity.
    Falls back to simulated responses if AI is unavailable.
    """
    niche_topic = opportunity.get("niche_topic", "an unspecified niche")
    product_idea = opportunity.get("product_idea", "a detailed report")
    problem_statement = opportunity.get("problem_statement", "a general problem")
    target_audience = opportunity.get("target_audience", "general audience")
    
    prompt = f"""
    Generate a comprehensive, high-quality digital product for the following opportunity:
    
    Product Idea: {product_idea}
    Niche Topic: {niche_topic}
    Problem Addressed: {problem_statement}
    Target Audience: {target_audience}
    
    Create a professional report or guide with the following structure:
    1. Executive Summary (2-3 paragraphs)
    2. Introduction to the Problem (detailed explanation)
    3. Market Analysis (current trends, opportunities)
    4. Detailed Solution/Strategy (at least 3 main sections with actionable insights)
    5. Implementation Guidelines (step-by-step recommendations)
    6. Tools and Resources (specific recommendations)
    7. Future Outlook and Trends
    8. Conclusion with Key Takeaways
    
    Make it authoritative, valuable, and actionable for the target audience.
    The content should be comprehensive (aim for 2000+ words) and provide genuine value.
    Use professional formatting with clear headings and bullet points where appropriate.
    """
    
    # Try to use Gemini AI
    try:
        if os.environ.get("GEMINI_API_KEY"):
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content(prompt)
            return f"# AI-Generated Product Report\n\n{response.text}\n\n---\n*Generated using Gemini AI*"
        else:
            raise Exception("No API key available")
            
    except Exception as e:
        print(f"AI generation failed ({e}), using simulated response")
        
    # Fallback to simulated response
    simulated_response = f"""
    # Executive Summary

    This is a simulated executive summary for the product idea: {product_idea}.

    # Introduction to the Problem

    The problem statement is: {problem_statement}.

    # Detailed Analysis/Solution

    This is a simulated detailed analysis/solution for the problem statement.

    # Actionable Recommendations or Next Steps

    These are simulated actionable recommendations or next steps for the target audience: {target_audience}.

    # Conclusion

    This is a simulated conclusion for the product idea.

    ---
    *Generated using simulated AI response*
    """
    
    return simulated_response

# --- API Endpoint ---
@app.route('/generate', methods=['POST'])
def generate_product():
    """API endpoint to generate a product from an opportunity."""
    try:
        # Get opportunity data from request
        data = request.get_json()
        if not data or 'opportunity' not in data:
            return jsonify({"status": "error", "message": "No opportunity data provided"}), 400
        
        opportunity = data['opportunity']
        
        # Optionally retrieve from GCS if only a path is provided
        gcs_path = data.get('gcs_path', None)
        if not opportunity and gcs_path:
            try:
                # Extract bucket and blob name from gs:// URL
                path_parts = gcs_path.replace('gs://', '').split('/', 1)
                if len(path_parts) == 2:
                    bucket_name, blob_name = path_parts
                    bucket = storage_client.bucket(bucket_name)
                    blob = bucket.blob(blob_name)
                    opportunity_json = blob.download_as_text()
                    opportunity = json.loads(opportunity_json)
            except Exception as e:
                print(f"Error retrieving opportunity from GCS: {e}")
                return jsonify({"status": "error", "message": f"Failed to retrieve opportunity from GCS: {e}"}), 500
        
        print(f"Generating product for niche: {opportunity.get('niche_topic', 'N/A')}")
        
        # Generate product content using AI
        product_content = generate_product_content(opportunity)
        
        # Save the generated product content to GCS
        # Sanitize niche_topic for filename
        safe_niche_topic = opportunity['niche_topic'].replace(' ', '_').replace('/', '-').replace(':', '').replace(',', '')
        product_blob_name = f"products/{safe_niche_topic}_{datetime.now().strftime('%Y%m%d%H%M%S')}.md"
        product_blob = storage_client.bucket(GCS_BUCKET_NAME).blob(product_blob_name)
        product_blob.upload_from_string(product_content, content_type="text/markdown")
        
        # Return success response
        response = {
            "status": "success", 
            "message": "Product generated and saved.", 
            "product_gcs_path": f"gs://{GCS_BUCKET_NAME}/{product_blob_name}", 
            "opportunity": opportunity
        }
        return jsonify(response), 200
            
    except Exception as e:
        print(f"Error in generate_product: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for Cloud Run."""
    return jsonify({"status": "healthy", "service": "anip-product-generator"}), 200

# Main entry point
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)
