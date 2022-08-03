[![pypi](https://img.shields.io/pypi/v/vivintpy?style=for-the-badge)](https://pypi.org/project/vivintpy)
[![downloads](https://img.shields.io/pypi/dm/vivintpy?style=for-the-badge)](https://pypi.org/project/vivintpy)
[![Buy Me A Coffee/Beer](https://img.shields.io/badge/Buy_Me_A_☕/🍺-F16061?style=for-the-badge&logo=ko-fi&logoColor=white&labelColor=grey)](https://ko-fi.com/natekspencer)

# vivintpy

Python library for interacting with a Vivint security and smart home system.

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
- add tests

---

## Support Me

I'm not employed by Vivint, and provide this python package as-is.

If you don't already own a Vivint system, please consider using [my referal code (kaf164)](https://www.vivint.com/get?refCode=kaf164&exid=165211vivint.com/get?refCode=kaf164&exid=165211) to get $50 off your bill (as well as a tip to me in appreciation)!

If you already own a Vivint system and still want to donate, consider buying me a coffee ☕ (or beer 🍺) instead by using the link below:

<a href='https://ko-fi.com/natekspencer' target='_blank'><img height='35' style='border:0px;height:46px;' src='https://az743702.vo.msecnd.net/cdn/kofi3.png?v=0' border='0' alt='Buy Me a Coffee at ko-fi.com' />
