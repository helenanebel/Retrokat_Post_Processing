import os
import urllib.request
from bs4 import BeautifulSoup
import json
import csv

def get_aurl_results(xml_soup, journal_ppn):
    review_ppn = None
    if xml_soup.find('zs:numberofrecords').text != '0':
        for record in xml_soup.find_all('record'):
            retrieve_signs = [retrieve_sign for retrieve_sign_list in [element.find_all('subfield', code='a').text for element in record.find_all('datafield', tag='209B')] for retrieve_sign in retrieve_sign_list]
            print(retrieve_signs)
            if 'aurl' not in retrieve_signs:
                continue
            ppn = record.find('datafield', tag='003@').find('subfield', code='0').text
            if record.find('datafield', tag='039B').find('subfield', code='9').text == journal_ppn:
                if (record.find('datafield', tag='039P').find('subfield', code='9').text == ppn):
                    review_ppn = ppn
                elif (record.find('datafield', tag='039U').find('subfield', code='9').text):
                    review_ppn = ppn
    return review_ppn


def search_review(ppn, journal_ppn):
    url = 'http://http://sru.k10plus.de/opac-de-627?version=1.1&operation=searchRetrieve&query=pica.1049%3D{0}+and+pica.1045%3Drel-tt+and+pica.1001%3Db&maximumRecords=5&recordSchema=picaxml'.format(ppn)
    print(url)
    xml_data = urllib.request.urlopen(url)
    xml_soup = BeautifulSoup(xml_data, features='lxml')
    review_ppn = get_aurl_results(xml_soup, journal_ppn)
    return review_ppn


def get_ppns_for_reciprocal_links(zeder_id, journal_ppn):
    review_ppn_list = {}
    file = zeder_id + '_ppns_linked.json'
    if file in os.listdir():
        with open(file, 'r') as ppns_linked_file:
            ppns_linked = json.load(ppns_linked_file)
        for ppn in ppns_linked:
            review_ppn = search_review(ppn, journal_ppn)
            review_ppn_list[ppn] = review_ppn
    with open(zeder_id + '_review_ppns_to_add.csv', 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile, delimiter=',',
                                quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for ppn in review_ppn_list:
            csv_writer.writerow([review_ppn_list[ppn], ppn])


if __name__ == '__main__':
    get_ppns_for_reciprocal_links('647', '34271855X')
