class ImageProcessor:
    def __init__(self):
        self.current_slices = {"axial": None, "sagittal": None, "coronal": None}

    def set_image_data(self, image_data):
        self.image_data = image_data

        # It holds the index of the middle slice of each view
        self.current_slices = {
            "axial": self.image_data.shape[0] // 2,
            "sagittal": self.image_data.shape[2] // 2,
            "coronal": self.image_data.shape[1] // 2,
        }

    def get_slice(self, plane):
        if self.image_data is None:
            return None

        if plane == "axial":
            return self.image_data[self.current_slices["axial"], :, :]
        elif plane == "coronal":
            return self.image_data[:, self.current_slices["coronal"], :]
        elif plane == "sagittal":
            return self.image_data[:, :, self.current_slices["sagittal"]]

    def update_slice(self, plane, slice_index):
        max_slices = {
            "axial": self.image_data.shape[0],
            "coronal": self.image_data.shape[1],
            "sagittal": self.image_data.shape[2],
        }

        if 0 <= slice_index < max_slices[plane]:
            self.current_slices[plane] = slice_index
