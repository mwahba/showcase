import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.model_helper import save_model

import tensorflow as tf
from tensorflow import keras
import numpy as np
import matplotlib.pyplot as plt

from utils.model_helper import save_model

# Constant Definitions


# Step 1: Import and Prepare the MNIST Dataset
def prepare_mnist_dataset() -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Load the MNIST digit dataset and preprocess it for training a neural network.

    Dataset Details:
    - 60,000 training images and 10,000 test images
    - Images are 28x28 pixels
    - Labels are integers from 0 to 9

    Returns: tuple with x/y training and testing data (4 numpy ndarrays)
    """
    (x_train, y_train), (x_test, y_test) = keras.datasets.mnist.load_data()

    # Normalize pixel values to be between 0 and 1: scale pizel values from 0-255 to 0-1
    # This helps the neural network converge faster, prevents large weight fluctuations,
    # and improves model training stability.
    x_train = x_train / 255.0
    x_test = x_test / 255.0

    # Reshape data for neural network: convert 2D images to 4D tensors
    # Dimensions:
    # 1. Number of images
    # 2/3: Image dimensions: height (28), width (28)
    # 4. Number of color channels (1 for grayscale)
    x_train = x_train.reshape(x_train.shape[0], 28, 28, 1)
    x_test = x_test.reshape(x_test.shape[0], 28, 28, 1)

    # Convert labels to categorical format
    # Example: 3 -> [0, 0, 0, 1, 0, 0, 0, 0, 0, 0]
    # Example: 9 -> [0, 0, 0, 0, 0, 0, 0, 0, 0, 1]
    # Why: neural networks need categorical output for multi-class classification
    y_train = keras.utils.to_categorical(y_train)
    y_test = keras.utils.to_categorical(y_test)

    return x_train, y_train, x_test, y_test

# Step 2: Create the Nerual Network Model
def create_mnist_model():
    """"""
    model = keras.Sequential([
        # Flatten the 28x28 images to a 1D array. Prepares images for dense (fully connected) layers.
        keras.layers.Flatten(input_shape=(28, 28, 1)),

        # Dense Layer (128 neurons)
        # First dense layer with ReLU (Rectified Linear Unit) activation. ReLU allows for non-linear transformations.
        # Helps the model learn complex patterns.
        keras.layers.Dense(128, activation='relu'),

        # Dropout Layer (0.2)
        # Dropout layer to prevent overfitting. Randomly drops 20% of neurons during training. Improves model generalization.
        keras.layers.Dropout(0.2),

        # Output Layer (10 neurons)
        # Output layer with softmax activation for multi-class classification. One neuron per digit (0-9).
        # Softmax activation converts outputs to probabilities. Ensures probabilities sum to 1.
        keras.layers.Dense(10, activation='softmax')
    ])

    # Compile the model
    model.compile(
        # Optimizer (Adam): Adaptive learning rate optimization algorithm.
        # Efficiently updates network weights, handles different parameter updates.
        optimizer='adam',
        # Loss function (Categorical Crossentropy): Measures model performance by measuring difference between predicted and actual distributions.
        loss='categorical_crossentropy',
        # Metrics: Used to evaluate model performance. Accuracy is the fraction (percentage) of correctly classified images.
        metrics=['accuracy']
    )

    return model


# Step 3: Train the Model
def train_mnist_model(model, x_train, y_train, x_test, y_test):
    # Train the model
    # Epochs: 10 -- Number of times the model will see the entire dataset during training.
    # Batch size: 32 -- Number of samples per gradient update. Smaller batch sizes provide a regularizing effect and reduce generalization error.
    #            Larger batch sizes can speed up training. Current processes 32 images before updating weights.
    # Validation split: 0.2 -- 20% of the training data is used for validation. Helps detect/monitor overfitting. Provides performance metrics during training.
    history = model.fit(
        x_train, y_train,
        epochs=10,
        batch_size=32,
        validation_split=0.2,
        verbose=1
    )

    return history


# Step 4: Evaluate the Model
# - Checks model performance on unseen test data.
# - Returns test loss and unbiased accuracy estimate.
def evaluate_model(model, x_test, y_test):
    test_loss, test_accuracy = model.evaluate(x_test, y_test, verbose=0)
    return test_loss, test_accuracy


# Step 5: Visualize Predictions
def visualize_predictions(model, x_test, y_test):
    # Predict on test data
    predictions = model.predict(x_test)

    # Plot some example predictions
    plt.figure(figsize=(10, 10))
    for i in range(25):
        plt.subplot(5, 5, i+1)
        plt.xticks([])
        plt.yticks([])
        plt.grid(False)

        # Display the image
        plt.imshow(x_test[i].reshape(28, 28), cmap=plt.cm.binary)

        # Determine the predicted and true labels
        predicted_label = np.argmax(predictions[i])
        actual_label = np.argmax(y_test[i])

        # Color code the title based on the correct/incorrect predictions
        color = 'green' if predicted_label == actual_label else 'red'
        plt.title(f"Predicted: {predicted_label}\nActual: {actual_label}", color=color)
    
    plt.tight_layout()
    plt.savefig('mnist_predictions.png')


def main(verbose: bool = False):
    # Prepare the dataset
    x_train, y_train, x_test, y_test = prepare_mnist_dataset()

    # Create the model
    model = create_mnist_model()

    # Train the model
    history = train_mnist_model(model, x_train, y_train, x_test, y_test)

    # Evaluate the model
    test_loss, test_accuracy = evaluate_model(model, x_test, y_test)

    if verbose:
        print(history)
        print(f"Test Loss: {test_loss}")
        print(f"Test accuracy: {test_accuracy * 100:.2f}%")

    # Visualize predictions
    visualize_predictions(model, x_test, y_test)

    # Save model
    save_model(model, 'mnist_digit_recognition', test_accuracy)


# Run main by default
if __name__ == "__main__":
    main(True)
