import cv2
import numpy as np
from scipy.ndimage import convolve, gaussian_filter


class ImageEnhancer:
    @staticmethod
    @staticmethod
    def apply_window(volume, window_level=None, window_width=None):
        # Apply windowing to a 3D volume
        def window_slice(slice_image):
            min_val = np.min(slice_image)
            max_val = np.max(slice_image)
            window_level_ = (
                window_level if window_level is not None else (min_val + max_val) / 2
            )
            window_width_ = (
                window_width if window_width is not None else (max_val - min_val)
            )

            lower_bound = window_level_ - window_width_ / 2
            upper_bound = window_level_ + window_width_ / 2

            slice_image = np.clip(slice_image, lower_bound, upper_bound)
            return (slice_image - lower_bound) / (upper_bound - lower_bound)

        # Apply windowing to each slice along the first axis
        windowed_volume = np.stack(
            [window_slice(volume[i]) for i in range(volume.shape[0])]
        )
        return windowed_volume

    @staticmethod
    def smooth_image(image, sigma=1, strength=1.0):
        return gaussian_filter(image, sigma=sigma) * strength

    @staticmethod
    def sharpen_image(image, strength=1.0):
        # Define the Laplacian kernel (3x3 in 3 channels)
        laplacian_kernel = np.array(
            [
                [[0, 0, 0], [0, -1, 0], [0, 0, 0]],
                [[0, -1, 0], [-1, 5 * strength, -1], [0, -1, 0]],
                [[0, 0, 0], [0, -1, 0], [0, 0, 0]],
            ]
        )

        # Apply the convolution operation to sharpen the image
        sharpened_image = convolve(image, laplacian_kernel)

        return sharpened_image

    @staticmethod
    def reduce_noise(image, filter_type, size=3, sigma_color=0.05, sigma_spatial=15):
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
            from scipy.ndimage import median_filter

            filtered_image = median_filter(filtered_image, size=size)
        elif filter_type == "Bilateral":
            from skimage.restoration import denoise_bilateral

            filtered_image = denoise_bilateral(
                filtered_image,
                sigma_color=sigma_color,
                sigma_spatial=sigma_spatial,
                multichannel=False,  # Assuming the image is grayscale or single-channel
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
