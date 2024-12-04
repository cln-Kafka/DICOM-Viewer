from pyqtgraph import ImageView

from utils.angle_roi import AngleROI
from utils.ruler_roi import RulerROI


class MeasurementTools:
    def __init__(self, backend):
        self.backend = backend
        self.active_measurements = (
            {}
        )  # Dictionary to track active measurements per viewer
        self.hidden_measurements = (
            {}
        )  # Dictionary to track hidden measurements per viewer

    def create_ruler(self, viewer: ImageView):
        """Create a ruler measurement tool."""
        ruler_roi = RulerROI(viewer)
        viewer.getView().addItem(ruler_roi)

        if viewer not in self.active_measurements:
            self.active_measurements[viewer] = []
        self.active_measurements[viewer].append(ruler_roi)

        return ruler_roi

    def create_angle_measurement(self, viewer: ImageView):
        """Create an angle measurement tool."""
        angle_roi = AngleROI(viewer)
        viewer.getView().addItem(angle_roi)

        if viewer not in self.active_measurements:
            self.active_measurements[viewer] = []
        self.active_measurements[viewer].append(angle_roi)

        return angle_roi

    def toggle_ruler(self, viewer: ImageView, checked):
        """Toggle the visibility of ruler measurements for the active viewer."""
        if viewer not in self.hidden_measurements:
            self.hidden_measurements[viewer] = []
        if viewer not in self.active_measurements:
            self.active_measurements[viewer] = []

        if checked:
            # Restore hidden rulers for the active viewer
            to_restore = [
                m for m in self.hidden_measurements[viewer] if isinstance(m, RulerROI)
            ]
            for measurement in to_restore:
                viewer.getView().addItem(measurement)
                viewer.getView().addItem(measurement.distance_text)
                self.active_measurements[viewer].append(measurement)
            self.hidden_measurements[viewer] = [
                m
                for m in self.hidden_measurements[viewer]
                if not isinstance(m, RulerROI)
            ]
        else:
            # Hide active rulers for the active viewer
            to_hide = [
                m for m in self.active_measurements[viewer] if isinstance(m, RulerROI)
            ]
            for measurement in to_hide:
                viewer.getView().removeItem(measurement)
                viewer.getView().removeItem(measurement.distance_text)
                self.hidden_measurements[viewer].append(measurement)
            self.active_measurements[viewer] = [
                m
                for m in self.active_measurements[viewer]
                if not isinstance(m, RulerROI)
            ]

    def toggle_angle(self, viewer: ImageView, checked):
        """Toggle the visibility of angle measurements for the active viewer."""
        if viewer not in self.hidden_measurements:
            self.hidden_measurements[viewer] = []
        if viewer not in self.active_measurements:
            self.active_measurements[viewer] = []

        if checked:
            # Restore hidden angles for the active viewer
            to_restore = [
                m for m in self.hidden_measurements[viewer] if isinstance(m, AngleROI)
            ]
            for measurement in to_restore:
                viewer.getView().addItem(measurement)
                viewer.getView().addItem(measurement.angle_text)
                self.active_measurements[viewer].append(measurement)
            self.hidden_measurements[viewer] = [
                m
                for m in self.hidden_measurements[viewer]
                if not isinstance(m, AngleROI)
            ]
        else:
            # Hide active angles for the active viewer
            to_hide = [
                m for m in self.active_measurements[viewer] if isinstance(m, AngleROI)
            ]
            for measurement in to_hide:
                viewer.getView().removeItem(measurement)
                viewer.getView().removeItem(measurement.angle_text)
                self.hidden_measurements[viewer].append(measurement)
            self.active_measurements[viewer] = [
                m
                for m in self.active_measurements[viewer]
                if not isinstance(m, AngleROI)
            ]
