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

A CircuitPython/Python library for communicating with Adafruit IO


* Author(s): Brent Rubell for Adafruit Industries

Implementation Notes
--------------------

**Hardware:**

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://github.com/adafruit/circuitpython/releases

* Adafruit's ESP32SPI library: https://github.com/adafruit/Adafruit_CircuitPython_ESP32SPI
"""

# imports

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_Adafruit_IO.git"

class AdafruitIO_ThrottleError(Exception):
    """Adafruit IO request error class for Throttle Errors"""
    def __init__(self):
        super(AdafruitIO_ThrottleError, self).__init__("Number of Adafruit IO Requests exceeded! \
                                                            Please try again in 30 seconds..")

class AdafruitIO_RequestError(Exception):
    """Base Adafruit IO request error class"""
    def __init__(self, response):
        response_content = response.json()
        error = response_content['error']
        super(AdafruitIO_RequestError, self).__init__("Adafruit IO Error {0}: {1}"
                                                      .format(response.status_code, error))

class Client():
  """
  TODO: Add Class DOCSTRING here!
  """
    def __init__(self, username, key, wifi_manager, api_version='v2'):
        """
        Adafruit IO API REST Client
        :param str username: Adafruit IO Username
        :param str key: Adafruit IO Key, from `settings.py`
        :param wifi_manager: ESP32WiFiManager Object
        :param str api_version: Adafruit IO REST API Version
        """
        self.api_version = api_version
        self.url = 'https://io.adafruit.com/api'
        self.username = username
        self.key = key
        if wifi_manager:
            self.wifi = wifi_manager
        else:
            raise TypeError("This library requires a WiFiManager object.")
        self.http_headers = [{bytes("X-AIO-KEY", "utf-8"):bytes(self.key, "utf-8"),
                              bytes("Content-Type", "utf-8"):bytes('application/json', "utf-8")},
                             {bytes("X-AIO-KEY", "utf-8"):bytes(self.key, "utf-8")}]

    # TODO: Convert these two methods to functions?
    def _compose_path(self, path):
        return "{0}/{1}/{2}/{3}".format(self.url, self.api_version, self.username, path)

    def _create_data(self, data, latitude, longitude, elevation, timestamp):
        return {'value':data, 'lat':latitude, 'lon':longitude,
                'ele':elevation, 'created_at':timestamp}

    def _handle_error(self, response):
        if response.status_code == 429:
            raise AdafruitIO_ThrottleError
        elif response.status_code == 400:
            raise AdafruitIO_RequestError(response)
        elif response.status_code >= 400:
            raise AdafruitIO_RequestError(response)
        # no error? do nothing

    # HTTP Requests
    def _post(self, path, packet):
        """
        Send data to Adafruit IO
        :param str path: Formatted Adafruit IO URL
        :param json packet: JSON data to send to Adafruit IO
        """
        response = self.wifi.post(
            path,
            json=packet,
            headers=self.http_headers[0])
        self._handle_error(response)
        return response.json()
        response.close()

    def _get(self, path):
        """
        Get data from Adafruit IO
        :param str path: Formatted Adafruit IO URL
        """
        response = self.wifi.get(
            path,
            headers=self.http_headers[1])
        self._handle_error(response)
        return response.json()
        response.close()

    def _delete(self, path):
        """
        Delete data from Adafruit IO.
        :param str path: Formatted Adafruit IO URL
        """
        response = self.wifi.delete(
            path,
            headers=self.http_headers[0])
        self._handle_error(response)
        return response.json()
        response.close()

    # Data
    def send_data(self, feed_key, data, lat=None, lon=None, ele=None, created_at=None):
        """
        Sends value data to an Adafruit IO feed.
        :param data: Data to send to an Adafruit IO feed
        :param str feed_key: Specified Adafruit IO feed
        :param int lat: Optional latitude
        :param int lon: Optional longitude
        :param int ele: Optional elevation
        :param string created_at: Optional date/time string
        """
        path = self._compose_path("feeds/{0}/data".format(feed_key))
        packet = self._create_data(data, lat, lon, ele, created_at)
        self._post(path, packet)

    def receive_data(self, feed_key):
        """
        Return the most recent value for the specified feed.
        :param string feed_key: Name/Key/ID of Adafruit IO feed.
        """
        path = self._compose_path("feeds/{0}/data/last".format(feed_key))
        return self._get(path)

    def delete_data(self, feed_key, data_id):
        """
        Delete an existing Data point from a feed.
        :param string feed: Feed Key
        :param string data_id: Data point to delete
        """
        path = self._compose_path("feeds/{0}/data/{0}".format(feed_key, data_id))
        return self._delete(path)

    # Groups
    def get_all_groups(self):
        """
        Returns information about the user's groups.
        """
        path = self._compose_path("groups")
        return self._get(path)

    def add_feed_to_group(self, group_key, feed_key):
        """
        Adds an existing feed to a group
        :param str group_key: Group
        :param str feed_key: Feed to add to the group
        """
        path = self._compose_path("groups/{0}/add".format(group_key))
        packet = {'feed_key':feed_key}
        return self._post(path, packet)

    def create_new_group(self, group_key, group_description):
        """
        Creates a new Adafruit IO Group.
        :param str group_key: Adafruit IO Group Key
        :param str group_description: Brief summary about the group
        """
        path = self._compose_path("groups")
        packet = {'name':group_key, 'description':group_description}
        return self._post(path, packet)

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
        Returns feed record
        :param str key: Feed Key
        :param bool detailed: Returns a more detailed feed record
        """
        if detailed:
            path = self._compose_path("feeds/{0}/details".format(feed_key))
        else:
            path = self._compose_path("feeds/{0}".format(feed_key))
        return self._get(path)

    def get_all_feeds(self):
        """
        Returns information about the user's feeds. The response includes
        the latest value of each feed, and other metadata about each feed.
        """
        path = self._compose_path("feeds")
        return self._get(path)

    def create_new_feed(self, feed_key, feed_desc, feed_license):
        """
        TODO: Add Docstring
        """
        path = self._compose_path("feeds")
        packet = packet = {'name':feed_key,
                           'description':feed_desc,
                           'license':feed_license}
        return self._post(path, packet)

    def delete_feed(self, feed_key):
        """
        Deletes an existing feed.
        :param str feed_key: Valid feed key
        """
        path = self._compose_path("feeds/{0}".format(feed_key))
        return self._delete(path)
