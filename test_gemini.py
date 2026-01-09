#!/usr/bin/env python3
"""
Quick test script to verify Gemini API is working.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_gemini():
    """Test if Gemini API is configured and working."""
    
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        print("[ERROR] GEMINI_API_KEY not found in environment variables")
        print("\nPlease create a .env file in the project root with:")
        print("GEMINI_API_KEY=your_api_key_here")
        return False
    
    print(f"[OK] GEMINI_API_KEY found: {api_key[:10]}...{api_key[-4:]}")
    
    try:
        import google.generativeai as genai
        print("[OK] google-generativeai package installed")
    except ImportError:
        print("[ERROR] google-generativeai package not installed")
        print("Run: pip install google-generativeai")
        return False
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.0-flash-exp")
        
        print("[OK] Testing Gemini API call...")
        response = model.generate_content("Say 'Hello' in one word.")
        
        if response and response.text:
            print(f"[OK] Gemini API working! Response: {response.text.strip()}")
            return True
        else:
            print("[ERROR] No response from Gemini API")
            return False
            
    except Exception as e:
        print(f"[ERROR] {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("Gemini API Configuration Test")
    print("=" * 50)
    print()
    
    success = test_gemini()
    
    print()
    print("=" * 50)
    if success:
        print("[SUCCESS] All checks passed! Your Gemini API is configured correctly.")
        print("\nMake sure your backend server is restarted to use the new code.")
    else:
        print("[FAILED] Configuration issues found. Please fix them above.")
    print("=" * 50)

