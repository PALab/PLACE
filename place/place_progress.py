"""Module for handling PLACE experiment progress"""
import os.path
from datetime import datetime
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np

from place.config import PlaceConfig
from placeweb.settings import MEDIA_ROOT


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
        self.liveplots[class_name] = [
            make_dict(class_name, plot_data) for plot_data in data]

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
        plots = [{'name': name, 'plots': data}
                 for name, data in self.liveplots.items()]
        progress = {
            'current_stage': self._stage,
            'current_plugin': self._plugin,
            'percentage': percent,
            'percentage_string': percent_str,
            'plugin_plots': plots,
        }
        return progress


def make_dict(class_name, data):
    """Convert data into a dictionary.

    If the number of points exceeds the PLACE maximum for network transfer,
    then PLACE will render a PNG file and transmit this to PLACE.
    """
    max_points = PlaceConfig().get_config_value(
        'PLACE', 'maximum points for network transfer', "1028")
    try:
        if sum([len(series['xdata']) for series in data['series']]) > int(max_points):
            return make_figure_dict(class_name, data)
        return make_data_dict(data)
    except TypeError:
        print('data = {}'.format(data))
        raise


def make_figure_dict(class_name, data):
    """Make a PNG file instead of sending all the data to PLACE."""
    fig = Figure(figsize=(7.29, 4.17), dpi=96)
    FigureCanvas(fig)
    ax = fig.add_subplot(111)
    title = None
    try:
        for series in data['series']:
            ax.plot(series['xdata'], series['ydata'])
        title = data['title']
        ax.set_title(title)
        ax.set_xlabel(data['xaxis'])
        ax.set_ylabel(data['yaxis'])
    except KeyError as err:
        ax.plot([0.0], [0.0])
        title = str(err)
        ax.set_title(title)
        ax.set_xlabel('xaxis')
        ax.set_ylabel('yaxis')
    directory = 'figures/progress_plot/'
    if not os.path.exists(os.path.join(MEDIA_ROOT, directory)):
        os.makedirs(os.path.join(MEDIA_ROOT, directory))
    src = os.path.join(directory, class_name + '.png')
    path = os.path.join(MEDIA_ROOT, src)
    with open(path, 'wb') as file_path:
        fig.savefig(file_path, format='png')
    return {'src': src + '?{}'.format(datetime.now().time()), 'alt': title}


def make_data_dict(data):
    """Convert NumPy data to dictionary data

    The input data will be the dictonary returned from the instrument plot
    phase.
    """
    try:
        return {
            'title': data['title'],
            'xaxis': data['xaxis'],
            'yaxis': data['yaxis'],
            'series': [_make_series_dict(series) for series in data['series']]
        }
    except KeyError as err:
        return {
            'title': str(err),
            'xaxis': 'xaxis',
            'yaxis': 'yaxis',
            'series': [{'name': 'invalid', 'xdata': [0.0], 'ydata': [0.0]}]
        }


def _make_series_dict(series):
    try:
        if isinstance(series['xdata'], list):
            series['xdata'] = np.array(series['xdata'])
        if isinstance(series['ydata'], list):
            series['ydata'] = np.array(series['ydata'])
        return {
            'name': series['name'],
            'xdata': series['xdata'].astype(float, casting='same_kind').tolist(),
            'ydata': series['ydata'].astype(float, casting='same_kind').tolist(),
        }
    except KeyError as err:
        return {
            'name': str(err),
            'xdata': [0.0],
            'ydata': [0.0],
        }
