import json
import re
import urllib.request
from bs4 import BeautifulSoup

all_zids = []
download_command_file = open('C:/Users/hnebel/Documents/download_commands.txt', 'w')
total_journal_number = 0
is_muse = False
muse_nr = 1
with open('C:/Users/hnebel/Documents/start_harvests.sh', 'w') as sh_file:
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
            if re.findall(r'zotero_update_window\s*=\s*(\d+)\n', line):
                do_harvest = re.findall(r'zotero_update_window\s*=\s*(\d+)\n', line)
                if do_harvest not in [['000'], ['111']]:
                    print('Fehler! Ungültige Angabe in zotero_update_window!')
                elif do_harvest == ['000']:
                    continue
                if total_journal_number % 10 == 0:
                    sh_file.write('wait; sudo systemctl restart zts;\n')
                if not is_muse:
                    raw_download_command = 'scp hnebel@benu.ub.uni-tuebingen.de:/home/hnebel/{0}/ixtheo/{0}.xml .\n'
                    download_command = raw_download_command.format(zid)
                    download_command_file.write(download_command)
                    raw_harvesting_command = 'nohup /usr/local/bin/zotero_harvester "--min-log-level=DEBUG" "--force-downloads" "--output-directory=/home/hnebel/{0}" "--output-filename={0}.xml" "--config-overrides=skip_online_first_articles_unconditionally=true" "/usr/local/var/lib/tuelib/zotero-enhancement-maps/zotero_harvester.conf" "JOURNAL" "{1}" &> "out_{0}.out";\n'
                    harvesting_command = raw_harvesting_command.format(zid, title)
                    sh_file.write('wait; ' + harvesting_command)
                    total_journal_number += 1
                    search_id = False
                else:
                    muse_nr = 1
                    total_journal_number += 1
                    muse_file = open('C:/Users/hnebel/Documents/conf-files/' + zid + '_' + str(muse_nr) + '.conf', 'w')
                    conf_nr = 0
                    muse_nr += 1
                    article_nr_in_file = 0
                    journal_page = urllib.request.urlopen(muse_url)
                    data = journal_page.read()
                    journal_soup = BeautifulSoup(data, "lxml")
                    issue_links = ['https://muse.jhu.edu/' + link for link in [tag['href'] for tag in journal_soup.find_all('a') if tag.has_attr('href')] if re.search(r'^/issue/\d+$', link)]
                    for issue_link in issue_links:
                        issue_page = urllib.request.urlopen(issue_link)
                        data = issue_page.read()
                        issue_soup = BeautifulSoup(data, "lxml")
                        article_nr = len(['https://muse.jhu.edu/' + link for link in
                                       [tag['href'] for tag in issue_soup.find_all('a') if tag.has_attr('href')] if
                                       re.search(r'^/article/\d+$', link)])
                        if (article_nr_in_file + article_nr) > 400:
                            raw_download_command = 'scp hnebel@benu.ub.uni-tuebingen.de:/home/hnebel/{0}/ixtheo/{1}.xml .\n'
                            download_command = raw_download_command.format(zid, zid + '_' + str(muse_nr))
                            download_command_file.write(download_command)
                            raw_harvesting_command = 'nohup /usr/local/bin/zotero_harvester "--min-log-level=DEBUG" "--force-downloads" "--output-directory=/home/hnebel/{0}" "--output-filename={1}.xml" "--config-overrides=skip_online_first_articles_unconditionally=true" "/usr/local/var/lib/tuelib/zotero-enhancement-maps/' + zid + '_' + str(
                                muse_nr) + '.conf' + '" "JOURNAL" &> "out_{1}.out";\n'
                            harvesting_command = raw_harvesting_command.format(zid, zid + '_' + str(muse_nr))
                            sh_file.write('wait; sleep 25m; wait;' + harvesting_command)
                            muse_file.close()
                            article_nr_in_file = article_nr
                            muse_file = open('C:/Users/hnebel/Documents/conf-files/' + zid + '_' + str(muse_nr) + '.conf', 'w')
                            conf_nr = 0
                            muse_conf = re.sub(r'\++]', ']', muse_conf)
                            muse_nr += 1
                        else:
                            article_nr_in_file += article_nr
                        muse_conf = re.sub(r'zotero_url\s*=\s*.+[^\n]*\n',
                                           'zotero_url     = ' + issue_link + '\n', muse_conf)
                        muse_conf = muse_conf.replace('\n\n', '\n')
                        if conf_nr > 0:
                            muse_conf = muse_conf.replace(title, title + '+')
                        muse_file.write(muse_conf + '\n')
                        conf_nr += 1
                    total_journal_number += 1
                    search_id = False
print(total_journal_number)
download_command_file.close()
