import tensorflow as tf
from tensorflow import keras
import numpy as np
import os
from model import ImageClassifier

# Training size is configurable so it fits a classroom laptop:
#   TRAIN_SAMPLES=50000 EPOCHS=5 python train.py   (full CIFAR-10, very slow on CPU)
TRAIN_SAMPLES = int(os.getenv("TRAIN_SAMPLES", "5000"))
TEST_SAMPLES = int(os.getenv("TEST_SAMPLES", "1000"))
EPOCHS = int(os.getenv("EPOCHS", "3"))
BATCH_SIZE = 32

def download_and_prepare_data():
    """Download CIFAR-10 dataset (kept at 32x32; resized batch by batch while training)"""
    print("Downloading CIFAR-10 dataset...")

    # Load CIFAR-10 dataset
    (x_train, y_train), (x_test, y_test) = keras.datasets.cifar10.load_data()

    # Use a subset so training finishes in minutes, not hours
    x_train, y_train = x_train[:TRAIN_SAMPLES], y_train[:TRAIN_SAMPLES]
    x_test, y_test = x_test[:TEST_SAMPLES], y_test[:TEST_SAMPLES]

    return (x_train, y_train), (x_test, y_test)

def make_dataset(x, y):
    """Normalize and resize to 224x224 on the fly.

    The original version resized ALL 50,000 images up front, which needs about
    30 GB of RAM (50000 x 224 x 224 x 3 x 4 bytes) and crashes on a normal laptop.
    """
    def prep(img, label):
        img = tf.cast(img, tf.float32) / 255.0
        img = tf.image.resize(img, [224, 224])
        return img, label

    ds = tf.data.Dataset.from_tensor_slices((x, y))
    return ds.map(prep, num_parallel_calls=tf.data.AUTOTUNE).batch(BATCH_SIZE).prefetch(1)

def train_model():
    """Train the image classification model"""
    print("Starting model training...")

    # Create models directory
    os.makedirs("models", exist_ok=True)

    # Create model instance
    classifier = ImageClassifier()
    model = classifier.model

    # Download and prepare data
    (x_train, y_train), (x_test, y_test) = download_and_prepare_data()
    train_ds = make_dataset(x_train, y_train)
    test_ds = make_dataset(x_test, y_test)

    print(f"Training samples: {len(x_train)}, test samples: {len(x_test)}, epochs: {EPOCHS}")

    # Train the model
    print("Training model...")
    history = model.fit(
        train_ds,
        epochs=EPOCHS,
        validation_data=test_ds,
        verbose=1
    )

    # Save the model
    model_path = "models/cifar10_model.h5"
    model.save(model_path)
    print(f"Model saved to {model_path}")

    # Evaluate the model
    test_loss, test_acc = model.evaluate(test_ds, verbose=0)
    print(f"Test accuracy: {test_acc:.4f}")

    return history

if __name__ == "__main__":
    train_model()
