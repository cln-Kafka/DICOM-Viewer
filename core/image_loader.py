import os
from typing import Tuple

import numpy as np
import SimpleITK as sitk


class ImageLoaderError(Exception):
    """Custom exception for ImageLoader errors."""

    pass


class ImageLoader:
    FILE_TYPE_HANDLERS = {
        (".nii", ".nii.gz"): "load_nifti",
        (".mgh", ".mgz", ".mhd", ".nrrd"): "load_image_with_sitk",
        (".dcm", "directory"): "load_dicom_series",
    }

    @staticmethod
    def load_image(file_path: str) -> Tuple[np.ndarray, Tuple[float, ...]]:
        """
        Load a medical image file based on its extension.

        Args:
            file_path (str): Path to the image file or directory.

        Returns:
            Tuple[np.ndarray, Tuple[float, ...]]: Image array and spacing.

        Raises:
            ImageLoaderError: If the file format is unsupported or loading fails.
        """
        try:
            ext = os.path.splitext(file_path)[-1].lower()
            if os.path.isdir(file_path):
                ext = "directory"  # Handle directories separately

            for extensions, handler in ImageLoader.FILE_TYPE_HANDLERS.items():
                if ext in extensions:
                    return getattr(ImageLoader, handler)(file_path)

            raise ImageLoaderError("Unsupported file format")
        except Exception as e:
            raise ImageLoaderError(f"Failed to load image: {e}")

    @staticmethod
    def load_nifti(file_path: str) -> Tuple[np.ndarray, Tuple[float, ...]]:
        """
        Load a NIfTI image file.

        Args:
            file_path (str): Path to the NIfTI file.

        Returns:
            Tuple[np.ndarray, Tuple[float, ...]]: Image array and spacing.

        Raises:
            ImageLoaderError: If loading fails.
        """
        try:
            image = sitk.ReadImage(file_path)
            return sitk.GetArrayFromImage(image), image.GetSpacing()
        except Exception as e:
            raise ImageLoaderError(f"Failed to load NIfTI file: {e}")

    @staticmethod
    def load_image_with_sitk(file_path: str) -> Tuple[np.ndarray, Tuple[float, ...]]:
        """
        Load a general image file supported by SimpleITK.

        Args:
            file_path (str): Path to the image file.

        Returns:
            Tuple[np.ndarray, Tuple[float, ...]]: Image array and spacing.

        Raises:
            ImageLoaderError: If loading fails.
        """
        try:
            image = sitk.ReadImage(file_path)
            return sitk.GetArrayFromImage(image), image.GetSpacing()
        except Exception as e:
            raise ImageLoaderError(f"Failed to load image with SimpleITK: {e}")

    @staticmethod
    def load_dicom_series(directory: str) -> Tuple[np.ndarray, Tuple[float, ...]]:
        """
        Load a DICOM series from a directory.

        Args:
            directory (str): Path to the directory containing DICOM files.

        Returns:
            Tuple[np.ndarray, Tuple[float, ...]]: Image array and spacing.

        Raises:
            ImageLoaderError: If the directory is empty or loading fails.
        """
        try:
            reader = sitk.ImageSeriesReader()
            dicom_files = reader.GetGDCMSeriesFileNames(directory)
            if not dicom_files:
                raise ImageLoaderError(
                    f"No DICOM files found in directory: {directory}"
                )
            reader.SetFileNames(dicom_files)
            image = reader.Execute()
            return sitk.GetArrayFromImage(image), image.GetSpacing()
        except Exception as e:
            raise ImageLoaderError(f"Failed to load DICOM series: {e}")

    @staticmethod
    def load_sample_image(file_path: str) -> Tuple[np.ndarray, Tuple[float, ...]]:
        """
        Load a sample NIfTI image for testing.

        Args:
            file_path (str): Path to the NIfTI file.

        Returns:
            Tuple[np.ndarray, Tuple[float, ...]]: Image array and spacing.

        Raises:
            ImageLoaderError: If loading fails.
        """
        try:
            return ImageLoader.load_nifti(file_path)
        except Exception as e:
            raise ImageLoaderError(f"Failed to load sample image: {e}")
