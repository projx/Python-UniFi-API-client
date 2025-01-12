# UniFi API Client Methods

This document describes all available methods in the UniFi API Client.

## Authentication Methods

### login()
Logs in to the UniFi Controller.

### logout()
Logs out from the UniFi Controller.

## Device Management

### list_devices(mac=None)
Lists all devices or a specific device by MAC address.
- `mac`: Optional MAC address to filter by

### adopt_device(mac)
Adopts a device to the site.
- `mac`: MAC address of the device to adopt

### set_device_settings(mac, settings)
Updates device settings.
- `mac`: MAC address of the device
- `settings`: Dictionary of settings to update

### set_device_name(mac, name)
Sets a device's name.
- `mac`: MAC address of the device
- `name`: New name for the device

### locate_device(mac, enable=True)
Toggles the locate LED function on a device.
- `mac`: MAC address of the device
- `enable`: True to enable locate LED, False to disable

## Network Management

### create_network(settings)
Creates a new network.
- `settings`: Dictionary containing network configuration

### list_networkconf()
Lists all network configurations.

### create_wlan(settings)
Creates a new wireless network (WLAN).
- `settings`: Dictionary containing WLAN configuration

### list_wlanconf()
Lists all WLAN configurations.

### set_wlansettings(wlan_id, settings)
Updates WLAN settings.
- `wlan_id`: ID of the WLAN to update
- `settings`: Dictionary of settings to update

## Client Management

### list_clients()
Lists all clients currently connected.

### list_all_clients()
Lists all clients (including historical).

### stat_client(mac)
Gets stats for a specific client.
- `mac`: MAC address of the client

### block_client(mac)
Blocks a client device.
- `mac`: MAC address of the client to block

### unblock_client(mac)
Unblocks a client device.
- `mac`: MAC address of the client to unblock

### reconnect_client(mac)
Forces a client device to reconnect.
- `mac`: MAC address of the client

### list_blocked_clients()
Lists all blocked client devices.

## Guest Management

### authorize_guest(mac, minutes, up=None, down=None, bytes=None)
Authorizes a guest device.
- `mac`: MAC address of the guest device
- `minutes`: Number of minutes for authorization
- `up`: Upload speed limit in Kbps
- `down`: Download speed limit in Kbps
- `bytes`: Data transfer limit in MB

### unauthorize_guest(mac)
Unauthorizes a guest device.
- `mac`: MAC address of the guest device

### extend_guest_validity(mac, minutes)
Extends guest authorization.
- `mac`: MAC address of the guest device
- `minutes`: Additional minutes to add

## Voucher Management

### create_voucher(minutes, count=1, quota=0, note="", up=None, down=None, bytes=None)
Creates one or more vouchers.
- `minutes`: Number of minutes the voucher is valid for
- `count`: Number of vouchers to create
- `quota`: Number of devices allowed per voucher
- `note`: Note to add to the voucher(s)
- `up`: Upload speed limit in Kbps
- `down`: Download speed limit in Kbps
- `bytes`: Data transfer limit in MB

### list_vouchers()
Lists all vouchers.

### stat_voucher(voucher_id)
Gets stats for a specific voucher.
- `voucher_id`: ID of the voucher

## Site Management

### list_sites()
Lists all sites.

### create_site(description)
Creates a new site.
- `description`: Description/name for the new site

### delete_site(site)
Deletes a site.
- `site`: Site ID to delete

## System Management

### stat_sysinfo()
Gets system information.

### stat_admin()
Gets admin information.

### set_auto_update_settings(enable=True, hour=4, day="sun", timezone="America/Los_Angeles")
Configures auto update settings.
- `enable`: True to enable auto updates, False to disable
- `hour`: Hour of the day to perform updates (0-23)
- `day`: Day of the week to perform updates
- `timezone`: Timezone for update schedule

## Utility Methods

### _api_request(endpoint, method="POST", data=None)
Makes an API request to the controller.
- `endpoint`: API endpoint
- `method`: HTTP method (GET/POST)
- `data`: Data to send with the request
