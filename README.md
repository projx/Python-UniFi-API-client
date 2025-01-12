# UniFi API Client

This is a Python port of the PHP UniFi API Client, designed to interact with Ubiquiti's UniFi Controller API. This client is compatible with Python 3.12 and later versions.

Note, this was a project done in about 2 hours on a Sunday evening using Codeium's Windsurf AI IDE... its written the code and examples, tested the outcodes and made it work.. it comes with no gaurantees or support.. if there is enough interest, then I will try to make it more robust and add more features.

# UniFi API Client for Python (Port of Unifi-API-client for PHP)

A Python port of the [PHP UniFi API Client](https://github.com/Art-of-WiFi/UniFi-API-client) maintained by Art-of-WiFi, currently based upon v2.0.4, as such the same limitations apply as with the PHP version, i.e. versions of the Unifi Controller that are supported.

### Supported Versions

| Software                             | Versions                                             |
|--------------------------------------|------------------------------------------------------|
| UniFi Network Application/controller | 5.x, 6.x, 7.x, 8.x, 9.0.x (**9.0.101 is confirmed**) |
| UniFi OS                             | 3.x, 4.1.x (**4.1.9 is confirmed**)                  |

###
## UniFi OS Support

Besides the "software-based" UniFi controllers, this class also supports UniFi OS-based controllers starting from
version **1.1.47**.

These devices/services have been verified to work with the PHP client, as such there is a high probability that they willwork with this Python port as well:

- UniFi Dream Router (UDR)
- UniFi Dream Machine (UDM)
- UniFi Dream Machine Pro (UDM PRO)
- UniFi Cloud Key Gen2 (UCK G2), firmware version 2.0.24 or higher
- UniFi Cloud Key Gen2 Plus (UCK G2 Plus), firmware version 2.0.24 or higher
- UniFi Express (UX)
- UniFi Dream Wall (UDW)
- UniFi Cloud Gateway Ultra (UCG-Ultra)
- UniFi CloudKey Enterprise (CK-Enterprise)
- UniFi Enterprise Fortress Gateway (EFG)
- Official UniFi Hosting, details [here](https://help.ui.com/hc/en-us/articles/4415364143511)

## Special Thanks

This project would not be possible without the incredible work of [Art-of-WiFi](https://github.com/Art-of-WiFi) and their [UniFi API Client for PHP](https://github.com/Art-of-WiFi/UniFi-API-client). Their meticulous documentation, comprehensive examples, and dedication to maintaining the PHP client have been invaluable in creating this Python port. We extend our deepest gratitude for their contribution to the UniFi community.

### 


## Installation

```bash
pip install unifi-api-client
```

## Basic Usage

```python
from unifi_api_client import Client

# Initialize the client
client = Client(
    username="your_username",
    password="your_password",
    baseurl="https://unifi.yourdomain.com:8443",
    site="default",
    verify_ssl=False  # Set to True in production
)

# Get list of all clients
clients = client.list_clients()
```

## Features

- Full UniFi Controller API support
- Support for UniFi OS and legacy controllers
- SSL verification options
- Comprehensive error handling
- Retry mechanism for failed requests
- Support for custom API endpoints

## Examples

Check the `examples` directory for comprehensive examples of various API operations.

## Requirements

- Python 3.12 or higher
- `requests` library

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Credits

This Python port is based on the original PHP implementation by Art of WiFi (info@artofwifi.net) and the contributions of the UniFi API Client community.
