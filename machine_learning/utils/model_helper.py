import os
from datetime import datetime as dt
import json
import tensorflow as tf


def save_model(model, model_base_name: str, test_accuracy: float, base_output_dir: str = './models') -> tuple[str, str]:
    # Create base output directory if it does not exist
    model_dir = os.path.join(base_output_dir, model_base_name)
    if not os.path.exists(model_dir):
        os.makedirs(model_dir)
    
    # Create a timestamped folder for this model version
    timestamp = dt.now().strftime('%Y%m%d-%H%M%S')
    
    model_name = f'{model_base_name}_{timestamp}'
    model_path = os.path.join(model_dir, f'{model_name}.keras')
    model.save(model_path)

    metadata = {
        'model_name': model_name,
        'model_path': model_path,
        'timestamp': timestamp,
        'accuracy': test_accuracy,
        'model_architecture': model.get_config(),
    }

    metadata_path = os.path.join(model_dir, f'{model_name}_metadata.json')

    with open(metadata_path, "w") as f:
        json.dump(str(metadata), f, indent=2)
    
    print(f"Model saved to: {model_path}")
    print(f"Metadata saved to: {metadata_path}")
    
    return model_path, metadata_path


def load_saved_model(model_path):
    """
    Load a saved model for inference
    """
    return tf.keras.models.load_model(model_path)
