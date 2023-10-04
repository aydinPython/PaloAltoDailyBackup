import requests
import xml.etree.ElementTree as ET
from datetime import datetime
import smtplib
from email.mime.text import MIMEText

# Firewall details
firewalls = [
    {'hostname': 'paloaltofw1.local', 'username': 'palo', 'password': 'palo'},
    {'hostname': 'paloaltofw2.local', 'username': 'palo', 'password': 'palo'},
]


# Email parameters
sender_email = "sender@mail.com"
receiver_email = "receiver@mail.com"
smtp_server = "MAIL_SERVER_ADDRESS"
smtp_port = 25

def send_email(ip_address):
    subject = "Network Backup Script Error"
    body = f"""
    The backup failed due to a TCP connection or device failure : {ip_address}.
    """
    msg = MIMEText(body)
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.sendmail(sender_email, receiver_email, msg.as_string())
    except Exception as e:
        print(f"Error occurred while sending email: {str(e)}")

for firewall in firewalls:
    hostname = firewall['hostname']
    username = firewall['username']
    password = firewall['password']

    # API endpoint
    url = f'https://{hostname}/api/'

    # API request parameters
    params = {
        'type': 'export',
        'category': 'configuration',
        'key': ''
    }

    try:
        # Get the API key
        keygen_params = {
            'type': 'keygen',
            'user': username,
            'password': password
        }
        response = requests.get(url, params=keygen_params)
        response.raise_for_status()  # Raise exception if the request failed

        xml_response = ET.fromstring(response.content)
        params['key'] = xml_response.find('./result/key').text

        # Get the configuration
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise exception if the request failed

        # Write the configuration to a file
        path = '/home/netadmin/HO-Backup/Palo-Alto/'
        filename = f'{path}{hostname}_{datetime.now().strftime("%Y%m%d")}.xml'
        with open(filename, 'wb') as f:
            f.write(response.content)
            print(f'Backup Succeeded {hostname}')

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        send_email(hostname)
        
    except ET.ParseError as e:
        print(f"Failed to parse XML: {e}")

