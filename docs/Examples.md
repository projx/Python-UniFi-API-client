# UniFi API Client Examples

This document describes all the example scripts provided with the UniFi API Client.

## Basic Examples

### test_connection.py
Tests connection to the UniFi controller and displays system information.

### list_clients.py
Lists all currently connected client devices and outputs in JSON format.

### list_devices.py
Lists all UniFi devices managed by the controller.

## Device Management

### adopt_device.py
Demonstrates how to adopt a new device to your UniFi network.

### ap_scanning_state.py
Shows how to manage AP scanning state.

### ap_upgrade_firmware.py
Demonstrates firmware upgrade process for access points.

### disable_device.py
Shows how to disable/enable a UniFi device.

### toggle_led.py
Demonstrates toggling the locate LED function on a UniFi device.

## Network Configuration

### change_super_mgmt.py
Changes the Super Management VLAN ID.

### change_wlan_password.py
Updates the password for a wireless network.

### set_vlan_to_port.py
Configures VLANs on UniFi switches.

### update_ac_iw_ports.py
Updates port settings on an AC-IW device.

### update_switch_poe_mode.py
Updates PoE mode on a switch port.

### update_device_wlan_settings_5.5.X.py
Updates WLAN settings for devices running 5.5.X firmware.

## Guest Management

### auth_guest_basic.py
Demonstrates basic guest authorization.

### auth_guest_with_note.py
Shows guest authorization with additional notes.

### extend_guest_auth.py
Extends an existing guest authorization.

### create_voucher.py
Creates guest vouchers with various parameters.

## Client Management

### block_list.py
Demonstrates blocking client devices.

### unblock_list.py
Shows how to unblock previously blocked clients.

### reconnect_client.py
Forces a client device to reconnect.

## Site Management

### create_site.py
Creates a new UniFi site.

### delete_site.py
Demonstrates site deletion.

### list_sites.py
Lists all available sites.

## Statistics and Monitoring

### list_alarms.py
Lists all system alarms.

### list_ap_connected_users.py
Shows users connected to specific access points.

### list_gateway_stats.py
Displays UniFi Gateway statistics.

### list_site_health.py
Shows health metrics for a site.

### list_social_auth_details.py
Lists social authentication details.

### list_user_stats.py
Displays user statistics.

## Advanced Examples

### execute_custom_api_request.py
Shows how to make custom API requests.

### modify_smartpower_pdu_outlet.py
Demonstrates controlling SmartPower PDU outlets.

## Site Provisioning Example

A complete workflow for setting up a new site:

### 01-create_site.py
Creates a new UniFi site.

### 02-adopt_devices.py
Adopts devices to the newly created site.

### 03-configure_site.py
Configures site-wide settings including WLANs and networks.

### 04-configure_devices.py
Configures individual devices with specific settings.

## Configuration

### config.template.py
Template for configuration settings. Copy to `config.py` and update with your settings:
- `CONTROLLER_USER`: Controller username
- `CONTROLLER_PASSWORD`: Controller password
- `CONTROLLER_URL`: Controller URL
- `CONTROLLER_VERSION`: Controller version
- `SITE_ID`: Site ID to manage
- `DEBUG`: Enable/disable debug mode
