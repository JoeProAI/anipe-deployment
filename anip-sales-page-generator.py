#!/usr/bin/env python3
"""
ANIPE Sales Page Generator Service
Automatically converts AI-generated products into professional sales pages
"""

import os
import json
import hashlib
from datetime import datetime
from flask import Flask, request, jsonify
from google.cloud import storage
import google.generativeai as genai

app = Flask(__name__)

def generate_ai_sales_copy(product_data, product_content):
    """Generate AI-powered sales copy based on the product content"""
    
    # Default sales copy in case AI fails
    default_copy = {
        "headline": f"Revolutionary {product_data.get('niche_topic', 'Digital Product')} Guide",
        "subheadline": "Transform your approach with AI-generated insights",
        "benefits": [
            "Comprehensive analysis and recommendations",
            "Data-driven insights you can't find elsewhere", 
            "Actionable strategies for immediate implementation",
            "Expert-level knowledge distilled into practical steps"
        ],
        "description": "This comprehensive guide provides cutting-edge insights that would cost thousands from consulting firms.",
        "urgency": "Limited time offer - Get instant access today!"
    }
    
    try:
        # Get API key and check if available
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            print("No GEMINI_API_KEY found, using default sales copy")
            return default_copy
            
        # Configure Gemini
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Create prompt for sales copy generation
        prompt = f"""
Generate compelling sales copy for a digital product based on this content:

PRODUCT TOPIC: {product_data.get('niche_topic', 'Digital Product')}
TARGET AUDIENCE: {product_data.get('target_audience', 'Professionals')}
PROBLEM STATEMENT: {product_data.get('problem_statement', 'Industry challenges')}
KEYWORDS: {', '.join(product_data.get('keywords', []))}

PRODUCT CONTENT PREVIEW:
{product_content[:1000]}...

Generate sales copy in this JSON format:
{{
    "headline": "Compelling headline that grabs attention (max 60 chars)",
    "subheadline": "Supporting subheadline that explains the value (max 120 chars)",
    "benefits": [
        "Specific benefit 1 based on actual content",
        "Specific benefit 2 based on actual content", 
        "Specific benefit 3 based on actual content",
        "Specific benefit 4 based on actual content"
    ],
    "description": "2-3 sentence description of what they'll get and why it's valuable",
    "urgency": "Urgency statement to encourage immediate action"
}}

Make it sound professional but exciting. Focus on the specific value this content provides.
"""
        
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Clean up response if needed
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
            
        # Parse AI response
        ai_copy = json.loads(response_text)
        
        # Validate required fields exist
        required_fields = ['headline', 'subheadline', 'benefits', 'description', 'urgency']
        for field in required_fields:
            if field not in ai_copy:
                raise ValueError(f"Missing required field: {field}")
                
        print(f"AI sales copy generated successfully for: {ai_copy['headline']}")
        return ai_copy
        
    except Exception as e:
        print(f"AI sales copy generation failed: {e}, using default copy")
        return default_copy

