import os
import json
from datetime import datetime
from flask import Flask, request, jsonify
from google.cloud import storage

# Initialize Flask app
app = Flask(__name__)

# Initialize GCP clients
try:
    storage_client = storage.Client()
except Exception as e:
    print(f"Error initializing GCP clients: {e}")

# Get environment variables
GCS_BUCKET_NAME = os.environ.get("GCS_BUCKET_NAME", "windsurf-anipe-data")

# --- Helper Function: Generate Product Content with Simulated AI Response ---
def generate_product_content(opportunity: dict) -> str:
    """
    Simulates an AI response for generating the content for the digital product based on the identified opportunity.
    """
    niche_topic = opportunity.get("niche_topic", "an unspecified niche")
    product_idea = opportunity.get("product_idea", "a detailed report")
    problem_statement = opportunity.get("problem_statement", "a common problem")
    target_audience = opportunity.get("target_audience", "general audience")
    
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
        
        # Generate product content using simulated AI response
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
