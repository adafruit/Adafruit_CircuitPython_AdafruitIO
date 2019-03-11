Adafruit_CircuitPython_AdafruitIO
=================================

.. image:: https://readthedocs.org/projects/adafruit-circuitpython-adafruitio/badge/?version=latest
    :target: https://circuitpython.readthedocs.io/projects/adafruitio/en/latest/
    :alt: Documentation Status

.. image:: https://img.shields.io/discord/327254708534116352.svg
    :target: https://discord.gg/nBQh6qu
    :alt: Discord

.. image:: https://travis-ci.com/adafruit/Adafruit_CircuitPython_AdafruitIO.svg?branch=master
    :target: https://travis-ci.com/adafruit/Adafruit_CircuitPython_AdafruitIO
    :alt: Build Status

CircuitPython wrapper library for communicating with `Adafruit IO <http://io.adafruit.com>`_.


Dependencies
============

This driver depends on:

* `Adafruit CircuitPython <https://github.com/adafruit/circuitpython>`_

You'll also need a library to communicate with an ESP32 as a coprocessor using a WiFiManager object. This library supports connecting an ESP32 using either SPI or UART.

* SPI: `Adafruit CircuitPython ESP32SPI <https://github.com/adafruit/Adafruit_CircuitPython_ESP32SPI>`_

* UART: `Adafruit CircuitPython ESP_ATcontrol <https://github.com/adafruit/Adafruit_CircuitPython_ESP_ATcontrol>`_

Please ensure all dependencies are available on the CircuitPython filesystem.
This is easily achieved by downloading
`the Adafruit library and driver bundle <https://github.com/adafruit/Adafruit_CircuitPython_Bundle>`_.

Usage Example
=============

Create an Adafruit IO Client object  

.. code-block:: python

   io = RESTClient(aio_username, aio_key, wifi)

Sending data to an Adafruit IO feed

.. code-block:: python

   io.send_data(feed, data)

Receiving data from an Adafruit IO feed

.. code-block:: python
  
   data = io.receive_data(feed)

Creating a new feed named circuitpython with a description

.. code-block:: python

    feed = io.create_new_feed('circuitpython', 'an Adafruit IO CircuitPython feed')

Listing the record of a specified feed:

.. code-block:: python
    
    feed = io.get_feed('circuitpython')

Contributing
============

Contributions are welcome! Please read our `Code of Conduct
<https://github.com/adafruit/Adafruit_CircuitPython_Adafruit_IO/blob/master/CODE_OF_CONDUCT.md>`_
before contributing to help this project stay welcoming.

Building locally
================

Zip release files
-----------------

To build this library locally you'll need to install the
`circuitpython-build-tools <https://github.com/adafruit/circuitpython-build-tools>`_ package.

.. code-block:: shell

    python3 -m venv .env
    source .env/bin/activate
    pip install circuitpython-build-tools

Once installed, make sure you are in the virtual environment:

.. code-block:: shell

    source .env/bin/activate

Then run the build:

.. code-block:: shell

    circuitpython-build-bundles --filename_prefix adafruit-circuitpython-adafruit_io --library_location .

Sphinx documentation
--------------------

Sphinx is used to build the documentation based on rST files and comments in the code. First,
install dependencies (feel free to reuse the virtual environment from above):

.. code-block:: shell

    python3 -m venv .env
    source .env/bin/activate
    pip install Sphinx sphinx-rtd-theme

Now, once you have the virtual environment activated:

.. code-block:: shell

    cd docs
    sphinx-build -E -W -b html . _build/html

This will output the documentation to ``docs/_build/html``. Open the index.html in your browser to
view them. It will also (due to -W) error out on any warning like Travis will. This is a good way to
locally verify it will pass.
