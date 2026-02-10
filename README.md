<!-- BEGIN AUTO-GENERATED HEADER -->

[![PyPI](https://img.shields.io/pypi/v/vivintpy?style=for-the-badge)](https://pypi.org/project/vivintpy/)
[![Python](https://img.shields.io/pypi/pyversions/vivintpy?style=for-the-badge)](https://pypi.org/project/vivintpy/)
[![License](https://img.shields.io/github/license/natekspencer/vivintpy?style=for-the-badge)](LICENSE)
[![Buy Me A Coffee/Beer](https://img.shields.io/badge/Buy_Me_A_☕/🍺-F16061?style=for-the-badge&logo=ko-fi&logoColor=white&labelColor=grey)](https://ko-fi.com/natekspencer)
[![Sponsor on GitHub](https://img.shields.io/badge/Sponsor_💜-6f42c1?style=for-the-badge&logo=github&logoColor=white&labelColor=grey)](https://github.com/sponsors/natekspencer)

![Downloads](https://img.shields.io/pypi/dm/vivintpy?style=flat-square)

<!-- END AUTO-GENERATED HEADER -->

# vivintpy

Python library for interacting with a Vivint security and smart home system.

This was built to support the [`Vivint`](https://github.com/natekspencer/hacs-vivint) integration in [Home-Assistant](https://www.home-assistant.io/) but _should_ work outside of it too. Currently, it can be utilized via [HACS](https://hacs.xyz/) by adding the [hacs-vivint](https://github.com/natekspencer/hacs-vivint) custom repository.

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

<!-- BEGIN AUTO-GENERATED FOOTER -->

## ❤️ Support Me

I maintain this python project in my spare time and provide it as-is, without guarantees. If you find it useful, consider supporting development:

- 💜 [Sponsor me on GitHub](https://github.com/sponsors/natekspencer)
- ☕ [Buy me a coffee / beer](https://ko-fi.com/natekspencer)
- 💸 [PayPal (direct support)](https://www.paypal.com/paypalme/natekspencer)
- ⭐ [Star this project](https://github.com/natekspencer/vivintpy)
- 📦 If you’d like to support in other ways, such as donating hardware for testing, feel free to [reach out to me](https://github.com/natekspencer)

If you don't already own a Vivint system, please consider using [my referral code (35fr23sv)](https://www.vivint.com/get?refCode=35fr23sv&v=200) and get a free Doorbell Camera Pro from Vivint (as well as a tip to me in appreciation)! You can also call (855) 747-7199 and mention referral code `35fr23sv`.

## 📈 Star History

[![Star History Chart](https://api.star-history.com/svg?repos=natekspencer/vivintpy)](https://www.star-history.com/#natekspencer/vivintpy)

<!-- END AUTO-GENERATED FOOTER -->
