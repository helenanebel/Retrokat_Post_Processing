import json
import re
import urllib.request
from bs4 import BeautifulSoup

with open('zotero_harvester_header.conf', 'r') as zotero_harvester_header_file:
    zotero_harvester_header = zotero_harvester_header_file.read()

all_zids = []
download_command_file = open('C:/Users/hnebel/Documents/download_commands.txt', 'w')
total_journal_number = 0
is_muse = False
muse_nr = 1
is_vr = False
with open('C:/Users/hnebel/Documents/start_harvests.sh', 'w', newline='\n') as sh_file:
    sh_file.write('# !/bin/bash\n')
    with open('C:/Users/hnebel/Documents/zotero_harvester.conf', 'r', encoding="utf-8") as conf_file:
        get_conf = False
        search_id = False
        for line in conf_file.readlines():
            if get_conf:
                muse_conf += line
            if (line[0] == '['):
                if line not in ['[IxTheo]\n', '[KrimDok]\n']:
                    title = re.findall(r'\[(.+)]\n', line)[0]
                    search_id = True
                    is_muse = False
                    muse_conf = line
                    get_conf = True
            if search_id:
                if re.findall(r'zeder_id\s*=\s*(\d+)\n', line):
                    zid = re.findall(r'zeder_id\s*=\s*(\d+)\n', line)[0]
                    while zid in all_zids:
                        zid = zid + '+'
                    all_zids.append(zid)
            if re.findall(r'zotero_url\s*=\s*.+(muse\.jhu\.edu/).*\n', line):
                is_muse = True
                muse_url = re.findall(r'zotero_url\s*=\s*(.+muse\.jhu\.edu/.*)\n', line)[0]
            if re.findall(r'zotero_url\s*=\s*.+(.+cambridge\.org/core/.*).*\n', line):
                cambridge_url = re.findall(r'zotero_url\s*=\s*(.+cambridge\.org/core/.*)\n', line)[0]
            if re.findall(r'zotero_update_window\s*=\s*(\d+)\n', line):
                do_harvest = re.findall(r'zotero_update_window\s*=\s*(\d+)\n', line)
                # print(do_harvest)
                if do_harvest not in [['000'], ['111'], ['222']]:
                    print('Fehler! Ungültige Angabe in zotero_update_window!')
                elif do_harvest == ['000']:
                    continue
                elif do_harvest == ['222']:
                    journal_title = title
                    is_vr = True
                    vr_nr = 0
                    conf_nr = 0
                    vr_file = open('C:/Users/hnebel/Documents/conf-files/' + zid + '.conf', 'w',
                                     newline='\n')
                    vr_file.write(zotero_harvester_header)
                    article_nr_in_file = 0
                    with open('article_links/' + zid + '.json') as article_link_file:
                        article_links = json.load(article_link_file)
                    for article_link in article_links:

                        # print(article_link)
                        vr_nr += 1
                        if vr_nr < 2700:
                            continue
                        # zotero_crawl_url_regex auskommentieren!
                        muse_conf = re.sub(r'zotero_crawl_url_regex\s*=\s*.+[^\n]*\n',
                                           '', muse_conf)
                        muse_conf = re.sub(r'zotero_url\s*=\s*.+[^\n]*\n',
                                           'zotero_url     = ' + 'https://www.vr-elibrary.de' + article_link + '\n', muse_conf)
                        muse_conf = re.sub(r'zotero_max_crawl_depth\s*=\s*.+[^\n]*\n', 'zotero_max_crawl_depth  = 0\n', muse_conf)
                        muse_conf = muse_conf.replace('\n\n', '\n')
                        muse_conf = muse_conf.replace(title, journal_title + '_' + str(vr_nr))
                        title = journal_title + '_' + str(vr_nr)
                        vr_file.write(muse_conf + '\n')
                        raw_download_command = 'scp hnebel@benu.ub.uni-tuebingen.de:/home/hnebel/{0}/ixtheo/{1}.xml .\n'
                        download_command = raw_download_command.format(zid, zid + '_' + str(vr_nr))
                        download_command_file.write(download_command)
                        raw_harvesting_command = 'nohup /usr/local/bin/zotero_harvester "--min-log-level=DEBUG" "--force-downloads" "--output-directory=/home/hnebel/{0}" "--output-filename={1}.xml" "--config-overrides=skip_online_first_articles_unconditionally=true" "/usr/local/var/lib/tuelib/zotero-enhancement-maps/' + zid + '.conf' + '" "JOURNAL" "{2}" &> "{1}.out";\n'
                        harvesting_command = raw_harvesting_command.format(zid, zid + '_' + str(vr_nr), title)
                        sh_file.write('wait;' + harvesting_command)
                        if conf_nr % 270 == 0:
                            sh_file.write('wait; sudo systemctl restart zts;\n')
                        conf_nr += 1
                    print(vr_nr)
                    vr_file.close()
                    total_journal_number += 1
                    search_id = False
                if total_journal_number % 4 == 0:
                    sh_file.write('wait; sudo systemctl restart zts;\n')
                if (not is_muse) and (not is_vr):
                    raw_download_command = 'scp hnebel@benu.ub.uni-tuebingen.de:/home/hnebel/{0}/ixtheo/{0}.xml .\n'
                    download_command = raw_download_command.format(zid)
                    download_command_file.write(download_command)
                    raw_harvesting_command = 'nohup /usr/local/bin/zotero_harvester "--min-log-level=DEBUG" "--force-downloads" "--output-directory=/home/hnebel/{0}" "--output-filename={0}.xml" "--config-overrides=skip_online_first_articles_unconditionally=true" "/usr/local/var/lib/tuelib/zotero-enhancement-maps/zotero_harvester.conf" "JOURNAL" "{1}" &> "{0}.out";\n'
                    harvesting_command = raw_harvesting_command.format(zid, title)
                    sh_file.write('wait; ' + harvesting_command)
                    total_journal_number += 1
                    search_id = False
                elif is_muse:
                    muse_nr = 0
                    conf_nr = 0
                    muse_file = open('C:/Users/hnebel/Documents/conf-files/' + zid + '_' + str(conf_nr) + '.conf', 'w', newline='\n')
                    muse_file.write(zotero_harvester_header)
                    article_nr_in_file = 0
                    journal_page = urllib.request.urlopen(muse_url)
                    data = journal_page.read()
                    journal_soup = BeautifulSoup(data, "lxml")
                    issue_links = ['https://muse.jhu.edu' + link for link in [tag['href'] for tag in journal_soup.find_all('a') if tag.has_attr('href')] if re.search(r'^/issue/\d+$', link)]
                    for issue_link in issue_links:
                        print(issue_link)
                        muse_conf = re.sub(r'zotero_url\s*=\s*.+[^\n]*\n',
                                           'zotero_url     = ' + issue_link + '\n', muse_conf)
                        muse_conf = re.sub(r'zotero_max_crawl_depth\s*=\s*.+[^\n]*\n', '', muse_conf)
                        muse_conf = muse_conf.replace('\n\n', '\n')
                        if conf_nr > 0:
                            muse_conf = muse_conf.replace(title, title + '+')
                            title = title.replace(title, title + '+')
                        muse_file.write(muse_conf + '\n')
                        raw_download_command = 'scp hnebel@benu.ub.uni-tuebingen.de:/home/hnebel/{0}/ixtheo/{1}.xml .\n'
                        download_command = raw_download_command.format(zid, zid + '_' + str(conf_nr))
                        download_command_file.write(download_command)
                        raw_harvesting_command = 'nohup /usr/local/bin/zotero_harvester "--min-log-level=DEBUG" "--force-downloads" "--output-directory=/home/hnebel/{0}" "--output-filename={1}.xml" "--config-overrides=skip_online_first_articles_unconditionally=true" "/usr/local/var/lib/tuelib/zotero-enhancement-maps/' + zid + '_' + str(
                            muse_nr) + '.conf' + '" "JOURNAL" "{2}" &> "{1}.out";\n'
                        harvesting_command = raw_harvesting_command.format(zid, zid + '_' + str(conf_nr), title)
                        sh_file.write('wait;' + harvesting_command)
                        sh_file.write('wait; sleep 25m;\n')
                        if conf_nr % 10 == 0:
                            sh_file.write('wait; sudo systemctl restart zts;\n')
                        conf_nr += 1
                    muse_file.close()
                    total_journal_number += 1
                    search_id = False
                sh_file.write('wait; sleep 15m;\n')
print(total_journal_number)
download_command_file.close()
print("Dateien auf den Server hochladen & Skript auf BENU starten:")
print("cd /Users/hnebel/Documents")
print("scp start_harvests.sh hnebel@benu.ub.uni-tuebingen.de:/home/hnebel"
      "\nscp zotero_harvester.conf hnebel@benu.ub.uni-tuebingen.de:/usr/local/zotero-enhancement-maps/hnebel_retrokat/zotero-enhancement-maps/zotero_harvester.conf\nssh hnebel@benu.ub.uni-tuebingen.de\nnohup ./start_harvests.sh &")
