Adafruit_CircuitPython_AdafruitIO
=================================

.. image:: https://readthedocs.org/projects/adafruit-circuitpython-adafruitio/badge/?version=latest
    :target: https://docs.circuitpython.org/projects/adafruitio/en/latest/
    :alt: Documentation Status

.. image:: https://raw.githubusercontent.com/adafruit/Adafruit_CircuitPython_Bundle/main/badges/adafruit_discord.svg
    :target: https://adafru.it/discord
    :alt: Discord

.. image:: https://github.com/adafruit/Adafruit_CircuitPython_AdafruitIO/workflows/Build%20CI/badge.svg
    :target: https://github.com/adafruit/Adafruit_CircuitPython_AdafruitIO/actions/
    :alt: Build Status

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
    :target: https://github.com/psf/black
    :alt: Code Style: Black

CircuitPython wrapper library for communicating with `Adafruit IO <http://io.adafruit.com>`_.


Dependencies
============

This driver depends on:

* `Adafruit CircuitPython <https://github.com/adafruit/circuitpython>`_
* `Adafruit CircuitPython ConnectionManager <https://github.com/adafruit/Adafruit_CircuitPython_ConnectionManager/>`_
* `Adafruit CircuitPython MiniMQTT <https://github.com/adafruit/Adafruit_CircuitPython_MiniMQTT>`_

Please ensure that all dependencies are available on the CircuitPython filesystem.
This is easily achieved by downloading
`the Adafruit library and driver bundle <https://github.com/adafruit/Adafruit_CircuitPython_Bundle>`_.

Installing from PyPI
====================

On supported GNU/Linux systems like the Raspberry Pi, you can install the driver locally `from
PyPI <https://pypi.org/project/adafruit-circuitpython-adafruitio/>`_. To install for current user:

.. code-block:: shell

    pip3 install adafruit-circuitpython-adafruitio

To install system-wide (this may be required in some cases):

.. code-block:: shell

    sudo pip3 install adafruit-circuitpython-adafruitio

To install in a virtual environment in your current project:

.. code-block:: shell

    mkdir project-name && cd project-name
    python3 -m venv .venv
    source .venv/bin/activate
    pip3 install adafruit-circuitpython-adafruitio

Usage Example
=============

Usage examples for the Adafruit IO HTTP API are within the examples/http folder.

Usage examples for the Adafruit IO MQTT API are within the examples/mqtt folder.

Documentation
=============

API documentation for this library can be found on `Read the Docs <https://docs.circuitpython.org/projects/adafruitio/en/latest/>`_.

For information on building library documentation, please check out `this guide <https://learn.adafruit.com/creating-and-sharing-a-circuitpython-library/sharing-our-docs-on-readthedocs#sphinx-5-1>`_.

Contributing
============

Contributions are welcome! Please read our `Code of Conduct
<https://github.com/adafruit/Adafruit_CircuitPython_AdafruitIO/blob/main/CODE_OF_CONDUCT.md>`_
before contributing to help this project stay welcoming.
