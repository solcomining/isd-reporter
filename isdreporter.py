""" 
ISD Reporter v1.1
- Reads config from isdreporter.cfg 
- Logs in to Galaxy Harvester to retrieve session token and current data export.
- Processes spawn info from saved interplanetary survey droid emails. 
- Submits potentially new spawns to Galaxy Harvester (new is any spawn that is NOT found in the GH data export).
- (Optional) Submits all spawns to Galaxy Harvester (aka verifying).
- (Optional) Sends Discord webhook message(s).
- (Optional) Moves processed .mail files to archive_folder_path.

isdreporter.cfg		Config file.
SwgMail.py			Parsing class (courtesy of Dasch).
restypes.txt		All resource types in SWG and GH format. Should work for any server. 
restypeseif.txt		EiF non-creature resource types. Much faster than using above (recommend making an equivalent for your own server).
current.xml			Current Galaxy Harvester data export (downloaded during runtime).
"""

import ast
import configparser
import os
import re
import sys
import time
from datetime import datetime
import json
import xml.etree.ElementTree as ET
from operator import itemgetter
from urllib.parse import urlencode
import httplib2
from SwgMail import SwgMail

def load_config(config_path='isdreporter.cfg'):

	config = configparser.ConfigParser()

	if not config.read(config_path):
		sys.exit(f"\nExiting: Could not find config file {config_path}")
	return config

def type_slowly(text):

	YELLOW = '\033[1;33m'
	RESET = '\033[0m'
	
	print(YELLOW, end='', flush=True)

	for letter in text:
		print(letter, end='', flush=True)
		time.sleep(0.025)

	print(RESET, end='', flush=True)
	
def gh_login():

	type_slowly("\nConnecting to Galaxy Harvester...\n")
	
	url = login_url + "?loginu=" + gh_name + "&passu=" + gh_pass
	http = httplib2.Http()
	(resp_headers, content) = http.request(url,"GET")

	# gh returns "success-1234567890\n " We need the part between - and \n	
	try:
		match = re.search('success-(.*)', str(content))
		gh_token = str(match.group(1))[:-3]
		print("\n\t Username: \t\t",gh_name)
		#print("\t Session: \t\t",gh_token)
	except:
		sys.exit(f"\nExiting: Login failed for user {gh_name}")

	return gh_token # used by the gh_submit function

def fetch_gh_data():

	# save the xml data export from GH	
	url = data_url
	http = httplib2.Http()
	(resp_headers, content) = http.request(url,"GET")
	
	if resp_headers.status != 200: 
		sys.exit(f"\nExiting: No data export found at {url}")  
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

	as_of_date = root.attrib['as_of_date']
	as_of_date = datetime.strptime(as_of_date, '%a, %d %b %Y %H:%M:%S %z')
	current_time = datetime.now(as_of_date.tzinfo)
	difference = current_time - as_of_date
	hours_old = difference.total_seconds() / 3600  

	print(f"\n\t Galaxy Harvester data export was generated {hours_old:.0f} hours ago.")
	print(f"\t All spawns younger than that will be counted as new.")

	if safety_checks == True:
		config_check = input("\n\t Safety check 1 of 2. Is that the correct galaxy? (y/n): ")
		if config_check != "y":
			sys.exit(f"\nExiting: Disastrous mess averted")
	
	return gh_current_resnames # used by the process_isdmails function

