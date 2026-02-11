# SPDX-FileCopyrightText: 2026 Adafruit Industries
# SPDX-License-Identifier: MIT

"""CPython example of creating and deleting an Adafruit IO+ Air Quality location.

This feature is only available to Adafruit IO+ subscribers.
"""

import time
from os import getenv

import requests

from adafruit_io.adafruit_io import IO_HTTP

# Adafruit IO keys (set as environment variables)
aio_username = getenv("ADAFRUIT_AIO_USERNAME")
aio_key = getenv("ADAFRUIT_AIO_KEY")

if not aio_username or not aio_key:
    raise RuntimeError("Missing ADAFRUIT_AIO_USERNAME or ADAFRUIT_AIO_KEY environment variables.")

io = IO_HTTP(aio_username, aio_key, requests)

# Location: Godrevy Lighthouse, Cornwall, UK
LOCATION = "50.2423591, -5.4001148"
NAME = "Godrevy Lighthouse, Cornwall" + time.strftime(" %Y-%m-%d %H:%M:%S")
PROVIDER = "open_meteo"

print("Creating air quality location...")
created = io.create_air_quality(LOCATION, name=NAME, provider=PROVIDER)
location_id = created["id"]
print(f"Created air quality location '{NAME}' with ID: {location_id}")

try:
    print("\nFetching air quality data...")
    data = io.receive_air_quality(location_id)
    print("Available keys:", list(data.keys()))
    try:
        print('\n"last_requested_at":', data["last_requested_at"])
        print('\n"current":', data["current"])
    except KeyError:
        pass

    print("\nListing air quality locations...")
    locations = io.get_air_quality()
    for loc in locations:
        print(loc["id"], loc["name"], loc["location"])
    found = any(loc.get("id") == location_id for loc in locations)
    print(f"Created location present in list: {found}")
finally:
    print("\nDeleting air quality location in 3s...")
    time.sleep(3)
    io.delete_air_quality(location_id)
    print("Deleted air quality location.")
