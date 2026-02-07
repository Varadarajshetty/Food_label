import os
import base64
import json
from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

class OpenAIOCR:
    """Extract nutrition values from food label images using OpenAI GPT Vision"""
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        self.client = OpenAI(api_key=self.api_key)
        self.model = "gpt-4o-mini" # Using gpt-4o-mini for efficient vision processing

    def _encode_image(self, image_path):
        """Encode image to base64, resizing if necessary to improve speed"""
        from PIL import Image
        import io
        
        try:
            with Image.open(image_path) as img:
                # Resize if too large (max 1024x1024)
                max_size = (1024, 1024)
                if img.width > max_size[0] or img.height > max_size[1]:
                    img.thumbnail(max_size)
                    print(f"[DEBUG] Resized image to {img.size}")
                
                # Convert to RGB if necessary (e.g. for PNG with transparency)
                if img.mode in ('RGBA', 'P'):
                    img = img.convert('RGB')
                    
                # Save to buffer as JPEG
                buffer = io.BytesIO()
                img.save(buffer, format="JPEG", quality=85)
                return base64.b64encode(buffer.getvalue()).decode('utf-8')
                
        except Exception as e:
            print(f"[WARNING] Image resize failed, falling back to raw read: {e}")
            # Fallback to raw read
            with open(image_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')

    def extract_nutrition(self, image_path):
        """
        Extract nutrition values from an image using OpenAI Vision
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Dictionary of nutrition values or None if failed
        """
        try:
            base64_image = self._encode_image(image_path)
            
            prompt = """
            Analyze this food label image and extract the following nutritional information per 100g or per serving.
            Return the data STRICTLY in the following JSON format:
            {
                "calories": float,
                "protein": float, (in grams)
                "carbs": float, (in grams)
                "fat": float, (in grams)
                "fiber": float, (in grams)
                "sugar": float, (in grams)
                "sodium": float, (in milligrams)
                "cholesterol": float, (in milligrams)
                "saturated_fat": float (in grams)
            }
            If a value is not found, use 0.0. If multiple values exist (e.g., per serving and per 100g), prefer the values per 100g.
            Only return the JSON object, nothing else.
            """

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=500,
                response_format={"type": "json_object"}
            )

            result_text = response.choices[0].message.content
            nutrition_data = json.loads(result_text)
            
            # Ensure all keys exist
            required_keys = ['calories', 'protein', 'carbs', 'fat', 'fiber', 'sugar', 'sodium', 'cholesterol', 'saturated_fat']
            for key in required_keys:
                if key not in nutrition_data:
                    nutrition_data[key] = 0.0
                else:
                    # Ensure values are floats
                    try:
                        nutrition_data[key] = float(nutrition_data[key])
                    except (ValueError, TypeError):
                        nutrition_data[key] = 0.0
            
            return nutrition_data

        except Exception as e:
            print(f"OpenAI OCR Error: {e}")
            return None

    def detect_label_type(self, image_path):
        """
        Determine if the image is a nutrition facts label or product front
        """
        try:
            base64_image = self._encode_image(image_path)
            
            prompt = """
            Is this image a 'nutrition_label' (showing a table of facts) or a 'product_front' (showing the brand and product name)?
            Return only one word: either 'nutrition_label' or 'product_front'.
            """

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=10
            )

            result = response.choices[0].message.content.strip().lower()
            if 'nutrition' in result:
                return 'nutrition_label'
            return 'product_front'

        except Exception as e:
            print(f"Label Detection Error: {e}")
            return 'unknown'

    def extract_product_name(self, image_path):
        """
        Extract the product brand and name from a front-of-pack image
        """
        try:
            base64_image = self._encode_image(image_path)
            
            prompt = """
            Identify the brand and product name from this food packaging image.
            Return ONLY the brand and product name, nothing else. For example: 'Lays Classic Salted' or 'Coca-Cola Zero Sugar'.
            """

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=20
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            print(f"Product Identification Error: {e}")
            return None

if __name__ == "__main__":
    # Quick test
    import sys
    if len(sys.argv) > 1:
        ocr = OpenAIOCR()
        test_path = sys.argv[1]
        print(f"Testing OCR on {test_path}...")
        data = ocr.extract_nutrition(test_path)
        print(json.dumps(data, indent=2))
