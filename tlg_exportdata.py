# -*- coding: utf-8 -*-

####################################################################################################

from telethon import TelegramClient
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsSearch

from collections import OrderedDict
from os import path, stat, remove, makedirs

import json

####################################################################################################

# Client parameters
api_id   = NNNNNN
api_hash = 'ffffffffffffffffffffffffffffffff'
phone    = '+NNNNNNNNNNN'
LOGIN_CODE = "NNNNN"

# Chat to inspect
CHAT_LINK  = "https://t.me/GroupName"

####################################################################################################

### Telegram basic functions ###

# Get all members data from a chat
def tlg_get_basic_info(client, chat):
	'''Get basic information (title, name, ) from a group/channel/chat'''
	# Get the corresponding chat entity
	chat_entity = client.get_entity(chat)
	# Get the number of users in the chat
	num_members = client(GetParticipantsRequest(channel=chat_entity, \
	filter=ChannelParticipantsSearch(''), offset=0, limit=0, hash=0)).count
	# Get messages data from the chat and extract the usefull data
	msgs = client.get_message_history(chat_entity, limit=1)
	basic_info = OrderedDict \
		([ \
			("id", msgs.data[0].to.id), \
			("title", msgs.data[0].to.title), \
			("username", msgs.data[0].to.username), \
			("num_members", num_members), \
			("num_messages", msgs.total), \
			("supergroup", msgs.data[0].to.megagroup) \
		])
	# Return basic info dict
	return basic_info


# Get all members data from a chat
def tlg_get_all_members(client, chat):
	'''Get all members information from a group/channel/chat'''
	# Get the corresponding chat entity
	chat_entity = client.get_entity(chat)
	# Get and save all users data in a single list
	i = 0
	members = []
	users = []
	num_members = client(GetParticipantsRequest(channel=chat_entity, \
	filter=ChannelParticipantsSearch(''), offset=0, limit=0, hash=0)).count
	while True:
		participants_i = client(GetParticipantsRequest(channel=chat_entity, \
		filter=ChannelParticipantsSearch(''), offset=i, limit=num_members, hash=0))
		if not participants_i.users:
			break
		users.extend(participants_i.users)
		i = i + len(participants_i.users)
	# Build our messages data structures and add them to the list
	for usr in users:
		usr_last_connection = ""
		if hasattr(usr.status, "was_online"):
			usr_last_connection = "{}/{}/{} - {}:{}:{}".format(usr.status.was_online.day, \
			usr.status.was_online.month, usr.status.was_online.year, usr.status.was_online.hour, \
			usr.status.was_online.minute, usr.status.was_online.second)
		else:
			usr_last_connection = "The user does not share this information"
		usr_data = OrderedDict \
			([ \
				("id", usr.id), \
				("username", usr.username), \
				("first_name", usr.first_name), \
				("last_name", usr.last_name), \
				("last_connection", usr_last_connection) \
			])
		members.append(usr_data)
	# Return members list
	return members


# Get messages data from a chat
def tlg_get_messages(client, chat, num_msg):
	'''Get all members information from a group/channel/chat'''
	# Set the result list
	messages = []
	# Get the corresponding chat entity
	chat_entity = client.get_entity(chat)
	# Get and save messages data in a single list
	msgs = client.get_message_history(chat_entity, limit=num_msg)
	# Build our messages data structures and add them to the list
	for msg in msgs.data:
		msg_sender = msg.sender.first_name
		if msg.sender.last_name:
			msg_sender = "{} {}".format(msg_sender, msg.sender.last_name)
		if msg.sender.username:
			msg_sender = "{} ({})".format(msg_sender, msg.sender.username)
		msg_sent_date = "{}/{}/{}".format(msg.date.day, msg.date.month, msg.date.year)
		msg_sent_time = "{}:{}:{}".format(msg.date.hour, msg.date.minute, msg.date.second)
		msg_data = OrderedDict \
			([ \
				("id", msg.id), ("text", msg.message), ("sent_time", msg_sent_time), \
				("sent_date", msg_sent_date), ("sender_user", msg_sender), \
				("sender_user_id", msg.sender.id), ("reply_to", msg.reply_to_msg_id) \
			])
		messages.append(msg_data)
	# Return the messages data list
	return messages


