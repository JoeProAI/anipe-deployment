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

def generate_sales_page_html(product_data, product_content):
    """Generate a professional sales page HTML from product data"""
    
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
    
    # Create the HTML template
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{niche_topic} - AI-Generated Business Intelligence Report</title>
    <meta name="description" content="{problem_statement[:160]}">
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
            <h1>{niche_topic}</h1>
            <p class="subtitle">{problem_statement}</p>
            <div class="price">${base_price}</div>
            <a href="#buy-now" class="buy-button" id="buyButton">📈 Get Instant Access Now</a>
        </div>
        
        <div class="features">
            <h2>🎯 What You'll Get:</h2>
            <ul>
                <li>Comprehensive market analysis for {target_audience.lower()}</li>
                <li>AI-powered opportunity identification and validation</li>
                <li>Actionable business recommendations and next steps</li>
                <li>Professional report format ready for implementation</li>
                <li>Data-driven insights from advanced AI analysis</li>
                <li>Instant download - get started immediately</li>
                <li>Commercial usage rights included</li>
            </ul>
        </div>
        
        <div class="preview">
            <h3>📋 Report Preview:</h3>
            <p><strong>Target Market:</strong> {target_audience}</p>
            <p><strong>Key Focus Areas:</strong> {', '.join(keywords[:5])}</p>
            <p><strong>Report Length:</strong> {len(product_content.split())} words of actionable content</p>
            <p><strong>Generated:</strong> {datetime.now().strftime('%B %Y')}</p>
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
