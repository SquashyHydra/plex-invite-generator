import requests, configparser, os, sys

class PlexLinkGenerator:
    def __init__(self):
        self.config = configparser.ConfigParser()
        current_execution_path = os.path.dirname(os.path.abspath(sys.executable if hasattr(sys, 'frozen') else __file__))
        self.config_path = os.path.join(current_execution_path, 'plex_config.ini')
        self.config.read(self.config_path)

    def create_config(self):
        self.config['Plex'] = {
            'plex_token': '',
            'plex_client_identifier': ''
        }
        with open('plex_config.ini', 'w') as configfile:
            self.config.write(configfile)

    def get_config(self):
        if 'Plex' in self.config and 'plex_token' in self.config['Plex'] and 'plex_client_identifier' in self.config['Plex']:
            if not self.config['Plex']['plex_token'] or not self.config['Plex']['plex_client_identifier']:
                raise ValueError("Plex token or client identifier is missing in the config file.")
            return self.config['Plex']['plex_token'], self.config['Plex']['plex_client_identifier']
        else:
            if not os.path.exists(self.config_path):
                self.create_config()
            raise ValueError("Plex token or client identifier is missing in the config file.")
    
    @staticmethod
    def get_invite_link(plex_token, plex_client_identifier) -> str | None:
        url = "https://community.plex.tv/api"

        headers = {
            "accept": "*/*",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "en-US,en;q=0.9,de;q=0.8",
            "content-type": "application/json",
            "x-plex-client-identifier": plex_client_identifier,
            "x-plex-platform": "Web App",
            "x-plex-product": "Plex Web",
            "x-plex-token": plex_token,
            "x-plex-version": "4.147.1"
        }

        payload = {
            "query": "\n    mutation generateInviteUrl {\n  generateInviteURL\n}\n    ",
            "operationName": "generateInviteUrl"
        }

        response = requests.post(url, json=payload, headers=headers)

        status_code = response.status_code

        if status_code == 200:
            result = response.json()
            invite_link = result.get("data", {}).get("generateInviteURL")
            return invite_link
        else:
            response.raise_for_status()
            return None

    def generate_invite_link(self) -> str | None:
        plex_token, plex_client_identifier = self.get_config()
        return self.get_invite_link(plex_token, plex_client_identifier)
    
if __name__ == "__main__":
    generator = PlexLinkGenerator()
    invite_link = generator.generate_invite_link()
    print(f"Generated invite link: {invite_link}")