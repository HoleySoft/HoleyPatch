# -*- coding: utf-8 -*-
import multiprocessing
from itertools import repeat
from .base import AnalysisBase
from .levels import Levels
from .fitting_functions import (gNDF)
import numpy as np
from scipy.optimize import curve_fit
import warnings
from .sql_database import SQL_database
import os
import time

def threshold_search(signal: np.ndarray, sampling_period: float, levels: tuple,
                     dwell_time=0, skip=2, trace=0, t0=0, t1=-1, database=None) -> tuple:
    """Event detection algorithm using threshold.
    
    This function uses a defined set of cut-off parameters (levels) to determine event locations.
    It utilizes a threshold for shot noise, to prevent preliminary decisions.
    
    Parameters
    ----------
    signal : numpy array
        The signal should be fed as a array of arrays.
        Each top-level array is threated as a trace of a signal allowing easy cross-trace analysis (for e.g. current dependent analysis).
    sampling_period : float
        The sampling_frequency is used in combination with the dwelltime argument exclude short events.
    levels : tuple
        The levels determine the center of the baseline and it's minimal threshold. 
        levels = ( center, threshold ).
    dwell_time : float
        The minimal event length event should have to be included.
    skip : int
        The skip parameter will exclude a number of events between events as shotnoise, and combines them into a single event.
        default = 2.
    trace : int
        The trace to be analysed (n-th number array)
    t0 : int
        The first datapoint to be analysed in the trace.
    t1 : int
        The last datapoint to be analysed in the trace
    
    Returns
    -------
    tuple
        A tuple containing (in order), the baseline events, signal events, baseline events start, basline events end, signal events start and signal events end.
        All start and ends are returned as position of the datapoint in the trace.
        
    """
    # Expand variables
    l0, l1 = levels

    # Trim the current trace
    trace_length = len(signal[trace])
    signal = signal[trace][t0:min(trace_length, t1)]

    # All data points above the threshold
    a = np.where(abs(np.array(signal)) < (abs(l0) - abs(l1)))[0]

    # Get all event starts (e.g. where two data points are maximum 'skip' apart), relative to vector a
    # Also, we need to append the last data point of the series
    level_1_end_index_a = np.where(np.diff(a) > skip)[0]
    level_1_end_index_a = np.append(level_1_end_index_a, len(a)-1)

    # We know that all data in vector a is above the baseline, and we know where each block ends
    # The start of these blocks are one index before the end (except the last index)
    # Instead, the first index should be 0
    level_1_start_index_a = np.delete(np.insert(level_1_end_index_a + 1, 0, 0), -1, 0)

    # While the dwell time suggests that also spikes can be seen, at least 2 data points are required to be an event
    n_filter = max(2, int(dwell_time / float(sampling_period)))

    # Only keep those events that are at least 2 or n_filter data points long
    idx = np.where(level_1_end_index_a - level_1_start_index_a > n_filter)[0]

    # The vector a contains the indices of the signal that are above the threshold
    # The level_1_end_index_a and level_1_start_index_a contain the indices in vector a
    # Which we consider to end or start the block. We also defined idx as the indices where
    # The difference between beginning and end are long enough to count as events.
    # We combine these factors to get the indices (in the signal) that correspond to the beginning
    # and end of the level 1 events.
    level_1_start = a[level_1_start_index_a[idx]]
    level_1_end = a[level_1_end_index_a[idx]]

    # We know that whenever level 1 starts, level 0 just ended one data point ahead.
    # We also know that whenever level 1 ends, level 0 starts one data point after.
    level_0_start = np.delete(np.insert(level_1_end + 1, 0, 0), -1, 0)
    level_0_end = level_1_start - 1

    # Simply insert the times from level_0 and level_1 to get the trace data
    # Also, the type must be object as we have an n-dimensional array of multiple sizes
    level_0 = np.array([signal[i:j] for i, j in zip(level_0_start, level_0_end)], dtype=object)
    level_1 = np.array([signal[i:j] for i, j in zip(level_1_start, level_1_end)], dtype=object)

    # remove potential nans
    nan_idx = [any([not np.isnan(np.median(i)), not np.isnan(np.median(i))]) for i, j in zip(level_0, level_1)]
    level_1 = level_1[nan_idx]
    level_1 = level_1[nan_idx]

    # Here we add the cut-off t0
    level_0_start = np.array([i+t0 for i in level_0_start])[nan_idx]
    level_0_end = np.array([i + t0 for i in level_0_end])[nan_idx]
    level_1_start = np.array([i + t0 for i in level_1_start])[nan_idx]
    level_1_end = np.array([i + t0 for i in level_1_end])[nan_idx]

    # Calculate the mean current and standard deviation of baseline events (level 0)
    level_0_mean = np.array([np.mean(i) for i in level_0])
    level_0_sd = np.array([np.std(i) for i in level_0])

    # Calculate the mean current and standard deviation of events (level 1)
    level_1_mean = np.array([np.mean(i) for i in level_1])
    level_1_sd = np.array([np.std(i) for i in level_1])

    # Calculate the excluded current, variance and dwell time (in seconds)
    residual_current = level_1_mean / level_0_mean
    excluded_current = (1 - residual_current)
    residual_current_sd_2 = ((level_1_mean / level_0_mean) ** 2) * (
                ((level_1_sd ** 2) / (level_1_mean ** 2)) + ((level_0_sd ** 2) / (level_0_mean ** 2)))
    dwell_time = np.array([len(i) * sampling_period for i in level_1])

    events = []
    for start, end in zip(level_1_start, level_1_end):
        approx_event_length = (end-start)
        events.append([max(0, start - approx_event_length), min(len(signal), end + approx_event_length)])

    if database:
        table_name = 'results'
        fields = ['Method', 'Trace', 'Level_0_median', 'Level_1_median', 'Level_0_start', 'Level_0_end', 'Level_1_start', 'Level_1_end', 'Ires', 'Ires_SD', 'Dwell_time', 'Event_index']
        result = database.add_table(table_name=table_name, fields=' float(53),'.join(fields) + ' float(53)')
        database.drop_trace(table_name=table_name, trace=trace)
        query_data = []
        for l0, l1, l0_start, l0_end, l1_start, l1_end, Ires, IresSD, dwt, event in zip(level_0, level_1, level_0_start, level_0_end, level_1_start, level_1_end, residual_current, residual_current_sd_2, dwell_time, events):
            query_data.append(['Threshold', trace, str(np.median(l0)),
                               str(np.median(l1)), str(l0_start*sampling_period),
                               str(l0_end*sampling_period),
                               str(l1_start*sampling_period),
                               str(l1_end*sampling_period),
                               Ires, IresSD, dwt, ';'.join(str(v) for v in event)])
        result = database.add_samples(table_name, fields, query_data)
    print('Done')
    # Return the level information
    return level_0, level_1, level_0_start, level_0_end, level_1_start, level_1_end


