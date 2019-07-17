# The MIT License (MIT)
#
# Copyright (c) 2019 Brent Rubell for Adafruit
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
`adafruit_io_errors.py`
======================================================
CircuitPython Adafruit IO Error Classes
* Author(s): Brent Rubell
"""


class AdafruitIO_ThrottleError(Exception):
    """Adafruit IO request error class for rate-limiting"""

    def __init__(self):
        super(AdafruitIO_ThrottleError, self).__init__(
            "Number of Adafruit IO Requests exceeded! \
                                                            Please try again in 30 seconds.."
        )


class AdafruitIO_RequestError(Exception):
    """Adafruit IO request error class"""

    def __init__(self, response):
        response_content = response.json()
        error = response_content["error"]
        super(AdafruitIO_RequestError, self).__init__(
            "Adafruit IO Error {0}: {1}".format(response.status_code, error)
        )


class AdafruitIO_MQTTError(Exception):
    """Adafruit IO MQTT error class"""

    def __init__(self, response):
        super(AdafruitIO_MQTTError, self).__init__("MQTT Error: {0}".format(response))
