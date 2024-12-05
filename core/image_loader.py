import os

import cv2
import SimpleITK as sitk


class ImageLoader:
    @staticmethod
    def load_image(file_path):
        try:
            if file_path.lower().endswith(".nii.gz"):
                ext = ".nii.gz"
            else:
                ext = os.path.splitext(file_path)[-1].lower()

            if ext in [".nii", ".nii.gz"]:
                return ImageLoader.load_nifti(file_path)

            elif ext in [".mgh", ".mgz", ".mhd", ".nrrd"]:
                image = sitk.ReadImage(file_path)
                return (
                    sitk.GetArrayFromImage(image),
                    image.GetSpacing(),
                )

            elif ext == ".dcm" or os.path.isdir(file_path):
                return ImageLoader.load_dicom_series(file_path)

            elif ext in [".png", ".jpg", ".jpeg"]:
                return ImageLoader.load_png(file_path)

        except Exception as e:
            raise ValueError(f"Unsupported image format: {e}")

    @staticmethod
    def load_nifti(file_path):
        try:
            image = sitk.ReadImage(file_path)
            return sitk.GetArrayFromImage(image), image.GetSpacing()
        except Exception as e:
            raise ValueError(f"Failed to load NIfTI file: {e}")

    @staticmethod
    def load_dicom_series(directory):
        try:
            reader = sitk.ImageSeriesReader()
            dicom_files = reader.GetGDCMSeriesFileNames(directory)
            reader.SetFileNames(dicom_files)
            image = reader.Execute()
            image = sitk.ReadImage(dicom_files)
            return sitk.GetArrayFromImage(image), image.GetSpacing()
        except Exception as e:
            raise ValueError(f"Failed to load DICOM series: {e}")

    @staticmethod
    def load_sample_image(file_path):
        try:
            return ImageLoader.load_nifti(file_path)
        except Exception as e:
            raise ValueError(f"Failed to load sample image: {e}")

    @staticmethod
    def load_png(file_path):
        try:
            image = cv2.imread(file_path, 0)
            return image, (1.0, 1.0, 1.0)
        except:
            raise ValueError("Failed to load PNG file")
