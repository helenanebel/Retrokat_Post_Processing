import os
import xml.etree.ElementTree as ElementTree
import re


def merge_journal_records():
    ElementTree.register_namespace('', "http://www.loc.gov/MARC21/slim")
    complete_tree = ElementTree.parse('marcxml_empty.xml')
    complete_root = complete_tree.getroot()
    zeder_id = input('Bitte geben Sie die ZEDER-ID der zusammenzuführenden Records ein: ')
    zeder_id = zeder_id.replace('+', '\\+')
    record_nr = 0
    for file in os.listdir('multiple_crawl'):
        if re.findall('^' + zeder_id + '_', file) or zeder_id + '+' in file or file == zeder_id + '.xml':
            try:
                print(file)
                tree = ElementTree.parse('multiple_crawl/' + file)
                root = tree.getroot()
                records = root.findall('.//{http://www.loc.gov/MARC21/slim}record')
                records = [record for record in records]
                for record in records:
                    record_nr += 1
                    if record_nr%200 == 0:
                        print(record_nr)
                    complete_root.append(record)
            except:
                print('no xml:', file)
    print("total records:", record_nr)
    complete_tree.write('result_files/' + zeder_id.replace('\\+', '+') + '.xml', encoding='utf-8', xml_declaration=True)


if __name__ == '__main__':
    merge_journal_records()
