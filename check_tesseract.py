
import sys
from pathlib import Path
import platform
import pytesseract
import cv2
import numpy as np

print("Checking Tesseract configuration...")

if platform.system() == 'Windows':
    tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    print(f"Expected Tesseract path: {tesseract_cmd}")
    pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
    
    import os
    if os.path.exists(tesseract_cmd):
        print("SUCCESS: Tesseract executable found.")
    else:
        print("ERROR: Tesseract executable NOT found at expected path.")
        print("If you installed it elsewhere, please update src/ocr_processor.py")

try:
    print("Attempting to run Tesseract on a dummy image...")
    # Create a dummy image
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    cv2.putText(img, 'TEST', (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    
    # Run OCR
    text = pytesseract.image_to_string(img)
    print(f"Tesseract returned text: '{text.strip()}'")
    print("SUCCESS: Tesseract is working.")
except Exception as e:
    print(f"ERROR: Tesseract execution failed: {e}")
