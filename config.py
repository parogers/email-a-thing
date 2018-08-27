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
import json

from oauth2client.file import Storage

SETTINGS_JSON = 'settings.json'
APP_FOLDER = 'email-a-thing'

class Settings:
    user_email = None
    smtp_server = None
    smtp_port = None

class Config:

    path = None
    
    def __init__(self, path=None):
        if path:
            self.path = path
        else:
            self.path = self.get_default_path()

        # Make the folder if it doesn't exist
        if not os.path.exists(self.path):
            os.mkdir(self.path)

    def get_default_path(self):
        return os.path.join(
            os.environ['HOME'],
            '.config',
            APP_FOLDER)

    def get_settings_path(self):
        return os.path.join(self.path, SETTINGS_JSON)

    def get_settings(self):
        data = json.load(open(self.get_settings_path()))
        settings = Settings()
        settings.user_email = data['user_email']
        settings.smtp_server = data['smtp_server']
        settings.smtp_port = data['smtp_port']
        return settings

    def put_settings(self, settings):
        data = {
            'user_email' : settings.user_email,
            'smtp_server' : settings.smtp_server,
            'smtp_port' : settings.smtp_port,
        }
        json.dump(data, open(self.get_settings_path(), 'w'))

    def get_secrets_path(self):
        return os.path.join(self.path, 'client_secret.json')

    def put_secrets(self, secrets):
        with open(self.get_secrets_path(), 'w') as file:
            file.write(secrets)

    def get_oauth_storage(self):
        storage_path = os.path.join(self.path, 'creds.storage')
        return Store(storage_path)

    def get_oauth_creds(self):
        storage = self.get_oauth_storage()
        if not os.path.exists(storage._filename):
            raise FileNotFoundError(storage._filename)
        return storage.get()

    def put_oauth_creds(self, creds):
        storage = self.get_oauth_storage()
        storage.put(creds)
