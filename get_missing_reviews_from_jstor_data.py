import xml.etree.ElementTree as ElementTree


def get_reviews_from_jstor(zeder_id, jstor_zeder_id):
    added_nr = 0
    ElementTree.register_namespace('', "http://www.loc.gov/MARC21/slim")
    jstor_tree = ElementTree.parse('W:/FID-Projekte/Team Retro-Scan/Zotero/result_files/' + jstor_zeder_id + '.xml')
    jstor_root = jstor_tree.getroot()
    jstor_records = jstor_root.findall('.//{http://www.loc.gov/MARC21/slim}record')
    bsw_tree = ElementTree.parse('W:/FID-Projekte/Team Retro-Scan/Zotero/result_files/' + zeder_id + '.xml')
    bsw_root = bsw_tree.getroot()
    for jstor_record in jstor_records:
        if jstor_record.find('{http://www.loc.gov/MARC21/slim}datafield[@tag="655"]'
                             '/{http://www.loc.gov/MARC21/slim}subfield[@code="a"]') is not None:
                bsw_root.append(jstor_record)
                added_nr += 1
    print(added_nr)
    bsw_tree.write(zeder_id + '_with_reviews.xml', encoding='utf-8', xml_declaration=True)


if __name__ == '__main__':
    zeder_id = input('Bitte geben Sie die Zeder-ID ein: ')
    jstor_id = input('Bitte geben Sie den Namen der JSTOR-Datei ein: ')
    get_reviews_from_jstor(zeder_id, jstor_id)