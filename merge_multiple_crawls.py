import os
import xml.etree.ElementTree as ElementTree
import re
from shutil import copy2


def merge_journal_records():
    ElementTree.register_namespace('', "http://www.loc.gov/MARC21/slim")
    complete_tree = ElementTree.parse('marcxml_empty.xml')
    complete_root = complete_tree.getroot()
    zeder_id = input('Bitte geben Sie die ZEDER-ID der zusammenzuführenden Records ein: ')
    zeder_id_for_regex = zeder_id.replace('+', '\\+')
    record_nr = 0
    if zeder_id in os.listdir('W:/FID-Projekte/Team Retro-Scan/Zotero/results'):
        for file in os.listdir('W:/FID-Projekte/Team Retro-Scan/Zotero/results/' + zeder_id):
            if re.findall('^' + zeder_id_for_regex + '_', file) or file == zeder_id + '.xml':
                try:
                    tree = ElementTree.parse('W:/FID-Projekte/Team Retro-Scan/Zotero/results/' + zeder_id + '/' + file)
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
        complete_tree.write('W:/FID-Projekte/Team Retro-Scan/Zotero/result_files/' + zeder_id + '.xml',
                            encoding='utf-8', xml_declaration=True)
    elif zeder_id + '.xml' in os.listdir('W:/FID-Projekte/Team Retro-Scan/Zotero/results'):
        copy2('W:/FID-Projekte/Team Retro-Scan/Zotero/results/' + zeder_id + '.xml', 'W:/FID-Projekte/Team Retro-Scan/Zotero/result_files/' + zeder_id + '.xml')
    print("total records:", record_nr)


if __name__ == '__main__':
    merge_journal_records()
