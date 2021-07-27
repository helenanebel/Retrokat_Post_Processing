import json
import re

with open('C:/Users/hnebel/Documents/start_harvests.sh', 'w') as sh_file:
    sh_file.write('# !/bin/bash\n')
    with open('C:/Users/hnebel/Documents/zotero_harvester.conf', 'r', encoding="utf-8") as conf_file:
        search_id = False
        for line in conf_file.readlines():
            if (line[0] == '['):
                if line not in ['[IxTheo]\n', '[KrimDok]\n']:
                    title = re.findall(r'\[(.+)]\n', line)[0]
                    search_id = True
            if search_id:
                if re.findall(r'zeder_id\s*=\s*(\d+)\n', line):
                    zid = re.findall(r'zeder_id\s*=\s*(\d+)\n', line)[0]
                    raw_command = 'nohup /usr/local/bin/zotero_harvester "--min-log-level=DEBUG" "--force-downloads" "--output-directory=/tmp/{0}" "--output-filename={0}.xml" "--config-overrides=skip_online_first_articles_unconditionally=true" "/usr/local/var/lib/tuelib/zotero-enhancement-maps/zotero_harvester.conf" "JOURNAL" "{1}" &> out_{0}.out &\n'
                    command = raw_command.format(zid, title)
                    sh_file.write(command)
                    search_id = False
