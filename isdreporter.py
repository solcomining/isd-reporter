""" 
ISD Reporter v1.0 
1. Logs in to Galaxy Harvester to retrieve session token and current data export.
2. Processes spawn info from saved interplanetary survey droid emails. 
3. Submits potentially new spawns to Galaxy Harvester.
4. (Optional) Submits all spawns to Galaxy Harvester.
5. (Optional) Sends Discord webhook messages.

Files
isdreporter.py 		This file.
SwgMail.py 			Parsing class (courtesy of Dasch).
restypes.txt 		All resource types in SWG and GH format. Should work for any server. 
restypeseif.txt 	EiF non-creature resource types. Faster than using above (recommend making an equivalent for your own server).
current.xml			Current Galaxy Harvester data export (downloaded during runtime).
"""

submit_everything = False						# False to only submit new spawns. Recommend False.
notify_discord = False							# True to send Discord webhook messages.
safety_checks = True							# True to enable y/n confirmation at config and mail stages. Recommend True.
max_age_hours = 1								# .mail files older than this will not be processed.

mail_folder_path = "/mnt/c/Games/SWGinstall/profiles/username/servername/mail_firstname lastname"
#mail_folder_path = "C:\Games\SWGinstall\profiles\username\servername\mail_firstname lastname"
restypes_file = "restypeseif.txt"				# Recommend editing restypes.txt to suit your own server.

galaxy_id = "1234"								# DO NOT get this wrong. It comes from e.g: https://galaxyharvester.net/resource.py/1234/exampleism
gh_name = "username"							# Extended characters might not work.
gh_pass = "password"

webhook_name = "ISD-Reporter"
webhook_urls = {								# Any number of webhook urls will work. The name can be whatever.
	"First server":"https://discord.com/api/webhooks/0123456789/abcdefghijklmnopqrstuvwxyz",
	"Second server":"https://discord.com/api/webhooks/0123456789/abcdefghijklmnopqrstuvwxyz",
	"Third server":"https://discord.com/api/webhooks/0123456789/abcdefghijklmnopqrstuvwxyz"
}

import sys
import os
import time
from datetime import datetime
import re
import json
import xml.etree.ElementTree as ET 
import httplib2
from SwgMail import SwgMail
from urllib.parse import urlencode
from operator import itemgetter

global session
global gh_current_resnames

def type_slowly(str):
	
	for letter in str:
		print(letter, end='', flush=True)
		time.sleep(0.025)

def show_banner():
    
    banner = '''\033[1;33m
    ╔───────────────────────────────────────────────╗
    │░█▀▀░█▀█░█░░░█▀▀░█▀█░░░█▄█░▀█▀░█▀█░▀█▀░█▀█░█▀▀░│
    │░▀▀█░█░█░█░░░█░░░█░█░░░█░█░░█░░█░█░░█░░█░█░█░█░│
    │░▀▀▀░▀▀▀░▀▀▀░▀▀▀░▀▀▀░░░▀░▀░▀▀▀░▀░▀░▀▀▀░▀░▀░▀▀▀░│
    │░░█▀▀░█▀█░█▀▄░█▀█░█▀█░█▀▄░█▀█░▀█▀░▀█▀░█▀█░█▀█░░│
    │░░█░░░█░█░█▀▄░█▀▀░█░█░█▀▄░█▀█░░█░░░█░░█░█░█░█░░│
    │░░▀▀▀░▀▀▀░▀░▀░▀░░░▀▀▀░▀░▀░▀░▀░░▀░░▀▀▀░▀▀▀░▀░▀░░│
    ╚───────────────────────────────────────────────╝
                 Survey Droid Reporter
    \033[0m'''

    print(banner)

def show_config():
	
	print(f"\t submit_everything: \t {submit_everything}")
	print(f"\t notify_discord: \t {notify_discord}")
	
def gh_login():

	type_slowly("\n\033[1;33mConnecting to Galaxy Harvester...\033[0m\n")
	
	url = "https://galaxyharvester.net/authUser.py?loginu=" + gh_name + "&passu=" + gh_pass
	http = httplib2.Http()
	(resp_headers, content) = http.request(url,"GET")

	# gh returns "success-1234567890\n " We need the numbers as our session token
	
	try:
		pattern = 'success-(.*)'
		match = re.search(pattern, str(content))
		gh_token = str(match.group(1))
		gh_token = gh_token[:-3]
		print("\n\t Username: \t\t",gh_name)
	except:
		sys.exit("\t Exiting - GH login failed")

	return gh_token # used by the gh_submit function

