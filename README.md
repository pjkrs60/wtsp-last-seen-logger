# Whatsapp Last Seen Logger
## Introduction
Simple python code to monitor the "online" status and log the last seen of a target whatsapp user (who has hidden their last seen) using whatsapp's web interface via selenium.

## Usage
1. First setup the telegram API:
- Create a telegram bot using [Botfather](https://t.me/botfather)
- Get the bot token and input it in the code
- Start a chat and send any message to the bot from the telegram account you wish to recieve the telegram notifications to
- Go to (https://api.telegram.org/bot< BOT-TOKEN >/getUpdates) and fetch the chat-id and input it in the code

2. Set the name of the target contact and username of windows user where chrome is installed

3. Run the program (preferably on a PC which you don't usually use or an RDP/VPS)

4. Login to whatsapp web from a spare whatsapp account running on a spare phone that's on charge
Preferably use/make a whatsapp account on a private phone number; one that your friends/coworkers don't know about because this number will mostly show up as online 24x7

5. That's all. Timestamps will be printed to the console and sent to the given telegram chat whenever the target contact goes online/offline

## Notes
You need to login to whatsapp web only on the first run; no need to login (scan QR code) after that unless you manually log out

This code also notifies and logs whenever the computer or host device get disconnected from the internet

This python script is written preferably for windows; chrome user data directory paths will be different for linux

### Algorithm
__ init __: Opens whatsapp web via selenium and loads chat of target contact
1. Monitors the page's source code for the "Online" keyword
2. As soon as target's online, the time is logged, printed to the console and sent to the given telegram chat
3. Following this when the target goes offline, the (last seen) time is logged, printed to the console and sent to the given telegram chat
4. The code loops forever while clearing the console every 24 hours.

### Telegram Notification
I wanted the last seen time to be available on my phone. As I was too lazy to implement any android push notification stuff, I wrote a simple <code>telegram_send()</code> function which sends a message to a specified telegram chat using the telegram API and deletes the previous message. When this function is called while passing the last seen time as the argument, a notification carrying the last seen appears on the phone (/laptop/pc etc.) and the previous last seen time disappears.

## Legal

This project is in no way affiliated with, authorized, maintained, sponsored or endorsed by Whatsapp or any of its affiliates or subsidiaries. This is an independent project. Use at your own risk.
