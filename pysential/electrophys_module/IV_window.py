# importing the required packages
from pysential.protomodules import (AbstractWindow, FormDialogs)
import numpy as np
import ast


class CurrentVoltageResults(AbstractWindow):
    def __init__(self, obj: object) -> None:
        # Inherent AbstractModule
        super(CurrentVoltageResults, self).__init__(obj)

        # Set the title of the workspace
        # Set workspace icon
        self.title = "IV curve"
        self.ico = "logo"
        self.toolbar = None
        self.chart = None
        self.voltage = None
        self.current = None

    def set_data(self, voltage, current):
        self.voltage = voltage
        self.current = current

    def run(self):
        self.chart = self.widgets.make_chart_view(grid=(5, 25, 1, 22))
        print(self.voltage)
        print(self.current)
        v, c = zip(*sorted(zip(self.voltage, self.current)))
        self.widgets.add_chart_data(self.chart, x_data=np.array(v), y_data=np.array(c),
                                    x_name="Voltage", x_unit="V", y_name="Current", y_unit="A", symbol="o", reset=True)
        self.widgets.add_chart_data(self.chart, x_data=np.array(v), y_data=np.array(c),
                                    x_name="Voltage", x_unit="V", y_name="Current", y_unit="A", reset=False)

        # Set window contents (finish)
        self.set_content()

