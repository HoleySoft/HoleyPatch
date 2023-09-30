# importing the required packages
# from pysential.protomodules import AbstractWindow
from pysential.protomodules import (AbstractWindow, FormDialogs)
from pysential.default_modules import sql_database
from pysential.database import DatabaseManager
import numpy as np
import ast
from scipy.fft import rfft, rfftfreq
from scipy import signal


import os
'''
    A not so nice way to import HoleyPy, Fix before release
'''
import sys
sys.path.insert(0, os.path.abspath('../HoleyPy'))
from holeypy import Trace, filters
from holeypy.analysis import (Levels, Events, Features, gNDF)


class ShowResults(AbstractWindow):
    def __init__(self, obj: object, path, data=None) -> None:
        # Inherent AbstractModule
        super(ShowResults, self).__init__(obj)

        # Set the title of the workspace
        # Set workspace icon
        self.title = "Results window"
        self.ico = "logo"
        self.toolbar = None
        self.db_view = None
        self.query_edit = None
        self.db_path = path
        self.database = DatabaseManager(db_module=sql_database, db_path=self.db_path)
        self.data = data

    def _optimize_dialog(self):
        dialog = FormDialogs(self.obj)
        dialog.connect(self._optimize_events)
        dropdown_apply = dialog.add_option(("Apply to", "Dropdown"))
        dropdown_apply.addItem("All traces")

        dropdown_method = dialog.add_option(("Event optimisation", "Dropdown"))
        # dropdown_method.addItem("Adept 2-State")
        dropdown_method.addItem("gNDF")
        dialog.run()

    def _optimize_events(self, result=None):
        if result is not None:
            if result['Apply to'] == 'All traces':
                trace = self.data.active_trace
                for i in range(self.data.n_traces):
                    self.data.set_active(i)
                    Events(self.data).optimise_events(function=result['Event optimisation'])
                self.data.set_active(trace)
            else:
                Events(self.data).optimise_events(function=result['Event optimisation'])

    def run(self):
        self.toolbar = self.widgets.make_toolbar(grid=(0, 10, 0, 1))

        self.widgets.toolbar_add(self.toolbar, self._optimize_dialog, img='search_button')

        self.widgets.toolbar_add(self.toolbar, self._optimize_dialog, img='export')
        '''
        self.widgets.toolbar_add(self.toolbar, self._add_sample, img='add_button')
        self.widgets.toolbar_add(self.toolbar, self._add_field, img='add_field')
        self.widgets.toolbar_add(self.toolbar, self._add_table, img='add_database')
        self.widgets.toolbar_add(self.toolbar, self._export_database, img='export')
        '''

        # self.query_edit = self.widgets.make_line_edit(grid=(10, 20, 0, 1), on_change=self._search_database)

        # tables = self.database.get_tables()
        # fields = self.database.get_fields(tables)
        # samples = self.database.get_samples(table_names=tables)

        self.db_view = self.widgets.make_database_view(database=self.database, grid=(0, 10, 1, 21), function_connect=self.show_event)
        self.chart_Ires_hist = self.widgets.make_chart_view(grid=(10, 18, 1, 11))
        self.chart_Ires_dwt = self.widgets.make_chart_view(grid=(18, 25, 1, 11))
        self.chart = self.widgets.make_chart_view(grid=(10, 15, 11, 21))
        self.chart_residual = self.widgets.make_chart_view(grid=(15, 20, 11, 21))
        self.chart_freq = self.widgets.make_chart_view(grid=(20, 25, 11, 21))

        '''
        trace_events = self.database.get_sample(table_name="results_gNDF", field_name='*')
        self.trace_events = {}
        for c, field_name in enumerate(self.database.get_fields(table_names=["results_gNDF"])[0]):
            self.trace_events[field_name] = [i[c] for i in trace_events]

        x_data = self.trace_events['Amplitude_block']
        y_data = self.trace_events['Dwell_time']
        self.widgets.add_chart_data(self.chart, x_data=x_data, y_data=y_data, symbol='o', y_range=(0.00001, 0.01), x_range=(0, 120), log_y=False)
        '''

        # Set window contents (finish)
        self.set_content()

    def _get_event(self, x, row_idx, data):
        y = []
        level_1_start = float(data['event_start'][row_idx])
        level_1_end = float(data['event_end'][row_idx])
        for i in x:
            if all([i > level_1_start, i < level_1_end]):
                y.append(float(data['event_current'][row_idx]) * 10 ** -12)
            else:
                y.append(float(data['baseline_current'][row_idx]) * 10 ** -12)
        return np.array(y)

    def _get_pdf(self, x, row_idx, data):
        y = []
        level_1_start = float(data['event_start'][row_idx])
        level_1_end = float(data['event_end'][row_idx])
        for i in x:
            if all([i > level_1_start, i < level_1_end]):
                y.append(1)
            else:
                y.append(0)
        return np.array(y)

    def show_event(self, table_idx, row_idx):
        tables = self.database.get_tables()
        table_name = tables[table_idx]
        trace_events = self.database.get_sample(table_name=table_name, field_name='*')
        data = {}
        for c, field_name in enumerate(self.database.get_fields(table_names=[table_name])[0]):
            data[field_name] = [i[c] for i in trace_events]
        if data['Method'][row_idx] == "Threshold":
            x_data = [float(data['baseline_start'][row_idx]), float(data['baseline_end'][row_idx])]
            y_data = [float(data['baseline_current'][row_idx])*10**-12] * 2
            x_data += [float(data['event_start'][row_idx]), float(data['event_end'][row_idx])]
            y_data += [float(data['event_current'][row_idx])*10**-12] * 2
            x_data += [float(data['baseline_start'][row_idx+1]), float(data['baseline_end'][row_idx+1])]
            y_data += [float(data['baseline_current'][row_idx+1]) * 10 ** -12] * 2

            min_y = min(y_data) - abs(max(y_data) - min(y_data)) * 0.5
            max_y = min(y_data) + abs(max(y_data) - min(y_data)) * 1.5

            start, end = tuple(data['Event_index'][row_idx].split(';'))
            y = np.array(self.data[int(data['Trace'][row_idx])][int(start):int(end)])*10**-12
            x = np.linspace(int(start) * self.data.sampling_period, int(end) * self.data.sampling_period, len(y))
            y_fit = self._get_event(x, row_idx, data)

            x_bins = np.linspace(0, 100, 201)
            y_data, x_data = np.histogram(np.array(data['Ires'])*100, bins=x_bins)

            self.widgets.add_chart_data(self.chart_Ires_hist, x_data=x_data,
                                        y_data=y_data, hex_color="#cf081f",
                                        x_name="Residual current", x_unit="%", y_name="Counts", y_unit="Arb. units",
                                        reset=True)



            self.widgets.add_chart_data(self.chart_Ires_dwt, x_data=np.array(data['Ires'])*100, y_data=np.array(data['Dwell_time']), hex_color="#cf081f",
                                        x_range=(0, 100), symbol='x',
                                        x_name="Residual current", x_unit="%", y_name="Time", y_unit="s", reset=True)


            self.widgets.add_chart_data(self.chart, x_data=x, y_data=y_fit, hex_color="#cf081f",
                                        x_range=(min(x_data), max(x_data)), y_range=(min_y, max_y),
                                        x_name="Time", x_unit="s", y_name="Current", y_unit="A", reset=True)

            self.widgets.add_chart_data(self.chart, x_data=x, y_data=y, hex_color="#000000",
                                        x_range=(min(x), max(x)),
                                        y_range=(min_y, max_y),
                                        x_name="Time", x_unit="s", y_name="Current", y_unit="A", reset=False)

            y_res = (y - y_fit)*self._get_pdf(x, row_idx, data)
            min_y = min(y_res) - abs(max(y_res) - min(y_res)) * 0.5
            max_y = min(y_res) + abs(max(y_res) - min(y_res)) * 1.5

            self.widgets.add_chart_data(self.chart_residual, x_data=x, y_data=y_res, hex_color="#000000",
                                        x_range=(min(x), max(x)),
                                        y_range=(min_y, max_y),
                                        x_name="Time", x_unit="s", y_name="Current", y_unit="A", reset=True)

            # Number of samplepoints
            N = len(x)
            # sample spacing
            T = np.mean(np.diff(x))
            xf = np.linspace(0.0, 1.0 / (2.0 * T), int(N / 2))
            yf = rfft(y_res)
            yf = 2.0 / N * np.abs(yf[:N // 2])
            b, a = signal.bessel(N=4, Wn=(2 * np.pi) / T, btype='lowpass', analog=True)
            _, gain = signal.freqs(b, a, worN=xf * 2 * np.pi)
            gain[xf > 1/T] = 1
            gain = np.abs(gain)
            yf = (yf / gain) ** 2

            self.widgets.add_chart_data(self.chart_freq, x_data=xf, y_data=yf,
                                        hex_color="#000000",
                                        x_range=(min(xf), max(xf)),
                                        y_range=(min(yf) * 0.5, max(yf) * 1.5),
                                        x_name="Frequency", x_unit="Hz", y_name="Amplitude", y_unit="Arb. units",
                                        reset=True)

        elif data['Method'][row_idx] == "Fit":
            if data['Function'][row_idx] == "gNDF":
                dwt = float(data['Dwell_time'][row_idx])*5
                local = float(data['Localisation'][row_idx])
                start = int((local - dwt)*self.data.sampling_frequency)
                end = int((local + dwt) * self.data.sampling_frequency)


                '''
                trust = self.data.sampling_frequency / 2*np.array(data['Fs_event'])

                x_bins = np.linspace(0, 100, 201)

                y_data = []
                nc = [float(j) for j in data['Noise_component'][row_idx].split(',')]
                for i, t in zip(data['Noise_component'], trust):
                    nc2 = [float(j) for j in i.split(',')]
                    y_data.append(t*np.sum(signal.correlate(nc, nc2, mode='valid', method='fft'))**2)
                y_data = np.array(y_data)/np.sum(y_data)
                y_data_ires = []
                for a, o in zip(np.array(data['Amplitude_block']), np.array(data['Open_current'])):
                    y_data_ires.append(100*(abs(a)/abs(o)))
                y_data_ires = 100*np.array(y_data_ires)

                y_ires = 100 * np.abs(np.array(self.data[int(data['Trace'][row_idx])][int(start):int(end)])) / abs(np.array(data['Open_current'])[row_idx])

                y_hist, x_hist = np.histogram(y_data_ires, bins=x_bins, weights=y_data)
                y_px, _ = np.histogram(y_ires, bins=x_bins)

                print(y_hist)
                print(x_hist[np.argmax(y_hist)])
                print(y_px)
                print(x_hist[np.argmax(y_hist*y_px)])
                '''
                # print(np.sum(np.array(y_data)*Ires)/np.sum(np.array(y_data)))


                y_data_SD = []
                for i in range(len(data['Trace'])):
                    dwt = float(data['Dwell_time'][i]) * 5
                    local = float(data['Localisation'][i])
                    start = int((local - dwt) * self.data.sampling_frequency)
                    end = int((local + dwt) * self.data.sampling_frequency)
                    y = np.array(self.data[int(data['Trace'][row_idx])][int(start):int(end)]) * 10 ** -12
                    x = np.linspace(int(start) * self.data.sampling_period, int(end) * self.data.sampling_period,
                                    len(y))
                    popt = ast.literal_eval(data['Fitting_parameters'][i])
                    fit = gNDF(popt=popt)
                    y_fit = fit.get_fit(x)*10**-12
                    y_res = np.sqrt((y - y_fit) ** 2)
                    try:
                        avg = np.sum(y_res * fit.get_pdf(x)) / np.sum(fit.get_pdf(x))

                        y_data_SD.append(avg)
                    except ZeroDivisionError:
                        y_data_SD.append(0)

                idx = np.where(np.array(data['Fs_event']) < 10000)

                self.widgets.add_chart_data(self.chart_freq, x_data=100 - (
                            100 * np.array(data['Amplitude_block'])[idx] / abs(np.array(data['Open_current'])[idx])),
                                            y_data=np.array(y_data_SD)[idx], hex_color="#cf081f",
                                            x_range=(0, 100), symbol='x', y_range=(0, max(y_data_SD)),
                                            x_name="Residual current", x_unit="%", y_name="MSE", y_unit="A",
                                            reset=True)

                '''
                for i in y_data:
                    for j in y_data:
                        print(np.argmax(signal.correlate(i, j, mode='valid', method='fft')))
                '''

                y = np.array(self.data[int(data['Trace'][row_idx])][int(start):int(end)]) * 10 ** -12
                x = np.linspace(int(start) * self.data.sampling_period, int(end) * self.data.sampling_period, len(y))

                popt = ast.literal_eval(data['Fitting_parameters'][row_idx])
                fit = gNDF(popt=popt)

                y_fit = np.array(fit.get_fit(x) * 10 ** -12)

                min_y = min(y_fit) - abs(max(y_fit) - min(y_fit)) * 0.5
                max_y = min(y_fit) + abs(max(y_fit) - min(y_fit)) * 1.5

                idx = np.where(np.array(data['Fs_event']) < self.data.sampling_frequency)

                x_bins = np.linspace(0, 100, 201)
                y_data, x_data = np.histogram(100-(100*np.array(data['Amplitude_block'])[idx]/abs(np.array(data['Open_current'])[idx])), bins=x_bins)

                self.widgets.add_chart_data(self.chart_Ires_hist, x_data=x_data,
                                            y_data=y_data, hex_color="#cf081f",
                                            x_name="Residual current", x_unit="%", y_name="Counts", y_unit="Arb. Units",
                                            reset=True)

                idx = np.where(np.array(data['Fs_event']) < 10000)

                x_bins = np.linspace(0, 100, 201)
                y_data, x_data = np.histogram(
                    100 - (100 * np.array(data['Amplitude_block'])[idx] / abs(np.array(data['Open_current'])[idx])),
                    bins=x_bins)

                self.widgets.add_chart_data(self.chart_Ires_hist, x_data=x_data,
                                            y_data=y_data, hex_color="#4abb5f",
                                            x_name="Residual current", x_unit="%", y_name="Counts", y_unit="Arb. Units",
                                            reset=False)

                y_data, x_data = np.histogram(
                    100 - (100 * np.array(data['Amplitude_block']) / abs(np.array(data['Open_current']))),
                    bins=x_bins)
                self.widgets.add_chart_data(self.chart_Ires_hist, x_data=x_data,
                                            y_data=y_data, hex_color="#3333cc",
                                            x_name="Residual current", x_unit="%", y_name="Counts", y_unit="Arb. Units",
                                            reset=False)

                self.widgets.add_chart_data(self.chart_Ires_dwt, x_data=100-(100*np.array(data['Amplitude_block'])[idx]/abs(np.array(data['Open_current'])[idx])),
                                            y_data=np.array(data['Dwell_time'])[idx], hex_color="#cf081f",
                                            x_range=(0, 100), symbol='x', y_range=(1e-4, 1),
                                            x_name="Residual current", x_unit="%", y_name="Time", y_unit="s",
                                            reset=True)


                self.widgets.add_chart_data(self.chart, x_data=x, y_data=y, hex_color="#000000",
                                            x_range=(min(x), max(x)),
                                            y_range=(min_y, max_y),
                                            x_name="Time", x_unit="s", y_name="Current", y_unit="A", reset=True)

                self.widgets.add_chart_data(self.chart, x_data=x, y_data=np.array(y_fit), hex_color="#cf081f",
                                            x_range=(min(x), max(x)),
                                            y_range=(min_y, max_y),
                                            x_name="Time", x_unit="s", y_name="Current", y_unit="A", reset=False)

                '''
                y_res = ((y - y_fit)*fit.get_pdf(x))/np.sum(fit.get_pdf(x))
                # y_res = fit.get_pdf(x)
                print(np.sum(((y - y_fit)**2)*fit.get_pdf(x))/np.sum(fit.get_pdf(x)))
                min_y = min(y_res) - abs(max(y_res) - min(y_res)) * 0.5
                max_y = min(y_res) + abs(max(y_res) - min(y_res)) * 1.5

                self.widgets.add_chart_data(self.chart_residual, x_data=x, y_data=y_res, hex_color="#000000",
                                            x_range=(min(x), max(x)),
                                            y_range=(min_y, max_y),
                                            x_name="Time", x_unit="s", y_name="Current", y_unit="A", reset=True)
                '''



                '''
                xf, yf = fit.frequency_spectrum(x, y)
                self.widgets.add_chart_data(self.chart_freq, x_data=xf, y_data=yf,
                                            hex_color="#000000",
                                            x_range=(min(xf), max(xf)),
                                            y_range=(min(yf)*0.5, max(yf)*1.5),
                                            x_name="Frequency", x_unit="Hz", y_name="Amplitude", y_unit="Arb. units",
                                            reset=True)
                '''
        print(data['Dwell_time'][row_idx])
        print("Table %s with row %s" % (tables[table_idx], row_idx))

    @staticmethod
    def test_function():
        print("Test")

    def _add_sample(self, *args, tab_idx=None):
        print('Add Sample')

    def _add_field(self, *args, tab_idx=None):
        print('Add Field')

    def _search_database(self, *args, tab_idx=None):
        query = self.widgets.get_line_edit(self.query_edit)
        self.database.set_query(query)
        self.db_view = self.widgets.make_database_view(database=self.database, grid=(0, 20, 1, 2))

    def _export_database(self, *args):
        print('Export Database')

    def _add_table(self, *args):
        print('Add Table')
