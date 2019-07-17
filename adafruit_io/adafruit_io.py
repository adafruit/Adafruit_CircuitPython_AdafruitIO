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

A CircuitPython library for communicating with Adafruit IO.

* Author(s): Brent Rubell for Adafruit Industries

Implementation Notes
--------------------

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
    https://github.com/adafruit/circuitpython/releases
"""
from time import struct_time
from adafruit_io.adafruit_io_errors import (
    AdafruitIO_RequestError,
    AdafruitIO_ThrottleError,
    AdafruitIO_MQTTError,
)

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_Adafruit_IO.git"

CLIENT_HEADERS = {"User-Agent": "AIO-CircuitPython/{0}".format(__version__)}


class IO_MQTT:
    """
    Client for interacting with the Adafruit IO MQTT API.
    https://io.adafruit.com/api/docs/mqtt.html#adafruit-io-mqtt-api

    :param MiniMQTT mqtt_client: MiniMQTT Client object.
    """

    # pylint: disable=protected-access
    def __init__(self, mqtt_client):
        # MiniMQTT Object
        mqtt_client_type = str(type(mqtt_client))
        if "MQTT" in mqtt_client_type:
            self._client = mqtt_client
        else:
            raise TypeError(
                "This class requires a MiniMQTT client object, please create one."
            )
        # Adafruit IO Auth. requires a username
        try:
            self._user = self._client._user
        except:
            raise TypeError(
                "Adafruit IO requires a username, please set one in MiniMQTT"
            )
        # User-defined MQTT callback methods must be init'd to None
        self.on_connect = None
        self.on_disconnect = None
        self.on_message = None
        self.on_subscribe = None
        self.on_unsubscribe = None
        # MQTT event callbacks
        self._client.on_connect = self._on_connect_mqtt
        self._client.on_disconnect = self._on_disconnect_mqtt
        self._client.on_message = self._on_message_mqtt
        self._logger = False
        if self._client._logger is not None:
            self._logger = True
            self._client.set_logger_level("DEBUG")
        self._connected = False

    def connect(self):
        """Connects to the Adafruit IO MQTT Broker.
        Must be called before any other API methods are called.
        """
        try:
            self._client.connect()
        except error as e:
            AdafruitIO_MQTTError(e)

    def disconnect(self):
        """Disconnects from Adafruit IO.
        """
        if self._connected:
            self._client.disconnect()

    @property
    def is_connected(self):
        """Returns if connected to Adafruit IO MQTT Broker."""
        return self._client.is_connected

    # pylint: disable=not-callable
    def _on_connect_mqtt(self, client, userdata, flags, return_code):
        """Runs when the on_connect callback is run from code.
        """
        if self._logger:
            self._client._logger.debug("Client called on_connect.")
        if return_code == 0:
            self._connected = True
        else:
            raise AdafruitIO_MQTTError(return_code)
        # Call the user-defined on_connect callback if defined
        if self.on_connect is not None:
            self.on_connect(self)

    # pylint: disable=not-callable
    def _on_disconnect_mqtt(self, client, userdata, return_code):
        """Runs when the on_disconnect callback is run from
        code.
        """
        if self._logger:
            self._client._logger.debug("Client called on_disconnect")
        self._connected = False
        # Call the user-defined on_disconnect callblack if defined
        if self.on_disconnect is not None:
            self.on_disconnect(self)

    # pylint: disable=not-callable
    def _on_message_mqtt(self, client, topic, payload):
        """Runs when the on_message callback is run from code.
        Parses incoming data from special Adafruit IO feeds.
        :param MQTT client: A MQTT Client Instance.
        :param str topic: MQTT topic response from Adafruit IO.
        :param str payload: MQTT payload data response from Adafruit IO.
        """
        if self._logger:
            self._client._logger.debug("Client called on_message.")
        if self.on_message is not None:
            # Parse the MQTT topic string
            topic_name = topic.split("/")
            print(topic_name)
            if topic_name[1] == "groups":
                # Adafruit IO Group Feed(s)
                feeds = []
                messages = []
                # TODO: Remove eval here...
                payload = eval(payload)
                for feed in payload["feeds"]:
                    feeds.append(feed)
                for msg in feeds:
                    payload = payload["feeds"][msg]
                    messages.append(payload)
                topic_name = feeds
                message = messages
            elif topic_name[0] == "time":
                # Adafruit IO Time Topic
                topic_name = topic_name[1]
                message = payload
            else:
                # Standard Adafruit IO Feed
                topic_name = topic_name[2]
                message = payload
        else:
            raise ValueError(
                "You must define an on_message method before calling this callback."
            )
        self.on_message(self, topic_name, message)

    def loop(self):
        """Manually process messages from Adafruit IO.
        Use this method to check incoming subscription messages.
        """
        self._client.loop()

    def loop_blocking(self):
        """Starts a blocking loop and to processes messages
        from Adafruit IO. Code below this call will not run.
        """
        self._client.loop_forever()

    # Subscriptions
    def subscribe(self, feed_key=None, group_key=None, shared_user=None):
        """Subscribes to an Adafruit IO feed or group.
        Can also subscribe to someone else's feed.
        :param str feed_key: Adafruit IO Feed key.
        :param str group_key: Adafruit IO Group key.
        :param str shared_user: Owner of the Adafruit IO feed, required for shared feeds.

        Example of subscribing to an Adafruit IO Feed named 'temperature':

        .. code-block:: python

            client.subscribe('temperature')

        Example of subscribing to two Adafruit IO feeds: `temperature`
        and `humidity`

        .. code-block:: python

            client.subscribe([('temperature'), ('humidity')])
        """
        if shared_user is not None and feed_key is not None:
            self._client.subscribe("{0}/feeds/{1}".format(shared_user, feed_key))
        elif group_key is not None:
            self._client.subscribe("{0}/groups/{1}".format(self._user, group_key))
        elif feed_key is not None:
            self._client.subscribe("{0}/feeds/{1}".format(self._user, feed_key))
        else:
            raise AdafruitIO_MQTTError("Must provide a feed_key or group_key.")

    def subscribe_to_throttling(self):
        """Subscribes to your personal Adafruit IO /throttle feed.
        https://io.adafruit.com/api/docs/mqtt.html#mqtt-api-rate-limiting
        """
        self._client.subscribe("%s/throttle" % self._user)

    def subscribe_to_errors(self):
        """Subscribes to your personal Adafruit IO /errors feed.
        Notifies you of errors relating to publish/subscribe calls.
        """
        self._client.subscribe("%s/errors" % self._user)

    def subscribe_to_randomizer(self, randomizer_id):
        """Subscribes to a random data stream created by the Adafruit IO Words service.
        :param int randomizer_id: Random word record you want data for.
        """
        self._client.subscribe(
            "{0}/integration/words/{1}".format(self._user, randomizer_id)
        )

    def subscribe_to_weather(self, weather_record, forecast):
        """Subscribes to a weather forecast using the Adafruit IO PLUS weather
        service. This feature is only avaliable to Adafruit IO PLUS subscribers.
        :param int weather_record: Weather record you want data for.
        :param str forecast: Forecast data you'd like to recieve.
        """
        self._client.subscribe(
            "{0}/integration/weather/{1}/{2}".format(
                self._user, weather_record, forecast
            )
        )

    def subscribe_to_time(self, time_type):
        """Adafruit IO provides some built-in MQTT topics for getting the current server time.
        :param str time_type: Current Adafruit IO server time. Can be `seconds`, `millis`, or `iso`.
        Information about these topics can be found on the Adafruit IO MQTT API Docs.:
        https://io.adafruit.com/api/docs/mqtt.html#time-topics
        """
        if "seconds" or "millis" in time_type:
            self._client.subscribe("time/" + time_type)
        elif time_type == "iso":
            self._client.subscribe("time/ISO-8601")
        else:
            raise TypeError("Invalid time feed type specified")

    def unsubscribe(self, feed_key=None, group_key=None, shared_user=None):
        """Unsubscribes from an Adafruit IO feed or group.
        Can also subscribe to someone else's feed.
        :param str feed_key: Adafruit IO Feed key.
        :param str group_key: Adafruit IO Group key.
        :param str shared_user: Owner of the Adafruit IO feed, required for shared feeds.

        Example of unsubscribing from an Adafruit IO Feed named 'temperature':

        .. code-block:: python

            client.unsubscribe('temperature')

        Example of unsubscribing to two Adafruit IO feeds: `temperature`
        and `humidity`

        .. code-block:: python

            client.unsubscribe([('temperature'), ('humidity')])

        """
        if shared_user is not None and feed_key is not None:
            self._client.unsubscribe("{0}/feeds/{1}".format(shared_user, feed_key))
        elif group_key is not None:
            self._client.unsubscribe("{0}/groups/{1}".format(self._user, feed_key))
        elif feed_key is not None:
            self._client.unsubscribe("{0}/feeds/{1}".format(self._user, feed_key))
        else:
            raise AdafruitIO_MQTTError("Must provide a feed_key or group_key.")

    # Publishing
    def publish_multiple(self, feeds_and_data, timeout=3, is_group=False):
        """Publishes multiple data points to multiple feeds or groups.
        :param str feeds_and_data: List of tuples containing topic strings and data values.
        :param int timeout: Delay between publishing data points to Adafruit IO.
        :param bool is_group: Set to True if you're publishing to a group.

        Example of publishing multiple data points on different feeds to Adafruit IO:
        ..code-block:: python

            client.publish_multiple([('humidity', 24.5), ('temperature', 54)])

        """
        if isinstance(feeds_and_data, list):
            feed_data = []
            for t, d in feeds_and_data:
                feed_data.append((t, d))
        else:
            raise AdafruitIO_MQTTError("This method accepts a list of tuples.")
        for t, d in feed_data:
            if is_group:
                self.publish(t, d, is_group=True)
            else:
                self.publish(t, d)
            time.sleep(timeout)

    def publish(self, feed_key, data, shared_user=None, is_group=False):
        """Publishes to an An Adafruit IO Feed.
        :param str feed_key: Adafruit IO Feed key.
        :param str data: Data to publish to the feed or group.
        :param int data: Data to publish to the feed or group.
        :param float data: Data to publish to the feed or group.
        :param str shared_user: Owner of the Adafruit IO feed, required for
                                feed sharing.
        :param bool is_group: Set True if publishing to an Adafruit IO Group.

        Example of publishing an integer to Adafruit IO on feed 'temperature'.
        ..code-block:: python

            client.publish('temperature', 30)

        Example of publishing a floating point value to Adafruit IO on feed 'temperature'.
        ..code-block:: python

            client.publish('temperature', 3.14)

        Example of publishing a string to Adafruit IO on feed 'temperature'.
        ..code-block:: python

            client.publish('temperature, 'thirty degrees')
        
        Example of publishing an integer to Adafruit IO on group 'weatherstation'.
        ..code-block:: python

            client.publish('weatherstation', 12, is_group=True)

        Example of publishing to a shared Adafruit IO feed.
        ..code-block:: python

            client.publish('temperature', shared_user='myfriend')

        """
        if is_group:
            self._client.publish("{0}/groups/{1}".format(self._user, feed_key), data)
            return
        if shared_user is not None:
            self._client.publish("{0}/feeds/{1}".format(shared_user, feed_key), data)
        else:
            self._client.publish("{0}/feeds/{1}".format(self._user, feed_key), data)

    def get(self, feed_key):
        """Calling this method will make Adafruit IO publish the most recent
        value on feed_key.
        https://io.adafruit.com/api/docs/mqtt.html#retained-values
        :param str feed_key: Adafruit IO Feed key.
        """
        self._client.publish("{0}/feeds{1}/get".format(self._user, feed_key), "\0")


class IO_HTTP:
    """
    Client for interacting with the Adafruit IO HTTP API.
    https://io.adafruit.com/api/docs/#adafruit-io-http-api
        :param str adafruit_io_username: Adafruit IO Username
        :param str adafruit_io_key: Adafruit IO Key
        :param wifi_manager: WiFiManager object from ESPSPI_WiFiManager or ESPAT_WiFiManager

    """

    def __init__(self, adafruit_io_username, adafruit_io_key, wifi_manager):
        self.username = adafruit_io_username
        self.key = adafruit_io_key
        wifi_type = str(type(wifi_manager))
        if "ESPSPI_WiFiManager" in wifi_type or "ESPAT_WiFiManager" in wifi_type:
            self.wifi = wifi_manager
        else:
            raise TypeError("This library requires a WiFiManager object.")
        self._aio_headers = [
            {"X-AIO-KEY": self.key, "Content-Type": "application/json"},
            {"X-AIO-KEY": self.key},
        ]

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
            return {
                "value": data,
                "lat": metadata["lat"],
                "lon": metadata["lon"],
                "ele": metadata["ele"],
                "created_at": metadata["created_at"],
            }
        return {"value": data}

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
            path, json=payload, headers=self._create_headers(self._aio_headers[0])
        )
        self._handle_error(response)
        return response.json()

    def _get(self, path):
        """
        GET data from Adafruit IO
        :param str path: Formatted Adafruit IO URL from _compose_path
        """
        response = self.wifi.get(
            path, headers=self._create_headers(self._aio_headers[1])
        )
        self._handle_error(response)
        return response.json()

    def _delete(self, path):
        """
        DELETE data from Adafruit IO.
        :param str path: Formatted Adafruit IO URL from _compose_path
        """
        response = self.wifi.delete(
            path, headers=self._create_headers(self._aio_headers[0])
        )
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
            except NotImplementedError:  # received a non-float value
                raise NotImplementedError("Precision requires a floating point value")
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
        payload = {"feed_key": feed_key}
        return self._post(path, payload)

    def create_new_group(self, group_key, group_description):
        """
        Creates a new Adafruit IO Group.
        :param str group_key: Adafruit IO Group Key
        :param str group_description: Brief summary about the group
        """
        path = self._compose_path("groups")
        payload = {"name": group_key, "description": group_description}
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
        payload = {"name": feed_key, "description": feed_desc, "license": feed_license}
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
        path = self._compose_path("integrations/time/struct.json")
        time = self._get(path)
        return struct_time(
            (
                time["year"],
                time["mon"],
                time["mday"],
                time["hour"],
                time["min"],
                time["sec"],
                time["wday"],
                time["yday"],
                time["isdst"],
            )
        )
