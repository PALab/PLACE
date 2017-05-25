"""Demo instrument: a counter"""
# This is meant as both a test and a working demo for PLACE.
from time import sleep
from threading import Thread
import mpld3
import matplotlib.pyplot as plt
import numpy as np
from obspy import Stream, Trace, UTCDateTime
from obspy.core.trace import Stats
from place.plugins.instrument import Instrument, send_data_thread

class Counter(Instrument):
    """A unit counter"""
    # This instrument records a unit value for each update and sleeps for a
    # specific amount of time. The unit value is placed into the header and a
    # Trace is recorded into the hdf5 file. A plot of the unit values is
    # printed to the webapp plot window.
    def __init__(self, config):
        """Initialize the counter, without configuring.

        :param config: configuration data (as a parsed JSON object)
        :type config: dict
        """
        # First, we call the base class initializer with the config data.
        Instrument.__init__(self, config)
        # Class variables should be set to trivial values in this method as a
        # form of documentation.
        self._count = None
        # This Stream object will hold our recorded data.
        self._stream = None
        # Additionally, minimal resource gathering is appropriate here, if
        # needed. By following this design pattern, it creates a contrast
        # between instruments which have been initialized vs. instruments which
        # have been configured, which is a subtle but important difference.
    def config(self, header=Stats()):
        """Configure the counter

        :param header: metadata for the scan
        :type header: obspy.core.trace.Stats
        """
        # At this time, it is appropriate to initialize variables to their true
        # initial values.
        # This integer will hold the current count.
        self._count = 0
        # And this Stream object will collect data during the scan.
        self._stream = Stream()
        # During the config phase, we are provided the metadata for the scan.
        # We should put any scan-wide information about our information into
        # the header at this point.
        header['counter_sleep_time'] = self._config['sleep_time']
        # Note that we have chosen to include the sleep time in the header
        # information. This means that the sleep time will be put into every
        # trace generated by all instruments during this scan.

    def update(self, header=Stats(), socket=None):
        """Update the counter

        :param header: metadata for the scan
        :type header: obspy.core.trace.Stats

        :param socket: connection to the webapp plot frame
        :type socket: websocket
        """
        # We are now in the update phase. Since our counter starts at 0, we
        # should increment the counter before we record the data. Note that we
        # don't know how many time update will be called. We simply increment
        # and then record the value.
        self._count += 1
        header['counter_current_count'] = self._count
        # Set the start time to the current time.
        header.starttime = UTCDateTime()
        header.npts = 2**7
        # Make up a sample rate.
        header.sampling_rate = 10e6
        # Since this is a demo instrument, we also want to record a trace. We
        # will create a simple list to use as sample data. PLACE generally uses
        # NumPy arrays to store data.
        some_data = np.random.rand(header.npts)
        # And put this data into a Trace object and add this trace to our
        # stream of data.
        self._stream.append(Trace(some_data, header))
        # If the scan was started with the webapp, then during update, we are
        # given access to an iframe in the webapp window. Technically, it is a
        # socket to the webapp's iframe. Typically, this is used to plot data,
        # but we can send any valid HTML. We only want to do this if 'socket'
        # is not None and our instrument has been told to plot. If we have not
        # been provided a socket, we should still plot, but we will do so to
        # the current screen instead.
        if self._config['plot']:
            if socket is None:
                plt.ion()
            plt.clf()
            axis = plt.gca()
            stream = self._stream.copy()
            times = np.arange(0, stream[0].stats.npts) * stream[0].stats.delta * 1e6
            for trace in stream:
                trace.data += trace.stats['counter_current_count']
                axis.plot(trace.data, times, color='black', picker=True)
                axis.fill_betweenx(
                    times,
                    trace.data,
                    trace.stats['counter_current_count'],
                    where=trace.data > trace.stats['counter_current_count'],
                    color='black')
            plt.xlim((1, len(stream) + 1))
            plt.xlabel('Update Number')
            plt.ylim((stream[0].stats.npts * stream[0].stats.delta * 1e6, 0))
            plt.ylabel('Dummy Data')
            if socket is None:
                plt.pause(0.05)
            else:
                out = mpld3.fig_to_html(plt.gcf())
                thread = Thread(target=send_data_thread, args=(socket, out))
                thread.start()
                thread.join()
        # And now we sleep, as specified in the configuration.
        sleep(self._config['sleep_time'])

    def cleanup(self):
        """Stop the counter and return data."""
        # This method does not have any resources that need to be freed, or
        # connections that need to be closed. Basically, all that needs to be
        # done here is for the Stream data to be returned to Scan, where it
        # will be recorded for the user.
        if self._config['plot'] == 'yes':
            plt.ioff()
            plt.show()
            plt.close('all')
        return self._stream
