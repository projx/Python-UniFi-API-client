# UniFi API Client

This is a Python port of the PHP UniFi API Client, designed to interact with Ubiquiti's UniFi Controller API. This client is compatible with Python 3.12 and later versions.

Note, this was a project done in about 2 hours on a Sunday evening using Codeium's Windsurf AI IDE... its written the code and examples, tested the outcodes and made it work.. it comes with no gaurantees or support.. if there is enough interest, then I will try to make it more robust and add more features.


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
