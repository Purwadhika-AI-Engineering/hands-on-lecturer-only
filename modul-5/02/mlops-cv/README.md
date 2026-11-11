# Computer Vision Model Deployment with FastAPI & Docker

This project demonstrates how to deploy a simple image classification model using FastAPI in a Docker container. The model can classify images into 10 categories from the CIFAR-10 dataset.

## Project Structure

```
mlops-cv/
├── app.py              # FastAPI application
├── model.py            # Image classification model
├── train.py            # Model training script
├── test.py             # Testing script
├── requirements.txt    # Python dependencies
├── Dockerfile          # Docker container configuration
├── docker-compose.yml  # Docker Compose configuration
└── README.md          # This file
```

## Features

- **Simple FastAPI API** for image classification
- **Modular design** with separate files for different components
- **Docker containerization** for easy deployment
- **CIFAR-10 image classification** (10 classes: airplane, automobile, bird, cat, deer, dog, frog, horse, ship, truck)
- **No overengineering** - simple and straightforward implementation

## API Endpoints

- `GET /` - Welcome message
- `GET /health` - Health check
- `POST /predict` - Upload image and get classification result

## Step-by-Step Deployment Guide

### Prerequisites

- Docker installed on your system
- Docker Compose (usually comes with Docker Desktop)

### Step 1: Clone and Navigate to Project

```bash
cd /path/to/your/project
```

### Step 2: Train the Model (Optional)

If you want to train the model yourself:

```bash
# Install Python dependencies locally (optional)
pip install -r requirements.txt

# Train the model (this will take some time)
python train.py
```

This will create a `models/` directory with the trained model.

### Step 3: Build and Run with Docker Compose (Recommended)

The easiest way to deploy:

```bash
# Build and start the container
docker-compose up --build

# To run in background
docker-compose up --build -d
```

The API will be available at: `http://localhost:8000`

### Step 4: Alternative - Manual Docker Build

If you prefer to build manually:

```bash
# Build the Docker image
docker build -t cv-api .

# Run the container
docker run -p 8000:8000 -v $(pwd)/models:/app/models cv-api
```

### Step 5: Test the API

#### Option 1: Using the test script

```bash
# In another terminal, run the test script
python test.py
```

#### Option 2: Using curl

```bash
# Health check
curl http://localhost:8000/health

# Test prediction with an image
curl -X POST "http://localhost:8000/predict" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@your_image.jpg"
```

#### Option 3: Using the FastAPI docs

Visit `http://localhost:8000/docs` in your browser to use the interactive API documentation.

### Step 6: Stop the Application

```bash
# Stop docker-compose
docker-compose down

# Or stop manual Docker container
docker stop <container_id>
```

## Usage Examples

### Python Client Example

```python
import requests

# Upload an image for classification
with open('test_image.jpg', 'rb') as f:
    files = {'file': ('test_image.jpg', f, 'image/jpeg')}
    response = requests.post('http://localhost:8000/predict', files=files)
    
result = response.json()
print(f"Predicted class: {result['prediction']['class']}")
print(f"Confidence: {result['prediction']['confidence']:.2f}")
```

### Response Format

```json
{
  "filename": "test_image.jpg",
  "prediction": {
    "class": "cat",
    "confidence": 0.85,
    "all_predictions": {
      "airplane": 0.01,
      "automobile": 0.02,
      "bird": 0.03,
      "cat": 0.85,
      "deer": 0.02,
      "dog": 0.04,
      "frog": 0.01,
      "horse": 0.01,
      "ship": 0.01,
      "truck": 0.00
    }
  },
  "status": "success"
}
```

## Troubleshooting

### Common Issues

1. **Port already in use**: Change the port in `docker-compose.yml` or stop other services using port 8000
2. **Model not found**: Run `python train.py` first to create the model
3. **Memory issues**: The model loads into memory, ensure you have enough RAM

### Docker Issues

```bash
# Check if container is running
docker ps

# View container logs
docker-compose logs

# Rebuild without cache
docker-compose build --no-cache
```

## Customization

### Adding New Classes

1. Modify the `class_names` list in `model.py`
2. Update the model architecture if needed
3. Retrain the model with new data

### Changing Model Architecture

Edit the `create_simple_model()` function in `model.py` to modify the CNN architecture.

### Environment Variables

You can add environment variables in `docker-compose.yml`:

```yaml
environment:
  - MODEL_PATH=/app/models/my_model.h5
  - API_PORT=8000
```

## Production Considerations

For production deployment, consider:

1. **Security**: Add authentication and input validation
2. **Scaling**: Use multiple replicas with load balancing
3. **Monitoring**: Add logging and metrics collection
4. **Model versioning**: Implement model version management
5. **Error handling**: Add comprehensive error handling

## Next Steps

- Add more sophisticated models (ResNet, EfficientNet)
- Implement model versioning
- Add batch prediction endpoint
- Integrate with cloud storage for model artifacts
- Add comprehensive logging and monitoring

## Catatan perubahan (hands-on Docker, Nov 2026)

- `train.py` me-resize per batch (hemat RAM). Ukuran training diatur env `TRAIN_SAMPLES`, `TEST_SAMPLES`, `EPOCHS` (default 5000 / 1000 / 3). Latih di dalam container: `docker run --rm -v "$(pwd)/models:/app/models" cv-api python train.py`.
- Ditambahkan `.dockerignore` (bobot `models/*.h5` tidak ikut image; mount sebagai volume), `docker-compose.yml`, dan `HEALTHCHECK` di `Dockerfile`.
- Di hands-on kelas, container ini dipetakan ke port host **8001**.
