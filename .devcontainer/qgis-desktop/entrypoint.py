"""Entrypoint script for the QGIS Desktop docker image

This script will perform the following tasks:

- Create a new user with credentials supplied as env or secrets
- Start the `xrdp` process as a daemon
- Execute the `xrdp-sesman` process in the foreground

"""

import argparse
import crypt
import enum
import logging
import os
import shlex
import subprocess
import sys
import typing
from pathlib import Path

logger = logging.getLogger(__name__)


@enum.unique
class SecretKeys(enum.Enum):
    RDP_USERNAME = enum.auto()
    RDP_PASSWORD = enum.auto()

def plugin_link(username, link_name):
    try:
        os.makedirs('/home/gisuser/.local/share/QGIS/QGIS3/profiles/default/python/plugins', True)
    except:
        pass
    
    completed_process = subprocess.run(
        shlex.split(
            f'chown {username}:{username} -R /home/{username}/.local/share/QGIS'
        )
    )
    completed_process.check_returncode()

    try:
        os.symlink('/workspace', f'/home/gisuser/.local/share/QGIS/QGIS3/profiles/default/python/plugins/{link_name}')
    except:
        pass
    
    completed_process = subprocess.run(
        shlex.split(
            f'chown {username}:{username} /home/{username}/.local/share/QGIS/QGIS3/profiles/default/python/plugins/{link_name}'
        )
    )
    completed_process.check_returncode()

def start_xrdp():
    completed_xrdp_process = subprocess.run(shlex.split('/usr/sbin/xrdp'))
    completed_xrdp_process.check_returncode()
    logger.info('About to exec xrdp-sesman in the foreground...')
    sys.stdout.flush()
    os.execlp('xrdp-sesman', 'xrdp-sesman', '--nodaemon')


def create_user(username: str, password: str):
    encrypted_password = crypt.crypt(password)
    completed_process = subprocess.run(
        shlex.split(
            f'useradd --create-home --shell /bin/bash --uid 1000 --user-group '
            f'--password {encrypted_password} '
            f'{username}'
        )
    )
    # completed_process.check_returncode()


def get_secrets() -> typing.Dict[SecretKeys, str]:
    result = {}
    for name, member in SecretKeys.__members__.items():
        secret_path = Path(f'/run/{name}')
        try:
            value = secret_path.read_text().strip()
        except FileNotFoundError:
            value = None
        env_value = os.getenv(name, value)
        if env_value is None:
            raise RuntimeError(f'Specify a value for {name}')
        else:
            result[member] = os.getenv(name, value)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', action='store_true')
    args = parser.parse_args()
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO)
    secrets = get_secrets()
    logger.debug(f'secrets: {secrets}')
    create_user(
        secrets[SecretKeys.RDP_USERNAME], secrets[SecretKeys.RDP_PASSWORD])
    plugin_link(secrets[SecretKeys.RDP_USERNAME], 'inasafe')
    start_xrdp()