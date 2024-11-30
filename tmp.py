# def setup_mouse_handlers(self):
#     views = {
#         "axial": self.ui.axial_viewer.getView(),
#         "sagittal": self.ui.sagittal_viewer.getView(),
#         "coronal": self.ui.coronal_viewer.getView(),
#     }

#     for plane, view in views.items():
#         view.scene().sigMouseMoved.connect(
#             lambda pos, v=view, p=plane: self.on_mouse_moved(pos, v, p)
#         )

# def on_mouse_moved(self, pos, view: ViewBox, plane):
#     if view.sceneBoundingRect().contains(
#         pos
#     ):  # Check if the mouse is within the scene
#         mouse_point = view.mapSceneToView(
#             pos
#         )  # Map the scene position to the view's coordinates
#         x, y = int(mouse_point.x()), int(mouse_point.y())  # Get integer coordinates

#         # Update crosshair positions
#         self.ui.crosshairs[plane]["h_line"].setPos(y)
#         self.ui.crosshairs[plane]["v_line"].setPos(x)

#         # Update slices based on current plane
#         self.update_slices_from_crosshair(plane, x, y)

# def update_slices_from_crosshair(self, current_plane, x, y):
#     slice_indices = {
#         "axial": {"sagittal": y, "coronal": x},
#         "sagittal": {"axial": y, "coronal": x},
#         "coronal": {"axial": y, "sagittal": x},
#     }

#     if self.loaded_image_data is None:
#         return

#     for plane, idx in slice_indices[current_plane].items():
#         self.image_processor.update_slice(plane, idx)
#         slice_data = self.image_processor.get_slice(plane)
#         self.render_slice(getattr(self.ui, f"{plane}_viewer"), slice_data)

# def display_views(self):
#     if self.loaded_image_data is None:
#         return

#     views = {
#         "axial": self.ui.axial_viewer,
#         "sagittal": self.ui.sagittal_viewer,
#         "coronal": self.ui.coronal_viewer,
#     }

#     for plane, widget in views.items():
#         slice_data = self.image_processor.get_slice(plane)
#         self.render_slice(widget, slice_data)

#         # Get width and height of the slice
#         width, height = slice_data.shape

#         # Get the target range
#         target_range = (0, width) if width > height else (0, height)

#         # Set the X and Y limits for the view
#         widget.getView().setXRange(*target_range, padding=0)
#         widget.getView().setYRange(*target_range, padding=0)
#         widget.getView().setLimits(
#             xMin=target_range[0],
#             xMax=target_range[1],
#             yMin=target_range[0],
#             yMax=target_range[1],
#         )
