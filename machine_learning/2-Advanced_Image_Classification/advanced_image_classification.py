import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.model_helper import save_model

import tensorflow as tf
from tensorflow import keras
import numpy as np
import matplotlib.pyplot as plt
import datetime as dt
from tensorflow.keras.preprocessing.image import ImageDataGenerator

class CIFAR10Classifier:
    def __init__(self, model_dir='../model-outputs'):
        self.model_dir = model_dir
        self.class_names = ['airplane', 'automobile', 'bird', 'cat', 'deer',
                            'dog', 'frog', 'horse', 'ship', 'truck']
    
    def prepare_data(self):
        """Load and preprocess CIFAR-10 dataset"""
        # Load CIFAR-10 dataset
        (self.x_train, self.y_train), (self.x_test, self.y_test) = keras.datasets.cifar10.load_data()
        
        # Normalize pixel values
        self.x_train = self.x_train.astype('float32') / 255.0
        self.x_test = self.x_test.astype('float32') / 255.0
        
        # Convert class vectors to binary class matrices
        self.y_train = keras.utils.to_categorical(self.y_train, 10)
        self.y_test = keras.utils.to_categorical(self.y_test, 10)
        
        # Create data augmentation generator
        self.datagen = ImageDataGenerator(
            rotation_range=15,
            width_shift_range=0.1,
            height_shift_range=0.1,
            horizontal_flip=True,
            zoom_range=0.2
        )
        
        self.datagen.fit(self.x_train)
        
    def build_model(self):
        """Create CNN model with advanced architecture"""
        model = keras.Sequential([
            # First Convolutional Block
            keras.layers.Conv2D(32, (3, 3), padding='same', input_shape=(32, 32, 3)),
            keras.layers.BatchNormalization(),
            keras.layers.Activation('relu'),
            keras.layers.Conv2D(32, (3, 3), padding='same'),
            keras.layers.BatchNormalization(),
            keras.layers.Activation('relu'),
            keras.layers.MaxPooling2D((2, 2)),
            keras.layers.Dropout(0.25),
            
            # Second Convolutional Block
            keras.layers.Conv2D(64, (3, 3), padding='same'),
            keras.layers.BatchNormalization(),
            keras.layers.Activation('relu'),
            keras.layers.Conv2D(64, (3, 3), padding='same'),
            keras.layers.BatchNormalization(),
            keras.layers.Activation('relu'),
            keras.layers.MaxPooling2D((2, 2)),
            keras.layers.Dropout(0.25),
            
            # Third Convolutional Block
            keras.layers.Conv2D(128, (3, 3), padding='same'),
            keras.layers.BatchNormalization(),
            keras.layers.Activation('relu'),
            keras.layers.Conv2D(128, (3, 3), padding='same'),
            keras.layers.BatchNormalization(),
            keras.layers.Activation('relu'),
            keras.layers.MaxPooling2D((2, 2)),
            keras.layers.Dropout(0.25),
            
            # Dense Layers
            keras.layers.Flatten(),
            keras.layers.Dense(512),
            keras.layers.BatchNormalization(),
            keras.layers.Activation('relu'),
            keras.layers.Dropout(0.5),
            keras.layers.Dense(10, activation='softmax')
        ])
        
        # Compile model with learning rate schedule
        initial_learning_rate = 0.001
        lr_schedule = keras.optimizers.schedules.ExponentialDecay(
            initial_learning_rate, decay_steps=1000, decay_rate=0.9
        )
        optimizer = keras.optimizers.Adam(learning_rate=lr_schedule)
        
        model.compile(
            optimizer=optimizer,
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
        
        self.model = model
        return model
    
    def train_model(self, epochs=50, batch_size=64):
        """Train the model with data augmentation and callbacks"""
        # Create callbacks
        checkpoint_path = os.path.join(self.model_dir, 'checkpoints')
        os.makedirs(checkpoint_path, exist_ok=True)
        
        callbacks = [
            # Early stopping to prevent overfitting
            keras.callbacks.EarlyStopping(
                monitor = 'val_loss',
                patience = 10,
                restore_best_weights = True
            ),
            # Model checkpoint to save best model
            keras.callbacks.ModelCheckpoint(
                filepath = os.path.join(checkpoint_path, 'model_{epoch:02d}_{val_accuracy:.3f}.keras'),
                monitor = 'val_accuracy',
                save_best_only = True
            ),
            # TensorBoard logging
            keras.callbacks.TensorBoard(
                log_dir = os.path.join(self.model_dir, 'logs', dt.datetime.now().strftime("%Y%m%d-%H%M%S"))
            )
        ]

        # Train the model using data augmentation
        history = self.model.fit(
            self.datagen.flow(self.x_train, self.y_train, batch_size = batch_size),
            epochs = epochs,
            validation_data = (self.x_test, self.y_test),
            callbacks = callbacks
        )

        return history
    
    def evaluate_model(self):
        """Evaluate the model and create confusion matrix"""

        # Get predictions
        predictions = self.model.predict(self.x_test)
        predicted_classes = np.argmax(predictions, axis = 1)
        true_classes = np.argmax(self.y_test, axis = 1)

        # Calculate confusion matrix
        confusion_matrix = tf.math.confusion_matrix(true_classes, predicted_classes)

        # Plot confusion matrix
        plt.figure(figsize=(10, 8))
        plt.imshow(confusion_matrix, interpolation = 'nearest', cmap = plt.cm.Blues)
        plt.title('Confusion Matrix')
        plt.colorbar()

        # Add labels
        tick_marks = np.arange(len(self.class_names))
        plt.xticks(tick_marks, self.class_names, rotation = 45)
        plt.yticks(tick_marks, self.class_names)

        # Add numbers to the plot
        threshold = confusion_matrix.numpy().max() / 2.
        for i in range(confusion_matrix.shape[0]):
            for j in range(confusion_matrix.shape[1]):
                plt.text(j, i, format(confusion_matrix[i, j], 'd'), horizontalalignment = 'center', color = 'white' if confusion_matrix[i, j] > threshold else 'black')

        plt.ylabel('True label')
        plt.xlabel('Predicted label')
        plt.tight_layout
        # plt.show()
        plt.savefig('./confusion_matrix.png')

        # calculate and print classification report
        from sklearn.metrics import classification_report
        print("\nClassification Report:")
        print(classification_report(true_classes, predicted_classes, target_names = self.class_names))

def main():
    # Initialize Classifier
    classifier = CIFAR10Classifier()

    # Prepare data
    print('Preparing data...')
    classifier.prepare_data()

    # Build model
    print('Building model...')
    classifier.build_model()

    # Train model
    print('Training model...')
    history = classifier.train_model()

    print('Evaluating model...')
    classifier.evaluate_model()

    # Save model
    print('Saving model...')
    save_model(classifier.model, 'cifar10')

if __name__ == "__main__":
    main()
