# SPDX-FileCopyrightText: 2019 Brent Rubell for Adafruit Industries
#
# SPDX-License-Identifier: MIT

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

import json
import re
import time

try:
    from typing import Any, Callable, List, Optional
except ImportError:
    pass

from adafruit_minimqtt.adafruit_minimqtt import MMQTTException

from adafruit_io.adafruit_io_errors import (
    AdafruitIO_MQTTError,
    AdafruitIO_RequestError,
    AdafruitIO_ThrottleError,
)

__version__ = "0.0.0+auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_AdafruitIO.git"

CLIENT_HEADERS = {"User-Agent": f"AIO-CircuitPython/{__version__}"}


def validate_feed_key(feed_key: str):
    """Validates a provided feed key against Adafruit IO's system rules.
    https://learn.adafruit.com/naming-things-in-adafruit-io/the-two-feed-identifiers
    """
    if len(feed_key) > 128:  # validate feed key length
        raise ValueError("Feed key must be less than 128 characters.")
    if not bool(
        re.match(r"^[a-zA-Z0-9-]+((\/|\.)[a-zA-Z0-9-]+)?$", feed_key)
    ):  # validate key naming scheme
        raise TypeError(
            "Feed key must contain English letters, numbers, dash, and a period or a forward slash."
        )


def validate_n_values(n_values: int):
    """Validates a provided number of values to retrieve data from Adafruit IO.

    Although Adafruit IO will accept values < 1 and > 1000, this avoids two types of issues:
    n_values < 1 (coding errors) and n_values > 1000 (pagination required for HTTP API)

    """
    if n_values < 1 or n_values > 1000:  # validate 0 < n_values <= 1000
        raise ValueError(
            "Number of values must be greater than zero and less than or equal to 1000"
        )


