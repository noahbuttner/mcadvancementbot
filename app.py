import copy
import csv
import time
import os
import json
import requests
""" go to this url:
https://nightbot.tv/oauth2/authorize?
client_id=f88e7e1e7e6789c060c78bd315252945&
response_type=code&
scope=commands&
redirect_uri=https:%2F%2F127.0.0.1&
state=f
"""
lines = open("settings.txt", "r").read().split("\n")
mcpath = lines[0][lines[0].find(":") + 1:]
client_id = lines[1][lines[1].find(":") + 1:]
client_secret = lines[2][lines[2].find(":") + 1:]
code = lines[3][lines[3].find(":") + 1:]
token = lines[4][lines[4].find(":") + 1:]
refresh_token = lines[5][lines[5].find(":") + 1:]

def get_latest_world():
	worlds = os.listdir(mcpath)
	for world in worlds:
		if world[0] == ".":
			worlds.remove(world)
	times = {os.path.getctime("/".join([mcpath,world])): world for world in worlds}
	latest_file = times[max(times)]
	return latest_file

def get_advancement_file():
	latest_file = get_latest_world()
	world_path = "/".join((mcpath,latest_file))
	advancement_path = "/".join((world_path, "advancements"))
	if "advancements" in os.listdir(world_path):
		advancement_file = os.listdir(advancement_path)[0]
	else:
		return None
	advancement_file_path = advancement_path + "/" + advancement_file
	return open(advancement_file_path,"r").read()

def get_token(code):
	r = requests.post("https://api.nightbot.tv/oauth2/token", data={
		"client_id":client_id,
		"client_secret": client_secret,
		"code":code,
		"grant_type": "authorization_code",
		"redirect_uri":"https://127.0.0.1"})
	return r.text

csvfile = open("data.csv","r")
reader = csv.reader(csvfile)
translator = {}
names = []
for row in reader:
	names.append(row[1])
	translator.update({row[0]: {
		'name': row[1],
		'done': False,}})

def get_advancements():
	advancements = get_advancement_file()
	if not advancements:
		return None
	advancements = json.loads(advancements)
	new_advancements = copy.deepcopy(translator)
	for path, info in advancements.items():
		if path[0:17] != 'minecraft:recipes' and path != "DataVersion":
			if info['done']:
				new_advancements[path]['done'] = True
	return new_advancements

def get_different_advancements(current_advancements):
	the_new_advancements = get_advancements()
	if not the_new_advancements:
		return None, None
	different_advancements = {}
	for path, new_advancement in the_new_advancements.items():
		if path not in current_advancements:
			different_advancements.update({path: new_advancement})
		elif current_advancements[path] != new_advancement:
			different_advancements.update({path: new_advancement})
	return different_advancements, the_new_advancements

def send_request(url, token, args=None, method="POST"):
	headers = {"Authorization": "Bearer " + token}
	if method == "POST":
		r = requests.post(url, data=args, headers=headers)
	elif method == "GET":
		r = requests.get(url, data=args, headers=headers)
	elif method == "Delete":
		r = requests.delete(url, data=args, headers=headers)
	elif method == "PUT":
		r = requests.put(url, data=args, headers=headers)
	return r.json()

def set_all_commands(token):
	commands = names
	for command in commands:
		if command.replace(" ", "") not in all_commands:
			args = {
			"coolDown": 5,
			"message": command + " has not yet been completed.",
			'name': command.replace(" ", ""),
			'userLevel': "everyone",
			}
			send_request("https://api.nightbot.tv/1/commands", token, args=args)
	args.update({
		'message': "No advancements have been completed",
		'name': "!completed"})
	send_request("https://api.nightbot.tv/1/commands", token, args=args)
	args.update({
		'message': "No advancements have been completed",
		'name': "!left"})
	send_request("https://api.nightbot.tv/1/commands", token, args=args)

def get_all_commands(token):
	commands = send_request("https://api.nightbot.tv/1/commands", token, method="GET")
	factored_commands = {}
	for command in commands['commands']:
		if replaced_commands.get(command['name']):
			factored_commands.update({replaced_commands[command['name']]: command})
		elif command['name'] == "!left":
			factored_commands.update({'!left': command})
		elif command['name'] == "!completed":
			factored_commands.update({'!completed': command})
	return factored_commands

def delete_all_commands(token):
	for command in all_commands['commands']:
		send_request("https://api.nightbot.tv/1/commands/" + command['_id'], token, method="Delete")


def individual_commands(different_advancements):
	for path, advancement_info in different_advancements.items():
		if advancement_info['done']:
			message = advancement_info['name'] + " has been completed."
		else:
			message = advancement_info['name'] + " has not yet been completed."
		args = {
		'message': message,
		}
		if message != all_commands[advancement_info['name']]['message']:
			send_request("https://api.nightbot.tv/1/commands/" + all_commands[advancement_info['name']]['_id'],method="PUT", token=token, args=args)

def overall_commands(current_advancements):
	completed_advancements = []
	left_advancements = []
	for path, info in current_advancements.items():
		if info['done']:
			completed_advancements.append(info['name'])
		else:
			left_advancements.append(info['name'])
	completed_message = "The following advancements have been completed: {}".format(
		", ".join(completed_advancements))
	left_message = "The following advancements have not been completed: {}".format(
		", ".join(left_advancements))
	if completed_message > 500:
		completed_message = completed_message[0:496] + "..."
	if left_message > 500:
		left_message = left_message[0:496] + "..."
	print(send_request("https://api.nightbot.tv/1/commands/" + all_commands["!left"]['_id'],method="PUT", token=token, args={'message': left_message}))
	send_request("https://api.nightbot.tv/1/commands/" + all_commands["!completed"]['_id'],method="PUT", token=token, args={'message': completed_message})

def update_commands(different_advancements, current_advancements):
	individual_commands(different_advancements)
	overall_commands(current_advancements)


current_advancements = get_advancements()
replaced_commands = {command.replace(" ", "").lower(): command for command in names}
all_commands = get_all_commands(token)
update_commands(current_advancements, current_advancements)
set_all_commands(token)

running = True
while running:
	time.sleep(1)
	all_diff = get_different_advancements(current_advancements)
	diff = all_diff[0]
	if diff:
		current_advancements = all_diff[1]
		update_commands(diff, current_advancements)









