from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from .functions_gui import get_suitable_widget, get_label, get_scroll_area_widgets_and_layouts, \
    get_value_from_suitable_widget


class Widget_Tournament_Parameters(QWidget):
    def __init__(self, tournament, initial=False):
        super().__init__()
        self.tournament = tournament
        parameter_display = tournament.get_parameter_display()

        self.parameter_widget_data = tuple(
            (parameter, parameter_display[parameter], get_suitable_widget(value, translate=True))
            for parameter, value in self.tournament.get_changeable_parameters(initial).items()
            if value is not None and parameter_display[parameter] is not None
        )

        parameter_widgets = []
        for _, display, widget in self.parameter_widget_data:
            parameter_widgets.extend([get_label(display, "large", translate=True), widget, QLabel()])

        layout = QVBoxLayout(self)
        get_scroll_area_widgets_and_layouts(layout, parameter_widgets[:-1], margins=(20, 20, 40, 20), spacing=10)

    def apply_parameters(self):
        keys = [parameter for parameter, _, _ in self.parameter_widget_data]
        values = [get_value_from_suitable_widget(widget) for _, _, widget in self.parameter_widget_data]
        return self.tournament.set_parameters_validate(keys, values)
