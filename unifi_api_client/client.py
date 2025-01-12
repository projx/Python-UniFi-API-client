"""
UniFi API Client - Main Client Class

This UniFi API client class is based on the work done by the following developers:
   domwo: https://community.ui.com/questions/little-php-class-for-unifi-api/933d3fb3-b401-4499-993a-f9af079a4a3a
   fbagnol: https://github.com/fbagnol/class.unifi.php
and the API as published by Ubiquiti:
   https://dl.ui.com/unifi/<UniFi controller version number>/unifi_sh_api

@author Art of WiFi <info@artofwifi.net>
@license This class is subject to the MIT license bundled with this package in the file LICENSE.md
"""

import json
import time
from typing import Optional, Dict, Any, List, Union
import requests
from requests.exceptions import RequestException, Timeout
import urllib3

from .exceptions import (
    InvalidBaseUrlException,
    InvalidSiteNameException,
    LoginFailedException,
    LoginRequiredException,
    CurlGeneralErrorException,
    CurlTimeoutException,
)

# Disable InsecureRequestWarning when verify=False
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class Client:
    """UniFi API Client class for interacting with UniFi Controller API"""
    
    CLASS_VERSION = '2.0.3'
    HTTP_METHODS_ALLOWED = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']
    DEFAULT_HTTP_METHOD = 'GET'
    
    def __init__(
        self,
        username: str,
        password: str,
        baseurl: str = 'https://127.0.0.1:8443',
        site: Optional[str] = 'default',
        version: Optional[str] = '8.0.28',
        verify_ssl: bool = False,
        session_cookie_name: str = 'unificookie'
    ):
        """
        Initialize the UniFi API client
        
        Args:
            username: Username for the UniFi controller
            password: Password for the UniFi controller
            baseurl: Base URL of the UniFi controller (must include https://)
            site: Site name to access
            version: Controller version
            verify_ssl: Whether to verify SSL certificates
            session_cookie_name: Name of the session cookie to use
        """
        self._check_base_url(baseurl)
        self._check_site(site)
        
        self.baseurl = baseurl.strip()
        self.site = site.lower().strip()
        self.username = username.strip()
        self.password = password.strip()
        self.version = version.strip()
        self.session_cookie_name = session_cookie_name.strip()
        
        self.debug = False
        self.is_logged_in = False
        self.is_unifi_os = False
        self.exec_retries = 0
        
        self.session = requests.Session()
        self.session.verify = verify_ssl
        
        self.headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        
        self.session.headers.update(self.headers)
        
        # Default site stats attributes
        self.default_site_stats_attribs = [
            'bytes',
            'wan-tx_bytes',
            'wan-rx_bytes',
            'wlan_bytes',
            'num_sta',
            'lan-num_sta',
            'wlan-num_sta',
            'time',
        ]
    
    def _check_base_url(self, url: str) -> None:
        """Validate the base URL"""
        if not url.startswith('https://'):
            raise InvalidBaseUrlException('Base URL must begin with https://')
    
    def _check_site(self, site: str) -> None:
        """Validate the site name"""
        if not site or not isinstance(site, str):
            raise InvalidSiteNameException('Site name must be a non-empty string')
    
    def login(self) -> bool:
        """
        Login to the UniFi Controller
        
        Returns:
            bool: True if login successful
            
        Raises:
            LoginFailedException: If login fails
            RequestException: If there's a network error
        """
        # Skip if already logged in
        if self.is_logged_in:
            return True
            
        try:
            # Check if this is a UniFi OS controller
            response = self.session.get(f"{self.baseurl}/", verify=False)
            self.is_unifi_os = response.status_code == 200
            
            if self.debug:
                print(f"UniFi OS Detection - Status Code: {response.status_code}")
                print(f"Is UniFi OS: {self.is_unifi_os}")
            
            # Set login URL based on controller type
            login_url = f"{self.baseurl}/api/auth/login" if self.is_unifi_os else f"{self.baseurl}/api/login"
            
            if self.debug:
                print(f"Using login URL: {login_url}")
            
            # Prepare headers
            headers = {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
            
            if self.is_unifi_os:
                headers['Referer'] = f"{self.baseurl}/login"
            
            # Perform login
            login_data = {
                "username": self.username,
                "password": self.password,
                "remember": True
            }
            
            response = self.session.post(
                login_url,
                json=login_data,
                headers=headers,
                verify=False
            )
            
            if self.debug:
                print(f"Login Response - Status Code: {response.status_code}")
                print(f"Response Headers: {response.headers}")
                print(f"Response Body: {response.text}")
            
            if response.status_code == 200:
                self.is_logged_in = True
                self.headers = headers
                if self.is_unifi_os:
                    # Update headers with CSRF token if provided
                    csrf_token = response.headers.get('x-csrf-token')
                    if csrf_token:
                        self.headers['x-csrf-token'] = csrf_token
                return True
                
            raise LoginFailedException(f'HTTP response: {response.status_code}')
            
        except Timeout as e:
            raise CurlTimeoutException(str(e))
        except RequestException as e:
            raise CurlGeneralErrorException(str(e))
    
    def logout(self) -> bool:
        """
        Logout from the UniFi Controller
        
        Returns:
            bool: True if logout successful
            
        Raises:
            RequestException: If there's a network error
        """
        if not self.is_logged_in:
            return True
            
        try:
            logout_path = '/api/auth/logout' if self.is_unifi_os else '/logout'
            
            response = self.session.post(
                f"{self.baseurl}{logout_path}",
                headers=self.headers
            )
            
            self.is_logged_in = False
            self.session.cookies.clear()
            
            return True
            
        except Timeout as e:
            raise CurlTimeoutException(str(e))
        except RequestException as e:
            raise CurlGeneralErrorException(str(e))
    
    def _get_api_path(self, endpoint: str) -> str:
        """
        Construct the correct API path based on whether this is a UniFi OS controller
        
        Args:
            endpoint: The API endpoint to call
            
        Returns:
            str: The complete API path
        """
        if self.is_unifi_os:
            if endpoint.startswith('/api/s/'):
                # For UniFi OS, we need to add /proxy/network before /api/s/
                return f"{self.baseurl}/proxy/network{endpoint}"
            return f"{self.baseurl}{endpoint}"
        return f"{self.baseurl}{endpoint}"

    def _api_request(
        self,
        endpoint: str,
        method: str = 'GET',
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Make an API request to the UniFi Controller
        
        Args:
            endpoint: API endpoint to call
            method: HTTP method to use
            data: Data to send in the request body
            params: URL parameters to include
            
        Returns:
            Dict containing the API response
            
        Raises:
            LoginRequiredException: If not logged in
            RequestException: If there's a network error
        """
        if not self.is_logged_in:
            raise LoginRequiredException()
            
        if method not in self.HTTP_METHODS_ALLOWED:
            method = self.DEFAULT_HTTP_METHOD
            
        api_url = self._get_api_path(endpoint)
        
        if self.debug:
            print(f"API Request URL: {api_url}")
            print(f"Method: {method}")
            print(f"Data: {data}")
            print(f"Params: {params}")
            print(f"Headers: {self.headers}")
            
        try:
            response = self.session.request(
                method=method,
                url=api_url,
                json=data,
                params=params,
                headers=self.headers,
                verify=False
            )
            
            if self.debug:
                print(f"Response Status: {response.status_code}")
                print(f"Response Headers: {response.headers}")
                print(f"Response Body: {response.text}")
                
            response.raise_for_status()
            return response.json() if response.text else {}
            
        except requests.exceptions.HTTPError as e:
            raise CurlGeneralErrorException(f"{e.response.status_code} {e.response.reason} for url: {e.response.url}")
        except Timeout as e:
            raise CurlTimeoutException(str(e))
        except RequestException as e:
            raise CurlGeneralErrorException(str(e))
            
    def authorize_guest(
        self,
        mac: str,
        minutes: int,
        up: Optional[int] = None,
        down: Optional[int] = None,
        megabytes: Optional[int] = None,
        ap_mac: Optional[str] = None
    ) -> bool:
        """
        Authorize a client device
        
        Args:
            mac: Client MAC address
            minutes: Minutes until authorization expires
            up: Optional upload speed limit in kbps
            down: Optional download speed limit in kbps
            megabytes: Optional data transfer limit in MB
            ap_mac: Optional AP MAC address for faster authorization
            
        Returns:
            bool: True if successful
        """
        payload = {
            'cmd': 'authorize-guest',
            'mac': mac.lower(),
            'minutes': minutes
        }
        
        if up is not None:
            payload['up'] = up
            
        if down is not None:
            payload['down'] = down
            
        if megabytes is not None:
            payload['bytes'] = megabytes
            
        if ap_mac:
            # TODO: Add MAC address validation
            payload['ap_mac'] = ap_mac.lower()
            
        response = self._api_request('cmd/stamgr', method='POST', data=payload)
        return bool(response.get('meta', {}).get('rc') == 'ok')
    
    def unauthorize_guest(self, mac: str) -> bool:
        """
        Unauthorize a client device
        
        Args:
            mac: Client MAC address
            
        Returns:
            bool: True if successful
        """
        payload = {
            'cmd': 'unauthorize-guest',
            'mac': mac.lower()
        }
        
        response = self._api_request('cmd/stamgr', method='POST', data=payload)
        return bool(response.get('meta', {}).get('rc') == 'ok')
    
    def reconnect_sta(self, mac: str) -> bool:
        """
        Reconnect a client device
        
        Args:
            mac: Client MAC address
            
        Returns:
            bool: True if successful
        """
        payload = {
            'cmd': 'kick-sta',
            'mac': mac.lower()
        }
        
        response = self._api_request('cmd/stamgr', method='POST', data=payload)
        return bool(response.get('meta', {}).get('rc') == 'ok')
    
    def block_sta(self, mac: str) -> bool:
        """
        Block a client device
        
        Args:
            mac: Client MAC address
            
        Returns:
            bool: True if successful
        """
        payload = {
            'cmd': 'block-sta',
            'mac': mac.lower()
        }
        
        response = self._api_request('cmd/stamgr', method='POST', data=payload)
        return bool(response.get('meta', {}).get('rc') == 'ok')
    
    def unblock_sta(self, mac: str) -> bool:
        """
        Unblock a client device
        
        Args:
            mac: Client MAC address
            
        Returns:
            bool: True if successful
        """
        payload = {
            'cmd': 'unblock-sta',
            'mac': mac.lower()
        }
        
        response = self._api_request('cmd/stamgr', method='POST', data=payload)
        return bool(response.get('meta', {}).get('rc') == 'ok')
    
    def forget_sta(self, mac: Union[str, List[str]]) -> bool:
        """
        Forget one or more client devices
        
        Note:
            Only supported with controller versions 5.9.X and higher
            Can be slow (up to 5 minutes) on larger controllers
            
        Args:
            mac: Single MAC address or list of MAC addresses
            
        Returns:
            bool: True if successful
        """
        if isinstance(mac, str):
            macs = [mac]
        else:
            macs = mac
            
        payload = {
            'cmd': 'forget-sta',
            'macs': [m.lower() for m in macs]
        }
        
        response = self._api_request('cmd/stamgr', method='POST', data=payload)
        return bool(response.get('meta', {}).get('rc') == 'ok')
    
    def create_user(
        self,
        mac: str,
        user_group_id: str,
        name: Optional[str] = None,
        note: Optional[str] = None,
        is_guest: Optional[bool] = None,
        is_wired: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        Create a new user/client-device
        
        Args:
            mac: Client MAC address
            user_group_id: ID of the user group
            name: Optional name for the client
            note: Optional note for the client
            is_guest: Optional flag to mark as guest
            is_wired: Optional flag to mark as wired
            
        Returns:
            Dict containing the new user details
        """
        new_user = {
            'mac': mac.lower(),
            'usergroup_id': user_group_id
        }
        
        if name is not None:
            new_user['name'] = name
            
        if note is not None:
            new_user['note'] = note
            
        if is_guest is not None:
            new_user['is_guest'] = is_guest
            
        if is_wired is not None:
            new_user['is_wired'] = is_wired
            
        payload = {'objects': [{'data': new_user}]}
        
        return self._api_request('group/user', method='POST', data=payload)
    
    def set_sta_note(self, user_id: str, note: str = '') -> bool:
        """
        Add/modify/remove a client-device note
        
        Args:
            user_id: ID of the client device
            note: Note to apply (empty string to remove)
            
        Returns:
            bool: True if successful
        """
        payload = {'note': note}
        
        response = self._api_request(f'upd/user/{user_id.strip()}', method='POST', data=payload)
        return bool(response.get('meta', {}).get('rc') == 'ok')
    
    def set_sta_name(self, user_id: str, name: str = '') -> bool:
        """
        Add/modify/remove a client device name
        
        Args:
            user_id: ID of the client device
            name: Name to apply (empty string to remove)
            
        Returns:
            bool: True if successful
        """
        payload = {'name': name}
        
        response = self._api_request(f'upd/user/{user_id.strip()}', method='POST', data=payload)
        return bool(response.get('meta', {}).get('rc') == 'ok')
    
    def get_site_stats(
        self,
        start: Optional[int] = None,
        end: Optional[int] = None,
        attribs: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch 5-minute site stats
        
        Note:
            - Defaults to the past 12 hours
            - Only supported on controller versions 5.5.* and later
            
        Args:
            start: Optional Unix timestamp in milliseconds
            end: Optional Unix timestamp in milliseconds
            attribs: Optional list of attributes to collect
            
        Returns:
            List of stat objects
        """
        params = {}
        
        if start is not None:
            params['start'] = start
            
        if end is not None:
            params['end'] = end
            
        if attribs is not None:
            params['attrs'] = attribs
        else:
            params['attrs'] = self.default_site_stats_attribs
            
        return self._api_request('stat/report/5minutes.site', params=params)
    
    def get_site_stats_hourly(
        self,
        start: Optional[int] = None,
        end: Optional[int] = None,
        attribs: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch hourly site stats
        
        Note:
            - Defaults to the past 7*24 hours
            - "bytes" are no longer returned with controller version 4.9.1 and later
            
        Args:
            start: Optional Unix timestamp in milliseconds
            end: Optional Unix timestamp in milliseconds
            attribs: Optional list of attributes to collect
            
        Returns:
            List of stat objects
        """
        if end is None:
            end = int(time.time() * 1000)
        if start is None:
            start = end - (7 * 24 * 3600 * 1000)
            
        params = {
            'start': start,
            'end': end,
            'attrs': attribs if attribs is not None else self.default_site_stats_attribs
        }
        
        return self._api_request('stat/report/hourly.site', params=params)
    
    def get_site_stats_daily(
        self,
        start: Optional[int] = None,
        end: Optional[int] = None,
        attribs: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch daily site stats
        
        Note:
            - Defaults to the past 52*7*24 hours
            - "bytes" are no longer returned with controller version 4.9.1 and later
            
        Args:
            start: Optional Unix timestamp in milliseconds
            end: Optional Unix timestamp in milliseconds
            attribs: Optional list of attributes to collect
            
        Returns:
            List of stat objects
        """
        if end is None:
            end = int((time.time() - (time.time() % 3600)) * 1000)
        if start is None:
            start = end - (52 * 7 * 24 * 3600 * 1000)
            
        params = {
            'start': start,
            'end': end,
            'attrs': attribs if attribs is not None else self.default_site_stats_attribs
        }
        
        return self._api_request('stat/report/daily.site', params=params)
    
    def get_site_stats_monthly(
        self,
        start: Optional[int] = None,
        end: Optional[int] = None,
        attribs: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch monthly site stats
        
        Note:
            - Defaults to the past 52 weeks (52*7*24 hours)
            - "bytes" are no longer returned with controller version 4.9.1 and later
            
        Args:
            start: Optional Unix timestamp in milliseconds
            end: Optional Unix timestamp in milliseconds
            attribs: Optional list of attributes to collect
            
        Returns:
            List of stat objects
        """
        if end is None:
            end = int((time.time() - (time.time() % 3600)) * 1000)
        if start is None:
            start = end - (52 * 7 * 24 * 3600 * 1000)
            
        params = {
            'start': start,
            'end': end,
            'attrs': attribs if attribs is not None else self.default_site_stats_attribs
        }
        
        return self._api_request('stat/report/monthly.site', params=params)
    
    def get_ap_stats_5minutes(
        self,
        start: Optional[int] = None,
        end: Optional[int] = None,
        mac: Optional[str] = None,
        attribs: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch 5-minutes stats for a single access point or all access points
        
        Note:
            - Defaults to the past 12 hours
            - Only supported on controller versions 5.5.* and later
            
        Args:
            start: Optional Unix timestamp in milliseconds
            end: Optional Unix timestamp in milliseconds
            mac: Optional AP MAC address to return stats for
            attribs: Optional list of attributes to collect
            
        Returns:
            List of stat objects
        """
        if end is None:
            end = int(time.time() * 1000)
        if start is None:
            start = end - (12 * 3600 * 1000)
            
        params = {
            'start': start,
            'end': end,
            'attrs': attribs if attribs is not None else ['bytes', 'num_sta', 'time']
        }
        
        if mac:
            params['mac'] = mac.lower()
            
        return self._api_request('stat/report/5minutes.ap', params=params)
    
    def get_ap_stats_hourly(
        self,
        start: Optional[int] = None,
        end: Optional[int] = None,
        mac: Optional[str] = None,
        attribs: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch hourly stats for a single access point or all access points
        
        Note:
            - Defaults to the past 7*24 hours
            
        Args:
            start: Optional Unix timestamp in milliseconds
            end: Optional Unix timestamp in milliseconds
            mac: Optional AP MAC address to return stats for
            attribs: Optional list of attributes to collect
            
        Returns:
            List of stat objects
        """
        if end is None:
            end = int(time.time() * 1000)
        if start is None:
            start = end - (7 * 24 * 3600 * 1000)
            
        params = {
            'start': start,
            'end': end,
            'attrs': attribs if attribs is not None else ['bytes', 'num_sta', 'time']
        }
        
        if mac:
            params['mac'] = mac.lower()
            
        return self._api_request('stat/report/hourly.ap', params=params)
    
    def get_ap_stats_daily(
        self,
        start: Optional[int] = None,
        end: Optional[int] = None,
        mac: Optional[str] = None,
        attribs: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch daily stats for a single access point or all access points
        
        Note:
            - Defaults to the past 7*24 hours
            
        Args:
            start: Optional Unix timestamp in milliseconds
            end: Optional Unix timestamp in milliseconds
            mac: Optional AP MAC address to return stats for
            attribs: Optional list of attributes to collect
            
        Returns:
            List of stat objects
        """
        if end is None:
            end = int(time.time() * 1000)
        if start is None:
            start = end - (7 * 24 * 3600 * 1000)
            
        params = {
            'start': start,
            'end': end,
            'attrs': attribs if attribs is not None else ['bytes', 'num_sta', 'time']
        }
        
        if mac:
            params['mac'] = mac.lower()
            
        return self._api_request('stat/report/daily.ap', params=params)
    
    def get_ap_stats_monthly(
        self,
        start: Optional[int] = None,
        end: Optional[int] = None,
        mac: Optional[str] = None,
        attribs: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch monthly stats for a single access point or all access points
        
        Note:
            - Defaults to the past 52 weeks (52*7*24 hours)
            
        Args:
            start: Optional Unix timestamp in milliseconds
            end: Optional Unix timestamp in milliseconds
            mac: Optional AP MAC address to return stats for
            attribs: Optional list of attributes to collect
            
        Returns:
            List of stat objects
        """
        if end is None:
            end = int(time.time() * 1000)
        if start is None:
            start = end - (52 * 7 * 24 * 3600 * 1000)
            
        params = {
            'start': start,
            'end': end,
            'attrs': attribs if attribs is not None else ['bytes', 'num_sta', 'time']
        }
        
        if mac:
            params['mac'] = mac.lower()
            
        return self._api_request('stat/report/monthly.ap', params=params)
    
    def list_alarms(self, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        List all alarms in the system
        
        Args:
            params: Optional parameters to filter alarms
            
        Returns:
            List of alarm objects
        """
        return self._api_request('list/alarm', params=params)
    
    def stat_5minutes_user(
        self,
        mac: Optional[str] = None,
        start: Optional[int] = None,
        end: Optional[int] = None,
        attribs: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch 5-minutes stats for a single user/client device or all user/client devices.
        
        Note:
            - Defaults to the past 12 hours
            - Only supported with UniFi controller versions 5.8.X and higher
            - Make sure that the retention policy for 5-minute stats is set correctly
            - Make sure that "Clients Historical Data" is enabled in the UniFi controller settings
        
        Args:
            mac: Optional MAC address of the user/client device
            start: Optional Unix timestamp in milliseconds
            end: Optional Unix timestamp in milliseconds
            attribs: Optional list of attributes to return. Valid values:
                    rx_bytes, tx_bytes, signal, rx_rate, tx_rate, rx_retries,
                    tx_retries, rx_packets, tx_packets, satisfaction,
                    wifi_tx_attempts, duration
        
        Returns:
            List of 5-minute stats objects
        """
        end = end if end is not None else int(time.time() * 1000)
        start = start if start is not None else end - (12 * 3600 * 1000)
        attribs = ['time', 'rx_bytes', 'tx_bytes'] if attribs is None else ['time'] + attribs
        
        params = {
            'attrs': attribs,
            'start': start,
            'end': end,
        }
        
        if mac:
            params['mac'] = mac.lower()
            
        return self._api_request('stat/report/5minutes.user', params=params)
        
    def stat_hourly_user(
        self,
        mac: Optional[str] = None,
        start: Optional[int] = None,
        end: Optional[int] = None,
        attribs: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch hourly stats for a single user/client device or all user/client devices.
        
        Note:
            - Defaults to the past 7*24 hours
            - Only supported with UniFi controller versions 5.8.X and higher
            - Make sure that the retention policy for hourly stats is set correctly
            - Make sure that "Clients Historical Data" is enabled in the UniFi controller settings
        
        Args:
            mac: Optional MAC address of the user/client device
            start: Optional Unix timestamp in milliseconds
            end: Optional Unix timestamp in milliseconds
            attribs: Optional list of attributes to return
        
        Returns:
            List of hourly stats objects
        """
        end = end if end is not None else int(time.time() * 1000)
        start = start if start is not None else end - (7 * 24 * 3600 * 1000)
        attribs = ['time', 'rx_bytes', 'tx_bytes'] if attribs is None else ['time'] + attribs
        
        params = {
            'attrs': attribs,
            'start': start,
            'end': end,
        }
        
        if mac:
            params['mac'] = mac.lower()
            
        return self._api_request('stat/report/hourly.user', params=params)
        
    def stat_daily_user(
        self,
        mac: Optional[str] = None,
        start: Optional[int] = None,
        end: Optional[int] = None,
        attribs: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch daily stats for a single user/client device or all user/client devices.
        
        Note:
            - Defaults to the past 7*24 hours
            - Only supported with UniFi controller versions 5.8.X and higher
            - Make sure that the retention policy for daily stats is set correctly
            - Make sure that "Clients Historical Data" is enabled in the UniFi controller settings
        
        Args:
            mac: Optional MAC address of the user/client device
            start: Optional Unix timestamp in milliseconds
            end: Optional Unix timestamp in milliseconds
            attribs: Optional list of attributes to return
        
        Returns:
            List of daily stats objects
        """
        end = end if end is not None else int(time.time() * 1000)
        start = start if start is not None else end - (7 * 24 * 3600 * 1000)
        attribs = ['time', 'rx_bytes', 'tx_bytes'] if attribs is None else ['time'] + attribs
        
        params = {
            'attrs': attribs,
            'start': start,
            'end': end,
        }
        
        if mac:
            params['mac'] = mac.lower()
            
        return self._api_request('stat/report/daily.user', params=params)
        
    def stat_monthly_user(
        self,
        mac: Optional[str] = None,
        start: Optional[int] = None,
        end: Optional[int] = None,
        attribs: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch monthly stats for a single user/client device or all user/client devices.
        
        Note:
            - Defaults to the past 13 weeks (52*7*24 hours)
            - Only supported with UniFi controller versions 5.8.X and higher
            - Make sure that the retention policy for monthly stats is set correctly
            - Make sure that "Clients Historical Data" is enabled in the UniFi controller settings
        
        Args:
            mac: Optional MAC address of the user/client device
            start: Optional Unix timestamp in milliseconds
            end: Optional Unix timestamp in milliseconds
            attribs: Optional list of attributes to return
        
        Returns:
            List of monthly stats objects
        """
        end = end if end is not None else int(time.time() * 1000)
        start = start if start is not None else end - (13 * 7 * 24 * 3600 * 1000)
        attribs = ['time', 'rx_bytes', 'tx_bytes'] if attribs is None else ['time'] + attribs
        
        params = {
            'attrs': attribs,
            'start': start,
            'end': end,
        }
        
        if mac:
            params['mac'] = mac.lower()
            
        return self._api_request('stat/report/monthly.user', params=params)
        
    def stat_5minutes_gateway(
        self,
        start: Optional[int] = None,
        end: Optional[int] = None,
        attribs: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch 5-minute gateway stats.
        
        Note:
            - Defaults to the past 12 hours
            - Only supported on controller versions 5.5.* and later
            - Make sure that the retention policy for 5 minutes stats is set correctly
            - Requires a UniFi gateway
        
        Args:
            start: Optional Unix timestamp in milliseconds
            end: Optional Unix timestamp in milliseconds
            attribs: Optional list of attributes to return. Valid values:
                    mem, cpu, loadavg_5, lan-rx_errors, lan-tx_errors,
                    lan-rx_bytes, lan-tx_bytes, lan-rx_packets, lan-tx_packets,
                    lan-rx_dropped, lan-tx_dropped
        
        Returns:
            List of 5-minute stats objects for the gateway
        """
        end = end if end is not None else int(time.time() * 1000)
        start = start if start is not None else end - (12 * 3600 * 1000)
        attribs = ['time', 'mem', 'cpu', 'loadavg_5'] if attribs is None else ['time'] + attribs
        
        params = {
            'attrs': attribs,
            'start': start,
            'end': end,
        }
        
        return self._api_request('stat/report/5minutes.gw', params=params)
        
    def stat_hourly_gateway(
        self,
        start: Optional[int] = None,
        end: Optional[int] = None,
        attribs: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch hourly gateway stats.
        
        Note:
            - Defaults to the past 7*24 hours
            - Requires a UniFi gateway
        
        Args:
            start: Optional Unix timestamp in milliseconds
            end: Optional Unix timestamp in milliseconds
            attribs: Optional list of attributes to return
        
        Returns:
            List of hourly stats objects for the gateway
        """
        end = end if end is not None else int(time.time() * 1000)
        start = start if start is not None else end - (7 * 24 * 3600 * 1000)
        attribs = ['time', 'mem', 'cpu', 'loadavg_5'] if attribs is None else ['time'] + attribs
        
        params = {
            'attrs': attribs,
            'start': start,
            'end': end,
        }
        
        return self._api_request('stat/report/hourly.gw', params=params)
    
    def stat_daily_gateway(
        self,
        start: Optional[int] = None,
        end: Optional[int] = None,
        attribs: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch daily gateway stats.
        
        Note:
            - Defaults to the past 52 weeks (52*7*24 hours)
            - Requires a UniFi gateway
        
        Args:
            start: Optional Unix timestamp in milliseconds
            end: Optional Unix timestamp in milliseconds
            attribs: Optional list of attributes to return
        
        Returns:
            List of daily stats objects for the gateway
        """
        end = end if end is not None else int((time.time() - (time.time() % 3600)) * 1000)
        start = start if start is not None else end - (52 * 7 * 24 * 3600 * 1000)
        attribs = ['time', 'mem', 'cpu', 'loadavg_5'] if attribs is None else ['time'] + attribs
        
        params = {
            'attrs': attribs,
            'start': start,
            'end': end,
        }
        
        return self._api_request('stat/report/daily.gw', params=params)
        
    def stat_monthly_gateway(
        self,
        start: Optional[int] = None,
        end: Optional[int] = None,
        attribs: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch monthly gateway stats.
        
        Note:
            - Defaults to the past 52 weeks (52*7*24 hours)
            - Requires a UniFi gateway
        
        Args:
            start: Optional Unix timestamp in milliseconds
            end: Optional Unix timestamp in milliseconds
            attribs: Optional list of attributes to return
        
        Returns:
            List of monthly stats objects for the gateway
        """
        end = end if end is not None else int((time.time() - (time.time() % 3600)) * 1000)
        start = start if start is not None else end - (52 * 7 * 24 * 3600 * 1000)
        attribs = ['time', 'mem', 'cpu', 'loadavg_5'] if attribs is None else ['time'] + attribs
        
        params = {
            'attrs': attribs,
            'start': start,
            'end': end,
        }
        
        return self._api_request('stat/report/monthly.gw', params=params)
        
    def stat_speedtest_results(
        self,
        start: Optional[int] = None,
        end: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch speed test results.
        
        Note:
            - Defaults to the past 24 hours
            - Requires a UniFi gateway
        
        Args:
            start: Optional Unix timestamp in milliseconds
            end: Optional Unix timestamp in milliseconds
        
        Returns:
            List of speed test result objects
        """
        end = end if end is not None else int(time.time() * 1000)
        start = start if start is not None else end - (24 * 3600 * 1000)
        
        params = {
            'attrs': ['xput_download', 'xput_upload', 'latency', 'time'],
            'start': start,
            'end': end,
        }
        
        return self._api_request('stat/report/archive.speedtest', params=params)
        
    def stat_ips_events(
        self,
        start: Optional[int] = None,
        end: Optional[int] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch IPS/IDS events.
        
        Note:
            - Defaults to the past 24 hours
            - Requires a UniFi gateway
            - Supported in UniFi controller versions 5.9.X and higher
        
        Args:
            start: Optional Unix timestamp in milliseconds
            end: Optional Unix timestamp in milliseconds
            limit: Optional maximum number of events to return (default: 10000)
        
        Returns:
            List of IPS/IDS event objects
        """
        end = end if end is not None else int(time.time() * 1000)
        start = start if start is not None else end - (24 * 3600 * 1000)
        limit = limit if limit is not None else 10000
        
        params = {
            'start': start,
            'end': end,
            '_limit': limit,
        }
        
        return self._api_request('stat/ips/event', params=params)
        
    def stat_sessions(
        self,
        start: Optional[int] = None,
        end: Optional[int] = None,
        mac: Optional[str] = None,
        type: str = 'all'
    ) -> List[Dict[str, Any]]:
        """
        Fetch login sessions.
        
        Note:
            Defaults to the past 7*24 hours
        
        Args:
            start: Optional Unix timestamp in milliseconds
            end: Optional Unix timestamp in milliseconds
            mac: Optional client MAC address (only when start and end are provided)
            type: Optional client type ('all', 'guest' or 'user')
        
        Returns:
            List of login session objects
        """
        if type not in ['all', 'guest', 'user']:
            raise ValueError("type must be one of: 'all', 'guest', 'user'")
            
        end = end if end is not None else int(time.time())
        start = start if start is not None else end - (7 * 24 * 3600)
        
        params = {
            'type': type,
            'start': start,
            'end': end,
        }
        
        if mac:
            params['mac'] = mac.lower()
            
        return self._api_request('stat/session', params=params)
        
    def stat_sta_sessions_latest(
        self,
        mac: str,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch latest 'n' login sessions for a single client device.
        
        Note:
            Defaults to the past 7*24 hours
        
        Args:
            mac: Client MAC address
            limit: Optional maximum number of sessions to get (default: 5)
        
        Returns:
            List of login session objects
        """
        limit = limit if limit is not None else 5
        
        params = {
            'mac': mac.lower(),
            '_limit': limit,
            '_sort': '-assoc_time',
        }
        
        return self._api_request('stat/session', params=params)
        
    def stat_auths(
        self,
        start: Optional[int] = None,
        end: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch authorizations.
        
        Note:
            Defaults to the past 7*24 hours
        
        Args:
            start: Optional Unix timestamp in milliseconds
            end: Optional Unix timestamp in milliseconds
        
        Returns:
            List of authorization objects
        """
        end = end if end is not None else int(time.time())
        start = start if start is not None else end - (7 * 24 * 3600)
        
        params = {
            'start': start,
            'end': end,
        }
        
        return self._api_request('stat/authorization', params=params)
        
    def stat_allusers(self, historyhours: int = 8760) -> List[Dict[str, Any]]:
        """
        Fetch client devices that connected to the site within given timeframe.
        
        Note:
            historyhours is only used to select clients that were online within that period,
            the returned stats per client are all-time totals, irrespective of the value
            of historyhours
        
        Args:
            historyhours: Optional hours to go back (default: 8760 hours or 1 year)
        
        Returns:
            List of client device objects
        """
        params = {
            'type': 'all',
            'conn': 'all',
            'within': historyhours,
        }
        
        return self._api_request('stat/alluser', params=params)
        
    def list_guests(self, within: int = 8760) -> List[Dict[str, Any]]:
        """
        Fetch guest devices.
        
        Note:
            Defaults to the past 7*24 hours
        
        Args:
            within: Optional time frame in hours to go back (default: 24*365 hours)
        
        Returns:
            List of guest device objects with valid access
        """
        params = {'within': within}
        return self._api_request('stat/guest', params=params)
        
    def list_clients(self, mac: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Fetch online client device(s)
        
        Args:
            mac: Optional MAC address of a specific client to fetch
            
        Returns:
            List of client device objects
        """
        endpoint = f"/api/s/{self.site}/stat/sta"
        if mac:
            endpoint = f"{endpoint}/{mac.lower()}"
            
        return self._api_request(endpoint)

    def list_sites(self) -> List[Dict[str, Any]]:
        """
        List all sites
        
        Returns:
            List of site objects
        """
        endpoint = "/proxy/network/api/self/sites" if self.is_unifi_os else "/api/sites"
        return self._api_request(endpoint)

    def stat_sites(self) -> List[Dict[str, Any]]:
        """
        List site stats
        
        Returns:
            List of site stats
        """
        return self._api_request(f"/api/s/{self.site}/stat/sites")

    def list_devices(self, mac: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all devices or a specific device
        
        Args:
            mac: Optional MAC address of specific device
            
        Returns:
            List of device objects
        """
        endpoint = f"/api/s/{self.site}/stat/device"
        if mac:
            endpoint = f"{endpoint}/{mac.lower()}"
        return self._api_request(endpoint)

    def list_health(self) -> List[Dict[str, Any]]:
        """
        List health metrics
        
        Returns:
            List of health metrics
        """
        return self._api_request(f"/api/s/{self.site}/stat/health")

    def list_dashboard(self) -> List[Dict[str, Any]]:
        """
        List dashboard metrics
        
        Returns:
            List of dashboard metrics
        """
        return self._api_request(f"/api/s/{self.site}/stat/dashboard")

    def list_users(self) -> List[Dict[str, Any]]:
        """
        List all users
        
        Returns:
            List of user objects
        """
        return self._api_request(f"/api/s/{self.site}/list/user")

    def list_alarms(self) -> List[Dict[str, Any]]:
        """
        List all alarms
        
        Returns:
            List of alarm objects
        """
        return self._api_request(f"/api/s/{self.site}/list/alarm")

    def stat_hourly_gateway(self, start: Optional[int] = None, end: Optional[int] = None, attrs: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Get gateway stats by hour
        
        Args:
            start: Start time in milliseconds
            end: End time in milliseconds
            attrs: List of attributes to include
            
        Returns:
            List of gateway stat objects
        """
        params = {}
        if start:
            params['start'] = start
        if end:
            params['end'] = end
        if attrs:
            params['attrs'] = attrs

        return self._api_request(f"/api/s/{self.site}/stat/report/hourly.gw", params=params)

    def authorize_guest(
        self,
        mac: str,
        minutes: int,
        up: Optional[int] = None,
        down: Optional[int] = None,
        bytes_quota: Optional[int] = None,
        ap_mac: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Authorize a guest device
        
        Args:
            mac: MAC address of the guest device
            minutes: Number of minutes for authorization
            up: Upload speed limit in Kbps
            down: Download speed limit in Kbps
            bytes_quota: Quota in MB
            ap_mac: AP MAC address
            
        Returns:
            Response from the authorization request
        """
        data = {
            'cmd': 'authorize-guest',
            'mac': mac.lower(),
            'minutes': minutes
        }

        if up:
            data['up'] = up
        if down:
            data['down'] = down
        if bytes_quota:
            data['bytes'] = bytes_quota
        if ap_mac:
            data['ap_mac'] = ap_mac.lower()

        return self._api_request(f"/api/s/{self.site}/cmd/stamgr", method='POST', data=data)

    def unauthorize_guest(self, mac: str) -> Dict[str, Any]:
        """
        Unauthorize a guest device
        
        Args:
            mac: MAC address of the guest device
            
        Returns:
            Response from the unauthorization request
        """
        data = {
            'cmd': 'unauthorize-guest',
            'mac': mac.lower()
        }

        return self._api_request(f"/api/s/{self.site}/cmd/stamgr", method='POST', data=data)

    def create_site(self, desc: str, name: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new site
        
        Args:
            desc: Site description
            name: Optional site name (if different from desc)
            
        Returns:
            Response from site creation request
        """
        data = {'desc': desc}
        if name:
            data['name'] = name

        return self._api_request("/api/s/default/cmd/sitemgr", method='POST', data=data)

    def delete_site(self, site_id: str) -> Dict[str, Any]:
        """
        Delete a site
        
        Args:
            site_id: ID of the site to delete
            
        Returns:
            Response from site deletion request
        """
        data = {
            'site': site_id,
            'cmd': 'delete-site'
        }

        return self._api_request("/api/s/default/cmd/sitemgr", method='POST', data=data)

    def list_wlanconf(self, wlan_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List WLAN configuration
        
        Args:
            wlan_id: Optional ID of specific WLAN to fetch
            
        Returns:
            List of WLAN configuration objects
        """
        endpoint = f"/api/s/{self.site}/rest/wlanconf"
        if wlan_id:
            endpoint = f"{endpoint}/{wlan_id}"
        return self._api_request(endpoint)

    def set_wlansettings(self, wlan_settings: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update WLAN settings
        
        Args:
            wlan_settings: Dictionary containing WLAN settings to update
            
        Returns:
            Response from update request
        """
        wlan_id = wlan_settings.get('_id')
        if not wlan_id:
            raise ValueError('WLAN settings must include _id field')
            
        endpoint = f"/api/s/{self.site}/rest/wlanconf/{wlan_id}"
        return self._api_request(endpoint, method='PUT', data=wlan_settings)

    def create_voucher(
        self,
        minutes: int,
        count: int = 1,
        quota: int = 1,
        note: Optional[str] = None,
        up: Optional[int] = None,
        down: Optional[int] = None,
        bytes_quota: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Create voucher(s)
        
        Args:
            minutes: Minutes the voucher is valid for
            count: Number of vouchers to create
            quota: Number of devices allowed per voucher
            note: Optional note to add to voucher(s)
            up: Upload speed limit in kbps
            down: Download speed limit in kbps
            bytes_quota: Data transfer quota in MB
            
        Returns:
            Response from voucher creation request
        """
        data = {
            'cmd': 'create-voucher',
            'expire': minutes,
            'n': count,
            'quota': quota
        }
        
        if note:
            data['note'] = note
        if up:
            data['up'] = up
        if down:
            data['down'] = down
        if bytes_quota:
            data['bytes'] = bytes_quota
            
        return self._api_request(f"/api/s/{self.site}/cmd/hotspot", method='POST', data=data)

    def stat_voucher(self, voucher_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get voucher(s) status
        
        Args:
            voucher_id: Optional ID of specific voucher to fetch
            
        Returns:
            List of voucher objects
        """
        endpoint = f"/api/s/{self.site}/stat/voucher"
        if voucher_id:
            endpoint = f"{endpoint}/{voucher_id}"
        return self._api_request(endpoint)

    def disable_device(self, mac: str, disable: bool = True) -> Dict[str, Any]:
        """
        Disable/enable a device
        
        Args:
            mac: MAC address of the device
            disable: True to disable, False to enable
            
        Returns:
            Response from update request
        """
        data = {
            'disabled': disable,
            'mac': mac.lower()
        }
        
        return self._api_request(f"/api/s/{self.site}/rest/device/{mac.lower()}", method='PUT', data=data)

    def set_device_settings(self, mac: str, settings: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update device settings
        
        Args:
            mac: MAC address of the device
            settings: Dictionary containing settings to update
            
        Returns:
            Response from update request
        """
        return self._api_request(f"/api/s/{self.site}/rest/device/{mac.lower()}", method='PUT', data=settings)

    def list_social_auth(self) -> List[Dict[str, Any]]:
        """
        List social auth details
        
        Returns:
            List of social auth objects
        """
        return self._api_request(f"/api/s/{self.site}/stat/social-auth")

    def extend_guest_validity(self, mac: str, minutes: int) -> Dict[str, Any]:
        """
        Extend guest authorization
        
        Args:
            mac: MAC address of the guest device
            minutes: Number of minutes to extend authorization
            
        Returns:
            Response from extension request
        """
        data = {
            'cmd': 'extend',
            'mac': mac.lower(),
            'minutes': minutes
        }
        
        return self._api_request(f"/api/s/{self.site}/cmd/hotspot", method='POST', data=data)

    def reconnect_client(self, mac: str) -> Dict[str, Any]:
        """
        Force client device to reconnect
        
        Args:
            mac: MAC address of the client device
            
        Returns:
            Response from reconnect request
        """
        data = {
            'cmd': 'kick-sta',
            'mac': mac.lower()
        }
        
        return self._api_request(f"/api/s/{self.site}/cmd/stamgr", method='POST', data=data)

    def locate_device(self, mac: str, enable: bool = True) -> Dict[str, Any]:
        """
        Toggle the locate LED function on a UniFi device
        
        Args:
            mac: MAC address of the device
            enable: True to turn on locate LED, False to turn off
            
        Returns:
            Response from locate request
        """
        data = {
            'cmd': 'set-locate',
            'mac': mac.lower()
        }
        
        if not enable:
            data['cmd'] = 'unset-locate'
            
        return self._api_request(f"/api/s/{self.site}/cmd/devmgr", method='POST', data=data)

    def set_auto_update_settings(
        self,
        enable: bool = True,
        hour: int = 4,
        day: str = "sun",
        timezone: str = "America/Los_Angeles"
    ) -> Dict[str, Any]:
        """
        Configure auto update settings for the UniFi controller
        
        Args:
            enable: True to enable auto updates, False to disable
            hour: Hour of the day to perform updates (0-23)
            day: Day of the week to perform updates (sun, mon, tue, wed, thu, fri, sat)
            timezone: Timezone for update schedule
            
        Returns:
            Response from update request
        """
        data = {
            'cmd': 'set-auto-update-settings',
            'enabled': enable,
            'hour': hour,
            'day': day,
            'timezone': timezone
        }
        
        return self._api_request(f"/api/s/{self.site}/cmd/system", method='POST', data=data)

    def __del__(self):
        """Cleanup when the object is destroyed"""
        if self.is_logged_in:
            try:
                self.logout()
            except Exception:
                pass  # Ignore any errors during cleanup
