import numpy as np
import pandas as pd
import tensorflow as tf
from PIL import Image
from PyQt5.QtCore import QThread, pyqtSignal
from tensorflow.keras.losses import SparseCategoricalCrossentropy
from tensorflow.keras.models import load_model
from tensorflow.keras.optimizers import Adam


class CDSSWorker(QThread):
    prediction_signal = pyqtSignal(str)  # Signal to emit the prediction result

    def __init__(self, model_path, annotations_path):
        super().__init__()
        # Load and compile the model
        self.model = load_model(model_path, compile=False)
        self.model.compile(
            optimizer=Adam(), loss=SparseCategoricalCrossentropy(), metrics=["accuracy"]
        )
        self.annotations = pd.read_csv(annotations_path)  # Load annotations
        self.annotations_dict = dict(
            zip(self.annotations["filename"], self.annotations["class"])
        )
        self.classes = {"Fillings": 0, "Implant": 1, "Impacted Tooth": 2, "Cavity": 3}
        self.reverse_classes = {v: k for k, v in self.classes.items()}

        self.image_path = None  # Placeholder for the image path

    def set_image(self, image_path):
        """Set the image path for processing."""
        self.image_path = image_path

    def preprocess_image(self, image_path):
        """
        Preprocess the image for the model.
        Resizes, normalizes, and adds a batch dimension.
        """
        IMG_SIZE = (256, 256)  # Ensure consistency with training
        img = Image.open(image_path).convert("RGB")
        img = img.resize(IMG_SIZE)
        img_array = np.array(img) / 255.0  # Normalize to [0, 1]
        img_array = np.expand_dims(img_array, axis=0)  # Add batch dimension
        return img_array

    def run(self):
        """Perform predictions and emit results."""
        if self.image_path is not None:
            try:
                # Extract the image name for annotation lookup
                image_name = self.image_path.split("\\")[-1]
                true_label = self.annotations_dict.get(image_name, "Unknown")

                # Preprocess the image
                img_array = self.preprocess_image(self.image_path)

                # Make predictions
                predictions = self.model.predict(img_array)
                predicted_class = np.argmax(predictions, axis=1)[0]
                predicted_label = self.reverse_classes[predicted_class]

                # Prepare result message
                result_message = f"True: {true_label}, Predicted: {predicted_label}"
                if predicted_label == true_label:
                    result_message += " (Correct)"
                else:
                    result_message += " (Incorrect)"

                # Emit the result
                self.prediction_signal.emit(result_message)

            except Exception as e:
                self.prediction_signal.emit(f"Error: {str(e)}")
        else:
            self.prediction_signal.emit("No image provided for prediction.")