def fetch_gh_data():

	# save the xml data export from GH
	
	url = "https://galaxyharvester.net/exports/current" + galaxy_id + ".xml"
	http = httplib2.Http()
	(resp_headers, content) = http.request(url,"GET")
	
	if resp_headers.status != 200: 
		sys.exit("\t Exiting - no data export found")  
	else:
		str_content = content.decode('utf-8')
		with open('current.xml', 'w') as f:
			f.write(str_content) 

	# make a list of resource names known to GH
						
	root = ET.fromstring(str_content)
	gh_current_resnames = set()

	for resource in root.findall('resource'):
		resname = resource.find('name').text
		gh_current_resnames.add(resname)

	# and some safety

	galaxy_name = root.find('.//galaxy').text	
	print('\t',"Galaxy:",'\t\t',galaxy_name) 

	name_count = len(gh_current_resnames)
	print('\t',"Spawns:",'\t\t',name_count) 

	as_of_date = root.attrib['as_of_date']
	as_of_date = datetime.strptime(as_of_date, '%a, %d %b %Y %H:%M:%S %z')
	current_time = datetime.now(as_of_date.tzinfo)
	difference = current_time - as_of_date
	hours_old = difference.total_seconds() / 3600  

	print(f"\n\t Galaxy Harvester data export was generated {hours_old:.0f} hours ago.")
	print(f"\t All spawns younger than that will be counted as new.")

	if safety_checks == True:
		config_check = input("\n\t Safety check 1 of 2. Continue? (y/n): ")
		if config_check != "y":
			sys.exit("\t Exiting - disastrous mess averted")
	
	return gh_current_resnames # used by the process_isdmails function

def find_isdmails(mail_folder_path, max_age_hours):
    
	type_slowly("\n\033[1;33mLooking for saved survey reports...\033[0m\n\n")
	
	isdmails = []
	current_time = time.time()

	# make a list of files 

	for fname in os.listdir(mail_folder_path):
		if fname.endswith(".mail"):
			file_path = os.path.join(mail_folder_path, fname)
			file_mod_time = os.path.getmtime(file_path)
			file_age_hours = (current_time - file_mod_time) / 3600

			if file_age_hours <= max_age_hours: # this is fairly naive, and relies on the player only saving NEW ISD emails ingame / deleting OLD ISD emails ingame
				with open(file_path) as mail:
					line = mail.readlines()
					subject = line[2]
					incoming = line[4]

					if incoming.strip() == "Incoming planetary survey report...":
						isdmails.append((fname, subject))

	# sort and display

	isdmails.sort(key=itemgetter(1)) 

	for item in isdmails:
		print('\t', item[0][:-5], '\t', item[1][:-1]) 
	
	print(f"\t Survey reports: {len(isdmails)} newer than {max_age_hours} hour(s)")

	# more safety
	
	if len(isdmails) == 0 :
		print(f"\t Exiting - no survey reports found")
		sys.exit()

	if safety_checks == True:
		mails_check = input("\n\t Safety check 2 of 2. Continue? (y/n): ")
		if mails_check != "y":
			sys.exit("\t Exiting - disastrous mess averted")

	# process in order from Chandrila chemical to Yavin water

	process_isdmails(isdmails) 

