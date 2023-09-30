# importing the required packages
import os
import ast
import types
from pysential.protomodules import (AbstractModule, FormDialogs)
from pysential.default_modules import sql_database
from pysential.database import DatabaseManager
from .heka_reader import *


from scipy.ndimage.filters import gaussian_filter
from scipy.optimize import curve_fit
from .results_database import ShowResults
from .IV_window import CurrentVoltageResults

'''
    A not so nice way to import HoleyPy, Fix before release
'''
import sys
sys.path.insert(0, os.path.abspath('../HoleyPy'))
from holeypy import Trace, filters
from holeypy.analysis import Levels, Events, Features


class ePhysModule(AbstractModule):
    def __init__(self, obj: object, *args, **kwargs) -> None:
        # Inherent AbstractModule
        super(ePhysModule, self).__init__(obj)

        # Set the title of the workspace
        # Set workspace icon
        self.title = "Maglia lab viewer"
        self.ico = "logo"

        # Show when starting the program
        # self.show = True
        self.show = False

        self.data = list()
        # Add menu bar items
        # self.add_menu('File', 'Open', self.test_function)
        # self.add_menu('Analyze', 'Filter', self.test_function)
        # self.add_menu('Tests2', 'Test', self.test_function2, args="TETETE")
        self.filter = None
        self.filter_freq = None
        self.list_view = None
        self.toolbar = None
        self.toolbar_bottom = None
        self.chart_view = None
        self.voltage_chart = None
        self.chart_view2 = None
        self.series = 0
        self.sweeps = list()
        self.charts = list()
        self.toolbars = list()
        self.tree = None
        self.chart = None
        self.y_data = np.array([0, 0])
        self.x_data = np.array([0, 1])
        self.v_data = np.array([0, 1])
        self.type = ""
        self.file_path = ""
        self.results_window = None
        self.IV_window = None
        self.database = None
        self.db_path = ""
        self.trace_events = dict()
        self.event_idx = list()
        self.active_item = None

    def handle_file(self, file_path: str):
        self.file_path = file_path
        try:
            if file_path.endswith('.abf'):
                self.data = Trace.from_abf(self.file_path)
                self.type = "ABF"
                print("Loading ABF")
                return self
        except:
            return False

    def _open_IV(self):
        self.IV_window = CurrentVoltageResults(self.obj)
        voltage, current = self.active_item.IV
        self.IV_window.set_data(voltage, current)
        self.IV_window.run()

    def _update_from_tree_HEKA(self, item):
        self.active_item = item
        data = self.data.filter_items(group=item.group, series=item.series, sweep=item.sweep, trace=item.trace)
        self.y_data, self.x_data, self.v_data = self.data.fetch_and_concat(data)
        try:
            title = "Group %s, Series %s, Sweep %s, Channel %s @ %s" % (int(item.group)+1, int(item.series)+1, int(item.sweep)+1, int(item.trace)+1, os.path.basename(self.file_path))
        except TypeError:
            title = "Series %s, Channel %s @ %s" % (int(item.series) + 1, int(item.trace) + 1, os.path.basename(self.file_path))
        self._plot_data(series_name=title)

        self.widgets.add_chart_data(self.voltage_chart, x_data=self.x_data, y_data=self.v_data,
                                    series_name='Voltage',
                                    x_range=(0, max(self.x_data)),
                                    x_name="Time", x_unit="s", y_name="Holding potential", y_unit="V", reset=True)
        self.voltage_chart.add_cursor()



    def _update_from_tree_ABF(self, item):
        if item == "concat":
            x0 = 0
            for i in range(self.data.n_traces):
                reset = True if i == 0 else False

                a = time.time()
                self.data.set_active(i)
                y_data = self.data.rawdata * 10 ** -12

                print("Data load time: %s" % str(time.time() - a))
                a = time.time()

                x_data = self.data.time + x0

                print("Time load time: %s" % str(time.time()-a))
                a = time.time()

                x0 = max(x_data)
                self.x_data[-1] = max(x_data)
                self._plot_data(x_data=x_data, y_data=y_data, reset=reset, hex_color="#181d7a")

                print("Plot time: %s" % str(time.time() - a))
                a = time.time()
        else:
            self.data.set_active(item)
            self.y_data = self.data.rawdata * 10 ** -12
            self.x_data = self.data.time
            # title = "Trace %s" % int(self.data.active_trace)
            title = "Trace %s @ %s" % (int(self.data.active_trace), os.path.basename(self.file_path))

            self._plot_data(series_name=title, reset=True)
            self.plot_simple_events()
            # self.chart.add_source(self.file_path)

    def _add_vertical_cursor(self):
        self.baseline_cursor = self.chart.add_cursor(angle=90)
        self.baseline_cursor.setValue(np.mean(self.x_data))

    def _filter(self, result):
        self.filter_freq = int(result["Filter frequency"])
        self._plot_data()

    def _filter_dialog(self):
        dialog = FormDialogs(self.obj)
        dialog.connect(self._filter)
        dropdown = dialog.add_option(("Method", "Dropdown"))
        dropdown.addItem("Gaussian filter")
        dialog.add_option(("Filter frequency", "VARCHAR"))
        dialog.run()

    def _events_dialog(self):
        dialog = FormDialogs(self.obj)
        dialog.connect(self._get_events_simple)
        dropdown_apply = dialog.add_option(("Apply to", "Dropdown"))
        dropdown_apply.addItem("Active trace")
        dropdown_apply.addItem("All traces")

        dialog.add_option(("Please select baseline and noise level", "Label"))
        dropdown_detection_method = dialog.add_option(("Method", "Dropdown"))
        dropdown_detection_method.addItem("Threshold")
        dialog.add_option(("Baseline", "VARCHAR"))
        dialog.add_option(("Baseline SD", "VARCHAR"))
        dropdown_method = dialog.add_option(("From", "Dropdown"))
        dropdown_method.addItem("Cursors")
        dropdown_method.addItem("Values")

        dialog.add_option(("---", "Label"))
        dropdown_method = dialog.add_option(("Event optimisation", "Dropdown"))
        dropdown_method.addItem("None (long-lived events)")
        dropdown_method.addItem("Adept 2-State")
        dropdown_method.addItem("gNDF")

        dialog.add_option(("t0", "VARCHAR"))
        dialog.add_option(("t1", "VARCHAR"))

        dialog.run()
        self.baseline_cursor = self.chart.add_cursor(angle=0)
        self.baseline_cursor.setValue(-100*10**-12)
        self.baseline_SD_cursor = self.chart.add_cursor(angle=0)

    def _get_events_simple(self, result=None):
        print(result)

        if result is not None:
            if result['From'] == "Values":
                baseline = float(result['Baseline'])*10**-12
                baseline_SD = float(result['Baseline SD'])*10**-12
            elif result['From'] == "Cursors":
                baseline = self.baseline_cursor.value()
                baseline_SD = (self.baseline_SD_cursor.value() - baseline)
            self.baseline_cursor.dettach()
            self.baseline_SD_cursor.dettach()
            del self.baseline_cursor
            del self.baseline_SD_cursor
            self.data.set_levels(baseline*10**12, baseline_SD*10**12)

        try:
            t0 = float(result['t0'])
        except ValueError:
            t0 = 0
        try:
            t1 = float(result['t1'])
        except ValueError:
            t1 = -1
        print("Start cutoff: %s and end %s s" % (t0, t1))
        self.data.set_trim(t0=t0, t1=t1)

        if result['Apply to'] == 'All traces':
            trace = self.data.active_trace
            for i in range(self.data.n_traces):
                self.data.set_active(i)
                Events(self.data).run()
            self.data.set_active(trace)
        else:
            Events(self.data).run()

        if result['Event optimisation'] != 'None (long-lived events)':
            Events(self.data).optimise_events(function=result['Event optimisation'])

        self.update_events()
        self.plot_simple_events()

    def update_events(self):
        trace_events = self.database.get_sample(table_name="results", field_name='*')
        self.trace_events = {}
        for c, field_name in enumerate(self.database.get_fields(table_names=["results"])[0]):
            self.trace_events[field_name] = [i[c] for i in trace_events]

    def plot_simple_events(self):
        y_data = []
        x_data = []
        for c, method in enumerate(self.trace_events['Method']):
            if all([self.trace_events['Trace'][c] == self.data.active_trace, method == "Threshold"]):
                x_data += [self.trace_events['baseline_start'][c], self.trace_events['baseline_end'][c]]
                y_data += [self.trace_events['baseline_current'][c]] * 2
                x_data += [self.trace_events['event_start'][c], self.trace_events['event_end'][c]]
                y_data += [self.trace_events['event_current'][c]] * 2
        x_data = np.array(x_data)
        y_data = np.array(y_data)*10**-12
        self._plot_data(x_data=x_data, y_data=y_data, reset=False, hex_color="#cf081f")

    def _histogram_dialog(self):
        dialog = FormDialogs(self.obj)
        dialog.connect(self._make_histogram)
        dialog.add_option(("Lower bound", "VARCHAR"))
        dialog.add_option(("Upper bound", "VARCHAR"))
        dialog.add_option(("Steps", "VARCHAR"))
        dialog.run()

    def _make_histogram(self, result):
        hist_mod = ePhysPlotModule(self.obj, title="Current histogram")
        x_bins = np.linspace(float(result['Lower bound']) * 10 ** -12, float(result['Upper bound']) * 10 ** -12, int(result['Steps']))
        y_data, x_data = np.histogram(self.y_data, bins=x_bins)
        hist_mod.set_data(x_data, y_data, x_name="Current", x_unit="A", y_name="Counts (a.u.)")
        self.obj.parent.init_workspace(hist_mod)

    @staticmethod
    def filter_gaussian(signal, sampling_period, Fs):
        sigma = 1 / (sampling_period * Fs * 2 * np.pi)
        return gaussian_filter(signal, sigma)

    def _plot_data(self, series_name='', x_data=None, y_data=None, reset=True, hex_color="#000000"):
        if all((x_data is None, y_data is None)):
            x_data = self.x_data
            y_data = self.y_data
        try:
            if self.filter_freq is None:
                filter_freq = int(self.widgets.get_line_edit(self.filter))
            else:
                filter_freq = self.filter_freq
            y_data = self.filter_gaussian(y_data, np.diff(x_data)[0], filter_freq)
        except ValueError:
            pass
        if len(x_data) == len(y_data):
            max_points = 100000
            reset = False
            if len(y_data) > max_points:
                remained_after_division = (len(y_data) % max_points)
                n_blocks = (len(y_data)-remained_after_division) / max_points
                for block in range(int(n_blocks)):
                    if block == 0:
                        reset = True
                    else:
                        reset = False

                    self.widgets.add_chart_data(self.chart, x_data=x_data[int(max_points*block):int(max_points*(block+1))], y_data=y_data[int(max_points*block):int(max_points*(block+1))],
                                                series_name=series_name, hex_color=hex_color,
                                                x_range=(0, max(self.x_data)), y_range=(-1000*10**-12, 1000*10**-12),
                                                x_name="Time", x_unit="s", y_name="Current", y_unit="A", reset=reset)
                self.widgets.add_chart_data(self.chart, x_data=x_data[int(-remained_after_division)::],
                                            y_data=y_data[int(-remained_after_division)::],
                                            series_name=series_name, hex_color=hex_color,
                                            x_range=(0, max(self.x_data)),
                                            y_range=(-1000 * 10 ** -12, 1000 * 10 ** -12),
                                            x_name="Time", x_unit="s", y_name="Current", y_unit="A", reset=False)
            else:
                self.widgets.add_chart_data(self.chart, x_data=x_data, y_data=y_data,
                                            series_name=series_name, hex_color=hex_color,
                                            x_range=(0, max(self.x_data)),
                                            y_range=(-1000 * 10 ** -12, 1000 * 10 ** -12),
                                            x_name="Time", x_unit="s", y_name="Current", y_unit="A", reset=reset)

    def add_cursor(self):
        cursors = self.chart.add_cursor()
        print(cursors.value())

    def _tabulate_results(self):
        self.results_window.run()

    def run(self, win: object, *args, **kwargs):
        # Setup a new window
        self.new_window(win)
        if self.type == "HEKA":
            self.generate_view_HEKA()
        if self.type == "ABF":
            self.generate_view_ABF()
        self.results_window = ShowResults(self.obj, os.path.splitext(self.file_path)[0], data=self.data)
        self.db_path = os.path.splitext(self.file_path)[0]
        self.database = DatabaseManager(db_module=sql_database, db_path=self.db_path)
        self.update_events()

    def generate_view_ABF(self):
        self.tree = self.widgets.make_tree_view(function_connect=self._update_from_tree_ABF, grid=(0, 5, 2, 21))
        self.tree.add_item("Concatenate all traces", "", marker="concat")
        for i in range(self.data.n_traces):
            self.tree.add_item("Trace %s" % str(i), "", marker=i)

        self.y_data = self.data.rawdata*10**-12
        self.x_data = self.data.time
        self.data.set_active(0)
        self.chart = self.widgets.make_chart_view(grid=(5, 25, 1, 22))
        self.widgets.make_label(grid=(0, 2, 1, 2), text="Filter frequency")
        self.filter = self.widgets.make_line_edit(grid=(2, 5, 1, 2))

        self.toolbar = self.widgets.make_toolbar(grid=(0, 20, 0, 1))
        self.widgets.toolbar_add(self.toolbar, self._filter_dialog, arguments=None, img='filter')
        self.widgets.toolbar_add(self.toolbar, self._events_dialog, arguments=None, img='add_field')
        self.widgets.toolbar_add(self.toolbar, self._histogram_dialog, arguments=None, img='bars')
        self.widgets.toolbar_add(self.toolbar, self._add_vertical_cursor, arguments=None, img='search_button')
        self.widgets.toolbar_add(self.toolbar, self._tabulate_results, arguments=None, img='search_button')

        # Set window contents (finish)
        self.set_content()
        self._plot_data(series_name="Trace %s" % int(self.data.active_trace))

    def generate_view_HEKA(self):
        self.tree = self.widgets.make_tree_view(function_connect=self._update_from_tree_HEKA, grid=(0, 5, 2, 21))
        '''
            Overly complex method to import HEKA data in a ClampFit style
            The code is a mess, but it works
        '''
        channel_nodes = []
        # Add groups
        for i, item in zip(self.data.index, self.data.items):
            if len(i) == 1:
                node = self.tree.new_node(item.type, item.label)
                node.group, node.series, node.sweep, node.trace = item.group, item.series, item.sweep, item.trace
                channel_nodes.append(node)

        # Add series
        channels = []
        for i, item in zip(self.data.index, self.data.items):
            if all([item.sweep is None, not (item.series is None)]):
                for element in channel_nodes:
                    if all([element.group == item.group, not element.series]):
                        node = self.tree.new_node(item.type, item.label, parent=element)
                        node.group, node.series, node.sweep, node.trace = item.group, item.series, item.sweep, item.trace
                        channels.append(node)
        channel_nodes += channels

        # Add Channels
        channels = []
        for i in range(self.data.get_channels()):
            for element in channel_nodes:
                if all([not (element.series is None), not element.trace]):
                    item = types.SimpleNamespace()
                    item.group = element.group
                    item.series = element.series
                    item.trace = i
                    item.sweep = None
                    node = self.tree.new_node('Channel %s' % str(i + 1), '', parent=element, marker=item)
                    node.group, node.series, node.sweep, node.trace = item.group, item.series, item.sweep, item.trace
                    channels.append(node)
        channel_nodes += channels

        # Add Sweeps
        for i, item in zip(self.data.index, self.data.items):
            if len(i) == 4:
                for element in channel_nodes:
                    if all([item.trace == element.trace, item.series == element.series, item.group == element.group]):
                        self.tree.add_item("Pulse %s" % item.sweep, item.label, marker=item, parent=element)

        self.chart = self.widgets.make_chart_view(grid=(5, 25, 1, 11))
        self.voltage_chart = self.widgets.make_chart_view(grid=(5, 25, 11, 22))
        self.widgets.make_label(grid=(0, 2, 1, 2), text="Filter frequency")
        self.filter = self.widgets.make_line_edit(grid=(2, 5, 1, 2))

        self.toolbar = self.widgets.make_toolbar(grid=(0, 20, 0, 1))
        self.widgets.toolbar_add(self.toolbar, self._filter_dialog, arguments=None, img='filter')
        self.widgets.toolbar_add(self.toolbar, self._histogram_dialog, arguments=None, img='bars')
        self.widgets.toolbar_add(self.toolbar, self._add_vertical_cursor, arguments=None, img='search_button')
        self.widgets.toolbar_add(self.toolbar, self._open_IV, arguments=None, img='IV_curve')

        # Set window contents (finish)
        self.set_content()
        self._plot_data()


