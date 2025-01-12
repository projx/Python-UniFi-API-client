# UniFi API Client

This is a Python port of the PHP UniFi API Client, designed to interact with Ubiquiti's UniFi Controller API. This client is compatible with Python 3.12 and later versions.

Note, this was a project done in about 2 hours on a Sunday evening using Codeium's Windsurf AI IDE... its written the code and examples, tested the outcodes and made it work.. it comes with no gaurantees or support.. if there is enough interest, then I will try to make it more robust and add more features.

# UniFi API Client for Python

A Python port of the [PHP UniFi API Client](https://github.com/Art-of-WiFi/UniFi-API-client) maintained by Art-of-WiFi.

## Special Thanks

This project would not be possible without the incredible work of [Art-of-WiFi](https://github.com/Art-of-WiFi) and their [UniFi API Client for PHP](https://github.com/Art-of-WiFi/UniFi-API-client). Their meticulous documentation, comprehensive examples, and dedication to maintaining the PHP client have been invaluable in creating this Python port. We extend our deepest gratitude for their contribution to the UniFi community.

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
