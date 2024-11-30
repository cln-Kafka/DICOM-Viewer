import nibabel as nib
import SimpleITK as sitk
from vtkmodules.util import numpy_support


class ImageLoader:
    @staticmethod
    def load_nifti(file_path):
        try:
            nii_image = nib.load(file_path)
            return nii_image.get_fdata()
        except Exception as e:
            raise ValueError(f"Failed to load NIfTI file: {e}")

    @staticmethod
    def load_dicom_series(directory):
        try:
            reader = sitk.ImageSeriesReader()
            dicom_files = reader.GetGDCMSeriesFileNames(directory)
            reader.SetFileNames(dicom_files)
            image = reader.Execute()
            return sitk.GetArrayFromImage(image), image.GetSpacing()
        except Exception as e:
            raise ValueError(f"Failed to load DICOM series: {e}")

    @staticmethod
    def load_sample_image(file_path):
        try:
            return ImageLoader.load_nifti(file_path)
        except Exception as e:
            raise ValueError(f"Failed to load sample image: {e}")