class IO_MQTT:
    """
    Client for interacting with Adafruit IO MQTT API.
    https://io.adafruit.com/api/docs/mqtt.html#adafruit-io-mqtt-api

    :param MiniMQTT mqtt_client: MiniMQTT Client object.
    """

    def __init__(self, mqtt_client):
        # Check for MiniMQTT client
        mqtt_client_type = str(type(mqtt_client))
        if "MQTT" in mqtt_client_type:
            self._client = mqtt_client
        else:
            raise TypeError("This class requires a MiniMQTT client object, please create one.")
        # Adafruit IO MQTT API MUST require a username
        try:
            self._user = self._client._username
        except Exception as err:
            raise TypeError("Adafruit IO requires a username, please set one in MiniMQTT") from err
        # User-defined MQTT callback methods must be init'd to None
        self.on_connect = None
        self.on_disconnect = None
        self.on_message = None
        self.on_subscribe = None
        self.on_unsubscribe = None
        self.on_publish = None
        # MQTT event callbacks
        self._client.on_connect = self._on_connect_mqtt
        self._client.on_disconnect = self._on_disconnect_mqtt
        self._client.on_message = self._on_message_mqtt
        self._client.on_subscribe = self._on_subscribe_mqtt
        self._client.on_unsubscribe = self._on_unsubscribe_mqtt
        self._client.on_publish = self._on_publish_mqtt
        self._connected = False

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self.disconnect()

    def reconnect(self):
        """Attempts to reconnect to the Adafruit IO MQTT Broker."""
        try:
            self._client.reconnect()
        except Exception as err:
            raise AdafruitIO_MQTTError("Unable to reconnect to Adafruit IO.") from err

    def connect(self):
        """Connects to the Adafruit IO MQTT Broker.
        Must be called before any other API methods are called.
        """
        try:
            self._client.connect()
        except Exception as err:
            raise AdafruitIO_MQTTError("Unable to connect to Adafruit IO.") from err

    def disconnect(self):
        """Disconnects from Adafruit IO MQTT Broker."""
        if self._connected:
            self._client.disconnect()

    @property
    def is_connected(self):
        """Returns if connected to Adafruit IO MQTT Broker."""
        try:
            return self._client.is_connected()
        except MMQTTException:
            return False

    def _on_connect_mqtt(self, client, userdata, flags, return_code):
        """Runs when the client calls on_connect."""
        if return_code == 0:
            self._connected = True
        else:
            raise AdafruitIO_MQTTError(return_code)
        # Call the user-defined on_connect callback if defined
        if self.on_connect is not None:
            self.on_connect(self)

    def _on_disconnect_mqtt(self, client, userdata, return_code):
        """Runs when the client calls on_disconnect."""
        self._connected = False
        # Call the user-defined on_disconnect callblack if defined
        if self.on_disconnect is not None:
            self.on_disconnect(self)

    def _on_message_mqtt(self, client, topic: str, payload: str):
        """Runs when the client calls on_message. Parses and returns
        incoming data from Adafruit IO feeds.

        :param MQTT client: A MQTT Client Instance.
        :param str topic: MQTT topic response from Adafruit IO.
        :param str payload: MQTT payload data response from Adafruit IO.
        """
        if self.on_message is not None:
            # Parse the MQTT topic string
            topic_name = topic.split("/")
            if topic_name[1] == "groups":
                # Adafruit IO Group Feed(s)
                feeds = []
                messages = []
                # Conversion of incoming group to a json response
                payload = json.loads(payload)
                for feed in payload["feeds"]:
                    feeds.append(feed)
                for msg in feeds:
                    payload = payload["feeds"][msg]
                    messages.append(payload)
                topic_name = feeds
                message = messages
            elif topic_name[1] == "throttle":
                raise AdafruitIO_ThrottleError(payload)
            elif topic_name[0] == "time":
                # Adafruit IO Time Topic
                topic_name = topic_name[1]
                message = payload
            else:
                # Standard Adafruit IO Feed
                topic_name = topic_name[2]
                message = payload
        else:
            raise ValueError("You must define an on_message method before calling this callback.")
        self.on_message(self, topic_name, message)

    def _on_publish_mqtt(self, client, user_data, topic, pid):
        """Runs when the client calls on_publish."""
        if self.on_publish is not None:
            self.on_publish(self, user_data, topic, pid)

    def _on_subscribe_mqtt(self, client, user_data, topic, qos):
        """Runs when the client calls on_subscribe."""
        if self.on_subscribe is not None:
            self.on_subscribe(self, user_data, topic, qos)

    def _on_unsubscribe_mqtt(self, client, user_data, topic, pid):
        """Runs when the client calls on_unsubscribe."""
        if self.on_unsubscribe is not None:
            self.on_unsubscribe(self, user_data, topic, pid)

    def add_feed_callback(self, feed_key: str, callback_method: Callable):
        """Attaches a callback_method to an Adafruit IO feed.
        The callback_method function is called when a
        new value is written to the feed.

        NOTE: The callback_method registered to this method
        will only execute during loop().

        :param str feed_key: Adafruit IO feed key.
        :param str callback_method: Name of callback method.
        """
        validate_feed_key(feed_key)
        self._client.add_topic_callback(f"{self._user}/f/{feed_key}", callback_method)

    def remove_feed_callback(self, feed_key: str):
        """Removes a previously registered callback method
        from executing whenever feed_key receives new data.

        After this method is called, incoming messages
        call the shared on_message.

        :param str feed_key: Adafruit IO feed key.
        """
        validate_feed_key(feed_key)
        self._client.remove_topic_callback(f"{self._user}/f/{feed_key}")

    def loop(self, timeout=1):
        """Manually process messages from Adafruit IO.
        Call this method to check incoming subscription messages.

        :param int timeout: Socket timeout, in seconds.

        Example usage of polling the message queue using loop.

        .. code-block:: python

            while True:
                io.loop()
        """
        self._client.loop(timeout)

    # Subscriptions
    def subscribe(
        self,
        feed_key: str = None,
        group_key: str = None,
        shared_user: Optional[str] = None,
    ):
        """Subscribes to your Adafruit IO feed or group.
        Can also subscribe to someone else's feed.

        :param str feed_key: Adafruit IO Feed key.
        :param str group_key: Adafruit IO Group key.
        :param str shared_user: Owner of the Adafruit IO feed, required for shared feeds.

        Example of subscribing to an Adafruit IO Feed named 'temperature'.

        .. code-block:: python

            client.subscribe('temperature')
        """
        if shared_user is not None and feed_key is not None:
            validate_feed_key(feed_key)
            self._client.subscribe(f"{shared_user}/f/{feed_key}")
        elif group_key is not None:
            validate_feed_key(group_key)
            self._client.subscribe(f"{self._user}/g/{group_key}")
        elif feed_key is not None:
            validate_feed_key(feed_key)
            self._client.subscribe(f"{self._user}/f/{feed_key}")
        else:
            raise AdafruitIO_MQTTError("Must provide a feed_key or group_key.")

    def subscribe_to_throttling(self):
        """Subscribes to your personal Adafruit IO /throttle topic.
        https://io.adafruit.com/api/docs/mqtt.html#mqtt-api-rate-limiting
        """
        self._client.subscribe("%s/throttle" % self._user)

    def subscribe_to_errors(self):
        """Subscribes to your personal Adafruit IO /errors topic.
        Notifies you of errors relating to publish/subscribe calls.
        """
        self._client.subscribe("%s/errors" % self._user)

    def subscribe_to_randomizer(self, randomizer_id: int):
        """Subscribes to a random data stream created by the Adafruit IO Words service.

        :param int randomizer_id: Random word record you want data for.
        """
        self._client.subscribe(f"{self._user}/integration/words/{randomizer_id}")

    def subscribe_to_weather(self, weather_record: int, forecast: str):
        """Subscribes to a weather forecast using the Adafruit IO PLUS weather
        service. This feature is only avaliable to Adafruit IO PLUS subscribers.

        :param int weather_record: Weather record you want data for.
        :param str forecast: Forecast data you'd like to recieve.
        """
        self._client.subscribe(f"{self._user}/integration/weather/{weather_record}/{forecast}")

    def subscribe_to_time(self, time_type: str):
        """Adafruit IO provides some built-in MQTT topics for getting the current server time.

        :param str time_type: Current Adafruit IO server time. Can be 'seconds', 'millis', or 'iso'.

        Information about these topics can be found on the Adafruit IO MQTT API Docs.:
        https://io.adafruit.com/api/docs/mqtt.html#time-topics
        """
        if time_type == "iso":
            self._client.subscribe("time/ISO-8601")
        else:
            self._client.subscribe("time/" + time_type)

    def unsubscribe(
        self,
        feed_key: str = None,
        group_key: str = None,
        shared_user: Optional[str] = None,
    ):
        """Unsubscribes from an Adafruit IO feed or group.
        Can also subscribe to someone else's feed.

        :param str feed_key: Adafruit IO Feed key.
        :param str group_key: Adafruit IO Group key.
        :param str shared_user: Owner of the Adafruit IO feed, required for shared feeds.

        Example of unsubscribing from a feed.

        .. code-block:: python

            client.unsubscribe('temperature')

        Example of unsubscribing from a shared feed.

        .. code-block:: python

            client.unsubscribe('temperature', shared_user='adabot')
        """
        if shared_user is not None and feed_key is not None:
            validate_feed_key(feed_key)
            self._client.unsubscribe(f"{shared_user}/f/{feed_key}")
        elif group_key is not None:
            validate_feed_key(group_key)
            self._client.unsubscribe(f"{self._user}/g/{group_key}")
        elif feed_key is not None:
            validate_feed_key(feed_key)
            self._client.unsubscribe(f"{self._user}/f/{feed_key}")
        else:
            raise AdafruitIO_MQTTError("Must provide a feed_key or group_key.")

    # Publishing
    def publish_multiple(self, feeds_and_data: List, timeout: int = 3, is_group: bool = False):
        """Publishes multiple data points to multiple feeds or groups with a variable
        timeout.

        :param list feeds_and_data: List of tuples containing topic strings and data values.
        :param int timeout: Delay between publishing data points to Adafruit IO, in seconds.
        :param bool is_group: Set to True if you're publishing to a group.

        Example of publishing multiple data points on different feeds to Adafruit IO:

        .. code-block:: python

            client.publish_multiple([('humidity', 24.5), ('temperature', 54)])
        """
        if isinstance(feeds_and_data, list):
            feed_data = []
            for topic, data in feeds_and_data:
                feed_data.append((topic, data))
        else:
            raise AdafruitIO_MQTTError("This method accepts a list of tuples.")
        for topic, data in feed_data:
            if is_group:
                self.publish(topic, data, is_group=True)
            else:
                self.publish(topic, data)
            time.sleep(timeout)

    def publish(
        self,
        feed_key: str,
        data: str,
        metadata: str = None,
        shared_user: str = None,
        is_group: bool = False,
    ):
        """Publishes to an Adafruit IO Feed.

        :param str feed_key: Adafruit IO Feed key.
        :param str data: Data to publish to the feed or group.
        :param int data: Data to publish to the feed or group.
        :param float data: Data to publish to the feed or group.
        :param str metadata: Optional metadata associated with the data.
        :param str shared_user: Owner of the Adafruit IO feed, required for
                                feed sharing.
        :param bool is_group: Set True if publishing to an Adafruit IO Group.

        Example of publishing an integer to Adafruit IO on feed 'temperature'.

        .. code-block:: python

            client.publish('temperature', 30)

        Example of publishing a floating point value to feed 'temperature'.

        .. code-block:: python

            client.publish('temperature', 3.14)

        Example of publishing a string to feed 'temperature'.

        .. code-block:: python

            client.publish('temperature, 'thirty degrees')

        Example of publishing an integer to group 'weatherstation'.

        .. code-block:: python

            client.publish('weatherstation', 12, is_group=True)

        Example of publishing to a shared feed.

        .. code-block:: python

            client.publish('temperature', shared_user='myfriend')

        Example of publishing a value along with locational metadata to a feed.

        .. code-block:: python

            data = 42
            # format: "lat, lon, ele"
            metadata = "40.726190, -74.005334, -6"
            io.publish("location-feed", data, metadata)
        """
        validate_feed_key(feed_key)
        if is_group:
            self._client.publish(f"{self._user}/g/{feed_key}", data)
        if shared_user is not None:
            self._client.publish(f"{shared_user}/f/{feed_key}", data)
        if metadata is not None:
            if isinstance(data, int or float):
                data = str(data)
            csv_string = data + "," + metadata
            self._client.publish(f"{self._user}/f/{feed_key}/csv", csv_string)
        else:
            self._client.publish(f"{self._user}/f/{feed_key}", data)

    def get(self, feed_key: str):
        """Calling this method will make Adafruit IO publish the most recent
        value on feed_key.
        https://io.adafruit.com/api/docs/mqtt.html#retained-values

        :param str feed_key: Adafruit IO Feed key.

        Example of obtaining a recently published value on a feed:

        .. code-block:: python

            io.get('temperature')
        """
        validate_feed_key(feed_key)
        self._client.publish(f"{self._user}/f/{feed_key}/get", "\0")


