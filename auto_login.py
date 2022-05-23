"""auto_login.py
Auto login to CUHK ResNet when required.
"""

import argparse
import time

import requests

from utils import setup_logger, convert_to_seconds


def check_redirect(url: str) -> bool:
    """Access the given URL, and check whether give the redirect meta.
    A redirect meta tells the brower to redirect the page to the login page.
    """
    # Fire up a HTTP GET.
    try:
        r = requests.get(url, timeout=30)
    # If connection error, go to login.
    except ConnectionError:
        return True
    except TimeoutError:
        return True
    else:
        # Define redirect patterns.
        meta_redirect_pattern = "meta http-equiv='refresh'"
        aruba_pattern = "arubalp"
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


def check_connection(args, logger):
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
        else:
            if not check_redirect(args.check_url):
                logger.info(f'Auto login succeed.')
    return
    


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
    parser.add_argument('--run_once', action='store_true',
                        help='If this flag is activated, run check and login once.')
    parser.add_argument('--login_only', action='store_true',
                        help='POST login immediately without testing connection.')

    return parser.parse_args()


def main() -> None:
    """Main function"""
    # Parse arguments.
    args = parse_args()
    # Get current time for log file namming.
    logger = setup_logger()
    # Get interval.
    interval = convert_to_seconds(args.check_interval)
    # Welcome information.
    logger.info(f'CUHK ResNet Auto Login:\n'
                f'  check URL: {args.check_url}\n'
                f'  check interval: {interval} seconds\n'
                f'  username: {args.username}\n'
                f'  password: {args.password}')
    if args.run_once:
        logger.info(f'Check connection once.')
        check_connection(args, logger)
        return 0
    if args.login_only:
        logger.info(f'Login immediately.')
        post_login(args.username, args.password)
        return 0
    while True:
        check_connection(args, interval, logger)
        time.sleep(interval)


if __name__ == '__main__':
    main()
