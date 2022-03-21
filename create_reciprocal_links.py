import os
import urllib.request
from bs4 import BeautifulSoup
import json
import csv
import shutil
from time import strftime


def get_results(xml_soup, journal_ppn, ppn):
    review_ppn = None
    if xml_soup.find('zs:numberofrecords').text != '0':
        for record in xml_soup.find_all('record'):
            if record.find('datafield', tag='002@').find('subfield', code='0').text == 'Osn':
                found_ppn = record.find('datafield', tag='003@').find('subfield', code='0').text
                # print(found_ppn)
                if record.find('datafield', tag='039B').find('subfield', code='9').text == journal_ppn:
                    # hier muss über die Liste aller rezensierten Werke iteriert werden!
                    reviewed_works_a = [datafield.find('subfield', code='9').text for datafield in record.find_all('datafield', tag='039P')]
                    reviewed_works_b = [datafield.find('subfield', code='9').text for datafield in record.find_all('datafield', tag='039U')]
                    if ppn in reviewed_works_a:
                        review_ppn = found_ppn
                    elif ppn in reviewed_works_b:
                        print('other branch')
    else:
        print('no reviews found')
    return review_ppn


def search_review(ppn, journal_ppn):
    url = 'http://sru.k10plus.de/opac-de-627?version=1.1&operation=searchRetrieve&query=pica.1049%3D{0}+and+pica.1045%3Drel-tt+and+pica.1001%3Db&maximumRecords=5&recordSchema=picaxml'.format(ppn)
    xml_data = urllib.request.urlopen(url)
    xml_soup = BeautifulSoup(xml_data, features='lxml')
    review_ppn = get_results(xml_soup, journal_ppn, ppn)
    return review_ppn


def get_ppns_for_reciprocal_links(zeder_id, journal_ppn):
    timestamp = strftime('%Y%m%d')
    review_ppn_list = {}
    ssg1_list = []
    ssg0 = False
    is_ssg0 = input('Soll das SSG-Kennzeichen 0 gesetzt werden? ')
    if is_ssg0 == 'j':
        ssg0 = True
    if zeder_id + '_rezensierte_werke_nicht_ixtheo.json' in os.listdir('final_additional_information'):
        with open('final_additional_information/' + zeder_id + '_rezensierte_werke_nicht_ixtheo.json', 'r') as non_ixtheo_ppn_file:
            non_ixtheo_ppns = json.load(non_ixtheo_ppn_file)
    file = zeder_id + '_ppns_linked.json'
    if file in os.listdir('final_additional_information'):
        with open('final_additional_information/' + file, 'r') as ppns_linked_file:
            ppns_linked = json.load(ppns_linked_file)
        '''url = "http://sru.k10plus.de/opac-de-627?version=1.1&operation=searchRetrieve&query=pica.ppn%3D{0}&maximumRecords=10&recordSchema=picaxml".format(
            journal_ppn)
        xml_data = urllib.request.urlopen(url)
        xml_soup = BeautifulSoup(xml_data, features='lxml')
        record = xml_soup.find('record')
        ssg_signs = [field.find('subfield', code='a').text for field in record.find_all('datafield', tag='045V')]'''
        for ppn in ppns_linked:
            review_ppn = search_review(ppn, journal_ppn)
            review_ppn_list[ppn] = review_ppn
            print(ppn, review_ppn)
            if ppn in non_ixtheo_ppns:
                ssg1_list.append(ppn)
    option = 'w'
    if timestamp + '_PPNs_4262_8910.csv' in os.listdir('review_information'):
        option = 'a'
    print(option)
    with open('review_information/' + timestamp + '_PPNs_4262_8910.csv', option, newline='') as csvfile:
        csv_writer = csv.writer(csvfile, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for ppn in review_ppn_list:
            csv_writer.writerow([ppn, review_ppn_list[ppn]])
    if ssg1_list:
        with open('review_information/' + timestamp + '_PPNs_5056_1.csv', option, newline='') as csvfile:
            csv_writer = csv.writer(csvfile, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            for ppn in ssg1_list:
                csv_writer.writerow([ppn])
        if ssg0:
            shutil.copyfile('review_information/' + timestamp + '_PPNs_5056_1.csv',
                            'review_information/' + timestamp + '_PPNs_5056_0.csv')


if __name__ == '__main__':
    with open('review_information/journals_previously_processed.json', 'r') as journal_file:
        processed_journals = json.load(journal_file)
    zeder_id = input('Bitte geben Sie die Zeder-ID ein: ')
    if zeder_id not in processed_journals:
        with open('W:/FID-Projekte/Team Retro-Scan/Zotero/conf.json', 'r') as conf_file:
            conf_dict = json.load(conf_file)
            eppn = conf_dict[zeder_id]['eppn']
        get_ppns_for_reciprocal_links(zeder_id, eppn)
        processed_journals.append(zeder_id)
        with open('review_information/journals_previously_processed.json', 'w') as journal_file:
            json.dump(processed_journals, journal_file)
    else:
        print('Diese Zeder-ID wurde bereits verarbeitet.')
