from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from .tournament import Tournament
from .gui_functions import get_label, get_scroll_area_widgets_and_layouts
from .gui_options import get_suitable_widget, get_value_from_suitable_widget


class Widget_Tournament_Parameters(QWidget):
    def __init__(self, tournament: Tournament, initial: bool = False) -> None:
        super().__init__()
        self.tournament: Tournament = tournament
        parameters_display = tournament.get_parameters_display()

        self.parameter_widget_data = tuple(
            (parameter, parameters_display[parameter], get_suitable_widget(value, translate=True))
            for parameter, value in self.tournament.get_changeable_parameters(initial).items()
            if value is not None and parameters_display[parameter] is not None
        )

        parameter_widgets = []
        for _, display, widget in self.parameter_widget_data:
            assert(display is not None)
            parameter_widgets.extend([get_label(display, "large", translate=True), widget, QLabel()])

        self.layout_main: QVBoxLayout = QVBoxLayout(self)
        get_scroll_area_widgets_and_layouts(
            self.layout_main, parameter_widgets[:-1], margins=(20, 20, 60, 20), spacing=10
        )

    def apply_parameters(self) -> bool:
        keys = [parameter for parameter, _, _ in self.parameter_widget_data]
        values = [get_value_from_suitable_widget(widget) for _, _, widget in self.parameter_widget_data]
        return self.tournament.set_parameters_validate(keys, values)