def generate_sales_page_html(product_data, product_content):
    """Generate a professional sales page HTML from product data"""
    
    # Generate AI-powered sales copy based on the product content
    sales_copy = generate_ai_sales_copy(product_data, product_content)
    
    # Extract key information
    niche_topic = product_data.get('niche_topic', 'Digital Product')
    problem_statement = product_data.get('problem_statement', 'Solving important problems')
    target_audience = product_data.get('target_audience', 'Professional audience')
    keywords = product_data.get('keywords', [])
    
    # Create a clean title and filename
    clean_title = niche_topic.replace(' ', '_').replace('/', '_')[:50]
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Generate a price based on content length and topic complexity
    content_length = len(product_content)
    base_price = min(97, max(27, (content_length // 100) + len(keywords) * 3))
    
    # Create the HTML template with AI-generated sales copy
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{sales_copy['headline']} - AI-Generated Business Intelligence Report</title>
    <meta name="description" content="{sales_copy['description'][:160]}">
    <meta name="keywords" content="{', '.join(keywords)}">
    
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background: white;
            margin-top: 20px;
            margin-bottom: 20px;
            border-radius: 10px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
        }}
        
        .header {{
            text-align: center;
            padding: 40px 0;
            border-bottom: 2px solid #f0f0f0;
            margin-bottom: 30px;
        }}
        
        .header h1 {{
            font-size: 2.5rem;
            color: #2c3e50;
            margin-bottom: 10px;
            font-weight: 700;
        }}
        
        .header .subtitle {{
            font-size: 1.2rem;
            color: #7f8c8d;
            margin-bottom: 20px;
        }}
        
        .price {{
            font-size: 3rem;
            color: #e74c3c;
            font-weight: bold;
            margin: 20px 0;
        }}
        
        .buy-button {{
            display: inline-block;
            background: linear-gradient(45deg, #3498db, #2980b9);
            color: white;
            padding: 20px 40px;
            text-decoration: none;
            border-radius: 50px;
            font-size: 1.3rem;
            font-weight: bold;
            margin: 20px 0;
            transition: transform 0.3s ease;
            box-shadow: 0 10px 20px rgba(52, 152, 219, 0.3);
        }}
        
        .buy-button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 15px 30px rgba(52, 152, 219, 0.4);
        }}
        
        .features {{
            margin: 40px 0;
        }}
        
        .features h2 {{
            color: #2c3e50;
            margin-bottom: 20px;
            font-size: 1.8rem;
        }}
        
        .features ul {{
            list-style: none;
            padding-left: 0;
        }}
        
        .features li {{
            padding: 10px 0;
            border-bottom: 1px solid #ecf0f1;
            position: relative;
            padding-left: 30px;
        }}
        
        .features li:before {{
            content: "✓";
            position: absolute;
            left: 0;
            color: #27ae60;
            font-weight: bold;
            font-size: 1.2rem;
        }}
        
        .guarantee {{
            background: #f8f9fa;
            padding: 30px;
            border-radius: 10px;
            text-align: center;
            margin: 30px 0;
            border-left: 5px solid #27ae60;
        }}
        
        .preview {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
            border-left: 5px solid #3498db;
        }}
        
        .preview h3 {{
            color: #2c3e50;
            margin-bottom: 15px;
        }}
        
        .ai-badge {{
            display: inline-block;
            background: linear-gradient(45deg, #9b59b6, #8e44ad);
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9rem;
            margin: 10px 0;
        }}
        
        .urgency {{
            background: #fff3cd;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            margin: 20px 0;
            border-left: 5px solid #ffc107;
            font-weight: bold;
            color: #856404;
        }}
        
        @media (max-width: 768px) {{
            .container {{ margin: 10px; padding: 15px; }}
            .header h1 {{ font-size: 2rem; }}
            .price {{ font-size: 2.5rem; }}
            .buy-button {{ padding: 15px 30px; font-size: 1.1rem; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="ai-badge">🤖 AI-Generated Business Intelligence</div>
            <h1>{sales_copy['headline']}</h1>
            <p class="subtitle">{sales_copy['subheadline']}</p>
            <div class="price">${base_price}</div>
            <a href="#buy-now" class="buy-button" id="buyButton">📈 Get Instant Access Now</a>
        </div>
        
        <div class="features">
            <h2>🎯 What You'll Get:</h2>
            <ul>
                {''.join([f'<li>{benefit}</li>' for benefit in sales_copy['benefits']])}
            </ul>
        </div>
        
        <div class="preview">
            <h3>📋 About This Report:</h3>
            <p>{sales_copy['description']}</p>
            <p><strong>Target Market:</strong> {target_audience}</p>
            <p><strong>Key Focus Areas:</strong> {', '.join(keywords[:5])}</p>
            <p><strong>Report Length:</strong> {len(product_content.split())} words of actionable content</p>
            <p><strong>Generated:</strong> {datetime.now().strftime('%B %Y')}</p>
        </div>
        
        <div class="urgency">
            ⚡ {sales_copy['urgency']}
        </div>
        
        <div class="guarantee">
            <h3>💯 Your Success is Guaranteed</h3>
            <p>This AI-generated report provides cutting-edge insights that would cost thousands from consulting firms. If you're not completely satisfied with the actionable intelligence provided, contact us for a full refund within 30 days.</p>
        </div>
        
        <div style="text-align: center; margin: 40px 0;">
            <a href="#buy-now" class="buy-button" id="buyButton2">🚀 Transform Your Business Today - ${base_price}</a>
        </div>
        
        <div style="text-align: center; padding: 20px; color: #7f8c8d; font-size: 0.9rem;">
            <p>Generated by ANIPE - Autonomous Niche Intelligence & Product Engine</p>
            <p>© {datetime.now().year} AI Business Intelligence. All rights reserved.</p>
        </div>
    </div>
    
    <script>
        // Add click tracking and redirect functionality
        document.addEventListener('DOMContentLoaded', function() {{
            const buyButtons = document.querySelectorAll('#buyButton, #buyButton2');
            buyButtons.forEach(button => {{
                button.addEventListener('click', function(e) {{
                    e.preventDefault();
                    // This will be replaced with actual payment link
                    alert('Payment integration coming soon! Contact support to purchase this report.');
                    // window.open('PAYMENT_LINK_HERE', '_blank');
                }});
            }});
        }});
    </script>
</body>
</html>"""
    
    return html_content, f"{clean_title}_{timestamp}.html"

@app.route('/generate', methods=['POST'])
def generate_sales_page():
    """Generate a sales page from product data"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        # Extract the opportunity and product content
        opportunity = data.get('opportunity', {})
        product_content = data.get('product_content', '')
        
        if not product_content:
            return jsonify({"error": "No product content provided"}), 400
        
        # Generate the sales page
        html_content, filename = generate_sales_page_html(opportunity, product_content)
        
        # Upload to GCS if configured
        gcs_url = None
        bucket_name = os.environ.get('GCS_BUCKET_NAME', 'windsurf-anipe-sales-pages')
        if bucket_name:
            try:
                client = storage.Client()
                bucket = client.bucket(bucket_name)
                blob = bucket.blob(f"sales-pages/{filename}")
                blob.upload_from_string(html_content, content_type='text/html')
                
                # Make the blob publicly accessible
                blob.make_public()
                gcs_url = blob.public_url
                print(f"Sales page uploaded: {gcs_url}")
                
            except Exception as e:
                print(f"GCS upload failed: {e}")
        
        return jsonify({
            "status": "success",
            "filename": filename,
            "gcs_url": gcs_url,
            "html_content": html_content[:500] + "..." if len(html_content) > 500 else html_content,
            "message": "Sales page generated successfully"
        })
        
    except Exception as e:
        print(f"Sales page generation failed: {e}")
        return jsonify({
            "error": str(e),
            "status": "failed"
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "anip-sales-page-generator"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=True)
