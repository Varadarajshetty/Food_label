"""
OCR Image Processing Module
Extracts nutrition information from food label images using Tesseract OCR
"""

import re
import cv2
import numpy as np
from PIL import Image
import pytesseract
from pathlib import Path

# Set Tesseract path (Windows default installation)
# Update this path if Tesseract is installed elsewhere
# Set Tesseract path (Windows default installation)
# On Linux (Render), tesseract is usually in PATH, so strict path not needed
import platform
if platform.system() == 'Windows':
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
# else: Assume it's in PATH for Linux/Deployments


class NutritionLabelOCR:
    """Extract nutrition values from food label images"""
    
    def __init__(self):
        # Patterns to match nutrition values
        self.patterns = {
            'calories': [
                r'calories?\s*[:=]?\s*(\d+\.?\d*)',
                r'energy\s*[:=]?\s*(\d+\.?\d*)\s*kcal',
                r'(\d+\.?\d*)\s*kcal'
            ],
            'protein': [
                r'protein\s*[:=]?\s*(\d+\.?\d*)\s*g',
                r'proteins?\s*[:=]?\s*(\d+\.?\d*)'
            ],
            'carbs': [
                r'carbohydrate[s]?\s*[:=]?\s*(\d+\.?\d*)\s*g',
                r'total\s*carb[s]?\s*[:=]?\s*(\d+\.?\d*)',
                r'carbs?\s*[:=]?\s*(\d+\.?\d*)'
            ],
            'fat': [
                r'total\s*fat\s*[:=]?\s*(\d+\.?\d*)\s*g',
                r'fat\s*[:=]?\s*(\d+\.?\d*)\s*g',
                r'fats?\s*[:=]?\s*(\d+\.?\d*)'
            ],
            'fiber': [
                r'dietary\s*fiber\s*[:=]?\s*(\d+\.?\d*)\s*g',
                r'fiber\s*[:=]?\s*(\d+\.?\d*)\s*g',
                r'fibre\s*[:=]?\s*(\d+\.?\d*)'
            ],
            'sugar': [
                r'total\s*sugars?\s*[:=]?\s*(\d+\.?\d*)\s*g',
                r'sugars?\s*[:=]?\s*(\d+\.?\d*)\s*g'
            ],
            'sodium': [
                r'sodium\s*[:=]?\s*(\d+\.?\d*)\s*mg',
                r'salt\s*[:=]?\s*(\d+\.?\d*)\s*g'
            ],
            'cholesterol': [
                r'cholesterol\s*[:=]?\s*(\d+\.?\d*)\s*mg'
            ],
            'saturated_fat': [
                r'saturated\s*fat\s*[:=]?\s*(\d+\.?\d*)\s*g',
                r'saturated\s*[:=]?\s*(\d+\.?\d*)'
            ]
        }
    
    def preprocess_image(self, image_path):
        """
        Preprocess image for better OCR accuracy
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Preprocessed image
        """
        # Read image
        img = cv2.imread(str(image_path))
        
        if img is None:
            raise ValueError(f"Could not read image: {image_path}")
        
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Check size and rescale if too small (improves OCR for low-res images)
        height, width = gray.shape
        if width < 1000:
            scale = 2.0
            gray = cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
        
        # Apply adaptive thresholding (better for varying lighting)
        thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                     cv2.THRESH_BINARY, 11, 2)
        
        return thresh
    
    def preprocess_improved(self, image_path):
        """
        Advanced preprocessing pipeline for better OCR
        """
        img = cv2.imread(str(image_path))
        if img is None:
            raise ValueError(f"Could not read image: {image_path}")
            
        # 1. Grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # 2. Denoising
        # h=10 (filter strength), templateWindowSize=7, searchWindowSize=21
        denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
        
        # 3. Contrast Enhancement (CLAHE)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        contrast = clahe.apply(denoised)
        
        # 4. Resize if too small suitable for OCR
        height, width = contrast.shape
        if width < 1000:
            scale = 2.0
            contrast = cv2.resize(contrast, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
            
        # 5. Adaptive Thresholding
        thresh = cv2.adaptiveThreshold(contrast, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                     cv2.THRESH_BINARY, 11, 2)
                                     
        return thresh

    def preprocess_image(self, image_path):
        """Wrapper for improved preprocessing (backward compatibility)"""
        return self.preprocess_improved(image_path)
    
    def extract_text(self, image_path):
        """
        Extract text from image using OCR
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Extracted text string
        """
        try:
            # Preprocess image
            processed_img = self.preprocess_image(image_path)
            
            # Convert to PIL Image
            pil_img = Image.fromarray(processed_img)
            
            # Perform OCR with Data Output to get confidence
            from pytesseract import Output
            data = pytesseract.image_to_data(pil_img, config='--psm 6', output_type=Output.DICT)
            
            # Reconstruct text
            text_parts = [word for word in data['text'] if word.strip()]
            text = " ".join(text_parts)
            
            # Calculate Average Confidence
            # Filter out entries with no text or low confidence (-1)
            confidences = [int(conf) for i, conf in enumerate(data['conf']) 
                          if int(conf) != -1 and data['text'][i].strip()]
            
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
            
            print(f"[OCR] Average Confidence: {avg_confidence:.1f}%")
            
            return text, avg_confidence
        
        except Exception as e:
            print(f"OCR Error: {e}")
            return ""
    
    def extract_nutrition_values(self, text):
        """
        Extract nutrition values from OCR text
        
        Args:
            text: OCR extracted text
            
        Returns:
            Dictionary of nutrition values
        """
        # Convert to lowercase for easier matching
        text_lower = text.lower()
        
        nutrition_data = {}
        
        # Try to extract each nutrient
        for nutrient, patterns in self.patterns.items():
            value = self._extract_value(text_lower, patterns)
            
            # Special handling for sodium from salt
            if nutrient == 'sodium' and value is None:
                # If salt is given in grams, convert to mg (1g salt ≈ 400mg sodium)
                salt_match = re.search(r'salt\s*[:=]?\s*(\d+\.?\d*)\s*g', text_lower)
                if salt_match:
                    salt_g = float(salt_match.group(1))
                    value = salt_g * 400  # Approximate conversion
            
            nutrition_data[nutrient] = value if value is not None else 0.0
        
        return nutrition_data
    
    def _extract_value(self, text, patterns):
        """
        Extract numeric value using multiple patterns
        
        Args:
            text: Text to search
            patterns: List of regex patterns
            
        Returns:
            Extracted value or None
        """
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    return float(match.group(1))
                except (ValueError, IndexError):
                    continue
        
        return None
    
    def process_image(self, image_path):
        """
        Complete pipeline: Extract text and parse nutrition values
        
        Args:
            image_path: Path to nutrition label image
            
        Returns:
            Dictionary with nutrition values
        """
        print(f"Processing image: {image_path}")
        
        # Extract text
        text, confidence = self.extract_text(image_path)
        
        if not text:
            raise ValueError("Could not extract text from image")
        
        print(f"\nExtracted text (Conf: {confidence:.1f}%):\n{text}\n")
        
        # Parse nutrition values
        nutrition_data = self.extract_nutrition_values(text)
        
        print(f"Extracted nutrition data:")
        for key, value in nutrition_data.items():
            print(f"  {key}: {value}")
        
        return nutrition_data, confidence
    
    def validate_extraction(self, nutrition_data):
        """
        Validate extracted data has reasonable values
        
        Args:
            nutrition_data: Extracted nutrition dictionary
            
        Returns:
            Boolean indicating if data is valid
        """
        # Check if at least calories or protein is extracted
        if nutrition_data.get('calories', 0) == 0 and nutrition_data.get('protein', 0) == 0:
            return False
        
        # Check for unreasonable values
        if nutrition_data.get('calories', 0) > 10000:  # Too high
            return False
        
        if nutrition_data.get('protein', 0) > 200:  # Unrealistic
            return False
        
        return True


    
    def extract_product_name(self, image_path):
        """
        Extract potential product name from image
        Uses a different PSM mode to handle sparse text on front of pack
        """
        try:
            processed_img = self.preprocess_image(image_path)
            pil_img = Image.fromarray(processed_img)
            
            # PSM 3 is fully automatic page segmentation, better for front of pack with scattered text
            # PSM 11 is sparse text, also good
            text = pytesseract.image_to_string(pil_img, config='--psm 11')
            
            # Simple heuristic: Split into lines, take longest line that isn't a likely keyword
            lines = [line.strip() for line in text.split('\n') if len(line.strip()) > 3]
            
            # Filter out likely non-name lines (e.g. weights, common words)
            candidates = []
            for line in lines:
                if not any(char.isdigit() for char in line): # Avoid lines with numbers (weights, counts)
                    candidates.append(line)
            
            if candidates:
                # Return top 3 unique candidates sorted by length (descending)
                # This helps if the brand name is shorter than the flavor description
                # e.g. "Lays" (4) vs "Classic Salted" (14)
                unique_candidates = sorted(list(set(candidates)), key=len, reverse=True)
                return unique_candidates[:3]
            
            return []
            
        except Exception as e:
            print(f"Product Name OCR Error: {e}")
            return None

    def detect_label_type(self, text):
        """
        Detect if text looks like a nutrition label or a product front
        """
        text_lower = text.lower()
        
        # Keywords strong indicator of a nutrition table
        nutrition_keywords = [
            'nutrition facts', 'calories', 'daily value', 
            'total fat', 'cholesterol', 'sodium', 'protein'
        ]
        
        # Count how many keywords appear
        keyword_count = sum(1 for kw in nutrition_keywords if kw in text_lower)
        
        if keyword_count >= 2:
            return 'nutrition_label'
        else:
            return 'product_front'

def test_ocr():
    """Test OCR with sample image"""
    ocr = NutritionLabelOCR()
    
    # Test with a sample image (you'll need to provide one)
    test_image = Path('test_nutrition_label.jpg')
    
    if test_image.exists():
        try:
            # First detect type (simulating app flow)
            # We need to extract text first for detection to work on the nutrition label path
            # But for product front we might use different extraction. 
            # Let's use the standard extraction for detection first.
            text, conf = ocr.extract_text(test_image)
            print(f"Extracted Text Confidence: {conf:.1f}%")
            
            label_type = ocr.detect_label_type(text)
            print(f"Detected Label Type: {label_type}")
            
            if label_type == 'nutrition_label':
                result = ocr.extract_nutrition_values(text)
                if ocr.validate_extraction(result):
                    print("\n[OK] Extraction successful and validated!")
                else:
                    print("\n[WARN] Extraction may be incomplete")
                return result
            else:
                print("Identified as product front, attempting name extraction...")
                name = ocr.extract_product_name(test_image)
                print(f"Extracted Name: {name}")
                return name
        
        except Exception as e:
            print(f"Error: {e}")
    else:
        print(f"Test image not found: {test_image}")

if __name__ == "__main__":
    print("="*80)
    print("NUTRITION LABEL OCR TEST")
    print("="*80)
    test_ocr()
