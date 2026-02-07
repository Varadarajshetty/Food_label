# Quick Start Guide - AI Food Label Decoder

Welcome! This guide will help you set up and run the AI Food Label Decoder locally.

## 🚀 First Time Setup (One-Time Only)

If you received this project as a ZIP file:
1. **Unzip** the folder to your desktop or preferred location.
2. Double-click **`setup.bat`**.
   - This script will automatically install all required Python libraries (like Flask, OpenCV, XGBoost) from the included `packages` folder.
   - **No internet connection is required** for this step if the `packages` folder is present.

## 🏃‍♂️ How to Run the App

After setup is complete, you need to start the Backend (server) and the Frontend (interface).

### Step 1: Start the Backend Server
1. Open the project folder.
2. Double-click **`run_app.bat`** (if available) OR verify running manually:
   - Open a terminal/command prompt in the `Food_Label` folder.
   - Type: `cd backend`
   - Type: `python app.py`
   - You should see "Running on http://127.0.0.1:5000". Keep this window OPEN.

### Step 2: Open the App
1. Go to the `frontend` folder.
2. Double-click **`index.html`**.
   - This will open the application in your web browser.

## 📸 How to Use
1. **Upload**: Click "Scan" and upload an image of a Lays packet or a Nutrition Facts table.
2. **Analyze**: The AI will detect the product, check nutrition values, and give you a Healthy/Limit/Avoid verdict.
3. **Explore**: See traffic lights, health scores, and alternative suggestions!

## ❓ Troubleshooting
- **"Python not found"**: Install Python 3.10+ from python.org and try again.
- **"Tesseract not found"**: You may need to install Tesseract OCR if the app complains about it (see `setup.bat` output).
