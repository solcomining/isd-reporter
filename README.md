### ISD Reporter
Tools to manage Interplanetary Survey Droids in SWGEmu.

### Files
| Filename           |            |
| :----------------- | :--------- |
| isdreporter.au3    | Auto-It script. Uses hotkeys ingame to automate sending ISD droids. |
| isdreporter.py     | Python script. Processes saved ISD mails. Submits new spawns to Galaxy Harvester. |
| SwgMail.py 		     | Mail parsing class (courtesy of Dasch). |
| restypes.txt 	     | All resource types in SWG and Galaxy Harvester format. Should work for any server. |
| restypeseif.txt    | EiF non-creature resource types. Faster than using above (recommend making an equivalent for your own server). |
| current.xml			   | Current Galaxy Harvester data export (created/downloaded during runtime). |

### Usage
1. Start SWG in windowed mode.
2. Start AutoIt editor/terminal (SciTE) as admin, load `isdreporter.au3`, press `F5` to run the script.
3. Manually get stacks of ISD droids from a crate ingame. I normally use 3 stacks (for chemical, flora, and mineral).
4. Use the `ctrl-shift-t` hotkey ingame to auto-get a set of survey tools from a crate.
5. Use the `ctrl-shift-d` hotkey ingame to auto-send a stack of ISD droids.
6. Press `ESC` ingame to end the script.
7. After the ISD emails arrive, use the `/mailsave` command ingame.
8. After the ISD emails have been saved, use the `/emptymail` command ingame (or manually delete the ISD emails).
9. Run `isdreporter.py` to process the saved mails and submit new spawns to Galaxy Harvester.

### Ingame config
1. The "Choose survey tool" window must be positioned top right corner. Sized as narrow and short as possible at 1080p.
2. The "Choose planet" window must be positioned top right corner. Sized as narrow and tall as possible at 1080p.
3. The stack of ISD droids must not move around in the inventory. Sorting inventory by type helps to avoid that.

### Auto-It config
Download is available from: https://www.autoitscript.com/site/autoit/downloads/

| isdreporter.au3    |            |
| :----------------- | :--------- |
| $delayms           | Delay between actions, in ms. |
| $tools             | Number of survey tools to use. This should match the number of planets and uses per ISD stack. |
| $aToolPos          | Where to click in the "Choose survey tool" window. |
| $aPlanetNames      | List of planet names as shown in the "Choose planet" window. |
| $aPlanetPos        | List of Y coordinates to click in the "Choose planet" window.  |

By default `isdreporter.au3` is configured for 13 survey tools being used by a 13-use ISD stack for 13 planets, and with the ISD windows positioned top right on a 1080p screen. To edit the script to account for other screen resolutions, take a screenshot of the positioned ISD windows and use MS Paint to find the x,y coordinates.

### Python config
| isdreporter.py     |            |
| :----------------- | :--------- |
| submit_everything  | False to only submit new spawns to Galaxy Harvester. Recommend False. |
| notify_discord     | True to send Discord webhook messages. |
| safety_checks      | False to disable y/n confirmation at config and mail stages. Recommend True. |
| mail_folder_path   | If using WSL, path looks like `/mnt/c/Games/EmpireInFlames/profiles/username/Starsider/mail_charactername`|
| restypes_file      | Recommend editing `restypes.txt` to suit your own server. |
| max_age_hours      | .mail files older than this will not be processed. |
| galaxy_id 				 | DO NOT get this wrong. It comes from e.g : https://galaxyharvester.net/resource.py/99/exampleism |
| gh_name  					 | Extended characters might not work. |
| gh_pass            | Extended characters might not work. |
| webhook_name       | Name of the Discord message sender. |
| webhook_urls       | Any number of webhook urls will work. Their name can be whatever. The URL is created by a Discord server admin, from the integrations menu option. |

### Caveats
1. Be very careful with the `galaxy_id` value in `isdreporter.py`. 
2. `isdreporter.py` does not mark expired spawns as unavailable. 
3. `isdreporter.py` processes .mail files sequentially, and submits new spawns as it finds them.

An improved approach might be to process all mails into one structure, formatted similarly to current.xml. That would allow for creation of a set of new spawns, and a set of expired spawns. Then those sets could be submitted to Galaxy Harvester in one operation.

***
### Screenshots
Using the `ctrl-shift-t` hotkey ingame:

![isdreporterTools](https://github.com/user-attachments/assets/afa95446-0ad6-4130-9ab5-6758ac53f136)

Using the `ctrl-shift-d` hotkey ingame:

![isdreporterDroids](https://github.com/user-attachments/assets/69e7a6d1-c1c9-41e8-b317-78aca6080c79)

First safety check of the `isdreporter.py` script:

![isdreporter1n](https://github.com/user-attachments/assets/c68f31ea-89fe-4c4b-a780-9cbc935b6c05)

Second safety check of the `isdreporter.py` script:

![isdreporter2n](https://github.com/user-attachments/assets/92b22ead-59ab-4aa4-9fa0-1814acf70316)

`isdreporter.py` submitting new spawns to Galaxy Harvester:

![isdreporter3n](https://github.com/user-attachments/assets/f527d676-71f3-496b-831a-4d48c90c2600)

`isdreporter.py` completion:

![isdreporter4n](https://github.com/user-attachments/assets/c849e5ea-210c-4632-9816-9d4c5fc666a1)

Discord webhook message:

![isdreporterWebhookMessage](https://github.com/user-attachments/assets/95a55c3d-f71f-4b37-96a5-f055351de19e)






