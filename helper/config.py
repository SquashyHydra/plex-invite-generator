import configparser, os, sys

class ConfigFile():
    def __init__(self):
        self.config = configparser.ConfigParser()
        current_execution_path = os.path.dirname(os.path.abspath(sys.executable if hasattr(sys, 'frozen') else __file__))
        current_execution_path = current_execution_path if os.path.basename(current_execution_path) != 'helper' else os.path.dirname(current_execution_path)
        self.config_path = os.path.join(current_execution_path, 'plex_config.ini')
        self.config.read(self.config_path)

    def create_config(self):
        self.config['Plex_Bundled'] = {
            'plex_token': '',
            'plex_client_identifier': ''
        }
        self.config['Plex_Standalone'] = {
            'plex_token': '',
            'plex_client_identifier': ''
        }
        with open(self.config_path, 'w') as configfile:
            self.config.write(configfile)

    def get_bundled_config(self):
        if 'Plex_Bundled' in self.config and 'plex_token' in self.config['Plex_Bundled'] and 'plex_client_identifier' in self.config['Plex_Bundled']:
            if not self.config['Plex_Bundled']['plex_token'] or not self.config['Plex_Bundled']['plex_client_identifier']:
                raise ValueError("Plex token or client identifier is missing in the config file.")
            return self.config['Plex_Bundled']['plex_token'], self.config['Plex_Bundled']['plex_client_identifier']
        else:
            if not os.path.exists(self.config_path):
                self.create_config()
            raise ValueError("Plex token or client identifier is missing in the config file.")

    def get_standalone_config(self):
        if 'Plex_Standalone' in self.config and 'plex_token' in self.config['Plex_Standalone'] and 'plex_client_identifier' in self.config['Plex_Standalone']:
            if not self.config['Plex_Standalone']['plex_token'] or not self.config['Plex_Standalone']['plex_client_identifier']:
                raise ValueError("Plex token or client identifier is missing in the config file.")
            return self.config['Plex_Standalone']['plex_token'], self.config['Plex_Standalone']['plex_client_identifier']
        else:
            if not os.path.exists(self.config_path):
                self.create_config()
            raise ValueError("Plex token or client identifier is missing in the config file.")
        
    def set_bundled_config(self, plex_token: str, plex_client_identifier: str):
        if not os.path.exists(self.config_path):
            self.create_config()
        self.config['Plex_Bundled']['plex_token'] = plex_token
        self.config['Plex_Bundled']['plex_client_identifier'] = plex_client_identifier
        with open(self.config_path, 'w') as configfile:
            self.config.write(configfile)

    def set_standalone_config(self, plex_token: str, plex_client_identifier: str):
        if not os.path.exists(self.config_path):
            self.create_config()
        self.config['Plex_Standalone']['plex_token'] = plex_token
        self.config['Plex_Standalone']['plex_client_identifier'] = plex_client_identifier
        with open(self.config_path, 'w') as configfile:
            self.config.write(configfile)
