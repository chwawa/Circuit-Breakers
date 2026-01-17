import asyncio
import os
import sys
import base64
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

def analyze_image_with_gemini(image_path: str) -> str:
    """
    Use Google Gemini to analyze the image and return a description.
    """
    # Get Gemini API key
    gemini_key = os.getenv('GEMINI_API_KEY')
    if not gemini_key:
        raise ValueError("GEMINI_API_KEY not found in environment")
    
    # Configure Gemini
    genai.configure(api_key=gemini_key)
    
    # Read and encode image
    with open(image_path, 'rb') as f:
        image_data = base64.b64encode(f.read()).decode('utf-8')
    
    # Get image media type
    if image_path.lower().endswith('.jpg') or image_path.lower().endswith('.jpeg'):
        media_type = "image/jpeg"
    elif image_path.lower().endswith('.png'):
        media_type = "image/png"
    else:
        media_type = "image/jpeg"  # default
    
    prompt = 'Describe this image in detail by speaking directly to the main object in second person (using "you"). Start with: "You are a ____."'
    
    print(f"📸 Sending image to Gemini for analysis...")
    
    # Call Gemini API
    model = genai.GenerativeModel('gemini-2.5-flash-lite')
    
    # Create image part
    image_part = {
        "mime_type": media_type,
        "data": image_data
    }
    
    # Generate content
    response = model.generate_content([prompt, image_part])
    description = response.text
    
    return description.strip()

def main(image_path: str):
    """
    Main flow: analyze image with Gemini and print description
    """
    # Validate image exists
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image not found: {image_path}")
    
    print(f"📸 Analyzing image: {image_path}\n")
    
    # Analyze with Gemini
    description = analyze_image_with_gemini(image_path)
    print("✅ Image analyzed!")
    print(f"\n📋 Description:\n{description}\n")
    
    return description

if __name__ == "__main__":
    # Get image path from command line or use default
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
    else:
        image_path = r"C:\Users\victo\OneDrive\Desktop\Programming\Circuit-Breakers\server\app\graces_airpods.jpg"
    
    result = main(image_path)
