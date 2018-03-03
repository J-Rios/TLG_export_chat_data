# -*- coding: utf-8 -*-
'''
Script:
    tlg_exportdata.py
Description:
    Python script that use the Telegram Client API to get all basic usefull data of a 
	group/channel/chat and export them in json files (chat data, members data and messages data).
Author:
    Jose Rios Rubio
Creation date:
    02/02/2018
Last modified date:
    03/03/2018
Version:
    1.2.5
'''

####################################################################################################

### Libraries/Modules ###

from telethon import TelegramClient
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsSearch

from collections import OrderedDict
from os import path, stat, remove, makedirs

import json

####################################################################################################

### Constants ###

# Client parameters
API_ID     = NNNNNN
API_HASH   = 'ffffffffffffffffffffffffffffffff'
PHONE_NUM  = '+NNNNNNNNNNN'
LOGIN_CODE = "NNNNN"

# Chat to inspect
CHAT_LINK  = "https://t.me/GroupName"

####################################################################################################

### Telegram basic functions ###

# Get basic info from a chat
def tlg_get_basic_info(client, chat):
	'''Get basic information (id, title, name, num_users, num_messages) from a group/channel/chat'''
	# Get the corresponding chat entity
	chat_entity = client.get_entity(chat)
	# Get Chat info
	chat_info = client(GetFullChannelRequest(chat_entity))
	# Get the date when the chat becomes public
	become_public_date = ""
	if hasattr(chat_entity, "date"):
		become_public_date = "{}/{}/{} - {}:{}:{}".format(chat_entity.date.day, \
			chat_entity.date.month, chat_entity.date.year, chat_entity.date.hour, \
			chat_entity.date.minute, chat_entity.date.second)
	else:
		become_public_date = "The chat is not public"
	# Get messages data from the chat and extract the usefull data related to chat
	msgs = client.get_message_history(chat_entity, limit=1)
	basic_info = OrderedDict \
		([ \
			("id", chat_info.full_chat.id), \
			("title", chat_info.chats[0].title), \
			("description", chat_info.full_chat.about), \
			("username", chat_info.chats[0].username), \
			("num_members", chat_info.full_chat.participants_count), \
			("num_messages", msgs.total), \
			("supergroup", chat_info.chats[0].megagroup), \
			("become_public", become_public_date) \
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
	participants = []
	num_members = client(GetParticipantsRequest(channel=chat_entity, \
		filter=ChannelParticipantsSearch(''), offset=0, limit=0, hash=0)).count
	while True:
		participants_i = client(GetParticipantsRequest(channel=chat_entity, \
			filter=ChannelParticipantsSearch(''), offset=i, limit=num_members, hash=0))
		if participants_i.participants:
			participants.extend(participants_i.participants)
		if participants_i.users:
			users.extend(participants_i.users)
		else:
			break
		i = i + len(participants_i.users)
	# Build our messages data structures and add them to the list
	num_members = i
	i = 0
	for i in range(0, num_members):
    	# Get join date of user
		join_date = ""
		for participant in participants:
			if users[i].id == participant.user_id:
				if hasattr(participant, "date"):
					join_date = "{}/{}/{} - {}:{}:{}".format(participant.date.day, \
						participant.date.month, participant.date.year, participant.date.hour, \
						participant.date.minute, participant.date.second)
					# Check if the user was in before the chat becomes public
					if hasattr(chat_entity, "date"):
						if not tlg_date_is_after(participant.date, chat_entity.date):
							join_date = "Before the Chat becomes public ({})".format(join_date)
		if not join_date: # Participant ID not found, so it must be the creator of group/channel
			join_date = "Big-Bang (Creator of the Chat)" # Creator is not a participant
    	# Get last connection date
		usr_last_connection = ""
		if hasattr(users[i].status, "was_online"):
			was_online_date = users[i].status.was_online
			usr_last_connection = "{}/{}/{} - {}:{}:{}".format(was_online_date.day, \
				was_online_date.month, was_online_date.year, was_online_date.hour,  \
				was_online_date.minute,	was_online_date.second)
		else:
			usr_last_connection = "The user does not share this information"
		usr_data = OrderedDict \
			([ \
				("id", users[i].id), \
				("username", users[i].username), \
				("first_name", users[i].first_name), \
				("last_name", users[i].last_name), \
				("Group/Channel_join", join_date), \
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
	for msg in reversed(msgs.data):
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
	for msg in reversed(msgs.data):
		msg_sender = msg.sender.first_name
		if msg.sender.last_name:
			msg_sender = "{} {}".format(msg_sender, msg.sender.last_name)
		if msg.sender.username:
			msg_sender = "{} (@{})".format(msg_sender, msg.sender.username)
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

# Check if one date is after another one for telegram format dates (t1 > t2)
def tlg_date_is_after(t1, t2):
	'''Check if one date is after another one for telegram format dates (t1 > t2)'''
	date_after = False
	if t1.year > t2.year:
		date_after = True
	elif t1.year == t2.year:
		if t1.month > t2.month:
			date_after = True
		elif t1.month == t2.month:
			if t1.day > t2.day:
				date_after = True
			elif t1.day == t2.day:
				if t1.hour > t2.hour:
					date_after = True
				elif t1.hour == t2.hour:
					if t1.minute > t2.minute:
						date_after = True
					elif t1.minute == t2.minute:
						if t1.second > t2.second:
							date_after = True
	return date_after

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
	try:
		# Create the directories of the file path if them does not exists
		directory = path.dirname(file)
		if not path.exists(directory):
			makedirs(directory)
		# If the file does not exists or is empty, write the JSON content skeleton
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
		# Overwrite the JSON file with the modified content data
		with open(file, "w", encoding="utf-8") as f:
			json.dump(content, fp=f, ensure_ascii=False, indent=4)
	# Catch and handle errors
	except IOError as e:
		print("    I/O error({0}): {1}".format(e.errno, e.strerror))
	except ValueError:
		print("    Error: Can't convert data value to write in the file")
	except MemoryError:
		print("    Error: You are trying to write too much data")

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
    	# Get chat basic info
		chat_info = tlg_get_basic_info(client, CHAT_LINK)

		# Create output JSON files from basic info chat name
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

		# Get all users data from the chat and save to the output file
		members = tlg_get_all_members(client, CHAT_LINK)
		if path.exists(fjson_users):
			remove(fjson_users)
		json_write_list(fjson_users, members)

		# Get all messages data from the chat and save to the output file
		messages = tlg_get_all_messages(client, CHAT_LINK)
		if path.exists(fjson_messages):
			remove(fjson_messages)
		json_write_list(fjson_messages, messages)

####################################################################################################

### Execute the main function if the file is not an imported module ###
if __name__ == "__main__":
	main()