def fit_events(trace, sampling_period, database, class_function=gNDF):
    signal = trace.data
    print('Fetching database: %s' % str(time.time()))
    trace_events = database.get_samples(table_name="results", field_name='*')
    events = {}
    for c, field_name in enumerate(database.get_fields(table_name="results")):
        events[field_name] = [i[c] for i in trace_events]

    func = class_function()
    table_name = 'results_%s' % func.name
    # for i in np.unique(trace):
    #     database.drop_trace(table_name=table_name, trace=i)
    fields = ['Method', 'Trace', 'Function', 'Fitting_parameters'] + list(func.features())
    result = database.add_table(table_name=table_name, fields=' float(53),'.join(fields) + ' float(53)')
    database.drop_trace(table_name=table_name, trace=trace.active_trace)

    print('Started fitting: %s' % str(time.time()))
    for c, event_index in enumerate(events['Event_index']):
        start, end = tuple(event_index.split(';'))
        trace_index = int(events['Trace'][c])
        if trace_index == trace.active_trace:
            y = np.array(signal[trace_index][int(start):int(end)])
            x = np.linspace(int(start)*sampling_period, int(end)*sampling_period, len(y))
            try:
                print('\tFit start  : %s' % str(time.time()))
                func = class_function()
                result = func.fit(x, y, I0=events['Level_0_median'][c])
                if result:
                    table_name = 'results_%s' % func.name
                    print(func.features().keys())
                    fields = ['Method', 'Trace', 'Function', 'Fitting_parameters'] + list(func.features().keys())
                    query_data = [['Fit', trace_index, func.name, '(' + ','.join(str(v) for v in func.popt) + ')'] + list(func.features().values())]
                    result = database.add_samples(table_name, fields, query_data)
            except RuntimeError:
                pass


