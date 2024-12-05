import numpy as np
import torch
from PIL import Image
from PyQt5.QtCore import QThread, pyqtSignal
from transformers import AutoImageProcessor, AutoModelForImageClassification


class CDSSWorker(QThread):
    prediction_signal = pyqtSignal(str)  # Signal to emit the prediction result

    def __init__(self):
        super().__init__()
        # Load the Hugging Face model and processor
        self.processor = AutoImageProcessor.from_pretrained(
            "vishnu027/dental_classification_model_010424_2"
        )
        self.model = AutoModelForImageClassification.from_pretrained(
            "vishnu027/dental_classification_model_010424_2"
        )
        self.slice_data = None  # Placeholder for the 2D slice

    def set_slice(self, slice_data):
        """Set the 2D slice data for processing."""
        self.slice_data = slice_data

    def preprocess_slice(self, slice_data):
        """
        Preprocess the 2D slice for the Hugging Face model.
        Normalizes the image and converts it to a format suitable for the processor.
        """
        IMG_SIZE = (224, 224)  # Resize for model input consistency

        # Normalize the slice to [0, 255] range
        normalized_slice = (slice_data - np.min(slice_data)) / (
            np.max(slice_data) - np.min(slice_data)
        )
        normalized_slice = (normalized_slice * 255).astype(np.uint8)

        # Convert to RGB using PIL
        img = Image.fromarray(normalized_slice).convert("RGB")

        # Resize to model's input size
        img = img.resize(IMG_SIZE)

        # Use the processor to prepare the image
        inputs = self.processor(img, return_tensors="pt")
        return inputs

    def run(self):
        """Perform predictions and emit results."""
        if self.slice_data is not None:
            try:
                # Preprocess the 2D slice
                inputs = self.preprocess_slice(self.slice_data)

                # Perform inference
                with torch.no_grad():
                    outputs = self.model(**inputs)
                    predicted_class_idx = outputs.logits.argmax(-1).item()

                # Get the predicted label
                predicted_label = self.model.config.id2label[predicted_class_idx]

                # Emit the result
                result_message = f"Predicted: {predicted_label}"
                self.prediction_signal.emit(result_message)

            except Exception as e:
                self.prediction_signal.emit(f"Error: {str(e)}")
        else:
            self.prediction_signal.emit("No slice data provided for prediction.")
