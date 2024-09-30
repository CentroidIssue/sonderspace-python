<!-- 
    Fill in and replace all Sonder Space (Python)
-->
# Sonder Space (Python)

Sonder Space: Messenger-Based Anonymous Messaging Application (Python)

This project is abandoned for a renewed Sonder Space using MERN Stack

This repository is a clone of the legacy Sonder Space Python. Due to privacy reasons, the original repository will not be public (Commit history contains sensitive information)

## Table of contents

* [1. General information](#1-general-information)
* [2. Structures](#2-structure)
* [3. Installation](#3-installation)
* [4. Usage](#4-usage)
* [5. Contributing](#5-contributing)
* [6. Code of conduct](#6-code-of-conduct)
* [7. Funding](#7-funding)
* [8. License](#8-license)
* [9. Todo](#9-todo)

## 1. General information

Sonder Space is an entertainment facebook page that connects people within it into conversations [Sonder Space](https://facebook.com/sonderspace.ss)
This application is using Python-Flask WebFramework to host a webapp receiving and sending APIs externally. More information relating this webapp can be reached via this url [https://midnightmelancholia.pythonanywhere.com](https://midnightmelancholia.pythonanywhere.com).
Cloud hosting plan on **Pythonanywhere** is free-of-charge.

## 2. Structure

Your directory tree

## 3. Installation

### Prerequisites

Python>=3.10

### Getting Started

To run this project, please clone the repo into your local devices

```bash
git clone https://github.com/centroidissue/sonderspace-python
cd Sonder-Space
python -m pip install -r requirements.txt
python app.py
```

## 4. Usage

Then open another terminal and tunnel your server externally

```bash
sh -R 80:127.0.0.1:80 serveo.net #Or any other SSH tunnelers
```

Go to [https://developers.facebook.com](https://developers.facebook.com) and login, please assure that you have an application to connect to the website. If you have none, please create one.

After choosing your application, click on **Dashboard** on your top left, scroll down and set up **Webhooks** and **Messenger** (If you have not processed)

On your left, go to Messenger -> Settings, scroll down, click **Add or remove Pages** then add your preferred page to be used for the application.

Once you are done, edit **Callback URL** to the address after tunneling and **Verify token** to *appsify*

Finally, you can message your Facebook page and see the application running

## 5. Contributing

If you're interested in contributing to Sonder Space (Python), we welcome your input. Whether you're a seasoned developer or just starting out, there are many ways you can help improve the project. You can contribute code, documentation, bug reports, or feature requests. To get started, check out the contributing guidelines in the [Contributing](CONTRIBUTING.md) file.

## 6. Code of conduct

We want everyone who participates in Sonder Space (Python) to feel welcome and respected. To ensure that happens, we've established a code of conduct that outlines our expectations for behavior. You can read the full text of the code of conduct in the [Code of Conduct](CODE_OF_CONDUCT.md) file.

## 7. Funding

Sonder Space (Python) is currently self-funded and developed on a volunteer basis. If you're interested in supporting the project financially, we welcome your contributions. You can donate through our/my [Open Collective](https://opencollective.com/phong-thien) page.

## 8. License

Sonder Space (Python) is released under the [MIT License](LICENSE.md). This means you're free to use, modify, and distribute the software for any purpose, including commercial use. However, we provide no warranties or guarantees, so use the software at your own risk.

## 9. Todo

Re-ininitialisation of Sonder Space
