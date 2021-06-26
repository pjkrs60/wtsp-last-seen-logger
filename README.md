# Whatsapp Last Seen Logger
## Introduction
Simple python code to monitor the "online" status and log the last seen of a target whatsapp user (who has hidden their last seen) using whatsapp's web interface via selenium.

## Usage
1. Setup the telegram API:
- Create a telegram bot using [Botfather](https://t.me/botfather) and get the bot token
- Open a chat with the bot from the telegram account you wish to recieve the telegram notifications to and click "Start"
- Fetch the chat-id from (https://api.telegram.org/bot-----BOT-TOKEN-----/getUpdates) [Guide](https://sean-bradley.medium.com/get-telegram-chat-id-80b575520659)

2. Input the tokens fetched above near the end of code and run the program preferably on a Linux PC/RDP/VPS which you don't usually use like a Raspberry Pi. If you only have a windows PC, use the windows version preferably with Spyder IDE

3. Login to the opened whatsapp web preferably from a spare whatsapp account (as this number might show up to be online 24x7) running on a spare phone that will be on charge and have internet connectivity 24x7

4. That's all. Now as and when the target contact uses whatsapp, timestamps will be printed to the console, logged to the log file and sent to the given telegram chat whenever the target contact goes online/offline

## Notes
You need to login to whatsapp web only on the first run; no need to login (scan QR code) after that unless you manually log out

This code also notifies and logs whenever the computer or host device get disconnected from the internet.

Another reason to use the linux version: In my case, when the phone lost internet access, the yellow coloured "phone not connected" popups appeared only on windows (and the online status stopped appearing) and not on linux, on linux the whatsapp window behaved normally just like when the phone was connected to the internet.

### Algorithm
__ init __: Opens whatsapp web via selenium and loads chat of target contact
1. Monitors the page's source code for the "Online" keyword
2. As soon as target's online, the time is logged, printed to the console and sent to the given telegram chat
3. Following this when the target goes offline, the (last seen) time is logged, printed to the console and sent to the given telegram chat
4. The code loops forever while clearing the console every 24 hours as well as logging error messages and restarting incase of errors

### Telegram Notification
Initially I wanted the last seen time to be available on my phone but since I was too lazy to implement any android push notification stuff, I wrote a simple <code>telegram_send()</code> function which sends a message to a specified telegram chat using the telegram API and deletes the previous message. When this function is called while passing the last seen time as the argument, a notification carrying the last seen appears on the phone (/laptop/pc etc.) and the previous last seen time disappears.

## Legal

This project is in no way affiliated with, authorized, maintained, sponsored or endorsed by Whatsapp or any of its affiliates or subsidiaries. This is an independent project. Use at your own risk.