def find_isdmails(mail_folder_path, max_age_hours):
    
	type_slowly("\nLooking for saved survey reports...\n\n")
	
	isdmails = []
	current_time = time.time()

	# make a list of files
	for fname in os.listdir(mail_folder_path):
		if fname.endswith(".mail"):
			file_path = os.path.join(mail_folder_path, fname)
			file_mod_time = os.path.getmtime(file_path)
			file_age_hours = (current_time - file_mod_time) / 3600

			# best practice is for the player to only save *new* ISD emails from ingame i.e to delete *old* ISD emails
			if file_age_hours <= max_age_hours: 
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
	
	print(f"\t Found {len(isdmails)} newer than {max_age_hours} hour(s)")

	# more safety	
	if len(isdmails) == 0 :
		sys.exit(f"\nExiting: No survey reports found at {mail_folder_path}")

	if safety_checks == True:
		mails_check = input("\n\t Safety check 2 of 2. Are those the correct emails? (y/n): ")
		if mails_check != "y":
			sys.exit("\nExiting: Disastrous mess averted")

	# process in order from Chandrila chemical to Yavin water
	process_isdmails(isdmails) 

def process_isdmails(isdmails):
	
	type_slowly("\nProcessing spawns from reports...\n\n")

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
			if submit_only_new_spawns is True:	
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

	# make and show the message text
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
	
	type_slowly("\nTask summary...\n\n")		
	print(message)

	# and send the message to Discord
	if discord_notify is True:	
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
			url = submit_url + "?galaxy=" + galaxy_id + "&planet=" + planet + "&resName=" + resname + "&resType=" + restype + "&CR=" + CR + "&CD=" + CD + "&DR=" + DR + "&FL=" + FL + "&HR=" + HR + "&MA=" + MA + "&PE=" + PE + "&OQ=" + OQ + "&SR=" + SR + "&UT=" + UT
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
        "username": discord_name,
        "content": message
    }

    for server_name, url in webhook_urls.items():
        try:
            response = httplib2.Http().request(
                url,
                'POST',
                urlencode(webhook_data).encode('utf-8'),  
                headers={'Content-Type': 'application/x-www-form-urlencoded'}
            )
            print(f"{server_name} webhook response: {response[0].status}")
        
        except Exception as e:
            print(f"{server_name} webhook error: {e}")

def move_to_archive(mail_folder_path):

	if not os.path.exists(archive_folder_path):
		os.makedirs(archive_folder_path)

	for filename in os.listdir(mail_folder_path):
		if filename.endswith('.mail'):
			source_file = os.path.join(mail_folder_path, filename)
			destination_file = os.path.join(archive_folder_path, filename)
			os.rename(source_file, destination_file)

###########	start here ###########

config = load_config()

try:
	banner = config['settings']['banner']
	title = config['settings']['title']
	show_banner = ast.literal_eval(config['settings']['show_banner'])
	safety_checks = ast.literal_eval(config['settings']['safety_checks'])
	max_age_hours = int(config['settings']['max_age_hours'])
	archive_mail_files = ast.literal_eval(config['settings']['archive_mail_files'])

	archive_folder_path = config['paths']['archive_folder_path']
	mail_folder_path = config['paths']['mail_folder_path']
	restypes_file = config['paths']['restypes_file']
	
	galaxy_id = config['galaxyharvester']['galaxy_id']
	gh_name = config['galaxyharvester']['gh_name']
	gh_pass = config['galaxyharvester']['gh_pass']
	data_url = "https://galaxyharvester.net/exports/current" + galaxy_id + ".xml"
	login_url = config['galaxyharvester']['login_url']
	submit_url = config['galaxyharvester']['submit_url']
	submit_only_new_spawns = ast.literal_eval(config['galaxyharvester']['submit_only_new_spawns'])	

	discord_name = config['discord']['discord_name']
	discord_notify = ast.literal_eval(config['discord']['discord_notify'])
	webhook_urls = dict(config.items('webhook_urls'))
except (ValueError, KeyError) as e:
	sys.exit(f"Error: Missing or invalid configuration option {e}")

if show_banner is True:
	print(f"\033[1;33m{banner}\033[0m")
	print(f"\t     {title}")	

session = gh_login()	
gh_current_resnames = fetch_gh_data()		
find_isdmails(mail_folder_path, max_age_hours)	

if archive_mail_files is True:
	move_to_archive(mail_folder_path)