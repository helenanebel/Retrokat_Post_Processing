import urllib.request
from bs4 import BeautifulSoup
import json


def get_records_with_missing_links(eppn, zid):
    records_with_missing_links = []
    empty_page = False
    start_nr = 1
    while not empty_page:
        filedata = urllib.request.urlopen('http://sru.k10plus.de/'
                                          'opac-de-627?version=1.1&operation=searchRetrieve&query=pica.1049%3D' + eppn +
                                          '+and+pica.1045%3Drel-nt+and+pica.1001%3Db&maximumRecords=100&startRecord=' + str(start_nr) + '&recordSchema=picaxml')
        data = filedata.read()
        xml_soup = BeautifulSoup(data, "lxml")
        if not xml_soup.find('zs:records'):
            empty_page = True
            continue
        start_nr += 100
        for record in xml_soup.find('zs:records').find_all('zs:record'):
            if record.find('datafield', tag='017C'):
                pass
            else:
                title = record.find('datafield', tag='021A').find('subfield', code='a').text
                if record.find('datafield', tag='028A'):
                    if record.find('datafield', tag='028A').find('subfield', code='A') and record.find('datafield', tag='028A').find('subfield', code='D'):
                        author = record.find('datafield', tag='028A').find('subfield', code='A').text + ', ' + record.find('datafield', tag='028A').find('subfield', code='D').text
                    else:
                        author = None
                else:
                    author = None
                source_information = record.find('datafield', tag='031A')
                if source_information.find('subfield', code='j'):
                    year = source_information.find('subfield', code='j').text
                else:
                    year = None
                if source_information.find('subfield', code='d'):
                    volume = source_information.find('subfield', code='d').text
                else:
                    volume = None
                if source_information.find('subfield', code='e'):
                    issue = source_information.find('subfield', code='e').text
                else:
                    issue = None
                if source_information.find('subfield', code='h'):
                    pages = source_information.find('subfield', code='h').text
                else:
                    pages = None
                record_id = record.find('datafield', tag='003@').find('subfield', code='0').text
                records_with_missing_links.append({'title': title, 'author': author, 'year': year, 'volume': volume, 'issue': issue, 'pages': pages, 'id': record_id})
    with open('W:/FID-Projekte/Team Retro-Scan/Zotero/missing_links/' + zid + '.json', 'w') as json_file:
        json.dump(records_with_missing_links, json_file)


if __name__ == '__main__':
    get_records_with_missing_links('341897612', '394')