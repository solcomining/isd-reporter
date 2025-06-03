### ISD Reporter
Tools to manage Interplanetary Survey Droid tasks for SWGEmu. Can send droids ingame, parse spawn info from saved emails, and submit spawn info to Galaxy Harvester. 

Get permission from your server admin before using Auto-It to automate keyboard and mouse control. I'm not responsible if you get banned.

| Filename           |            |
| :----------------- | :--------- |
| isdreporter.au3    | Auto-It script. Uses hotkeys ingame to automate sending ISD droids. |
| isdreporter.py     | Python script. Processes saved ISD emails and submits spawn info to Galaxy Harvester. |
| isdreporter.cfg    | Config file for the Python script.|
| SwgMail.py 		     | Mail parsing class (courtesy of Dasch). |
| restypes.txt 	     | All resource types in SWG and Galaxy Harvester format. Should work for any server. |
| restypeseif.txt    | EiF non-creature resource types. Faster than using above (recommend making an equivalent for your own server). |

### Usage
1. Start SWG in windowed mode.
2. (optional) Start AutoIt editor/terminal (SciTE) as admin, load `isdreporter.au3`, press `F5` to run the script.
3. Manually get stacks of ISD droids from a crate ingame. I normally use 3 stacks (for chemical, flora, and mineral).
4. (optional) Use the `ctrl-shift-t` hotkey ingame to auto-get a set of survey tools from a crate.
5. (optional) Use the `ctrl-shift-d` hotkey ingame to auto-send a stack of ISD droids.
6. (optional) Press `ESC` ingame to end the Auto-It script.
7. After the ISD emails arrive, use the `/mailsave` command ingame.
8. After the ISD emails have been saved, use the `/emptymail` command ingame (or manually delete the ISD emails).
9. Run `isdreporter.py` to process the saved emails and submit new spawns to Galaxy Harvester.

### Python config
Minimum to edit would be `mail_folder_path`, `galaxy_id`, `gh_name`, and `gh_pass`. Discord and archive features are optional. 

| isdreporter.cfg     |            |
| :--------------     | :--------- |
| [settings]          |            |
| safety_checks       | True to enable y/n confirmation. Recommend True.         |
| max_age_hours       | .mail files older than this will not be processed.          |
| archive_mail_files  | True to move processed .mail files to `archive_folder_path`         |
| [paths]             |             |
| archive_folder_path | .mail files get moved here after processing. |
| mail_folder_path    | Something like `/mnt/c/Games/SWGInstall/profiles/username/servername/mail_firstname lastname` (spaces are ok) |
| restypes_file       | For improved speed, recommend editing `restypes.txt` to suit your own server. |
| [galaxyharvester]   |
| galaxy_id           | DO NOT get this wrong. It comes from e.g : https://galaxyharvester.net/resource.py/99/exampleism |
| gh_name             | Username |
| gh_pass             | Password |
| login_url           | To use a different server other than galaxyharvester.net |
| submit_url          | To use a different server other than galaxyharvester.net  |
| submit_only_new_spawns | False to submit every spawn, i.e to verify existing spawns. |
| [discord]           |
| discord_name        | The name of the Discord message sender. |
| discord_notify      | True to send Discord webhook messages. |
| [webhook_urls]      |
| AnyNameHere1        | Discord webhook URL. Any name and number of servers will work.  |
| AnyNameHere2        | Discord webhook URL. Any name and number of servers will work.  |
| AnyNameHere3        | Discord webhook URL. Any name and number of servers will work.  |

### Caveats
1. Be careful with the `galaxy_id` value. You don't want to submit to the wrong galaxy.
2. `isdreporter.py` does not mark expired spawns as unavailable. 
3. `isdreporter.py` processes .mail files sequentially, and submits new spawns as it finds them. A new spawn is one that is found in a .mail file but not in the GH data export.

### Auto-It config
Using Auto-It is optional. Download is available from: https://www.autoitscript.com/site/autoit/downloads/

| isdreporter.au3    |            |
| :----------------- | :--------- |
| $delayms           | Delay between actions, in ms. |
| $tools             | Number of survey tools to use. This should match the number of planets and uses per ISD stack. |
| $aToolPos          | Where to click in the "Choose survey tool" window. |
| $aPlanetNames      | List of planet names as shown in the "Choose planet" window. |
| $aPlanetPos        | List of Y coordinates to click in the "Choose planet" window.  |

By default `isdreporter.au3` is configured for 13 survey tools being used by a 13-use ISD stack for 13 planets, and with the ISD windows positioned top right on a 1080p screen. To edit the script to account for other screen resolutions, take a screenshot of the positioned ISD windows and use MS Paint to find the x,y coordinates.

### Ingame config if using Auto-It
1. The "Choose survey tool" window must be positioned top right corner. Sized as narrow and short as possible at 1080p.
2. The "Choose planet" window must be positioned top right corner. Sized as narrow and tall as possible at 1080p.
3. The stack of ISD droids must not move around in the inventory. Sorting inventory by type is helpful..

***
### Screenshots
Using the `ctrl-shift-t` hotkey ingame:

![isdreporterTools](https://github.com/user-attachments/assets/afa95446-0ad6-4130-9ab5-6758ac53f136)

Using the `ctrl-shift-d` hotkey ingame:

![isdreporterDroids](https://github.com/user-attachments/assets/69e7a6d1-c1c9-41e8-b317-78aca6080c79)

First safety check of the `isdreporter.py` script:

![isdreporter1n](https://github.com/user-attachments/assets/48f22ab0-3acb-4c89-bf18-114613e601f5)

Second safety check of the `isdreporter.py` script:

![isdreporter2n](https://github.com/user-attachments/assets/f0213bff-8eab-4b47-8024-2ba4e8483f94)

`isdreporter.py` submitting new spawns to Galaxy Harvester:

![isdreporter3n](https://github.com/user-attachments/assets/219fb1fb-4a7d-4d31-b46d-d18f728e8f46)

`isdreporter.py` completion:

![isdreporter4n](https://github.com/user-attachments/assets/c849e5ea-210c-4632-9816-9d4c5fc666a1)

Discord webhook message:

![isdreporterWebhookMessage](https://github.com/user-attachments/assets/95a55c3d-f71f-4b37-96a5-f055351de19e)

Positioning of the "Choose survey tool" window at 1080p:

![isdreporterWindowPos1](https://github.com/user-attachments/assets/9fa6168b-fda2-42b0-9439-96834bad3977)

Positioning of the "Choose planet" window at 1080p:

![isdreporterWindowPos2](https://github.com/user-attachments/assets/08146b02-6abc-4cf3-bb86-34a5c8806a70)








