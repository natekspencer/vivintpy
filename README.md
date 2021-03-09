# vivintpy

Python library for interacting with the Vivint Sky API.

This was built to support the `Vivint` integration in [Home-Assistant](https://www.home-assistant.io/) but _should_ work outside of it too. Currently, it can be utilized via [HACS](https://hacs.xyz/) by adding the [hacs-vivint](https://github.com/natekspencer/hacs-vivint) custom repository.

## Credit

This was inspired by the great work done by [Mike Reibard](https://github.com/Riebart/vivint.py) to reverse engineer the Vivint Sky API and [Ovidiu Stateina](https://github.com/ovirs/pyvivint) for the repository from which this is forked and expanded on.

## Features

It currently has support for the following device types:

- alarm panels
- cameras
- door locks
- garage doors
- switches
  - binary
  - multilevel
- thermostats
- wireless sensors
  - carbon monoxide
  - door/window
  - flood
  - glass break
  - motion
  - smoke/fire
  - etc

In addition, it integrates with PubNub to receive real-time updates for devices. This subscription stops receiving notifications around 15-20 minutes unless a call is made to the Vivint Sky API periodically. This **might** be related to the cookie expiration since it expires 20 minutes after the last API call was received. If another client connects, however, the notifications start to stream again for all currently connected clients.

## Usage

See demo.py for a demonstration on how to use this library.

## TODO:

- write a better readme
- write some documentation
- add advanced support for:
  - thermostats
- implement 2FA
- add tests
