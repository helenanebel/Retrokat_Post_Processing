import os
import re
import json
import xml.etree.ElementTree as ElementTree


def get_review_information(zeder_id, jstor_zeder_id):
    if zeder_id + '_reviews.json' not in os.listdir('W:/FID-Projekte/Team Retro-Scan/Zotero/jstor_mapping'):
        review_dict = {}
        jstor_tree = ElementTree.parse('result_files/' + jstor_zeder_id + '.xml')
        jstor_root = jstor_tree.getroot()
        ElementTree.register_namespace('', "http://www.loc.gov/MARC21/slim")
        records = jstor_root.findall('.//{http://www.loc.gov/MARC21/slim}record')
        for record in records:
            urls = record.findall('{http://www.loc.gov/MARC21/slim}datafield[@tag="856"]/{http://www.loc.gov/MARC21/slim}subfield[@code="u"]')
            for url in urls:
                tags = record.findall \
                    ('{http://www.loc.gov/MARC21/slim}datafield[@tag="650"]/{http://www.loc.gov/MARC21/slim}subfield[@code="a"]')
                for tag in tags:
                    if re.search(r'^#reviewed_pub#', tag.text, re.IGNORECASE):
                        if url.text not in review_dict:
                            review_dict[url.text] = []
                        review_dict[url.text].append(tag.text)
        with open('W:/FID-Projekte/Team Retro-Scan/Zotero/jstor_mapping/' + zeder_id + '_reviews.json', 'w') as json_file:
            json.dump(review_dict, json_file)
