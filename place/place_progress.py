"""Module for handling PLACE experiment progress"""
import json
import numpy as np


class PlaceProgress:
    """A class to handle the progress of PLACE experiment

    The lifecycle of an experiment goes through these stages:

    1. Created
    2. Started
    3. Initializing
    4. Configuring
    5. Updating
    6. Cleaning
    7. Finished

    """

    def __init__(self):
        self._stage = 'Created'
        self._progress = -1
        self._total = -1
        self._plugin = 'None'
        self.liveplots = {}

    def __str__(self):
        if self._total == -1:
            return 'Experiment created'
        if self._total == -2:
            return 'Experiment finished'
        return 'Experiment {}: {:.2f}%{}'.format(
            self._stage,
            100 * self._progress / self._total,
            ('' if self._plugin == 'None' else (' ({})'.format(self._plugin)))
        )

    def started(self):
        """Call this when the experiment starts"""
        self._stage = 'Started'
        self._plugin = 'None'

    def initializing(self, total):
        """Call this when the experiment starts initializing"""
        self._stage = 'Initializing'
        self._progress = 0
        self._total = total
        self._plugin = 'None'

    def configuring(self, total):
        """Call this when the experiment starts configuring"""
        self._stage = 'Configuring'
        self._progress = 0
        self._total = total
        self._plugin = 'None'

    def updating(self, total):
        """Call this when the experiment starts updating"""
        self._stage = 'Updating'
        self._progress = 0
        self._total = total
        self._plugin = 'None'

    def cleaning(self, total):
        """Call this when the experiment starts cleaning up"""
        self._stage = 'Cleaning'
        self._progress = 0
        self._total = total
        self._plugin = 'None'

    def finished(self):
        """Call this when the experiment is finished"""
        self._stage = 'Finished'
        self._progress = -2
        self._total = -2
        self._plugin = 'None'

    def set_progress(self, progress, plugin='None'):
        """Call this to update the plugin and progress"""
        self._progress = progress
        self._plugin = plugin

    def set_plot_data(self, class_name, data):
        """Set the internal plot data for a running experiment"""
        self.liveplots[class_name] = data

    def is_finished(self):
        """Is the experiment finished"""
        return self._stage == 'Finished'

    def get_progress(self):
        """Return the experiment progress as a dictionary"""
        percent = 0.0
        percent_str = ''
        if self._stage == 'Created' or self._stage == 'Started':
            percent = 0.0
            percent_str = '0.00%'
        elif self._stage == 'Finished':
            percent = 1.0
            percent_str = '100.00%'
        else:
            percent = self._progress / self._total
            percent_str = '{:.2f}%'.format(percent * 100)
        plots = [make_plot_dict(name, data)
                 for name, data in self.liveplots.items()]
        progress = {
            'current_stage': self._stage,
            'current_plugin': self._plugin,
            'percentage': percent,
            'percentage_string': percent_str,
            'live_plots': [plot for plot in plots if plot is not None],
        }
        return progress


def make_plot_dict(name, data):
    """Convert NumPy data to dictionary data

    The input data can either be a NumPy ndarray of shape (N,2), (2,N) or
    (N,) or a list of such arrays.
    """
    if isinstance(data, np.ndarray):
        return make_plot_dict(name, [data])
    if not isinstance(data, list) or data == []:
        return None
    return {
        'title': name,
        'series': [_make_series_dict(series) for series in data]
    }


def _make_series_dict(series):
    try:
        if len(series.shape) == 1:  # 1D array is okay
            series = np.vstack([list(range(len(series))), series])
        if len(series.shape) == 2 and series.shape[1] != 2 and series.shape[0] == 2:
            series = series.T  # transpose the array
        if len(series.shape) != 2 or series.shape[1] != 2:
            print('make_series_dict error: shape is {}'.format(series.shape))
            raise TypeError
        xdata, ydata = series.T.astype(
            float, casting='same_kind').tolist()
        return {
            'xdata': xdata,
            'ydata': ydata,
        }
    except TypeError:
        return {
            'xdata': [0.0],
            'ydata': [0.0],
        }