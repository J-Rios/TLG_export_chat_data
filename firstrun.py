# -*- coding: utf-8 -*-

from telethon import TelegramClient

####################################################################################################

# Client parameters
api_id   = NNNNNN
api_hash = 'ffffffffffffffffffffffffffffffff'
phone    = '+NNNNNNNNNNN'

####################################################################################################

### Main function ###
def main():
    ''' Main Function'''
    # Create the client, connect and send an auth code request
    client = TelegramClient('Session', api_id, api_hash)
    client.connect()
    client.send_code_request(phone)
    print('A Code has been request to Telegram.')
    print('Check your telegram App to obtain the \"login_code\" and use it in the main script.')

####################################################################################################

### Execute the main function if the file is not an imported module ###
if __name__ == '__main__':
	main()
