#!/usr/bin/env python3
"""
Quick test to verify Gemini API key format and basic functionality.
This file should NOT be committed to Git (contains sensitive data).
"""

import google.generativeai as genai

# Test the API key format
api_key = "AIzaSyAUZgIT2o1RsY4cQLFTtC6om-B-6ESzsbQ"
print(f"API Key format check: {'✅ Valid format' if api_key.startswith('AIzaSy') else '❌ Invalid format'}")

try:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-pro')
    
    # Simple test prompt
    response = model.generate_content("Say 'Hello from Gemini!' in exactly 3 words.")
    print(f"✅ API Test Success: {response.text.strip()}")
    
except Exception as e:
    print(f"❌ API Test Failed: {str(e)}")
