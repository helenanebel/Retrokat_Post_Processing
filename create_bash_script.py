import json
import os
import re
from get_urls_download_failed import get_urls
from datetime import datetime
from shutil import copy2
import urllib.request
from bs4 import BeautifulSoup
from get_name import get_name

BENU_username = get_name()
with open('W:/FID-Projekte/Team Retro-Scan/Zotero/BENU/zotero_harvester_header.conf', 'r') as zotero_harvester_header_file:
    zotero_harvester_header = zotero_harvester_header_file.read()

upload_files = []
all_zids = []
time = datetime.now()
timestamp = time.strftime("%y-%m-%d__%H_%M")
download_command_file = open('W:/FID-Projekte/Team Retro-Scan/Zotero/BENU/download_commands_' + timestamp + '.txt', 'w')
check_success_file = open('W:/FID-Projekte/Team Retro-Scan/Zotero/BENU/check_success_' + timestamp + '.txt', 'w')
raw_check_success_command = 'cat {0}_*.out | egrep -c "Skipped \(undesired item type\): [^0]"\ncat {0}_*.out | egrep -c "Unsuccessful: [^0]"\ncat {0}_*.out | egrep -c "Unsuccessful *: [^0]"\ncat {0}_*.out | grep -c \'unable to normalize language: "*\'\ncat {0}_*.out | grep -c "couldn\'t convert record"\ncat {0}_*.out | grep -c "Aborted (core dumped)"\ncat {0}_*.out | egrep -c "Skipped \(exclusion filter\): [^0]"\nfind . \( \( -name "{0}_*.out" \) -prune -a \( -size -4100c \) -prune \) -a -print\n\nfind . -name "{0}_*.out" -exec grep -H "Aborted (core dumped)" {{}} \;\n\nfind . -name "{0}_*.out" -exec egrep -H "Skipped \(exclusion filter\): [^0]" {{}} \;\n\nfind . -name "{0}_*.out" -exec egrep -H "Skipped \(undesired item type\): [^0]" {{}} \;\n\nfind . -name "{0}_*.out" -exec egrep -H "Unsuccessful: [^0]" {{}} \;\n\nfind . -name "{0}_*.out" -exec egrep -H "Unsuccessful *: [^0]" {{}} \;\n\nfind . -name "{0}_*.out" -exec grep -H \'unable to normalize language: "*\' {{}} \;\n\nfind . -name "{0}_*.out" -exec grep -H "couldn\'t convert record" {{}} \;\n\nW:\ncd FID-Projekte/Team Retro-Scan/Zotero/results/\nscp -r {1}@benu.ub.uni-tuebingen.de:/home/{1}/{0}_out .\n\n\n'
failing_link_string = ""
total_journal_number = 0
total_muse_nr = 0
is_vr = False
with open('W:/FID-Projekte/Team Retro-Scan/Zotero/BENU/start_harvests.sh', 'w', newline='\n') as sh_file:
    sh_file.write('# !/bin/bash\n')
    sh_file.write('wait; sudo systemctl restart zts;\nsleep 1m;\n')
    with open('W:/FID-Projekte/Team Retro-Scan/Zotero/BENU/zotero_harvester.conf', 'r', encoding="utf-8") as conf_file:
        get_conf = False
        search_id = False
        for line in conf_file.readlines():
            if get_conf:
                muse_conf += line
            if (line[0] == '['):
                if line not in ['[IxTheo]\n', '[KrimDok]\n']:
                    title = re.findall(r'\[(.+)]\n', line)[0]
                    search_id = True
                    muse_conf = line
                    get_conf = True
            if search_id:
                if re.findall(r'zeder_id\s*=\s*(\d+)\n', line):
                    zid = re.findall(r'zeder_id\s*=\s*(\d+)\n', line)[0]
                    while zid in all_zids:
                        zid = zid + '+'
                    all_zids.append(zid)
            if re.findall(r'zotero_url\s*=\s*.+(.+cambridge\.org/core/.*).*\n', line):
                cambridge_url = re.findall(r'zotero_url\s*=\s*(.+cambridge\.org/core/.*)\n', line)[0]
            if re.findall(r'zotero_update_window\s*=\s*(\d+)\n', line):
                get_urls(zid)
                do_harvest = re.findall(r'zotero_update_window\s*=\s*(\d+)\n', line)
                # print(do_harvest)
                if do_harvest not in [['000'], ['111'], ['222'], ['333'], ['444']]:
                    print('Fehler! Ungültige Angabe in zotero_update_window!', zid)
                elif do_harvest == ['000'] and zid + '_failing_links.json' not in os.listdir():
                    continue
                elif do_harvest == ['111'] or zid + '_failing_links.json' in os.listdir():
                    if zid + '_failing_links.json' not in os.listdir():
                        raw_download_command_failing_urls = 'scp {1}@benu.ub.uni-tuebingen.de:/home/{1}/{0}/ixtheo/{0}.xml .\n'
                        download_command = raw_download_command_failing_urls.format(zid, BENU_username)
                        download_command_file.write('W:\n')
                        download_command_file.write('cd FID-Projekte/Team Retro-Scan/Zotero/results/\n')
                        download_command_file.write(download_command)
                        raw_harvesting_command = '/usr/local/bin/zotero_harvester "--min-log-level=DEBUG" "--force-downloads" "--output-directory=/home/{2}/{0}" "--output-filename={0}.xml" "--config-overrides=skip_online_first_articles_unconditionally=true" "/usr/local/var/lib/tuelib/zotero-enhancement-maps/zotero_harvester.conf" "JOURNAL" "{1}" > "{0}.out" 2>&1;\n'
                        harvesting_command = raw_harvesting_command.format(zid, title, BENU_username)
                        sh_file.write('wait; ' + harvesting_command)
                        raw_check_success_command_single_file = 'cat {0}.out | egrep -c "Skipped \(undesired item type\): [^0]"\ncat {0}.out | egrep -c "Unsuccessful: [^0]"\ncat {0}.out | egrep -c "Unsuccessful *: [^0]"\ncat {0}.out | grep -c \'unable to normalize language: "*\'\ncat {0}.out | grep -c "couldn\'t convert record"\ncat {0}.out | grep -c "Aborted (core dumped)"\ncat {0}.out | egrep -c "Skipped \(exclusion filter\): [^0]"\nfind . \( \( -name "{0}.out" \) -prune -a \( -size -4100c \) -prune \) -a -print\n\nfind . -name "{0}.out" -exec grep -H "Aborted (core dumped)" {{}} \;\n\nfind . -name "{0}.out" -exec egrep -H "Skipped \(exclusion filter\): [^0]" {{}} \;\n\nfind . -name "{0}.out" -exec egrep -H "Skipped \(undesired item type\): [^0]" {{}} \;\n\nfind . -name "{0}.out" -exec egrep -H "Unsuccessful: [^0]" {{}} \;\n\nfind . -name "{0}.out" -exec egrep -H "Unsuccessful *: [^0]" {{}} \;\n\nfind . -name "{0}.out" -exec grep -H \'unable to normalize language: "*\' {{}} \;\n\nfind . -name "{0}.out" -exec grep -H "couldn\'t convert record" {{}} \;\n\nW:\ncd FID-Projekte/Team Retro-Scan/Zotero/results/\nscp {1}@benu.ub.uni-tuebingen.de:/home/{1}/{0}.out .\n\n\n'
                        check_success_command = raw_check_success_command_single_file.format(zid, BENU_username)
                        check_success_file.write(check_success_command)
                        total_journal_number += 1
                        search_id = False
                    else:
                        waiting_time = 0
                        journal_title = title
                        is_vr = True
                        vr_nr = 0
                        conf_nr = 0
                        sh_file.write('wait;' + 'mkdir ' + zid + '_out;\n')
                        vr_file = open('W:/FID-Projekte/Team Retro-Scan/Zotero/BENU/conf-files/' + zid + '.conf', 'w',
                                       newline='\n')
                        upload_files.append(zid + '.conf')
                        vr_file.write(zotero_harvester_header)
                        article_nr_in_file = 0
                        article_list = []
                        with open(zid + '_failing_links.json') as article_link_file:
                            article_links = json.load(article_link_file)
                            if zid + '.json' in os.listdir('W:/FID-Projekte/Team Retro-Scan/Zotero/article_links/'):
                                with open('W:/FID-Projekte/Team Retro-Scan/Zotero/article_links/' + zid + '.json') as previous_article_link_file:
                                    article_list = json.load(previous_article_link_file)
                        for article_link in article_links:
                            vr_nr += 1
                            if article_list:
                                index = article_list.index(article_link) + 1
                            else:
                                index = vr_nr
                            muse_conf = re.sub(r'zotero_crawl_url_regex\s*=\s*.+[^\n]*\n',
                                               '', muse_conf)
                            muse_conf = re.sub(r'zotero_url\s*=\s*.+[^\n]*\n',
                                               'zotero_url     = ' + article_link + '\n', muse_conf)
                            muse_conf = re.sub(r'zotero_max_crawl_depth\s*=\s*.+[^\n]*\n',
                                               'zotero_max_crawl_depth  = 0\n', muse_conf)
                            new_extraction_regex = article_link.replace('/', '\/')
                            muse_conf = re.sub(r'zotero_extraction_regex\s*=\s*.+[^\n]*\n',
                                               'zotero_extraction_regex  = ' + new_extraction_regex + '\n', muse_conf)
                            muse_conf = re.sub(r'zotero_type\s*=\s*.+[^\n]*\n', 'zotero_type  = DIRECT\n', muse_conf)
                            muse_conf = muse_conf.replace('\n\n', '\n')
                            muse_conf = muse_conf.replace(title, journal_title + '_' + str(index))
                            title = journal_title + '_' + str(index)
                            # print(title)
                            vr_file.write(muse_conf + '\n')
                            raw_harvesting_command_failing_url = '/usr/local/bin/zotero_harvester "--min-log-level=DEBUG" "--force-downloads" "--output-directory=/home/{3}/{0}" "--output-filename={1}.xml" "--config-overrides=skip_online_first_articles_unconditionally=true" "/usr/local/var/lib/tuelib/zotero-enhancement-maps/' + zid + '.conf' + '" "JOURNAL" "{2}" > "{0}_out/{1}.out" 2>&1 1>"{0}_out/{1}.out";\n'
                            failing_link_string += 'wait;' + raw_harvesting_command_failing_url.format(zid, zid + '_' + str(index), title, BENU_username)
                            failing_link_string += 'wait; sleep 10s;\n'
                            waiting_time += 10
                        raw_download_command = 'scp -r {1}@benu.ub.uni-tuebingen.de:/home/{1}/{0}/ixtheo {0}\n'
                        download_command = raw_download_command.format(zid, BENU_username)
                        download_command_file.write('W:\n')
                        download_command_file.write('cd FID-Projekte/Team Retro-Scan/Zotero/results/\n')
                        download_command_file.write(download_command)
                        check_success_command = raw_check_success_command.format(zid, BENU_username)
                        check_success_file.write(check_success_command)
                        print(vr_nr)
                        vr_file.close()
                        total_journal_number += 1
                        search_id = False
                        print('Wartezeit:', waiting_time / 3600)
                elif do_harvest in [['222'], ['333']]:
                    waiting_time = 0
                    journal_title = title
                    is_vr = True
                    vr_nr = 0
                    conf_nr = 0
                    vr_file = open('W:/FID-Projekte/Team Retro-Scan/Zotero/BENU/conf-files/' + zid + '.conf', 'w',
                                     newline='\n')
                    sh_file.write('wait;' + 'mkdir ' + zid + '_out;\n')
                    upload_files.append(zid + '.conf')
                    vr_file.write(zotero_harvester_header)
                    article_nr_in_file = 0
                    with open('W:/FID-Projekte/Team Retro-Scan/Zotero/article_links/' + zid + '.json') as article_link_file:
                        article_links = json.load(article_link_file)
                    raw_harvesting_command_article_download = '/usr/local/bin/zotero_harvester "--min-log-level=DEBUG" "--force-downloads" "--output-directory=/home/{3}/{0}" "--output-filename={1}.xml" "--config-overrides=skip_online_first_articles_unconditionally=true" "/usr/local/var/lib/tuelib/zotero-enhancement-maps/' + zid + '.conf' + '" "JOURNAL" "{2}" > "{0}_out/{1}.out" 2>&1;\n'
                    for article_link in article_links:
                        vr_nr += 1
                        # zotero_crawl_url_regex auskommentieren!
                        muse_conf = re.sub(r'zotero_crawl_url_regex\s*=\s*.+[^\n]*\n',
                                           '', muse_conf)
                        muse_conf = re.sub(r'zotero_url\s*=\s*.+[^\n]*\n',
                                           'zotero_url     = ' + article_link + '\n', muse_conf)
                        muse_conf = re.sub(r'zotero_max_crawl_depth\s*=\s*.+[^\n]*\n', 'zotero_max_crawl_depth  = 0\n', muse_conf)
                        muse_conf = re.sub(r'zotero_type\s*=\s*.+[^\n]*\n', 'zotero_type  = DIRECT\n', muse_conf)
                        muse_conf = muse_conf.replace('\n\n', '\n')
                        muse_conf = muse_conf.replace(title, journal_title + '_' + str(vr_nr))
                        title = journal_title + '_' + str(vr_nr)
                        try:

                            vr_file.write(muse_conf + '\n')
                        except:
                            print(muse_conf)
                        harvesting_command = raw_harvesting_command_article_download.format(zid, zid + '_' + str(vr_nr), title, BENU_username)
                        sh_file.write('wait;' + harvesting_command)
                        if do_harvest == ['333']:
                            sh_file.write('wait; sleep 4s;\n')
                            waiting_time += 4
                        if do_harvest == ['333']:
                            if conf_nr != 0:
                                if "dialnet.unirioja.es" in article_link:
                                    if conf_nr % 15 == 0:
                                        sh_file.write('wait; sleep 20m;\n')
                                        waiting_time += 1200
                                elif "journals.uchicago.edu" in article_link:
                                    if conf_nr % 3000 == 0:
                                        sh_file.write('wait; sleep 20m;\n')
                                        waiting_time += 1200
                                elif "muse.jhu.edu" in article_link:
                                    total_muse_nr += 1
                                    if total_muse_nr % 400 == 0:
                                        sh_file.write('wait; sleep 10h;\n')
                                        waiting_time += 36000
                                elif "brill.com/" in article_link:
                                    if conf_nr % 400 == 0:
                                        sh_file.write('wait; sleep 30m;\n')
                                        waiting_time += 1800
                                    elif conf_nr % 100 == 0:
                                        sh_file.write('wait; sleep 5m;\n')
                                        waiting_time += 300
                                # sh_file.write('wait; sudo systemctl restart zts;\n')
                        conf_nr += 1
                    raw_download_command_article_download = 'scp -r {1}@benu.ub.uni-tuebingen.de:/home/{1}/{0}/ixtheo {0}\n'
                    download_command = raw_download_command_article_download.format(zid, BENU_username)
                    download_command_file.write('W:\n')
                    download_command_file.write('cd FID-Projekte/Team Retro-Scan/Zotero/results/\n')
                    download_command_file.write(download_command)
                    check_success_command = raw_check_success_command.format(zid, BENU_username)
                    check_success_file.write(check_success_command)
                    print(vr_nr)
                    vr_file.close()
                    total_journal_number += 1
                    search_id = False
                    print('Wartezeit:', waiting_time/3600)
                elif do_harvest == ['444']:
                    issn_to_ppn_file = open('W:/FID-Projekte/Team Retro-Scan/Zotero/BENU/issn_to_ppn.json', 'r')
                    issn_to_ppn = json.load(issn_to_ppn_file)
                    issn_to_ppn_file.close()

                    # vorhandene DOIs hinterlegen, dann jeweils für das aktuelle + das letzte Jahr neue DOIs suchen und diese hinzufügen
                    # jeweils gegenprüfen
                    #
                    conf_nr = 0
                    vr_nr = 0
                    vr_file = open('W:/FID-Projekte/Team Retro-Scan/Zotero/BENU/conf-files/' + zid + '.conf', 'w',
                                   newline='\n')
                    sh_file.write('wait;' + 'mkdir ' + zid + '_out;\n')
                    upload_files.append(zid + '.conf')
                    vr_file.write(zotero_harvester_header)
                    article_nr_in_file = 0
                    with open('W:/FID-Projekte/Team Retro-Scan/Zotero/article_links/' + zid + '.json') as article_link_file:
                        article_links = json.load(article_link_file)
                    raw_download_command_444 = 'scp -r {1}@benu.ub.uni-tuebingen.de:/home/{1}/{0}/ixtheo {0}\n'
                    download_command = raw_download_command_444.format(zid, BENU_username)
                    download_command_file.write('W:\n')
                    download_command_file.write('cd FID-Projekte/Team Retro-Scan/Zotero/results/\n')
                    download_command_file.write(download_command)
                    check_success_command = raw_check_success_command.format(zid, BENU_username)
                    check_success_file.write(check_success_command)
                    raw_harvesting_command_444 = '/usr/local/bin/zotero_harvester "--min-log-level=DEBUG" "--force-downloads" "--output-directory=/home/{3}/{0}" "--output-filename={1}.xml" "--config-overrides=skip_online_first_articles_unconditionally=true" "/usr/local/var/lib/tuelib/zotero-enhancement-maps/' + zid + '.conf' + '" "JOURNAL" "{2}" > "{0}_out/{1}.out" 2>&1;\n'
                    base_conf = '[{0}_{1}]\nzeder_id = 0000\nzeder_modified_time = "2022-02-22 02:22:22"\nonline_ppn = {2}\nonline_issn = {3}\nzotero_type = DIRECT\nzotero_delivery_mode = TEST\nzotero_group = IxTheo\nzotero_url = {4}\nzotero_expected_languages = eng,ger,fre,ita,spa,dut\n# ssgn =\nselective_evaluation = false\nzotero_review_regex = (?i)^(Books?\s+)?Reviews?\nzotero_extraction_regex = \/doi\/\n\n'
                    conf_string = ""

                    # wegen ssgn nachfragen
                    # wegen Suche nachfragen

                    all_issns = list(set([article_links[article_url] for article_url in article_links]))
                    for issn in all_issns:
                        if issn not in issn_to_ppn:
                            search_issn = issn[:8]
                            url = "https://sru.k10plus.de/opac-de-627?version=1.1&operation=searchRetrieve&query=pica.iss%3D{0}+AND+pica.bbg%3Dob*&maximumRecords=10&recordSchema=picaxml".format(search_issn)
                            xml_data = urllib.request.urlopen(url)
                            xml_soup = BeautifulSoup(xml_data, features='lxml')
                            if xml_soup.find('zs:numberofrecords').text != '0':
                                if xml_soup.find('zs:numberofrecords').text == '1':
                                    for record in xml_soup.find_all('record'):
                                        ppn = record.find('datafield', tag='003@').find('subfield', code='0').text
                                        if record.find('datafield', tag='021A'):
                                            title = record.find('datafield', tag='021A').find('subfield', code='a').text
                                        if record.find('datafield', tag='011@'):
                                            appearance = record.find('datafield', tag='011@').find('subfield', code='n').text
                                        issn_to_ppn[issn] = {'title': title, 'ppn': ppn, 'appearance': appearance, 'issn': search_issn}
                                else:
                                    print('found multiple matches:', issn)
                            else:
                                print('found no matches:', issn)
                    for article_url in article_links:
                        conf_nr += 1
                        vr_nr += 1
                        article_doi = re.findall(r'/doi/(.+)$', article_url)
                        if article_doi:
                            url = "https://sru.k10plus.de/opac-de-627?version=1.1&operation=searchRetrieve&query=pica.doi%3D{0}&maximumRecords=10&recordSchema=picaxml".format(
                                article_doi[0].replace('/', '*'))
                            xml_data = urllib.request.urlopen(url)
                            xml_soup = BeautifulSoup(xml_data, features='lxml')
                            if xml_soup.find('zs:numberofrecords').text != '0':
                                print('found doi', article_doi)
                                continue
                        if article_links[article_url] in issn_to_ppn:
                            journal = issn_to_ppn[article_links[article_url]]
                            conf = base_conf.format(journal['title'], str(conf_nr), journal['ppn'], journal['issn'], article_url)
                            conf_string += conf
                            vr_file.write(conf)
                            harvesting_command = raw_harvesting_command_444.format(zid, zid + '_' + str(vr_nr), journal['title'] + '_' + str(vr_nr), BENU_username)
                            sh_file.write('wait;' + harvesting_command)

                        else:
                            print('issn', article_links[article_url], 'not found')
                    print(vr_nr)
                    vr_file.close()
                    total_journal_number += 1
                    search_id = False
                    with open('W:/FID-Projekte/Team Retro-Scan/Zotero/BENU/issn_to_ppn.json', 'w', encoding='utf-8') as issn_to_ppn_file:
                        json.dump(issn_to_ppn, issn_to_ppn_file)
                if total_journal_number % 5 == 0:
                    sh_file.write('wait; sudo systemctl restart zts;\nsleep 1m;\n')
                sh_file.write('wait; sleep 3m;\n')
