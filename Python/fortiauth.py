#!/usr/bin/env python3

"""A script to automatically login to fortinet firewall captive portal.

Given a username and password this script automatically monitors the network and logs in to the fortinet captive portal
when needed. It also send keepalive requests periodically to maintain the login.
"""

import getpass
import logging
import re
import requests
import signal
import time
from typing import Tuple, Union

USERNAME = input("Username: ")
PASSWORD = getpass.getpass("Password: ")
ONE_ONE_ONE_ONE = 'http://1.1.1.1/'
ONE_ONE_ONE_ONE_HTTPS = 'https://1.1.1.1/'
RETRY_TIME = 30
KEEPALIVE_TIME = 60
logged_in = False
logout_url = ''


def interrupt_handler(sig, frame):
    """SIGINT handler. Logout user if they are logged in."""
    if logged_in:
        try:
            response = requests.get(logout_url, headers={'User-Agent': 'Mozilla/5.0'})
        except:
            logging.error(f'Error in opening url: {logout_url}.')

        if response.status_code == 200:
            logging.info('Successfully logged out.')
    else:
        logging.info('Exiting.')

    exit()


def state_check() -> Tuple[bool, requests.Response]:
    """Checks whether user is currently logged in or not.

    Returns
    -------
    Tuple[bool, requests.Response]
        Returns a tuple stating whether user is logged in, and the Response object.
    """
    # Keep trying to reach http://1.1.1.1 until status code is 200.
    while True:
        try:
            response = requests.get(ONE_ONE_ONE_ONE, headers={'User-Agent': 'Mozilla/5.0'})
        except requests.exceptions.RequestException:
            logging.error(f'Error in opening url: {ONE_ONE_ONE_ONE}. Retrying ...')
            continue

        if response.status_code == 200:
            break

    # If redirected url is https://1.1.1.1/ then user is probably logged in.
    if response.url == ONE_ONE_ONE_ONE_HTTPS:
        return True, response
    else:
        return False, response


def login(response: requests.Response) -> Tuple[bool, Union[requests.Response, None]]:
    """Try logging in to the network via the captive portal.

    Parameters
    ----------
    response : requests.Response
        Response object for captive portal.

    Returns
    -------
    Tuple[bool, requests.Response | None]
        Tuple with login status and response object (or None is response is not valid).
    """
    global logged_in
    global logout_url

    # Extract base url and magic token.
    url = re.search('https://[a-z:0-9.]*/', response.url)
    if url is None:
        logging.error('Could not find base url via regex match. Exiting.')
        exit()
    url = url[0]
    magic: str = re.search('(name="magic" value=")([a-zA-Z0-9]+)(")', response.text)
    if magic is None:
        logging.error('Could not find magic value via regex match. Exiting.')
        exit()
    magic = magic[2]

    # Prepare data.
    data = {
        'username': USERNAME,
        'password': PASSWORD,
        'magic': magic,
        '4Tredir': '/'
    }

    # Try to log in to the network.
    try:
        response = requests.post(url, headers={'User-Agent': 'Mozilla/5.0'}, data=data)
    except requests.exceptions.RequestException:
        logging.error(f'Error in opening url: {url}.')
        return False, None

    if response.status_code != 200:
        return False, response

    # If 'keepalive' is not in response url, then something went wrong. Likely invalid username/password.
    if 'keepalive' not in response.url:
        logging.error('Invalid username/password. Exiting.')
        exit()

    logging.info(f'Successfully logged in. Keepalive url: {response.url}')

    logged_in = True
    logout_url = response.url.replace('keepalive', 'logout')

    return True, response


def keepalive(url: str) -> None:
    """Send keepalive requests.

    Parameters
    ----------
    url : str
        The keepalive url.
    """
    global logged_in

    # Keep sending keepalive requests every KEEPALIVE_TIME seconds.
    while True:
        try:
            response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        except requests.exceptions.RequestException:
            logging.error(f'Error in opening url: {url}.')
            logged_in = False
            break

        # Ensure that no redirect occurs.
        if response.status_code == 200 and response.url == url:
            logging.info(f'Keeping alive ({KEEPALIVE_TIME} secs) ...')
            time.sleep(KEEPALIVE_TIME)
            continue

        else:
            logging.error('Something went wrong.')
            logged_in = False
            break


def main() -> None:
    """Main function for the script."""
    # Setup logging.
    logging.basicConfig(format='%(asctime)s %(levelname)s: %(message)s', level=logging.INFO)

    # Setup interrupt handler.
    signal.signal(signal.SIGINT, interrupt_handler)

    # Keep running a loop which checks current state, logs in and keeps alive.
    while True:
        logging.info('Checking state ...')
        status, response = state_check()

        # If already logged in, wait for a while and retry.
        if status:
            logging.info(f'Seems to be already logged in. Sleeping for {RETRY_TIME} seconds.')
            time.sleep(RETRY_TIME)
            continue

        # If not logged in, try to log in.
        logging.info(f'Not logged in. Captive portal url: {response.url}')
        status, response = login(response)

        # If log in was unsuccessful retry loop.
        if not status:
            continue

        # Send keepalive requests.
        keepalive(response.url)


if __name__ == '__main__':
    main()
