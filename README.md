# mail2talk

# Mail to Nextcloud Talk Script

This script is designed to send messages to Nextcloud Talk from emails sent to Postfix. Emails are redirected by Postfix via aliases (`/etc/aliases`) to this script, which processes them and sends the relevant information to a specified Nextcloud Talk room.

## Features

- **Room Selection**: Send messages to different rooms based on the provided room name.
- **Subject and Body Handling**: Extract and send either the subject, body, or both from the email.
- **Emoji Support**: Add emojis to the message based on the email subject (usefull for tools like Prometheus / Alertmanager)
- **HTML Extraction**: Extract and convert HTML content to plain text for specified rooms.

## Needs

- You need to add a user/password for a dedicated Talk User (Like a Bot user) who can access your different room
- And of course the URL of your Nextcloud instance

## Requirements

- Python 3.x
- Libraries: `requests`, `beautifulsoup4`, `email`
- Access to a Nextcloud Talk instance

Feel free to fit it to your needs !
