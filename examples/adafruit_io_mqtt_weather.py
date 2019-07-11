# Example of using the Adafruit IO CircuitPython MQTT Client
# for subscribe to a weather forecast provided by the
# Adafruit IO Weather Service (IO Plus subscribers ONLY).
# This example uses ESP32SPI to connect over WiFi
#
# by Brent Rubell for Adafruit Industries, 2019
import time
from random import randint
import board
import neopixel
import busio
from digitalio import DigitalInOut

# Import WiFi configuration
from adafruit_esp32spi import adafruit_esp32spi
from adafruit_esp32spi import adafruit_esp32spi_wifimanager
import adafruit_esp32spi.adafruit_esp32spi_socket as socket

# Import the Adafruit IO MQTT Class
from adafruit_io.adafruit_io import MQTT

### WiFi ###

# Get wifi details and more from a secrets.py file
try:
    from secrets import secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add them there!")
    raise

# If you are using a board with pre-defined ESP32 Pins:
esp32_cs = DigitalInOut(board.ESP_CS)
esp32_ready = DigitalInOut(board.ESP_BUSY)
esp32_reset = DigitalInOut(board.ESP_RESET)

# If you have an externally connected ESP32:
# esp32_cs = DigitalInOut(board.D9)
# esp32_ready = DigitalInOut(board.D10)
# esp32_reset = DigitalInOut(board.D5)

spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
esp = adafruit_esp32spi.ESP_SPIcontrol(spi, esp32_cs, esp32_ready, esp32_reset)
"""Use below for Most Boards"""
status_light = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=0.2) # Uncomment for Most Boards
"""Uncomment below for ItsyBitsy M4"""
# status_light = dotstar.DotStar(board.APA102_SCK, board.APA102_MOSI, 1, brightness=0.2)
# Uncomment below for an externally defined RGB LED
# import adafruit_rgbled
# from adafruit_esp32spi import PWMOut
# RED_LED = PWMOut.PWMOut(esp, 26)
# GREEN_LED = PWMOut.PWMOut(esp, 27)
# BLUE_LED = PWMOut.PWMOut(esp, 25)
# status_light = adafruit_rgbled.RGBLED(RED_LED, BLUE_LED, GREEN_LED)
wifi = adafruit_esp32spi_wifimanager.ESPSPI_WiFiManager(esp, secrets, status_light)

# Set to ID of the forecast to subscribe to for updates
forecast_id = 2127

# Set to the ID of the feed to subscribe to for updates.
"""
Valid forecast types are:
current
forecast_minutes_5
forecast_minutes_30
forecast_hours_1
forecast_hours_2
forecast_hours_6
forecast_hours_24
forecast_days_1
forecast_days_2
forecast_days_5
"""
# Subscribe to the current forecast
forecast_today = 'current'
# Subscribe to tomorrow's forecast
forecast_two_days = 'forecast_days_2'
# Subscribe to forecast in 5 days
forecast_in_5_days = 'forecast_days_5'

# Define callback functions which will be called when certain events happen.
# pylint: disable=redefined-outer-name
def connected(client):
    # Connected function will be called when the client is connected to Adafruit IO.
    # This is a good place to subscribe to feed changes.  The client parameter
    # passed to this function is the Adafruit IO MQTT client so you can make
    # calls against it easily.
    print('Connected to Adafruit IO!  Listening to forecast: {0}...'.format(forecast_id))
    # Subscribe to changes on the current forecast.
    client.subscribe_weather(forecast_id, forecast_today)

    # Subscribe to changes on tomorrow's forecast.
    client.subscribe_weather(forecast_id, forecast_two_days)

    # Subscribe to changes on forecast in 5 days.
    client.subscribe_weather(forecast_id, forecast_in_5_days)

# pylint: disable=unused-argument
def disconnected(client):
    # Disconnected function will be called when the client disconnects.
    print('Disconnected from Adafruit IO!')
    sys.exit(1)

# pylint: disable=unused-argument
def message(client, topic, payload):
    """Message function will be called when any subscribed forecast has an update.
    Weather data is updated at most once every 20 minutes.
    """
    print('NEW MESSAGE: ', topic, payload)
    # forecast based on mqtt topic
    if topic == 'current':
        # Print out today's forecast
        today_forecast = payload
        print('\nCurrent Forecast')
        parseForecast(today_forecast)
    elif topic == 'forecast_days_2':
        # Print out tomorrow's forecast
        two_day_forecast = payload
        print('\nWeather in Two Days')
        parseForecast(two_day_forecast)
    elif topic == 'forecast_days_5':
        # Print out forecast in 5 days
        five_day_forecast = payload
        print('\nWeather in 5 Days')
        parseForecast(five_day_forecast)

def parseForecast(forecast_data):
    """Parses and prints incoming forecast data
    """
    # incoming data is a utf-8 string, encode it as a json object
    forecast = json.loads(forecast_data)
    # Print out the forecast
    try:
        print('It is {0} and {1}F.'.format(forecast['summary'], forecast['temperature']))
    except KeyError:
        # future weather forecasts return a high and low temperature, instead of 'temperature'
        print('It will be {0} with a high of {1}F and a low of {2}F.'.format(
            forecast['summary'], forecast['temperatureLow'], forecast['temperatureHigh']))
    print('with humidity of {0}%, wind speed of {1}mph, and {2}% chance of precipitation.'.format(
        forecast['humidity'], forecast['windSpeed'], forecast['precipProbability']))

# Connect to WiFi
wifi.connect()

# Initialize a new Adafruit IO WiFi MQTT client.
client = MQTT(secrets['aio_user'],
              secrets['aio_password'],
              wifi,
              socket)

# Setup the callback functions defined above.
client.on_connect    = connected
client.on_disconnect = disconnected
client.on_message    = message

# Connect to the Adafruit IO server.
client.connect()

# Start a message loop that blocks forever waiting for MQTT messages to be
# received.  Note there are other options for running the event loop like doing
# so in a background thread--see the mqtt_client.py example to learn more.
client.loop_blocking()
