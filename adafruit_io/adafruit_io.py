# The MIT License (MIT)
#
# Copyright (c) 2019 Brent Rubell for Adafruit Industries
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
"""
`adafruit_io`
================================================================================

A CircuitPython/Python library for communicating with Adafruit IO over WiFi

* Author(s): Brent Rubell for Adafruit Industries

Implementation Notes
--------------------

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
    https://github.com/adafruit/circuitpython/releases

* Adafruit ESP32SPI or ESP_ATcontrol library:
    https://github.com/adafruit/Adafruit_CircuitPython_ESP32SPI
    https://github.com/adafruit/Adafruit_CircuitPython_ESP_ATcontrol
"""
from time import struct_time
from adafruit_io.adafruit_io_errors import AdafruitIO_RequestError, AdafruitIO_ThrottleError

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_Adafruit_IO.git"

CLIENT_HEADERS = {
    'User-Agent': 'AIO-CircuitPython/{0}'.format(__version__)
}

class RESTClient():
    """
    REST Client for interacting with the Adafruit IO API.
    """
    def __init__(self, adafruit_io_username, adafruit_io_key, wifi_manager):
        """
        Creates an instance of the Adafruit IO REST Client.
        :param str adafruit_io_username: Adafruit IO Username
        :param str adafruit_io_key: Adafruit IO Key
        :param wifi_manager: WiFiManager object from ESPSPI_WiFiManager or ESPAT_WiFiManager
        """
        self.username = adafruit_io_username
        self.key = adafruit_io_key
        wifi_type = str(type(wifi_manager))
        if ('ESPSPI_WiFiManager' in wifi_type or 'ESPAT_WiFiManager' in wifi_type):
            self.wifi = wifi_manager
        else:
            raise TypeError("This library requires a WiFiManager object.")
        self._aio_headers = [{"X-AIO-KEY":self.key,
                              "Content-Type":'application/json'},
                             {"X-AIO-KEY":self.key,}]

    @staticmethod
    def _create_headers(io_headers):
        """Creates http request headers.
        """
        headers = CLIENT_HEADERS.copy()
        headers.update(io_headers)
        return headers

    @staticmethod
    def _create_data(data, metadata):
        """Creates JSON data payload
        """
        if metadata is not None:
            return {'value':data, 'lat':metadata['lat'], 'lon':metadata['lon'],
                    'ele':metadata['ele'], 'created_at':metadata['created_at']}
        return {'value':data}

    @staticmethod
    def _handle_error(response):
        """Checks HTTP status codes
        and raises errors.
        """
        if response.status_code == 429:
            raise AdafruitIO_ThrottleError
        elif response.status_code == 400:
            raise AdafruitIO_RequestError(response)
        elif response.status_code >= 400:
            raise AdafruitIO_RequestError(response)

    def _compose_path(self, path):
        """Composes a valid API request path.
        :param str path: Adafruit IO API URL path.
        """
        return "https://io.adafruit.com/api/v2/{0}/{1}".format(self.username, path)

    # HTTP Requests
    def _post(self, path, payload):
        """
        POST data to Adafruit IO
        :param str path: Formatted Adafruit IO URL from _compose_path
        :param json payload: JSON data to send to Adafruit IO
        """
        response = self.wifi.post(
            path,
            json=payload,
            headers=self._create_headers(self._aio_headers[0]))
        self._handle_error(response)
        return response.json()

    def _get(self, path):
        """
        GET data from Adafruit IO
        :param str path: Formatted Adafruit IO URL from _compose_path
        """
        response = self.wifi.get(
            path,
            headers=self._create_headers(self._aio_headers[1]))
        self._handle_error(response)
        return response.json()

    def _delete(self, path):
        """
        DELETE data from Adafruit IO.
        :param str path: Formatted Adafruit IO URL from _compose_path
        """
        response = self.wifi.delete(
            path,
            headers=self._create_headers(self._aio_headers[0]))
        self._handle_error(response)
        return response.json()

    # Data
    def send_data(self, feed_key, data, metadata=None, precision=None):
        """
        Sends value data to a specified Adafruit IO feed.
        :param str feed_key: Adafruit IO feed key
        :param str data: Data to send to the Adafruit IO feed
        :param dict metadata: Optional metadata associated with the data
        :param int precision: Optional amount of precision points to send with floating point data
        """
        path = self._compose_path("feeds/{0}/data".format(feed_key))
        if precision:
            try:
                data = round(data, precision)
            except NotImplementedError: # received a non-float value
                raise NotImplementedError('Precision requires a floating point value')
        payload = self._create_data(data, metadata)
        self._post(path, payload)

    def receive_data(self, feed_key):
        """
        Return the most recent value for the specified feed.
        :param string feed_key: Adafruit IO feed key
        """
        path = self._compose_path("feeds/{0}/data/last".format(feed_key))
        return self._get(path)

    def delete_data(self, feed_key, data_id):
        """
        Deletes an existing Data point from a feed.
        :param string feed: Adafruit IO feed key
        :param string data_id: Data point to delete from the feed
        """
        path = self._compose_path("feeds/{0}/data/{1}".format(feed_key, data_id))
        return self._delete(path)

    # Groups
    def add_feed_to_group(self, group_key, feed_key):
        """
        Adds an existing feed to a group
        :param str group_key: Group
        :param str feed_key: Feed to add to the group
        """
        path = self._compose_path("groups/{0}/add".format(group_key))
        payload = {'feed_key':feed_key}
        return self._post(path, payload)

    def create_new_group(self, group_key, group_description):
        """
        Creates a new Adafruit IO Group.
        :param str group_key: Adafruit IO Group Key
        :param str group_description: Brief summary about the group
        """
        path = self._compose_path("groups")
        payload = {'name':group_key, 'description':group_description}
        return self._post(path, payload)

    def delete_group(self, group_key):
        """
        Deletes an existing group.
        :param str group_key: Adafruit IO Group Key
        """
        path = self._compose_path("groups/{0}".format(group_key))
        return self._delete(path)

    def get_group(self, group_key):
        """
        Returns Group based on Group Key
        :param str group_key: Adafruit IO Group Key
        """
        path = self._compose_path("groups/{0}".format(group_key))
        return self._get(path)

    # Feeds
    def get_feed(self, feed_key, detailed=False):
        """
        Returns an Adafruit IO feed based on the feed key
        :param str feed_key: Adafruit IO Feed Key
        :param bool detailed: Returns a more verbose feed record
        """
        if detailed:
            path = self._compose_path("feeds/{0}/details".format(feed_key))
        else:
            path = self._compose_path("feeds/{0}".format(feed_key))
        return self._get(path)

    def create_new_feed(self, feed_key, feed_desc=None, feed_license=None):
        """
        Creates a new Adafruit IO feed.
        :param str feed_key: Adafruit IO Feed Key
        :param str feed_desc: Optional description of feed
        :param str feed_license: Optional feed license
        """
        path = self._compose_path("feeds")
        payload = {'name':feed_key,
                   'description':feed_desc,
                   'license':feed_license}
        return self._post(path, payload)

    def delete_feed(self, feed_key):
        """
        Deletes an existing feed.
        :param str feed_key: Valid feed key
        """
        path = self._compose_path("feeds/{0}".format(feed_key))
        return self._delete(path)

    # Adafruit IO Connected Services
    def receive_weather(self, weather_id):
        """
        Get data from the Adafruit IO Weather Forecast Service
        NOTE: This service is avaliable to Adafruit IO Plus subscribers only.
        :param int weather_id: ID for retrieving a specified weather record.
        """
        path = self._compose_path("integrations/weather/{0}".format(weather_id))
        return self._get(path)

    def receive_random_data(self, generator_id):
        """
        Get data from the Adafruit IO Random Data Stream Service
        :param int generator_id: Specified randomizer record
        """
        path = self._compose_path("integrations/words/{0}".format(generator_id))
        return self._get(path)

    def receive_time(self):
        """
        Returns a struct_time from the Adafruit IO Server based on the device's IP address.
        https://circuitpython.readthedocs.io/en/latest/shared-bindings/time/__init__.html#time.struct_time
        """
        path = self._compose_path('integrations/time/struct.json')
        time = self._get(path)
        return struct_time((time['year'], time['mon'], time['mday'], time['hour'],
                            time['min'], time['sec'], time['wday'], time['yday'], time['isdst']))
