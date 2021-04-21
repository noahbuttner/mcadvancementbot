import webbrowser
import tkinter.font as tkFont
import datetime
import sys
import copy
import csv
import time
import os
import json
import requests
import tkinter as tk


class Application(tk.Frame):
	def __init__(self, master=None):
		super().__init__(master)

		self.settings = json.loads(open("settings.json", "r").read())
		self.mcpath = self.settings['mcpath']
		print(self.mcpath)
		self.client_id = self.settings['client_id']
		self.client_secret = self.settings['client_secret']
		self.code = self.settings['code']
		self.token = self.settings['token']
		self.refresh_token = self.settings['refresh_token']
		self.bgrnd = "#263D42"
		self.master = master
		self.pack()
		self.canvas = tk.Canvas(self, height=700, width=700, bg=self.bgrnd)
		self.canvas.pack()
		self.frame = tk.Frame(self, bg="white")
		self.frame.place(relwidth=0.8, relheight=0.8, relx=0.1, rely=0.1)
		fontStyle = tkFont.Font(family="Lucida Grande", size=20)
		self.settings_frame = tk.Frame(self.frame,bg="red")
		self.settings_frame.pack(side=tk.BOTTOM)
		self.instuctions = tk.Label(self.frame, text="Instructions", font=fontStyle)
		self.instuctions.pack()
		self.p1 = tk.Label(self.frame, text="Create a new app",cursor="hand1")
		self.p1.bind("<Button-1>", lambda e: self.link_it("https://nightbot.tv/account/applications"))
		self.p1.pack()
		self.p2 = tk.Label(self.frame, text="Paste the client_id and client_secret below, and enter the path to your mc saves folder")
		self.p2.pack()
		self.p3 = tk.Label(self.frame, cursor="hand1", text="Then, go here and authorize, then copy the code in the url that it redirects you to and paste it into the code section")
		self.p3.bind("<Button-1>", lambda e: self.link_it(
			"https://nightbot.tv/oauth2/authorize?client_id="+ self.client_id+ "&response_type=code&scope=commands&redirect_uri=https://127.0.0.1"))
		self.p3.pack()
		self.create_settings()
		self.create_buttons()
		csvfile = open("data.csv","r")
		reader = csv.reader(csvfile)
		self.translator = {}
		self.names = []
		for row in reader:
			self.names.append(row[1])
			self.translator.update({row[0]: {
				'name': row[1],
				'done': False,}})
		self.replaced_commands = {command.replace(" ", "").lower(): command for command in self.names}
		self.all_commands = self.get_all_commands()
 
	def link_it(self, url):
		webbrowser.open_new(url)
 
	def submit_code_entry(self):
		print(self.code_entry.get())
		self.code = self.code_entry.get()
 
	def create_settings(self):
		self.l1 = tk.Label(self.settings_frame, text="client_id")
		self.l1.grid(row=1, column=1)
		self.e1 = tk.Entry(self.settings_frame, text=self.client_id)
		self.e1.insert(0, self.client_id)
		self.e1.grid(row=1, column=2)
		self.b1 = tk.Button(self.settings_frame, text="Submit",command=self.submit_settings)
		self.b1.grid(row=1, column=3)
		self.l2 = tk.Label(self.settings_frame, text="client_secret")
		self.l2.grid(row=2, column=1)
		self.e2 = tk.Entry(self.settings_frame, text=self.client_secret)
		self.e2.insert(0, self.client_secret)
		self.e2.grid(row=2, column=2)
		self.b2 = tk.Button(self.settings_frame, text="Submit", command=self.submit_settings)
		self.b2.grid(row=2, column=3)
		self.l3 = tk.Label(self.settings_frame, text="access_code")
		self.l3.grid(row=3, column=1)
		self.e3 = tk.Entry(self.settings_frame, text=self.code)
		self.e3.insert(0, self.code)
		self.e3.grid(row=3, column=2)
		self.b3 = tk.Button(self.settings_frame, text="Submit", command=self.submit_settings)
		self.b3.grid(row=3, column=3)
		self.l4 = tk.Label(self.settings_frame, text="mcpath")
		self.l4.grid(row=4, column=1)
		self.e4 = tk.Entry(self.settings_frame, text=self.mcpath)
		self.e4.insert(0, self.mcpath)
		self.e4.grid(row=4, column=2)
		self.b4 = tk.Button(self.settings_frame, text="Submit", command=self.submit_settings)
		self.b4.grid(row=4, column=3)
 
	def submit_settings(self):
 
		self.client_id = self.e1.get()
		self.client_secret =self.e2.get()
		self.code = self.e3.get()
		self.mcpath = self.e4.get()
		self.settings.update({
			'client_id': self.client_id,
			'client_secret': self.client_secret,
			'code': self.code,
			'mcpath': self.mcpath,
			})
		with open("settings.json", "w") as settings_file:
			settings_file.write(str(json.dumps(self.settings,indent=4,sort_keys=True)))
 
	def create_buttons(self):
		self.get_token_button = tk.Button(self.frame, text="Get Token",
			padx=10, pady=5, fg="blue", command=self.get_token)
		self.get_token_button.pack(side=tk.BOTTOM)
		self.all_commands_button = tk.Button(self.frame, text="Add all Commands",
			padx=10, pady=5, fg="blue", command=self.set_all_commands)
		self.all_commands_button.pack(side=tk.BOTTOM)
		self.take_backup_button = tk.Button(self.frame,
			text="Take Backup",
			padx=10, pady=5, fg="blue", command=self.make_backup)
		self.take_backup_button.pack(side=tk.BOTTOM)
		self.start_button = tk.Button(self.frame,
			text="Start",
			padx=10, pady=5, fg="blue", command=self.main)
		self.start_button.pack(side=tk.BOTTOM)
		self.ac_button = tk.Button(self.frame,
			text="Get All Commands",
			padx=10, pady=5, fg="blue", command=self.get_all_commands)
		self.ac_button.pack(side=tk.BOTTOM)
 
	def get_token(self):
		r = requests.post("https://api.nightbot.tv/oauth2/token", data={
			"client_id": self.client_id,
			"client_secret": self.client_secret,
			"code": self.code,
			"grant_type": "authorization_code",
			"redirect_uri":"https://127.0.0.1"})
		if r.json().get("error"):
			self.error = tk.Label(self.frame, text=r.json().get('error_description'))
			self.error.pack()
		else:
			self.access_token_label = tk.Label(self.frame,text="access_token: " + r.json()['access_token'])
			self.refresh_token_label = tk.Label(self.frame, text="refresh_token: " + r.json()['refresh_token'])
			self.access_token_label.pack()
			self.refresh_token_label.pack()
			self.token = r.json()['access_token']
			self.settings.update({'token': self.token})
			with open(os.path.join(sys._MEIPASS,"settings.json"), "w") as settings_file:
				settings_file.write(str(json.dumps(self.settings,indent=4,sort_keys=True)))
 
	def set_all_commands(self):
		commands = self.names
		for command in commands:
			if command.replace(" ", "") not in self.all_commands:
				args = {
				"coolDown": 5,
				"message": command + " has not yet been completed.",
				'name': command.replace(" ", ""),
				'userLevel': "everyone",
				}
				self.send_request("https://api.nightbot.tv/1/commands", args=args)
		args.update({
			'message': "No advancements have been completed",
			'name': "!completed"})
		self.send_request("https://api.nightbot.tv/1/commands", args=args)
		args.update({
			'message': "No advancements have been completed",
			'name': "!left"})
		self.send_request("https://api.nightbot.tv/1/commands", args=args)
 
	def send_request(self, url, args=None, method="POST"):
		headers = {"Authorization": "Bearer " + self.token}
		if method == "POST":
			r = requests.post(url, data=args, headers=headers)
		elif method == "GET":
			r = requests.get(url, data=args, headers=headers)
		elif method == "Delete":
			r = requests.delete(url, data=args, headers=headers)
		elif method == "PUT":
			r = requests.put(url, data=args, headers=headers)
		print(r.text)
		return r.json()
 
	def get_all_commands(self):
		commands = self.send_request("https://api.nightbot.tv/1/commands", method="GET")
		factored_commands = {}
		if commands.get('commands'):
                        for command in commands['commands']:
                                if self.replaced_commands.get(command['name']):
                                        factored_commands.update({self.replaced_commands[command['name']]: command})
                                elif command['name'] == "!left":
                                        factored_commands.update({'!left': command})
                                elif command['name'] == "!completed":
                                        factored_commands.update({'!completed': command})
		self.all_commands = factored_commands
		return factored_commands
 
	def get_raw_commands(self):
		return self.send_request("https://api.nightbot.tv/1/commands", method="GET")
 
	def delete_all_commands(self):
		for command in self.all_commands['commands']:
			self.send_request("https://api.nightbot.tv/1/commands/" + command['_id'], method="Delete")
 
 
	def individual_commands(self, different_advancements):
		for path, advancement_info in different_advancements.items():
			if advancement_info['done']:
				message = advancement_info['name'] + " has been completed."
			else:
				message = advancement_info['name'] + " has not yet been completed."
			args = {
			'message': message,
			}
			if message != self.all_commands[advancement_info['name']]['message']:
				self.send_request("https://api.nightbot.tv/1/commands/" + self.all_commands[advancement_info['name']]['_id'],method="PUT", args=args)
 
	def overall_commands(self, current_advancements):
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
		if len(completed_message) > 500:
			completed_message = completed_message[0:496] + "..."
		if len(left_message) > 500:
			left_message = left_message[0:496] + "..."
		self.send_request("https://api.nightbot.tv/1/commands/" + self.all_commands["!left"]['_id'],method="PUT", args={'message': left_message})
		self.send_request("https://api.nightbot.tv/1/commands/" + self.all_commands["!completed"]['_id'],method="PUT", args={'message': completed_message})
 
	def update_commands(self, different_advancements, current_advancements):
		self.individual_commands(different_advancements)
		self.overall_commands(current_advancements)
 
	def make_backup(self):
		cmds = self.get_raw_commands()
		with open(os.path.join("backups",datetime.datetime.now().strftime("%S") + ".json"), "x") as backup_file:
			backup_file.write(str(json.dumps(cmds,indent=4,sort_keys=True)))
 
	def get_latest_world(self):
		worlds = os.listdir(self.mcpath)
		for world in worlds:
			if world[0] == ".":
				worlds.remove(world)
		times = {os.path.getctime(os.path.join(self.mcpath,world)): world for world in worlds}
		latest_file = times[max(times)]
		return latest_file
 
	def get_advancement_file(self):
		latest_file = self.get_latest_world()
		world_path = os.path.join(self.mcpath,latest_file)
		advancement_path = os.path.join(world_path, "advancements")
		if "advancements" in os.listdir(world_path):
			advancement_file = os.listdir(advancement_path)[0]
		else:
			return None
		advancement_file_path = os.path.join(advancement_path, advancement_file)
		return open(os.path.join(advancement_file_path),"r").read()
 
	def get_advancements(self):
		advancements = self.get_advancement_file()
		if not advancements:
			return None
		advancements = json.loads(advancements)
		new_advancements = copy.deepcopy(self.translator)
		for path, info in advancements.items():
			if path[0:17] != 'minecraft:recipes' and path != "DataVersion":
				if info['done']:
					new_advancements[path]['done'] = True
		return new_advancements

	def get_different_advancements(self, current_advancements):
		the_new_advancements = self.get_advancements()
		if not the_new_advancements:
			return None, None
		different_advancements = {}
		for path, new_advancement in the_new_advancements.items():
			if path not in current_advancements:
				different_advancements.update({path: new_advancement})
			elif current_advancements[path] != new_advancement:
				different_advancements.update({path: new_advancement})
		return different_advancements, the_new_advancements
	def main(self):
		current_advancements = self.get_advancements()
		self.update_commands(current_advancements, current_advancements)
		self.set_all_commands()
		self.running = True
		while self.running:
			time.sleep(1)
			all_diff = self.get_different_advancements(current_advancements)
			diff = all_diff[0]
			if diff:
				current_advancements = all_diff[1]
				self.update_commands(diff, current_advancements)
 
root = tk.Tk()
app = Application(master=root)
app.mainloop()