# pyvivint
python library for interacting with vivintsky API

This was built to support the `Vivint` integration in [home-assistant](https://www.home-assistant.io/) but _should_ work outside of it too. It can run on an existing ioloop or create its own if one is not provided.

## Credit
This was inspired by the great work done by [Mike Reibard](https://github.com/Riebart/vivint.py) to reverse engineer the VivintSky Api and it shamelessly reuses most of his code.

## Features
It currently has support for the following device types:
* alarm panels itself
* door locks
* wireless sensors (door/window sensor, glass break sensors, etc)
* cameras

In addition, it integrates with pubnub to receive real-time updates for the devices.

## TODO:
* write a better readme
* add tests
* write some documentation
