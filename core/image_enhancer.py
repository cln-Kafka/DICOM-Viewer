import cv2
import numpy as np
from scipy.ndimage import convolve, gaussian_filter, median_filter
from skimage.restoration import denoise_bilateral


class ImageEnhancer:
    @staticmethod
    def apply_window(image, window_level=None, window_width=None):
        min_val = np.min(image)
        max_val = np.max(image)

        # If window_level and window_width are not provided, use dynamic values
        if window_level is None:
            window_level = (min_val + max_val) / 2  # Center of the intensity range
        if window_width is None:
            window_width = max_val - min_val  # Full range of the intensities

        # Calculate the windowing bounds
        lower_bound = window_level - window_width / 2
        upper_bound = window_level + window_width / 2

        # Clip the image to the windowing range
        windowed_image = np.clip(image, lower_bound, upper_bound)

        # Normalize the image to the range [0, 1] for display purposes
        windowed_image = (windowed_image - lower_bound) / (upper_bound - lower_bound)

        return windowed_image

    @staticmethod
    def smooth_image(image, sigma=1, strength=1.0):
        return gaussian_filter(image, sigma=sigma) * strength

    @staticmethod
    def sharpen_image(image, strength=1.0):
        # Define the Laplacian kernel (3x3)
        laplacian_kernel = np.array(
            [[0, -1, 0], [-1, 4 * strength + 1, -1], [0, -1, 0]]
        )

        # Apply the convolution operation to sharpen the image
        sharpened_image = convolve(image, laplacian_kernel)

        return sharpened_image

    @staticmethod
    def denoise(image, filter_type, parameters):
        """
        Parameters:
            image (numpy.ndarray): 3D image array.
            filter_type (str): Type of noise reduction filter ('Median' or 'Bilateral').
            size (int): Size of the median filter kernel (used for 'Median').
            sigma_color (float): Range variance for bilateral filter (used for 'Bilateral').
            sigma_spatial (float): Spatial variance for bilateral filter (used for 'Bilateral').
        """
        filtered_image = image.copy()

        if filter_type == "Median":
            filtered_image = median_filter(filtered_image, size=parameters[0])
        elif filter_type == "Bilateral":
            filtered_image = denoise_bilateral(
                filtered_image,
                sigma_color=parameters[0],
                sigma_spatial=parameters[1],
            )
        else:
            raise ValueError(f"Unknown filter type: {filter_type}")

        return filtered_image

    @staticmethod
    def normalize_image(image):
        image = np.array(image, dtype=np.float32)
        normalized_image = (image - np.min(image)) / (np.max(image) - np.min(image))
        return normalized_image

    @staticmethod
    def high_pass_filter_cv(image, sigma=1.0, strength=1.0):
        # Apply Gaussian blur using OpenCV
        low_pass = cv2.GaussianBlur(image, (0, 0), sigma)

        # High-pass filtering by subtracting the blurred image
        high_pass = image - low_pass

        # Apply strength factor and add it back to the original image
        sharpened_image = image + (high_pass * strength)
        return sharpened_image