def process_isdmails(isdmails):
	
	type_slowly("\n\033[1;33mProcessing spawns from reports...\033[0m\n")

	spawn_count = 0
	resname_list = []

	# parse each file for spawns

	for mail in isdmails:
		mail_file = f"{mail_folder_path}/{mail[0]}"  # need full path
		mail_data = open(mail_file).read()
		mail_spawns = SwgMail.parse_survey_droid(mail_data) 
		
		# get the spawn data ready for GH submit

		for spawn in mail_spawns: 
			spawn_count +=1
			planet = spawn['planet']
			resname = spawn['name']
			restype = spawn['type']  
			stats = [spawn['stats']]
			raw_stats = str(spawn['stats'])
			cleaned_stats = " ".join(re.findall("[A-Z0-9]+",raw_stats))	

			for stat in stats:			
				try:
					CR = stat['CR']
				except KeyError:
					CR = ''
				try:
					CD = stat['CD']
				except KeyError:
					CD = ''
				try:
					DR = stat['DR']
				except KeyError:
					DR = ''
				try:
					FL = stat['FL']
				except KeyError:
					FL = ''
				try:
					HR = stat['HR']
				except KeyError:
					HR =''
				try:
					MA = stat['MA']
				except KeyError:
					MA = ''
				try:
					PE = stat['PE']
				except KeyError:
					PE = ''
				try:
					OQ = stat['OQ']
				except KeyError:
					OQ = ''
				try:
					SR = stat['SR']
				except KeyError:
					SR = ''
				try:
					UT = stat['UT']  
				except KeyError:
					UT = ''

			# submit to gh 

			if submit_everything == False:	
				if resname.lower() in gh_current_resnames: # check if name is known to gh
					print(spawn_count,'\t',resname.upper(),' \t',restype) # not new so we display but dont submit
				else:
					print(spawn_count,'\t',resname.upper(),' \t',restype,'on',spawn['planet']) # might be new so we display and submit
					print('\t',cleaned_stats)
					gh_submit(planet, resname, restype, CR, CD, DR, FL, HR, MA, PE, OQ, SR, UT) 
					resname_list.append(resname) # used to get a count of new spawns found
			else: 
				print(spawn_count,'\t',resname.upper(),' \t',restype,'on',spawn['planet']) # we submit every spawn without checking if it's known to GH
				print('\t',cleaned_stats)
				gh_submit(planet, resname, restype, CR, CD, DR, FL, HR, MA, PE, OQ, SR, UT) 
				resname_list.append(resname)

	# make the message text

	count_mails = len(isdmails)
	unique_resnames = set(resname_list)  
	count_unique = len(unique_resnames)

	tree = ET.parse('current.xml')
	root = tree.getroot()
	oq_values = [int(resource.find('.//OQ').text) for resource in root.findall('resource')]
	oq_average = round(sum(oq_values) / len(oq_values))

	message = (
	f"{count_mails} Interplanetary Survey Droid reports have been submitted to [Galaxy Harvester](https://galaxyharvester.net/).\n"
	f"||{count_unique} new resources were found. The current galactic OQ average is {oq_average}.||"
	)
			
	print("\n" + message)

	if notify_discord is True:	
		discord_webhook(message)
	
def gh_submit(planet, resname, restype, CR, CD, DR, FL, HR, MA, PE, OQ, SR, UT):
	
	gh_sid = 'gh_sid=' + session	
	
	with open(restypes_file) as f:
		try: 
			# change the restype from SWG to GH format
			data = f.read()
			js = json.loads(data)
			restype = js[restype] 
			
			# submit spawn to GH
			url = "https://galaxyharvester.net/postResource.py?galaxy=" + galaxy_id + "&planet=" + planet + "&resName=" + resname + "&resType=" + restype + "&CR=" + CR + "&CD=" + CD + "&DR=" + DR + "&FL=" + FL + "&HR=" + HR + "&MA=" + MA + "&PE=" + PE + "&OQ=" + OQ + "&SR=" + SR + "&UT=" + UT
			http = httplib2.Http()
			header = {'Cookie': gh_sid}
			(resp_headers, content) = http.request(url,'POST',headers=header)
			
			# show GH response
			root = ET.fromstring(content)
			result = root.find('resultText').text
			print('\t\033[1;32m',result,'\033[0m') # green for good
		
		except:
			print ("\t\033[1;31m ERROR - check resource type in restypes_file \033[0m") # red for not good

def discord_webhook(message):

    webhook_data = {
        "username": webhook_name,
        "content": message
    }

    for key, url in webhook_urls.items():
        try:
            response = httplib2.Http().request(
                url,
                'POST',
                urlencode(webhook_data).encode('utf-8'),  
                headers={'Content-Type': 'application/x-www-form-urlencoded'}
            )
            print(f"{key} webhook response: {response[0].status}")
        
        except Exception as e:
            print(f"{key} webhook error: {e}")

###	start ###
start_time = time.time()

show_banner()
show_config()	

session = gh_login()	
gh_current_resnames = fetch_gh_data()		
find_isdmails(mail_folder_path, max_age_hours)	

end_time = time.time()
execution_time = end_time - start_time
print(f"\n\033[1;33mCompleted in {execution_time:.0f} seconds.\033[0m")









