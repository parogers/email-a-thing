#!/usr/bin/env python3
#
# email-a-thing -- Send email via SMTP using oauth2 authentication
# Copyright (C) 2018  Peter Rogers
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import argparse
import os
import sys
from oauth2client.client import flow_from_clientsecrets, FlowExchangeError

from email_oauth2 import EmailSender
from config import Config, Settings

REDIRECT_URI = 'urn:ietf:wg:oauth:2.0:oob'
OAUTH_SCOPE = 'https://mail.google.com/'

def prompt_value(prompt, default=''):
    if default:
        prompt += ' (' + str(default) + ')'
    prompt += ': '
    value = input(prompt).strip()
    if not value:
        return default
    return value

def prompt_for_settings():
    settings = Settings()
    settings.user_email = prompt_value('Enter the email')
    assert '@' in settings.user_email
    settings.smtp_server = prompt_value(
        'Enter the SMTP server',
        'smtp.' + settings.user_email.split('@')[1])
    settings.smtp_port = prompt_value('Enter the SMTP port', 587)
    return settings

def prompt_for_secrets():
    print('Enter the oauth2 secrets as a json string')
    print('(eg visit https://console.developers.google.com)')
    return input('Copy+paste here: ')

########
# Main #
########

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('recipient', help='Email recipient')
    parser.add_argument('subject', help='Email subject line')
    parser.add_argument('--body', help='Email body (leave off option to read from stdin)', default=None)
    parser.add_argument('--test', help='Test program settings, but don\'t send anything')

    if '--test' in sys.argv: # TODO - this is not great
        args = None
    else:
        args = parser.parse_args(sys.argv[1:])

    if args and args.body == None:
        args.body = sys.stdin.read()

    cfg = Config()
    try:
        settings = cfg.get_settings()
    except FileNotFoundError:
        # Get the basic server settings
        print('Settings not found under: %s' % cfg.get_settings_path())
        settings = prompt_for_settings()
        cfg.put_settings(settings)
        # Now get the oauth access creds
        secrets = prompt_for_secrets()
        cfg.put_secrets(secrets)

    try:
        creds = cfg.get_oauth_creds()
    except FileNotFoundError:
        # Obtain access credentials
        flow = flow_from_clientsecrets(
            cfg.get_secrets_path(),
            scope=OAUTH_SCOPE,
            redirect_uri=REDIRECT_URI)

        print('Visit this URL:')
        print(flow.step1_get_authorize_url())
        print('')

        code = input('Enter access code: ')
        creds = flow.step2_exchange(code)
        cfg.put_oauth_creds(creds)

    if not args:
        # Just testing the settings
        sys.exit()

    access_token = creds.get_access_token().access_token

    print('Sending email...')
    sender = EmailSender(
        settings.smtp_server,
        settings.smtp_port,
        settings.user_email)
    sender.send_email(
        access_token,
        args.recipient,
        args.subject,
        args.body)
    print('Done')
