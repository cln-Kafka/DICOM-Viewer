import nibabel as nib


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
        # Future implementation for DICOM series loading
        raise NotImplementedError("DICOM series loading not yet implemented")

    @staticmethod
    def load_sample_image():
        # Future implementation for loading sample images
        raise NotImplementedError("Sample image loading not yet implemented")
