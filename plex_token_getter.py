import requests, uuid
import xml.etree.ElementTree as ET

class PlexTokenGetter:
    def __init__(self, plex_email: str, plex_password: str):
        self.plex_email = plex_email
        self.plex_password = plex_password
        self.client_identifier = None
        self.plex_client_identifier = None
        self.plex_token = None
        self.session = self.plex_login()

    def plex_login(self):
        request_session = requests.Session()
        login_url = "https://clients.plex.tv/api/v2/users/signin"
        self.client_identifier = str(uuid.uuid4())

        headers = {
            "authority": "clients.plex.tv",
            "origin": "https://app.plex.tv",
            "referer": "https://app.plex.tv/",
            "accept": "application/json",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "en-US,en;q=0.9,de;q=0.8",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "X-Plex-Product": "Plex SSO",
            "X-Plex-Client-Identifier": self.client_identifier
        }

        data = f"login={self.plex_email}&password={self.plex_password}&rememberMe=false"

        response = request_session.post(login_url, headers=headers, data=data)
        if response.status_code == 200 or response.status_code == 201:
            response_email = response.json().get("email")
            if response_email != self.plex_email:
                raise Exception("Login failed, email does not match.")
            return request_session
        else:
            response.raise_for_status()
            return None

    def return_plex_home(self):
        url = "https://www.plex.tv/"
        cookies = self.session.cookies.get_dict()
        headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "en-US,en;q=0.5",
            "content-type": "application/json",
            "cookie": "; ".join([f"{key}={value}" for key, value in cookies.items()]),
            "Host": "plex.tv",
        }

        # Only follow the first redirect to simulate browser login flow
        response = self.session.get(url, headers=headers, allow_redirects=False)
        if response.is_redirect or response.status_code in (301, 302, 303, 307, 308):
            return
        elif response.status_code == 200 or response.status_code == 304:
            return
        else:
            if response.status_code == 401:
                raise Exception("Please Sign In")
            response.raise_for_status()

    def get_device_list(self):
        if not self.session:
            raise Exception("Login failed, session is None.")
        cookies = self.session.cookies.get_dict()
        url = "https://plex.tv/devices.xml"
        headers = {
            "accept": "*/*",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "en-US,en;q=0.9,de;q=0.8",
            "content-type": "application/json",
            "cookie": "; ".join([f"{key}={value}" for key, value in cookies.items()]),
            "Host": "plex.tv",
        }
        response = self.session.get(url, headers=headers)
        if response.status_code == 200 or response.status_code == 304:
            return ET.fromstring(response.text)
        else:
            if response.status_code == 401:
                raise Exception("Please Sign In")
            response.raise_for_status()
            return None

    def plex_set_config_settings(self, plex_token: str, plex_client_identifier: str):
        import os, sys
        current_execution_path = os.path.dirname(os.path.abspath(sys.executable if hasattr(sys, 'frozen') else __file__))
        config_path = os.path.join(current_execution_path, 'plex_config.ini')
        import configparser
        config = configparser.ConfigParser()
        if os.path.exists(config_path):
            config.read(config_path)
            config['Plex'] = {
                'plex_token': plex_token,
                'plex_client_identifier': plex_client_identifier
            }
            with open(config_path, 'w') as configfile:
                config.write(configfile)

    def device_list(self):
        if not self.session:
            raise Exception("Login failed, session is None.")
        self.return_plex_home()
        media_container = self.get_device_list()
        device_json = {}
        devices = media_container.findall("Device")
        for i, device in enumerate(devices, 1):
            device_name = device.get("name")
            device_product = device.get("product")
            device_platform = device.get("device") if device.get("device") != "" else device.get("platform")
            device_json[i] = {
                "name": device_name,
                "product": device_product,
                "platform": device_platform,
                "clientIdentifier": device.get("clientIdentifier"),
                "plex_token": device.get("token")
            }
            print(f"{i}.\tDevice Name: {device_name:<20}\tProduct/Device: {device_product}/{device_platform}")
        choice = input("Select a device by number to get the Plex token or type 'exit' to quit: ")
        if choice.lower() == 'exit' or choice.lower() == 'q':
            print("Exiting...")
            return
        try:
            choice = int(choice)
            if choice in device_json:
                self.plex_token = device_json[choice-1]["plex_token"]
                self.plex_client_identifier = device_json[choice-1]["clientIdentifier"]
                print(f"Plex Token: {self.plex_token}")
                print(f"Plex Client Identifier: {self.plex_client_identifier}")
                self.plex_set_config_settings(self.plex_token, self.plex_client_identifier)
            else:
                print("Invalid choice, please try again.")
        except ValueError:
            print("Invalid input, please enter a number or 'exit' to quit.")
    
def password_check(password: str) -> bool:
    if not password:
        return False
    if len(password) < 6 or len(password) > 100:
        return False
    if " " in password:
        return False
    if not any(char.isdigit() for char in password):
        return False
    if not any(char.isalpha() for char in password):
        return False
    if not any(char in "!@#$%^&*()-_=+[]{}|;:'\",.<>?/" for char in password):
        return False
    if not any(char.isupper() for char in password):
        return False
    if not any(char.islower() for char in password):
        return False
    return True

def email_check(email: str) -> bool:
    if not email:
        return False
    if not email or "@" not in email or "." not in email.split("@")[-1]:
        return False
    if len(email) < 5:
        return False
    return True

if __name__ == "__main__":
    plex_email = input("Enter your Plex email: ")
    if not email_check(plex_email):
        raise ValueError("Invalid Plex email format.")
    plex_password = input("Enter your Plex password: ")
    if password_check(plex_password) is False:
        raise ValueError("Invalid Plex password. It must be 6-100 characters long, contain at least one digit, one letter, one special character, one uppercase letter, and one lowercase letter.")

    plex_token_getter = PlexTokenGetter(plex_email, plex_password)
    plex_token_getter.device_list()