class ePhysPlotModule(AbstractModule):
    def __init__(self, obj: object, *args, title='', **kwargs) -> None:
        # Inherent AbstractModule
        super(ePhysPlotModule, self).__init__(obj)

        # Set the title of the workspace
        # Set workspace icon
        self.title = title
        self.ico = "logo"
        self.x_data = [0, 1]
        self.y_data = [0, 0]
        self.toolbar = None
        self.tree = None
        self.chart = None
        self.x_name = None
        self.y_name = None
        self.x_unit = None
        self.y_unit = None
        self.y_fit_data = None
        self.fits = 1

    def set_data(self, x_data, y_data, x_name="", x_unit="", y_name="", y_unit=""):
        self.x_data = np.array(x_data, dtype="float64")
        self.y_data = np.array(y_data, dtype="float64")
        self.x_name = x_name
        self.y_name = y_name
        self.x_unit = x_unit
        self.y_unit = y_unit
        self.y_fit_data = np.zeros(len(y_data), dtype="float64")

    def _fit_dialog(self):
        dialog = FormDialogs(self.obj)
        dialog.connect(self._fit_NDF)
        dialog.add_option(("n-terms", "VARCHAR"))
        dialog.run()

    def _fit_NDF(self):
        p0 = (max(self.y_data), self.x_data[np.argmax(self.y_data)], np.diff(self.x_data)[0])
        x_data = self.x_data[0:-1] + np.diff(self.x_data)[0]
        y_data = self.y_data
        if self.y_fit_data is not None:
            y_data -= self.y_fit_data
        popt, pcov = curve_fit(self.rNDF, x_data, y_data, p0=p0)
        self.y_fit_data += self.rNDF(x_data, *popt)
        node = self.tree.new_node('Fit %s' % str(self.fits), '')
        self.tree.add_item('Amplitude', str(popt[0]), parent=node)
        self.tree.add_item('Amplitude S.D.', str(pcov[0][0]), parent=node)
        self.tree.add_item('Center', str(popt[1]), parent=node)
        self.tree.add_item('Center S.D.', str(pcov[1][1]), parent=node)
        self.tree.add_item('Standard deviation', str(popt[2]), parent=node)
        self.tree.add_item('Standard deviation S.D.', str(pcov[2][2]), parent=node)
        self.fits += 1
        self.widgets.add_chart_data(self.chart, x_data=self.x_data, y_data=self.rNDF(self.x_data, *popt), hex_color="#b80211", reset=False)

    @staticmethod
    def rNDF(x, a, x0, sigma):
        return a * np.exp(-(x - x0) ** 2 / (2 * sigma ** 2))

    def run(self, win: object, *args, **kwargs):
        # Setup a new window
        self.new_window(win)

        self.toolbar = self.widgets.make_toolbar(grid=(0, 25, 0, 1))
        self.widgets.toolbar_add(self.toolbar, self._fit_NDF, arguments=None, img='bars')

        self.tree = self.widgets.make_tree_view(grid=(0, 5, 2, 21))

        self.chart = self.widgets.make_chart_view(grid=(5, 25, 1, 21))
        self.widgets.add_chart_data(self.chart, x_data=self.x_data, y_data=self.y_data,
                                    x_name=self.x_name, x_unit=self.x_unit,
                                    y_name=self.y_name, y_unit=self.y_unit)
        self.set_content()

