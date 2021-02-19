# pyvivint

python library for interacting with vivintsky API

This was built to support the `Vivint` integration in [home-assistant](https://www.home-assistant.io/) but _should_ work outside of it too. It can run on an existing ioloop or create its own if one is not provided.

## Credit

This was inspired by the great work done by [Mike Reibard](https://github.com/Riebart/vivint.py) to reverse engineer the VivintSky API and it shamelessly reuses most of his code.

## Features

It currently has support for the following device types:

- alarm panels
- cameras
- door locks
- garage doors
- thermostats
- wireless sensors:
  - carbon monoxide
  - door/window
  - flood
  - glass break
  - motion
  - smoke/fire
  - etc

In addition, it integrates with pubnub to receive real-time updates for the devices. This subscription stops receiving notifications around 15-20 minutes unless a call is made to the VivintSky API periodically. This **might** be related to the cookie expiration since it expires 20 minutes after the last API call was received. If another client connects, however, the notifications start to stream again for all currently connected clients.

## Usage

See demo.py for a demonstration on how to use this library.

## TODO:

- write a better readme
- add tests
- write some documentation
- add device support for:
  - multi-level switches
- implement 2FA