# Get all messages data from a chat
def tlg_get_all_messages(client, chat):
	'''Get all members information from a group/channel/chat'''
	# Set the result list
	messages = []
	# Get the corresponding chat entity
	chat_entity = client.get_entity(chat)
	# Get and save all messages data in a single list
	num_msg = client.get_message_history(chat_entity, limit=1).total
	msgs = client.get_message_history(chat_entity, limit=num_msg)
	# Build our messages data structures and add them to the list
	for msg in msgs.data:
		msg_sender = msg.sender.first_name
		if msg.sender.last_name:
			msg_sender = "{} {}".format(msg_sender, msg.sender.last_name)
		if msg.sender.username:
			msg_sender = "{} ({})".format(msg_sender, msg.sender.username)
		msg_sent_date = "{}/{}/{}".format(msg.date.day, msg.date.month, msg.date.year)
		msg_sent_time = "{}:{}:{}".format(msg.date.hour, msg.date.minute, msg.date.second)
		msg_data = OrderedDict \
			([ \
				("id", msg.id), ("text", msg.message), ("sent_time", msg_sent_time), \
				("sent_date", msg_sent_date), ("sender_user", msg_sender), \
				("sender_user_id", msg.sender.id), ("reply_to", msg.reply_to_msg_id) \
			])
		messages.append(msg_data)
	# Return the messages data list
	return messages

####################################################################################################

### Json files handle functions ###

def json_write(file, data):
	'''Write element data to content of JSON file'''
	# Add the data to a empty list and use the write_list function implementation
	data_list = []
	data_list.append(data)
	json_write_list(file, data_list)


def json_write_list(file, list):
	'''Write all the list elements data to content of JSON file'''
	# Create the directories of the file path if them does not exists
	directory = path.dirname(file)
	if not path.exists(directory):
		makedirs(directory)
	# Try to write the data
	try:
		# If the file does not exists or is empty, write the data content skeleton
		if not path.exists(file) or not stat(file).st_size:
			with open(file, "w", encoding="utf-8") as f:
				f.write('\n{\n    "Content": []\n}\n')
		# Read file content structure
		with open(file, "r", encoding="utf-8") as f:
			content = json.load(f, object_pairs_hook=OrderedDict)
		# For each data in list, add to the json content structure
		for data in list:
			if data:
				content['Content'].append(data) # Añadir los nuevos datos al contenido del json
		# Overwrite the file with the modified json content data
		with open(file, "w", encoding="utf-8") as f:
			f.write("\n{}\n".format(json.dumps(content, ensure_ascii=False, indent=4)))
	# Catch and handle errors
	except IOError as e:
		print("    I/O error({0}): {1}".format(e.errno, e.strerror))
	except ValueError:
		print("    Error: Can't convert data value to write in the file")
	except:
		print("    Error: Can't open the file {}".format(file))

####################################################################################################

### Main function ###
def main():
	'''Main Function'''
	# Create the client and connect
	client = TelegramClient("Session", API_ID, API_HASH)
	client.connect()

	# Check and login the client if needed
	if not client.is_user_authorized():
		client.sign_in(PHONE_NUM, LOGIN_CODE)
	else:
    	# Get basic info, all users and all messages data from a chat
		chat_info = tlg_get_basic_info(client, CHAT_LINK)
		members = tlg_get_all_members(client, CHAT_LINK)
		messages = tlg_get_all_messages(client, CHAT_LINK)

		# Create output JSON files
		if chat_info["username"]:
			files_name = chat_info["username"]
		else:
			files_name = chat_info["id"]
		fjson_chat = "./output/{}/chat.json".format(files_name) # Chat basic info json file
		fjson_users = "./output/{}/users.json".format(files_name) # Chat basic info json file
		fjson_messages = "./output/{}/messages.json".format(files_name) # Chat basic info json file

		# Save chat basic info to the output file
		if path.exists(fjson_chat):
			remove(fjson_chat)
		json_write(fjson_chat, chat_info)

		# Save chat users data to the output file
		if path.exists(fjson_users):
			remove(fjson_users)
		json_write_list(fjson_users, members)

		# Save chat messages data to the output file
		if path.exists(fjson_messages):
			remove(fjson_messages)
		json_write_list(fjson_messages, messages)

####################################################################################################

### Execute the main function if the file is not an imported module ###
if __name__ == "__main__":
	main()

