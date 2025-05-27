#!/usr/bin/env python3
# Script to send messages on Nextcloud Talk from emails sent to Postfix / These emails are redirected via aliases (/etc/aliases) to this script

import subprocess
import requests
import json
import sys
import argparse
from bs4 import BeautifulSoup
from email import policy
from email import message_from_string

# Dictionary of available rooms with their identifiers
available_rooms = {
    "room1": "roomtoken1",
    "room2": "roomtoken2",
    "room3": "roomtoken3"
}

# List of rooms for which we only want the email subject
subject_only = ["room1"]

# List of rooms for which we only want the email body
body_only = ["room2"]

# List of rooms that require adding an emoji in the subject
emoji_add = ["room3"]

# List of rooms that require HTML extraction
html_body = ["room2", "room3"]

def copier_email_stdin(fichier_sortie):
    try:
        # Read the content from standard input
        contenu = sys.stdin.read()

        # Write the content to the output file
        with open(fichier_sortie, 'w', encoding='utf-8') as f_out:
            f_out.write(contenu)

        print(f"Content successfully written to {fichier_sortie}.")

    except Exception as e:
        print(f"An error occurred: {e}")

def extract_email_body(email_content):
    msg = message_from_string(email_content, policy=policy.default)

    if msg.is_multipart():
        for part in msg.iter_parts():
            charset = part.get_content_charset()
            if part.get_content_type() == "text/plain":
                return part.get_payload(decode=True).decode(charset if charset else 'utf-8', errors='replace')
            elif part.get_content_type() == "text/html":
                # Convert HTML to plain text
                soup = BeautifulSoup(part.get_payload(decode=True).decode(charset if charset else 'utf-8', errors='replace'), 'html.parser')
                return soup.get_text(separator="\n", strip=True)
    else:
        charset = msg.get_content_charset()
        return msg.get_payload(decode=True).decode(charset if charset else 'utf-8', errors='replace')

# Command line argument configuration
parser = argparse.ArgumentParser(description="Send a message to a specified room.")
parser.add_argument('room_name', type=str, help=f'The name of the room to use. Available choices: {", ".join(available_rooms.keys())}')
args = parser.parse_args()

# Check if the specified room name is in the dictionary of available rooms
if args.room_name not in available_rooms:
    print(f"Error: The room name '{args.room_name}' is not valid. Available choices: {', '.join(available_rooms.keys())}")
    sys.exit(1)

# Define the log file path based on the room name
log = f"/tmp/{args.room_name}_root2talk.log"

# Example usage
copier_email_stdin(log)

with open(log, 'r') as f:
    mail = f.read()

subject = subprocess.check_output(['formail', '-x', 'Subject'], input=mail, text=True)

# Extract the message body based on the room
if args.room_name in html_body:
    body = extract_email_body(mail)
else:
    body = subprocess.check_output(['sed', '-e', '1,/^$/ d'], input=mail, text=True)

# Get the room ID from the name
room_id = available_rooms[args.room_name]

url_template = f"https://nextcloud.example.com/ocs/v2.php/apps/spreed/api/v1/chat/{room_id}"
headers = {
    'accept': 'application/json, text/plain, */*',
    'cache-control': 'no-cache',
    'content-type': 'application/json',
    'OCS-APIRequest': 'true'
}
# User / Password to use to connect to Talk
auth = ('USER', 'PASSWORD')

# Initialize the message
message = "#"

# Add an emoji after the # if necessary
if args.room_name in emoji_add:
    if "FIRING" in subject:
        message += " 🚨"
    elif "RESOLVED" in subject:
        message += " ✅"

# Add the subject
if args.room_name not in body_only:
    message += f" {subject}"

# Add the message body if necessary
if args.room_name not in subject_only:
    message += f"\n{body}"

# Create the JSON payload
payload = json.dumps({"message": message})

response = requests.post(url_template, headers=headers, auth=auth, data=payload)
print(f"Response for the room {args.room_name}: {response.text}")
