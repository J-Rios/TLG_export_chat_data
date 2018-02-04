# -*- coding: utf-8 -*-
'''
Script:
    firstrun.py
Description:
    Python script to request a Telegram LOGIN_CODE from client API.
Author:
    Jose Rios Rubio
Creation date:
    02/02/2018
Last modified date:
    04/02/2018
Version:
    1.0.0
'''

####################################################################################################

### Libraries/Modules ###

from telethon import TelegramClient

####################################################################################################

### Constants ###

# Client parameters
API_ID   = NNNNNN
API_HASH = 'ffffffffffffffffffffffffffffffff'
PHONE_NUM    = '+NNNNNNNNNNN'

####################################################################################################

### Main function ###
def main():
    ''' Main Function'''
    # Create the client, connect and send an auth code request
    client = TelegramClient('Session', API_ID, API_HASH)
    client.connect()
    client.send_code_request(PHONE_NUM)
    print('A Code has been request to Telegram.')
    print('Check your telegram App to obtain the \"login_code\" and use it in the main script.')

####################################################################################################

### Execute the main function if the file is not an imported module ###
if __name__ == '__main__':
	main()