print(total_journal_number)
if failing_link_string:
    with open('W:/FID-Projekte/Team Retro-Scan/Zotero/BENU/failing_links_download_commands_' + timestamp + '.txt', 'w') as failing_link_file:
        failing_link_file.write(failing_link_string)
download_command_file.close()
check_success_file.close()
copy2('W:/FID-Projekte/Team Retro-Scan/Zotero/BENU/zotero_harvester.conf', 'W:/FID-Projekte/Team Retro-Scan/Zotero/zotero_harvester_backup/Zotero_harvester' + timestamp + '.conf')
print("Dateien auf den Server hochladen & Skript auf BENU starten:")
print('W:')
print("cd FID-Projekte/Team Retro-Scan/Zotero/BENU/")
upload_string = ""
for file in upload_files:
    upload_string += "\nscp conf-files/{0} {1}@benu.ub.uni-tuebingen.de:/usr/local/zotero-enhancement-maps/{1}_retrokat/zotero-enhancement-maps/{0}".format(file, BENU_username)
print("scp start_harvests.sh {0}@benu.ub.uni-tuebingen.de:/home/{0}"
      "\nscp zotero_harvester.conf {0}@benu.ub.uni-tuebingen.de:/usr/local/zotero-enhancement-maps/hnebel_retrokat/zotero-enhancement-maps/zotero_harvester.conf".format(BENU_username)
      + upload_string +
      "\nssh {0}@benu.ub.uni-tuebingen.de\nnohup ./start_harvests.sh &".format(BENU_username))