class IO_HTTP:
    """
    Client for interacting with the Adafruit IO HTTP API.
    https://io.adafruit.com/api/docs/#adafruit-io-http-api

    :param str adafruit_io_username: Adafruit IO Username
    :param str adafruit_io_key: Adafruit IO Key
    :param requests: A passed adafruit_requests module.
    """

    def __init__(self, adafruit_io_username, adafruit_io_key, requests):
        self.username = adafruit_io_username
        self.key = adafruit_io_key
        self._http = requests

        self._aio_headers = [
            {"X-AIO-KEY": self.key, "Content-Type": "application/json"},
            {"X-AIO-KEY": self.key},
        ]

    @staticmethod
    def _create_headers(io_headers):
        """Creates http request headers."""
        headers = CLIENT_HEADERS.copy()
        headers.update(io_headers)
        return headers

    @staticmethod
    def _create_data(data, metadata: dict):
        """Returns a data payload as expected by the Adafruit IO HTTP API

        :param data: Payload value.
        :param dict metadata: Payload metadata.
        """
        payload = {"value": data}
        if metadata:  # metadata is expected as a dict, append key/vals
            for k, val in metadata.items():
                payload[k] = val
        return payload

    @staticmethod
    def _handle_error(response):
        """Checks HTTP status codes
        and raises errors.
        """
        if response.status_code == 429:
            raise AdafruitIO_ThrottleError
        if response.status_code == 400:
            raise AdafruitIO_RequestError(response)
        if response.status_code >= 400:
            raise AdafruitIO_RequestError(response)

    def _compose_path(self, path: str):
        """Composes a valid API request path.

        :param str path: Adafruit IO API URL path.
        """
        return f"https://io.adafruit.com/api/v2/{self.username}/{path}"

    # HTTP Requests
    def _post(self, path: str, payload: Any):
        """
        POST data to Adafruit IO

        :param str path: Formatted Adafruit IO URL from _compose_path
        :param json payload: JSON data to send to Adafruit IO
        """
        with self._http.post(
            path, json=payload, headers=self._create_headers(self._aio_headers[0])
        ) as response:
            self._handle_error(response)
            json_data = response.json()

        return json_data

    def _get(self, path: str):
        """
        GET data from Adafruit IO

        :param str path: Formatted Adafruit IO URL from _compose_path
        """
        with self._http.get(path, headers=self._create_headers(self._aio_headers[1])) as response:
            self._handle_error(response)
            json_data = response.json()
        return json_data

    def _delete(self, path: str):
        """
        DELETE data from Adafruit IO.

        :param str path: Formatted Adafruit IO URL from _compose_path
        """
        with self._http.delete(
            path, headers=self._create_headers(self._aio_headers[0])
        ) as response:
            self._handle_error(response)
            json_data = response.json()

        return json_data

    # Data
    def send_data(
        self,
        feed_key: str,
        data: str,
        metadata: Optional[dict] = None,
        precision: Optional[int] = None,
    ):
        """
        Sends value data to a specified Adafruit IO feed.

        :param str feed_key: Adafruit IO feed key
        :param str data: Data to send to the Adafruit IO feed
        :param dict metadata: Optional metadata associated with the data
        :param int precision: Optional amount of precision points to send with floating point data
        """
        validate_feed_key(feed_key)
        path = self._compose_path(f"feeds/{feed_key}/data")
        if precision:
            try:
                data = round(data, precision)
            except NotImplementedError as err:  # received a non-float value
                raise NotImplementedError("Precision requires a floating point value") from err
        payload = self._create_data(data, metadata)
        self._post(path, payload)

    def send_batch_data(self, feed_key: str, data_list: list):
        """
        Sends a batch array of data to a specified Adafruit IO feed

        :param str feed_key: Adafruit IO feed key
        :param list Data: Data list to send (namedtuples or dicts with 'value' key)
        """
        validate_feed_key(feed_key)
        if not isinstance(data_list, list) or data_list == []:
            raise ValueError("Data must be a list of dicts or namedtuples")
        if not isinstance(data_list[0], dict):  # assume namedtuple
            data_list = type(data_list)(data._asdict() for data in data_list)
        if not all("value" in data for data in data_list):
            raise ValueError("Data list items must at least contain a 'value' key")
        path = self._compose_path(f"feeds/{feed_key}/data/batch")
        self._post(path, {"data": data_list})

    def send_group_data(
        self, group_key: str, feeds_and_data: list, metadata: Optional[dict] = None
    ):
        """
        Sends data to specified Adafruit IO feeds in a group

        :param str group_key: Adafruit IO feed key
        :param list feeds_and_data: A list of dicts, with feed "key" and "value" entries
        :param dict metadata: Optional metadata for the data e.g. created_at, lat, lon, ele
        """
        validate_feed_key(group_key)
        path = self._compose_path(f"groups/{group_key}/data")
        if not isinstance(feeds_and_data, list):
            raise ValueError('This method accepts a list of dicts with "key" and "value".')
        if metadata is not None:
            if not isinstance(metadata, dict):
                raise ValueError("Metadata must be a dictionary.")
            metadata.update({"feeds": feeds_and_data})
            self._post(path, metadata)
        else:
            self._post(path, {"feeds": feeds_and_data})

    def receive_all_data(self, feed_key: str):
        """
        Get all data values from a specified Adafruit IO feed. Data is
        returned in reverse order.

        :param str feed_key: Adafruit IO feed key
        """
        validate_feed_key(feed_key)
        path = self._compose_path(f"feeds/{feed_key}/data")
        return self._get(path)

    def receive_n_data(self, feed_key: str, n_values: int):
        """
        Get most recent n data values from a specified feed. Data is
        returned in reverse order.

        :param str feed_key: Adafruit IO feed key
        :param int n_values: Number of data values
        """
        validate_n_values(n_values)
        validate_feed_key(feed_key)
        path = self._compose_path(f"feeds/{feed_key}/data?limit={n_values}")
        return self._get(path)

    def receive_data(self, feed_key: str):
        """
        Return the most recent value for the specified feed.

        :param string feed_key: Adafruit IO feed key
        """
        validate_feed_key(feed_key)
        path = self._compose_path(f"feeds/{feed_key}/data/last")
        return self._get(path)

    def delete_data(self, feed_key: str, data_id: str):
        """
        Deletes an existing Data point from a feed.

        :param string feed: Adafruit IO feed key
        :param string data_id: Data point to delete from the feed
        """
        validate_feed_key(feed_key)
        path = self._compose_path(f"feeds/{feed_key}/data/{data_id}")
        return self._delete(path)

    # Groups
    def create_new_group(self, group_key: str, group_description: str):
        """
        Creates a new Adafruit IO Group.

        :param str group_key: Adafruit IO Group Key
        :param str group_description: Brief summary about the group
        """
        path = self._compose_path("groups")
        payload = {"name": group_key, "description": group_description}
        return self._post(path, payload)

    def delete_group(self, group_key: str):
        """
        Deletes an existing group.

        :param str group_key: Adafruit IO Group Key
        """
        path = self._compose_path(f"groups/{group_key}")
        return self._delete(path)

    def get_group(self, group_key: str):
        """
        Returns Group based on Group Key

        :param str group_key: Adafruit IO Group Key
        """
        path = self._compose_path(f"groups/{group_key}")
        return self._get(path)

    def create_feed_in_group(self, group_key: str, feed_name: str):
        """Creates a new feed in an existing group.

        :param str group_key: Group name.
        :param str feed_name: Name of new feed.
        """
        path = self._compose_path(f"groups/{group_key}/feeds")
        payload = {"feed": {"name": feed_name}}
        return self._post(path, payload)

    def add_feed_to_group(self, group_key: str, feed_key: str):
        """
        Adds an existing feed to a group

        :param str group_key: Group
        :param str feed_key: Feed to add to the group
        """
        validate_feed_key(feed_key)
        path = self._compose_path(f"groups/{group_key}/add")
        payload = {"feed_key": feed_key}
        return self._post(path, payload)

    # Feeds
    def get_feed(self, feed_key: str, detailed: bool = False):
        """
        Returns an Adafruit IO feed based on the feed key

        :param str feed_key: Adafruit IO Feed Key
        :param bool detailed: Returns a more verbose feed record
        """
        validate_feed_key(feed_key)
        if detailed:
            path = self._compose_path(f"feeds/{feed_key}/details")
        else:
            path = self._compose_path(f"feeds/{feed_key}")
        return self._get(path)

    def create_new_feed(
        self,
        feed_key: str,
        feed_desc: Optional[str] = None,
        feed_license: Optional[str] = None,
    ):
        """
        Creates a new Adafruit IO feed.

        :param str feed_key: Adafruit IO Feed Key
        :param str feed_desc: Optional description of feed
        :param str feed_license: Optional feed license
        """
        validate_feed_key(feed_key)
        path = self._compose_path("feeds")
        payload = {"name": feed_key, "description": feed_desc, "license": feed_license}
        return self._post(path, payload)

    def create_and_get_feed(
        self,
        feed_key: str,
        detailed: bool = False,
        feed_desc: Optional[str] = None,
        feed_license: Optional[str] = None,
    ):
        """
        Attempts to return a feed; if the feed does not exist, it is created, and then returned.

        :param str feed_key: Adafruit IO Feed Key
        :param bool detailed: Returns a more verbose existing feed record
        :param str feed_desc: Optional description of feed to be created
        :param str feed_license: Optional feed license to be created
        """
        try:
            return self.get_feed(feed_key, detailed=detailed)
        except AdafruitIO_RequestError:
            self.create_new_feed(feed_key, feed_desc=feed_desc, feed_license=feed_license)
            return self.get_feed(feed_key, detailed=detailed)

    def delete_feed(self, feed_key: str):
        """
        Deletes an existing feed.

        :param str feed_key: Valid feed key
        """
        validate_feed_key(feed_key)
        path = self._compose_path(f"feeds/{feed_key}")
        return self._delete(path)

    # Adafruit IO Connected Services
    def receive_weather(self, weather_id: int):
        """
        Get data from the Adafruit IO Weather Forecast Service
        NOTE: This service is avaliable to Adafruit IO Plus subscribers only.

        :param int weather_id: ID for retrieving a specified weather record.
        """
        path = self._compose_path(f"integrations/weather/{weather_id}")
        return self._get(path)

    def receive_random_data(self, generator_id: int):
        """
        Get data from the Adafruit IO Random Data Stream Service

        :param int generator_id: Specified randomizer record
        """
        path = self._compose_path(f"integrations/words/{generator_id}")
        return self._get(path)

    def get_user_info(self):
        """
        Get detailed account information for the current user.

        See https://io.adafruit.com/api/docs/#get-user-info
        """
        return self._get("https://io.adafruit.com/api/v2/user")

    def get_user_rate_info(self):
        """
        Get rate limit and usage information for the current user.

        See https://io.adafruit.com/api/docs/#get-detailed-user-info

        Example output:
        ```
        {
        "data_rate_limit": 30,
        "active_data_rate": 0,
        "authentication_rate": 0,
        "subscribe_authorization_rate": 0,
        "publish_authorization_rate": 0,
        "hourly_ban_rate": 0,
        "mqtt_ban_error_message": null,
        "active_sms_rate": 0
        }
        ```
        """
        path = self._compose_path("throttle")
        return self._get(path)

    def get_remaining_throttle_limit(self):
        """
        Get the remaining data points allowed before hitting the throttle limit.
        This retrieves the user rate limit and deducts usage for the current user.

        See https://io.adafruit.com/api/docs/#get-detailed-user-info
        """
        user_rates = self.get_user_rate_info()
        if user_rates is None:
            raise ValueError("Could not get user info, get_user_rate_info returned None.")
        return user_rates["data_rate_limit"] - user_rates["active_data_rate"]

    def get_throttle_limit(self):
        """
        Get user throttle limit a.k.a "data_rate_limit" for the current user.

        See https://io.adafruit.com/api/docs/#get-detailed-user-info
        """
        user_rates = self.get_user_rate_info()
        if user_rates is None:
            raise ValueError("Could not get user info, get_user_rate_info returned None.")
        return user_rates["data_rate_limit"]

    def get_current_usage(self):
        """
        Get current rate usage a.k.a "active_data_rate" for the current user.

        See https://io.adafruit.com/api/docs/#get-detailed-user-info
        """
        user_rates = self.get_user_rate_info()
        if user_rates is None:
            raise ValueError("Could not get user info, get_user_rate_info returned None.")
        return user_rates["active_data_rate"]

    def receive_time(self, timezone: str = None):
        """
        Returns a struct_time from the Adafruit IO Server based on the device's IP address.
        https://circuitpython.readthedocs.io/en/latest/shared-bindings/time/__init__.html#time.struct_time
        The default time returned is based on the device's IP address being geolocated,
        falling back to UTC if unable to be geolocated. The timezone can be manually set.

        :param str timezone: Timezone to return time in, see https://io.adafruit.com/services/time
        """
        path = self._compose_path("integrations/time/struct.json")
        if timezone is not None:
            path += f"?tz={timezone}"
        time_struct = self._get(path)
        return time.struct_time(
            (
                time_struct["year"],
                time_struct["mon"],
                time_struct["mday"],
                time_struct["hour"],
                time_struct["min"],
                time_struct["sec"],
                time_struct["wday"],
                time_struct["yday"],
                time_struct["isdst"],
            )
        )
