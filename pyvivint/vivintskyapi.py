"""Module that implements the VivintSkyApi class."""
import aiohttp
import asyncio
import base64
import certifi
import datetime
import json
import logging
import os
import re
import ssl
import time

from http.cookies import SimpleCookie
from typing import Optional
from urllib.parse import urlencode, quote, unquote

from pyvivint.enums import ArmedStates, DoorLockAttributes
from pyvivint.exceptions import (
    VivintSkyApiError,
    VivintSkyApiAuthenticationError,
    VivintSkyApiExpiredTokenError,
    VivintSkyApiMissingTokenError
)

_LOGGER = logging.getLogger(__name__)

VIVINT_AUTH_ENDPOINT = 'https://id.vivint.com'
VIVINT_API_ENDPOINT = 'https://www.vivintsky.com'
USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
BASE62_TABLE = (
    [chr(ord("a") + i) for i in range(26)]
    + [chr(ord("A") + i) for i in range(26)]
    + [chr(ord("0") + i) for i in range(10)]
)


class VivintSkyApi:
    """Class to communicate with the VivintSky API."""

    def __init__(
        self,
        username: str,
        password: str,
        loop: asyncio.events.AbstractEventLoop,
        client_session: Optional[aiohttp.ClientSession] = None,
    ):
        self.__username = username
        self.__password = password
        self.__loop = loop
        self.__client_session = client_session or self.__get_new_client_session()
        self.__has_custom_client_session = client_session is not None

        self.__openid_config: dict = None
        self.__openid_auth_data: dict = None
        self.__auth_user_data: dict = None

    @property
    def id_token(self) -> dict:
        """Return the current id_token."""
        if not self.__openid_auth_data:
            raise VivintSkyApiMissingTokenError('Missing openid auth data')

        return self.__openid_auth_data['id_token'][-1]

    async def connect(self) -> None:
        """Connect to VivintSky Cloud Service."""
        self.__openid_config = await self.__get_openid_config()
        self.__openid_auth_data = await self.__get_vivintsky_session(self.__username, self.__password)

    async def disconnect(self) -> None:
        """Disconnect from VivintSky Cloud Service."""
        if not self.__has_custom_client_session:
            await self.__client_session.close()

    def parse_id_token(self, id_token: str) -> dict:
        """
        Parse out the components of the ID token.
        """

        header_raw, payload_raw, data = [
            base64.urlsafe_b64decode(p + "=" * ((4 - (len(p) % 4)) % 4))
            for p in id_token.split(".")
        ]

        return {
            "header": json.loads(header_raw.decode()),
            "payload": json.loads(payload_raw.decode()),
            "data": base64.b64encode(data).decode(),
        }

    async def get_authuser_data(self) -> dict:
        """
        Get the authuser data

        Poll the Vivint authuser API endpoint resource to gather user-related data including enumeration of the systems
        that user has access to.
        """
        bearer_token = self.__get_bearer_token()
        resp = await self.__client_session.get(
            f'{VIVINT_API_ENDPOINT}/api/authuser',
            headers={
                'Authorization': f'Bearer {bearer_token}',
                'User-Agent': USER_AGENT,
            },
        )
        async with resp:
            return await resp.json(encoding='utf-8')

    async def refresh_token(self) -> None:
        """Refresh the openid token.

        Ping the token-delegate endpoint for a refresh token, geting the token-delegate
        endpoint from the OID configuration.
        """
        nonce = "".join([BASE62_TABLE[i % 62] for i in os.urandom(32)])
        state = "".join([BASE62_TABLE[i % 62] for i in os.urandom(32)])

        # When requesting a new token from the delegate, the following must be true:
        # - The original state and nonce must be in the Cookies header
        # - The new state and nonce must be in the query string
        #  > These don't appear to ever be used.
        # - The PF token supplied in the Cookies header must match that provided back
        #   in the Set-Cookie header from the original response to the auth ping
        #  > That is, not the "short" one, the "long" one.
        #
        # The response satisfies the following:
        # - The body is a JSON document with two keys: id_token, state
        # - The state value is as usual, "replay:%s"
        # - The new nonce to use is in the ID token returned.
        #  > Neither the new state or nonce need to be used anywhere.
        client_id = await self.__get_client_id()
        resp = await self.__client_session.get(
            self.__openid_config['token_delegate_endpoint'],
            params={
                'nonce': nonce,
                'state': f'replay:{state}',
                'response_type': 'id_token',
                'client_id': client_id,
                'redirect_uri': 'https://www.vivintsky.com/app/',
                'scope': 'openid email',
                'pfidpadapterid': 'vivintidp1',
            },
            headers={
                'Cookie': f'oidc_nonce={self.__openid_auth_data["nonce"][-1]}; oauth_state={self.__openid_auth_data["state"][-1]}; PF={self.__openid_auth_data["pf_token"]["long"][-1]}',  # noqa
                'User-Agent': USER_AGENT,
            },
        )
        async with resp:
            if resp.status == 200:
                resp_body = await resp.json()
                token_parts = self.parse_id_token(resp_body['id_token'])
                self.__openid_auth_data["id_token"].append(resp_body['id_token'])

                # It is the last valid value that we care about, because the new ones
                # generated aren't used for anything... oddly enough. So append the one
                # we used to get the new token to the end, so we keep using it.
                self.__openid_auth_data['state'] += [
                    unquote(resp_body['state']).split(":", 1)[1],
                    self.__openid_auth_data['state'][-2],
                ]
                self.__openid_auth_data['nonce'] += [
                    token_parts['payload']['nonce'],
                    self.__openid_auth_data['nonce'][-2],
                ]
                _LOGGER.info('vivint oauth token refreshed')
            else:
                # our session eventually expired. We need to re login
                # Attempt to re-login if there is a username and password
                if self.__username is not None and self.__password is not None:
                    # clear any pre-existing cookies for a fresh start
                    self.__client_session.cookie_jar.clear()
                    new_openid_auth_data = await self.__get_vivintsky_session(self.__username, self.__password)
                    self.__openid_auth_data['id_token'] += new_openid_auth_data['id_token']
                    self.__openid_auth_data['pf_token']['long'] += new_openid_auth_data['pf_token']['long']
                    self.__openid_auth_data['state'] += new_openid_auth_data['state']
                    self.__openid_auth_data['nonce'] += new_openid_auth_data['nonce']
                else:
                    raise VivintSkyApiAuthenticationError(
                        'Unable to refresh token with non-200 error, and no username/password available'
                    )

    async def get_system_data(self, panel_id: int) -> dict:
        """Gets the raw data for a system."""
        bearer_token = self.__get_bearer_token()
        resp = await self.__client_session.get(
            f'{VIVINT_API_ENDPOINT}/api/systems/{panel_id}',
            headers={
                'Authorization': f'Bearer {bearer_token}',
                'User-Agent': USER_AGENT,
            },
            params={'includerules': 'false'},
        )
        async with resp:
            return await resp.json(encoding='utf-8')

    async def set_alarm_state(self, panel_id: int, partition_id: int, state: bool) -> aiohttp.ClientResponse:
        bearer_token = self.__get_bearer_token()
        resp = await self.__client_session.put(
            f'{VIVINT_API_ENDPOINT}/api/{panel_id}/{partition_id}/armedstates',
            headers={
                'Authorization': f'Bearer {bearer_token}',
                'Content-Type': 'application/json;charset=UTF-8',
                'User-Agent': USER_AGENT,
            },
            data=json.dumps(
                {
                    'system': panel_id,
                    'partitionId': partition_id,
                    'armState': state,
                    'forceArm': False,
                }
            ).encode('utf-8'),
        )
        async with resp:
            if resp.status != 200:
                resp_body = await resp.text()
                _LOGGER.error(
                    f'failed to set state {ArmedStates.name(state)}. Code: {resp.status}, body: {resp_body},'
                    f'request url: {resp.request_info}'
                )
                raise VivintSkyApiError(
                    f'failed to set alarm status {ArmedStates.name(state)} for panel {self.id}'
                )

    async def set_lock_state(self, panel_id: int, partition_id: int, device_id: int, locked: bool) -> None:
        """Lock/Unlock door lock."""
        bearer_token = self.__get_bearer_token()
        resp = await self.__client_session.put(
            f'{VIVINT_API_ENDPOINT}/api/{panel_id}/{partition_id}/locks/{device_id}',
            headers={
                'Content-Type': 'application/json;charset=utf-8',
                'Authorization': f'Bearer {bearer_token}',
            },
            data=json.dumps({DoorLockAttributes.State: locked, DoorLockAttributes.Id: device_id}).encode('utf-8'),
        )
        async with resp:
            if resp.status != 200:
                _LOGGER.info(f'failed to set status locked: {locked} for lock: {device_id} @ {panel_id}:{partition_id}')
                raise VivintSkyApiError(f'failed to update lock status')

    async def request_camera_thumbnail(self, panel_id: int, partition_id: int, device_id: int) -> None:
        bearer_token = self.__get_bearer_token()
        resp = await self.__client_session.get(
            f'{VIVINT_API_ENDPOINT}/api/{panel_id}/{partition_id}/{device_id}/request-camera-thumbnail',
            headers={
                'Authorization': f'Bearer {bearer_token}',
                'User-Agent': USER_AGENT,
            },
        )
        async with resp:
            if resp.status < 200 or resp.status > 299:
                _LOGGER.info(f'failed to request thumbnail for camera id {self.id}. Error code: {resp.status}')

    async def get_camera_thumbnail_url(self, panel_id: int, partition_id: int, device_id: int,
                                       thumbnail_timestamp: datetime.datetime) -> str:
        bearer_token = self.__get_bearer_token()
        resp = await self.__client_session.get(
            f'{VIVINT_API_ENDPOINT}/api/{panel_id}/{partition_id}/{device_id}/camera-thumbnail',
            params={'time': thumbnail_timestamp},
            headers={
                'Authorization': f'Bearer {bearer_token}',
                'User-Agent': USER_AGENT,
            },
            allow_redirects=False,
        )

        async with resp:
            if resp.status != 302:
                _LOGGER.info(f'failed to request thumbnail for camera id {self.id}. Status code: {resp.status}')
                return

            return resp.headers.get('Location')

    def __get_new_client_session(self) -> aiohttp.ClientSession:
        """Create a new aiohttp.ClientSession object."""
        ssl_context = ssl.create_default_context(
            purpose=ssl.Purpose.SERVER_AUTH, cafile=certifi.where()
        )
        connector = aiohttp.TCPConnector(
            loop=self.__loop, enable_cleanup_closed=True, ssl=ssl_context
        )

        return aiohttp.ClientSession(
            loop=self.__loop,
            connector=connector
        )

    async def __get_openid_config(self) -> dict:
        """Fetch the OpenID Connect configuration data from the VivintSky webservice."""
        resp = await self.__client_session.get(
            f'{VIVINT_API_ENDPOINT}/api/openid-configuration',
            headers={'User-Agent': USER_AGENT}
        )
        async with resp:
            return await resp.json(encoding='utf-8') if resp.status == 200 else None

    async def __get_client_id(self) -> str:
        """Fetch the client_id from the Vivint's authuser service."""
        # Fetch https://vivintsky.com/api/authuser and check the WWW-Authenticate header which has the client_id baked
        # in
        resp = await self.__client_session.get(
            f'{VIVINT_API_ENDPOINT}/api/authuser', headers={'User-Agent': USER_AGENT}
        )

        async with resp:
            if resp.status != 401:
                raise VivintSkyApiAuthenticationError(
                    f'Attempt to fetch authuser resulted in unexpected response code {resp.status}'
                )
            # noqa  Bearer scope="openid email",redirect_uri="https://www.vivintsky.com/api/oauth-redirect/[UUID]",realm="vivintsy",response_type="code",client_id="[UUID]"
            match = re.search(
                r'client_id="([0-9a-f]*)"', resp.headers['WWW-Authenticate']
            )
            if match is None:
                raise VivintSkyApiAuthenticationError(
                    'Unable to find client id within the response from https://vivintsky.com/api/authuser.'
                )

            client_id = match.group(1)

            return client_id

    async def __get_vivintsky_session(self, username: str, password: str) -> dict:
        """Login into the Vivint Sky platform with the given username and password.

        Returns an object that includes the appropriate OpenID components.
        """
        # As per the app.js, this is just random garbage
        nonce = "".join([BASE62_TABLE[i % 62] for i in os.urandom(32)])
        state = "".join([BASE62_TABLE[i % 62] for i in os.urandom(32)])

        client_id = await self.__get_client_id()

        oauth_data = urlencode(
            {
                'nonce': nonce,
                'state': f'replay:{state}',
                'response_type': 'id_token',
                'client_id': client_id,
                'redirect_uri': f'{VIVINT_API_ENDPOINT}/app/',
                'scope': 'openid email',
                'pfidpadapterid': 'vivintidp1',
            },
            quote_via=quote,
        )

        login_form_resp = await self.__client_session.get(
            f'{VIVINT_AUTH_ENDPOINT}/as/authorization.oauth2?{oauth_data}',
            headers={
                'Referer': f'{VIVINT_AUTH_ENDPOINT}/app/',
                'User-Agent': USER_AGENT,
            },
            allow_redirects=False,
        )
        async with login_form_resp:
            if login_form_resp.status == 302:
                # If we're being redirected it means we're already logged in and the PF token is in the session cokie.
                # We can get the other oauth data from the Location header
                location_hdr = login_form_resp.headers.get("Location", None)

                for cookie in self.__websession.cookie_jar:
                    if cookie.key == 'PF' and cookie['domain'] == 'id.vivint.com':
                        pf_token_long = cookie.value
                        break

                if pf_token_long is None:
                    raise VivintSkyApiAuthenticationError('Unable to get PF token from existing cookie')

            else:
                if login_form_resp.headers.get('Set-Cookie', None) is None:
                    raise VivintSkyApiAuthenticationError(
                        'Unable to get Set-Cookie/Cookie header from response'
                    )

                login_form_return_cookies = SimpleCookie(
                    login_form_resp.headers['Set-Cookie']
                )

                pf_token = login_form_return_cookies['PF'].value

                if pf_token is None:
                    raise VivintSkyApiAuthenticationError(
                        'Unable to get PF token from Set-Cookie/Cookie header'
                    )

                match = re.search(
                    r'"/as/([^/]*)/resume/as/authorization.ping"',
                    await login_form_resp.text(),
                )

                if match is None:
                    raise VivintSkyApiAuthenticationError('Unable to find api ID from login form HTML')

                api_id = match.group(1)

                login_url = (
                    f'{VIVINT_AUTH_ENDPOINT}/as/{api_id}/resume/as/authorization.ping'
                )

                # NOTABLE NOTE
                #
                # There's a weird thing with the Vivint API here on this call, where if there are nonce and state values
                # in the cookies and the query string, the cookies take precedence. This is odd since there's a weird
                # behaviour with their web JavaScript code that will provide both, with the code inheriting the cookies
                # from somewhere as well as generating its own values for the query string.
                #
                # The webapp will use the generated values (supplied in the query string) for further API calls, despite
                # being unnecessary given the bearer token is provided. But thankfully the correct values, being kept in
                # the tokens, are still used for all token refreshes to the delegate endpoint.
                login_resp = await self.__client_session.post(
                    login_url,
                    headers={
                        'Referrer': f'{VIVINT_AUTH_ENDPOINT}/app/',
                        'User-Agent': USER_AGENT,
                        'Accept': '*/*',
                        'Accept-Encoding': 'gzip, deflate',
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'Cookie': f'oauth_state={state}; oidc_nonce={nonce}; PF={pf_token};',
                    },
                    data=urlencode(
                        {'pf.username': username, 'pf.pass': password}
                    ).encode('utf-8'),
                    allow_redirects=False,
                )
                async with login_resp:
                    login_resp_return_cookies = SimpleCookie(
                        login_resp.headers['Set-Cookie']
                    )

                    pf_token_long = login_resp_return_cookies['PF'].value

                    if pf_token_long is None:
                        raise VivintSkyApiAuthenticationError('Unable to get PF token from Set-Cookie header')

                    location_hdr = login_resp.headers.get('Location', None)

            if location_hdr is None:
                raise VivintSkyApiAuthenticationError(
                    'Unable to retrieve Location header from login response'
                )

            location_params = dict(
                [
                    kv.split('=', 1)
                    for kv in re.search(r'/#(.*)$', location_hdr)
                    .group(0)[2:]
                    .split('&')
                ]
            )

            if 'id_token' not in location_params:
                raise VivintSkyApiAuthenticationError(
                    'id_token not provided in Location header of login attempt'
                )

            if 'state' not in location_params:
                raise VivintSkyApiAuthenticationError(
                    'New state value not present in Location header of login attempt'
                )

            id_token_parts = self.parse_id_token(location_params['id_token'])

            return {
                'nonce': [nonce, id_token_parts['payload']['nonce']],
                'state': [state, unquote(location_params['state']).split(':', 1)[1]],
                'pf_token': {
                    'long': [pf_token_long]
                },
                'id_token': [location_params['id_token']]
            }

    def __get_bearer_token(self) -> dict:
        """
        Return a token suitable for inclusion into an Authorization header as
        a bearer token, refreshing the existing one if necessary.
        """
        id_token = self.__openid_auth_data["id_token"][-1]
        parsed_id_token = self.parse_id_token(id_token)
        if time.time() > parsed_id_token["payload"]["exp"]:
            raise VivintSkyApiExpiredTokenError()

        return id_token
