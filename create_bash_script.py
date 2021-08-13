import json
import re

all_zids = []
download_command_file = open('C:/Users/hnebel/Documents/download_commands.txt', 'w')
with open('C:/Users/hnebel/Documents/start_harvests.sh', 'w') as sh_file:
    sh_file.write('# !/bin/bash\n')
    with open('C:/Users/hnebel/Documents/zotero_harvester.conf', 'r', encoding="utf-8") as conf_file:
        search_id = False
        set_sleep_timer = False
        for line in conf_file.readlines():
            if (line[0] == '['):
                if line not in ['[IxTheo]\n', '[KrimDok]\n']:
                    title = re.findall(r'\[(.+)]\n', line)[0]
                    search_id = True
            if search_id:
                if re.findall(r'zeder_id\s*=\s*(\d+)\n', line):
                    zid = re.findall(r'zeder_id\s*=\s*(\d+)\n', line)[0]
                    while zid in all_zids:
                        zid = zid + '+'
                    all_zids.append(zid)
            # if re.findall(r'zotero_url\s*=\s*.+(muse\.jhu\.edu/).*\n', line):
                # set_sleep_timer = True
            if re.findall(r'zotero_update_window\s*=\s*(\d+)\n', line):
                do_harvest = re.findall(r'zotero_update_window\s*=\s*(\d+)\n', line)
                if do_harvest not in [['000'], ['111']]:
                    print('Fehler! Ungültige Angabe in zotero_update_window!')
                elif do_harvest == ['000']:
                    continue
                raw_download_command = 'scp hnebel@benu.ub.uni-tuebingen.de:/tmp/{0}/ixtheo/{0}.xml .\n'
                download_command = raw_download_command.format(zid)
                download_command_file.write(download_command)
                raw_harvesting_command = 'nohup /usr/local/bin/zotero_harvester "--min-log-level=DEBUG" "--force-downloads" "--output-directory=/home/hnebel/{0}" "--output-filename={0}.xml" "--config-overrides=skip_online_first_articles_unconditionally=true" "/usr/local/var/lib/tuelib/zotero-enhancement-maps/zotero_harvester.conf" "JOURNAL" "{1}" &> "out_{0}.out";\n'
                harvesting_command = raw_harvesting_command.format(zid, title)
                sh_file.write('wait; ' + harvesting_command)
                if set_sleep_timer:
                    sh_file.write('sleep 30m;\n')
                search_id = False
                set_sleep_timer = False
download_command_file.close()
