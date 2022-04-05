"""auto_login.py
Auto login to CUHK ResNet when required.
"""

import argparse
import time
from datetime import datetime

import requests

from utils import setup_logger, convert_to_seconds


def check_redirect(url: str) -> bool:
    """Access the given URL, and check whether give the redirect meta.
    A redirect meta tells the brower to redirect the page to the login page.
    """
    # Define patterns.
    meta_redirect_pattern = "meta http-equiv='refresh'"
    aruba_pattern = "arubalp"
    # Fire up a HTTP GET.
    r = requests.get(url)
    # Check whether contains the pattern.
    if (meta_redirect_pattern in r.text) and (aruba_pattern in r.text):
        return True
    else:
        return False


def post_login(username: str, password: str) -> str:
    """Send HTTP POST to the login URL."""
    url = 'http://securelogin.net.cuhk.edu.hk/cgi-bin/login'
    data = {
        'user': username,
        'password': password,
        'cmd': 'authenticate',
        'Login': 'Log+In'
    }
    # Fire up the HTTP POST.
    r = requests.post(url=url, data=data, allow_redirects=False)
    return r.text


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Auto login CUHK ResNet when required.',
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('username', type=str,
                        help='Your CUHK username. Student: student_id@link.cuhk.edu.hk, staff: alias@cuhk.edu.hk')
    parser.add_argument('password', type=str,
                        help='Your CUHK OnePass password.')
    parser.add_argument('--check_url', type=str, default='http://www.msftconnecttest.com/redirect',
                        help='A URL to check whether a login is needed.')
    parser.add_argument('--check_interval', type=str, default='1m',
                        help='Interval for checking connectivity.')
    parser.add_argument('--log_dir', type=str, default='logs',
                        help='Directory to save logs.')

    return parser.parse_args()


def main() -> None:
    """Main function"""
    # Parse arguments.
    args = parse_args()
    # Get current time for log file namming.
    current_time = datetime.now().strftime('%Y%m%d_%H%M%S')
    logger = setup_logger(work_dir=args.log_dir, logfile_name=f'{current_time}.log')
    # Get interval.
    interval = convert_to_seconds(args.check_interval)
    # Welcome information.
    logger.info(f'CUHK ResNet Auto Login:\n'
                f'  check URL: {args.check_url}\n'
                f'  check interval: {interval} seconds\n'
                f'  username: {args.username}\n'
                f'  password: {args.password}')
    while True:
        if not check_redirect(args.check_url):
            logger.info(f'Connection checked OK.')
        else:
            logger.warning(f'Connection failed. Sleep 30 seconds before login.')
            time.sleep(30)
            logger.warning(f'Try to log you in.')
            try:
                post_login(args.username, args.password)
            except Exception as e:
                logger.error(str(e))
                continue
            if check_redirect(args.check_url):
                logger.info(f'Auto login succeed.')
        time.sleep(interval)


if __name__ == '__main__':
    main()
