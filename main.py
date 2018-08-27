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

import os
import sys
from oauth2client.client import flow_from_clientsecrets, FlowExchangeError

from email_oauth2 import EmailSender
from config import Config, Settings

if __name__ == '__main__':
    def get_value(prompt, default=''):
        if default:
            prompt += ' (' + str(default) + ')'
        prompt += ': '
        value = input(prompt).strip()
        if not value:
            return default
        return value

    cfg = Config()
    try:
        settings = cfg.get_settings()
    except FileNotFoundError:
        # Get the basic server settings
        print('Settings not found under: %s' % cfg.get_settings_path())
        settings = Settings()
        settings.user_email = get_value('Enter the email')
        assert '@' in settings.user_email
        settings.smtp_server = get_value(
            'Enter the SMTP server',
            'smtp.' + settings.user_email.split('@')[1])
        settings.smtp_port = get_value('Enter the SMTP port', 587)

        cfg.put_settings(settings)
        settings = cfg.get_settings()

        # Now get the oauth access creds
        print('Enter the oauth2 secrets as a json string')
        print('(eg visit https://console.developers.google.com)')
        secrets = input('Copy+paste here: ')
        with open(cfg.get_secrets_path(), 'w') as file:
            file.write(secrets)

    try:
        creds = config.get_oauth_creds()
    except FileNotFoundError:
        # Obtain access credentials
        flow = flow_from_clientsecrets(cfg.get_secrets_path())

        print('Visit this URL:')
        print(flow.step1_get_authorize_url())
        print('')
        
        code = input('Enter access code: ')
        creds = flow.step2_exchange(code)
        config.put_oauth_creds(creds)

    access_token = creds.get_access_token().access_token

    to_email = 'peter.rogers@gmail.com'
    subject = 'Hello World'
    body = 'This is just a test'

    print('Sending email...')
    sender = EmailSender(
        settings.smtp_server,
        settings.smtp_port,
        settings.user_email)
    sender.send_email(access_token, to_email, subject, body)
    print('Done')