class Events(AnalysisBase):
    def _before(self):
        if self.trace.levels:
            self.levels = self.trace.levels
        else:
            self.levels = Levels(self.trace).run()

    def _operation(self):
        signal = np.array(self.trace.data)
        sampling_period = self.trace.sampling_period
        trace = self.trace.active_trace
        dwell_time = self.trace.minimal_dwell_time
        skip = self.trace.event_skip
        database = SQL_database(os.path.splitext(self.trace.file_name)[0])
        result = threshold_search(signal, sampling_period,
                                  levels=self.levels,
                                  dwell_time=dwell_time,
                                  skip=skip,
                                  trace=trace,
                                  t0=self.trace.t0,
                                  t1=self.trace.t1,
                                  database=database,
                                  )
        if self.trace.optimize_events:
            fit_events(self.trace, sampling_period, database)
        self.result = result

    def optimise_events(self, function='gNDF'):
        database = SQL_database(os.path.splitext(self.trace.file_name)[0])
        fit_events(self.trace, self.trace.sampling_period, database)

    def _after(self):
        for array in self.result:
            if len(array) == 0:
                warnings.warn("Found no events")






'''
def fit_events(signal, sampling_period, database, class_function=gNDF):
    print('Fetching database: %s' % str(time.time()))
    trace_events = database.get_samples(table_name="results", field_name='*')
    events = {}
    for c, field_name in enumerate(database.get_fields(table_name="results")):
        events[field_name] = [i[c] for i in trace_events]

    print('Started fitting: %s' % str(time.time()))
    trace = []
    fit = []
    dwt = []
    for c, event_index in enumerate(events['Event_index']):
        start, end = tuple(event_index.split(';'))
        trace_index = int(events['Trace'][c])
        y = np.array(signal[trace_index][int(start):int(end)])
        x = np.linspace(int(start)*sampling_period, int(end)*sampling_period, len(y))
        try:
            print('\tFit start  : %s' % str(time.time()))
            func = class_function()
            result = func.fit(x, y, I0=events['Level_0_median'][c])
            if result:
                fit.append(func.popt)
                dwt.append(func.dwell_time())
                trace.append(trace_index)
        except RuntimeError:
            pass
    print('Writing to database: %s' % str(time.time()))
    if database:
        table_name = 'results_fit'
        for i in np.unique(trace):
            database.drop_trace(table_name=table_name, trace=i)
        print('Adding tables')
        fields = ['Method', 'Trace', 'Function', 'Fitting_parameters', 'Amplitude_block', 'Localisation', 'Sigma', 'Beta', 'Open_current', 'Dwell_time']
        result = database.add_table(table_name=table_name, fields=' float(53),'.join(fields) + ' float(53)')
        query_data = []
        for t, popt, d in zip(trace, fit, dwt):
            if not any([np.any(np.isnan(popt)), np.isnan(d)]):
                query_data.append(['Fit', t, 'gNDF', '(' + ','.join(str(v) for v in popt) + ')'] + [p for p in popt] + [d])
        result = database.add_samples(table_name, fields, query_data)
        print('Finished task: %s' % str(time.time()))
'''