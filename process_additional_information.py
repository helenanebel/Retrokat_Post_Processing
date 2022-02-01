import os
import json
import csv


def add_5056(zeder_id):
    filename = zeder_id + '_rezensierte_werke_nicht_ixtheo.json'
    if filename in os.listdir('final_additional_information'):
        manipulation_dict = {}
        with open('final_additional_information/' + filename, 'r') as file:
            ppn_list = json.load(file)
            for ppn in ppn_list:
                manipulation_dict[ppn] = {'to_remove': [], 'to_add': '5056 1'}
        with open('W:/FID-Projekte/Team Retro-Scan/Zotero/Datensatz-Update/' + zeder_id + '_add_ssg_tags.json', 'w', encoding="utf-8") as json_file:
            json_file.write(str(manipulation_dict))


def add_links_and_doi(zeder_id):
    filename = zeder_id + '_links_to_add.csv'
    if filename in os.listdir('final_additional_information'):
        manipulation_dict = {}
        with open ('final_additional_information/' + zeder_id + '_links_to_add.csv', 'r', encoding="utf-8") as csv_file:
            all_rows = csv.reader(csv_file, quotechar='"', delimiter=',')
            for row in all_rows:
                to_add = []
                ppn = row[0]
                url = row[1]
                if url:
                    if 'https://doi.org/' in url:
                        to_add.append('4950 ' + url + '$xR$3Volltext$4ZZ$534')
                    else:
                        to_add.append('4950 ' + url + '$xH$3Volltext$4ZZ$534')
                doi = row[2]
                if doi:
                    to_add.append('2051 ' + doi)
                manipulation_dict[ppn] = {"to_remove": [], "to_add": to_add}
        with open('W:/FID-Projekte/Team Retro-Scan/Zotero/Datensatz-Update/' + zeder_id + '_add_links_and_dois.json', 'w', encoding="utf-8") as json_file:
            json_file.write(str(manipulation_dict))


if __name__ == '__main__':
    zeder_id = input('Bitte geben Sie die ZEDER-ID ein: ')
    # add_5056(zeder_id)
    add_links_and_doi(zeder_id)
    # hier evtl. noch einfügen, dass die reziproken Links generiert werden, dann kann das mit 5056 in einem Aufwasch erledigt werden; dazu auf Rückmeldung von Frau Kühn warten.
