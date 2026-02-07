
import base64
from PIL import Image
import io
import os

def test_resize(image_path):
    print(f"Testing resize on dummy image: {image_path}")
    
    # Create a dummy large image
    img = Image.new('RGB', (2000, 2000), color = 'red')
    img.save(image_path)
    print(f"Created large image: {img.size}")
    
    # Simulate the _encode_image logic
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
            encoded = base64.b64encode(buffer.getvalue()).decode('utf-8')
            print(f"Encoded string length: {len(encoded)}")
            print("Success!")
            
    except Exception as e:
        print(f"Failed: {e}")
    finally:
        if os.path.exists(image_path):
            os.remove(image_path)

if __name__ == "__main__":
    test_resize("test_large_image.jpg")
