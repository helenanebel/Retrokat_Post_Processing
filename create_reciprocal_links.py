import os
import urllib.request
from bs4 import BeautifulSoup
import json
import csv

def get_results(xml_soup, journal_ppn, ppn):
    review_ppn = None
    if xml_soup.find('zs:numberofrecords').text != '0':
        for record in xml_soup.find_all('record'):
            if record.find('datafield', tag='002@').find('subfield', code='0').text == 'Osn':
                found_ppn = record.find('datafield', tag='003@').find('subfield', code='0').text
                print(found_ppn)
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
    print(url)
    xml_data = urllib.request.urlopen(url)
    xml_soup = BeautifulSoup(xml_data, features='lxml')
    review_ppn = get_results(xml_soup, journal_ppn, ppn)
    return review_ppn


def get_ppns_for_reciprocal_links(zeder_id, journal_ppn):
    review_ppn_list = {}
    file = zeder_id + '_ppns_linked.json'
    if file in os.listdir('final_additional_information'):
        with open('final_additional_information/' + file, 'r') as ppns_linked_file:
            ppns_linked = json.load(ppns_linked_file)
        for ppn in ppns_linked:
            review_ppn = search_review(ppn, journal_ppn)
            review_ppn_list[ppn] = review_ppn
    with open(zeder_id + '_review_ppns_to_add.csv', 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for ppn in review_ppn_list:
            csv_writer.writerow([ppn, "4262 Rezensiert in!" + review_ppn_list[ppn] + "!"])


if __name__ == '__main__':
    get_ppns_for_reciprocal_links('1098', '368910555')
