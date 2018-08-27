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

# References:
#
# https://developers.google.com/api-client-library/python/guide/aaa_oauth
# https://developers.google.com/api-client-library/python/auth/installed-app

import datetime
import base64
import os
import sys
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
import httplib2
import smtplib

# Over-ride the default SMTP client implementation to capture all debug
# logging. (rather than just printing it to stderr) This allows us to
# dump the log in the event of an error, but otherwise not display it.
class LoggingSMTP(smtplib.SMTP):
    debug_log = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.debug_log = []
    
    def _print_debug(self, *args):
        self.debug_log.append((datetime.datetime.now(), args))

class EmailSender:
    """Convenience class for sending emails to a server, handling XOAUTH2
    authentication."""

    def __init__(self, server, port, user_email):
        self.server = server
        self.port = port
        self.user_email = user_email
        self.log = []

    def encode_oauth2_string(self, access_token):
        auth_str = 'user=%s\1auth=Bearer %s\1\1' % (
            self.user_email, access_token)
        return base64.b64encode(auth_str.encode("UTF-8"))

    def send_email(self, access_token, to_email, subject, body):
        # Build the base64 encoded auth string for passing via smtp
        oauth_string = self.encode_oauth2_string(access_token)
        # Open up the SMTP connection, attempt to use oauth2 authentication
        # via the XOAUTH2 extension.
        conn = LoggingSMTP(self.server, self.port)
        conn.set_debuglevel(True)
        try:
            conn.ehlo('test')
            conn.starttls()
            conn.docmd('AUTH', 'XOAUTH2 ' + oauth_string.decode("UTF-8"))
            msg = "\r\n".join((
                "From: %s" % self.user_email,
                "To: %s" % to_email,
                "Subject: %s" % subject,
                "",
                ""))
            msg += body
            conn.sendmail(self.user_email, to_email, msg)
        except Exception as e:
            print('SMTP connection failed. Log follows:')
            for tm, args in conn.debug_log:
                print(tm, *args)
            raise e
        finally:
            try:
                conn.quit()
            except:
                pass
