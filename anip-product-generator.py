import os
import json
from datetime import datetime
from flask import Flask, request, jsonify
from google.cloud import storage
import vertexai
from vertexai.generative_models import GenerativeModel

# Initialize Flask app
app = Flask(__name__)

# Initialize GCP clients
try:
    storage_client = storage.Client()
    vertexai.init(project=os.environ.get("GCP_PROJECT_ID", "windsurf-ai-project"), 
                  location=os.environ.get("GCP_REGION", "us-central1"))
except Exception as e:
    print(f"Error initializing GCP clients: {e}")

# Get environment variables
GCS_BUCKET_NAME = os.environ.get("GCS_BUCKET_NAME", "windsurf-anipe-data")

# --- Helper Function: Generate Product Content with LLM ---
def generate_product_content(opportunity: dict) -> str:
    """
    Uses an LLM to generate the content for the digital product based on the identified opportunity.
    """
    niche_topic = opportunity.get("niche_topic", "an unspecified niche")
    product_idea = opportunity.get("product_idea", "a detailed report")
    problem_statement = opportunity.get("problem_statement", "a common problem")
    target_audience = opportunity.get("target_audience", "general audience")
    
    prompt = f"""
    Generate a comprehensive, high-quality digital product.
    
    Product Idea: {product_idea}
    Niche Topic: {niche_topic}
    Problem Addressed: {problem_statement}
    Target Audience: {target_audience}
    
    Structure the content as a professional report or guide, including:
    1. An executive summary.
    2. Introduction to the problem.
    3. Detailed analysis/solution (at least 3 main sections).
    4. Actionable recommendations or next steps.
    5. Conclusion.
    
    Ensure the tone is authoritative and provides genuine value to the target audience.
    The report should be at least 1500 words.
    """
    
    try:
        model = GenerativeModel(model_id="gemini-pro")
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error generating product content with LLM: {e}")
        return f"Error: Could not generate product content. {e}"

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
        
        # Generate product content using LLM
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
