# Getting Started with UniFi API Client

This guide will help you get started with the UniFi API Client for Python.

## Prerequisites

- Python 3.6 or higher
- UniFi Controller 5.x or higher
- Network access to your UniFi Controller

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/unifi-api.git
cd unifi-api
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

1. Copy the template configuration file:
```bash
cp examples/config.template.py examples/config.py
```

2. Edit `examples/config.py` with your UniFi Controller details:
```python
CONTROLLER_USER     = "admin"               # Controller username
CONTROLLER_PASSWORD = "password"            # Controller password
CONTROLLER_URL      = "https://127.0.0.1:8443"  # Controller URL
CONTROLLER_VERSION  = "UDMP-unifiOS"       # Controller version
SITE_ID            = "default"             # Site ID to manage
DEBUG              = False                 # Enable/disable debug mode
```

## Basic Usage

Here's a simple example to get you started:

```python
from unifi_api_client import Client

# Initialize the client
unifi = Client(
    username="admin",
    password="password",
    baseurl="https://127.0.0.1:8443",
    site="default",
    version="UDMP-unifiOS"
)

# Login to the controller
unifi.login()

# List all devices
devices = unifi.list_devices()
for device in devices:
    print(f"Device: {device.get('name')} ({device.get('mac')})")

# Don't forget to logout
unifi.logout()
```

## SSL Verification

By default, SSL verification is enabled. If you're using a self-signed certificate, you can disable SSL verification:

```python
unifi = Client(
    username="admin",
    password="password",
    baseurl="https://127.0.0.1:8443",
    site="default",
    version="UDMP-unifiOS",
    ssl_verify=False  # Disable SSL verification
)
```

**Note**: Disabling SSL verification is not recommended for production environments.

## Error Handling

The client includes several exception classes for proper error handling:

```python
from unifi_api_client import Client
from unifi_api_client.exceptions import (
    LoginFailedException,
    LoginRequiredException,
    UniFiAPIError
)

try:
    unifi = Client(...)
    unifi.login()
    devices = unifi.list_devices()
except LoginFailedException:
    print("Failed to log in")
except LoginRequiredException:
    print("Not logged in")
except UniFiAPIError as e:
    print(f"API Error: {str(e)}")
```

## Example Scripts

Check out the `examples` directory for various usage examples:

1. Start with `test_connection.py` to verify your connection
2. Try `list_devices.py` to see all your UniFi devices
3. Explore other examples based on your needs

## Site Provisioning Example

The `examples/site_provisioning_example` directory contains a complete workflow for setting up a new site:

1. `01-create_site.py`: Creates a new site
2. `02-adopt_devices.py`: Adopts devices to the site
3. `03-configure_site.py`: Configures site settings
4. `04-configure_devices.py`: Configures individual devices

## Next Steps

1. Review the [API Documentation](API.md) for all available methods
2. Check out the [Examples Documentation](Examples.md) for detailed script descriptions
3. Join our community for support and discussions

## Support

If you encounter any issues or have questions:

1. Check the [documentation](docs/)
2. Look for similar issues in the issue tracker
3. Create a new issue if needed

## Contributing

We welcome contributions! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
