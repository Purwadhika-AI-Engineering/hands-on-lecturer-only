from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import uvicorn
from model import ImageClassifier
import io
from PIL import Image
import numpy as np

app = FastAPI(title="Computer Vision Model API", version="1.0.0")

# Initialize the model
classifier = ImageClassifier()

@app.get("/")
async def root():
    return {"message": "Computer Vision Model API is running!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/predict")
async def predict_image(file: UploadFile = File(...)):
    """
    Predict the class of an uploaded image
    """
    try:
        # Read the uploaded file
        contents = await file.read()
        
        # Convert to PIL Image
        image = Image.open(io.BytesIO(contents))
        
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Resize to model input size
        image = image.resize((224, 224))
        
        # Convert to numpy array
        image_array = np.array(image)
        
        # Make prediction
        prediction = classifier.predict(image_array)
        
        return JSONResponse(content={
            "filename": file.filename,
            "prediction": prediction,
            "status": "success"
        })
        
    except Exception as e:
        return JSONResponse(
            status_code=400,
            content={
                "error": str(e),
                "status": "error"
            }
        )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
