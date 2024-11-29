import numpy as np


class ImageProcessor:
    @staticmethod
    def get_slice(image_data, plane="axial"):
        """
        Extract a slice from 3D image data based on specified plane
        """
        if plane == "axial":
            return image_data[:, :, image_data.shape[2] // 2]
        elif plane == "sagittal":
            return image_data[image_data.shape[0] // 2, :, :]
        elif plane == "coronal":
            return image_data[:, image_data.shape[1] // 2, :]
