import re
import xml.etree.ElementTree as ElementTree


def get_reviews_from_jstor(zeder_id, jstor_zeder_id):
    ElementTree.register_namespace('', "http://www.loc.gov/MARC21/slim")
    jstor_tree = ElementTree.parse('W:/FID-Projekte/Team Retro-Scan/Zotero/result_files/' + jstor_zeder_id + '.xml')
    jstor_root = jstor_tree.getroot()
    jstor_records = jstor_root.findall('.//{http://www.loc.gov/MARC21/slim}record')
    brill_tree = ElementTree.parse('W:/FID-Projekte/Team Retro-Scan/Zotero/result_files/' + zeder_id + '.xml')
    brill_root = brill_tree.getroot()
    brill_records = brill_root.findall('.//{http://www.loc.gov/MARC21/slim}record')
    review_added_tree = ElementTree.parse('marcxml_empty.xml')
    review_added_root = review_added_tree.getroot()
    for record in brill_records:
        title = record.find('{http://www.loc.gov/MARC21/slim}datafield[@tag="245"]'
                            '/{http://www.loc.gov/MARC21/slim}subfield[@code="a"]').text
        # Change regex for Review Section here:
        if re.findall(r'^notices?\s+bibliographique', title, flags=re.IGNORECASE):
            print(title)
            source = record.find('{http://www.loc.gov/MARC21/slim}datafield[@tag="773"]'
                                '/{http://www.loc.gov/MARC21/slim}subfield[@code="g"]').text
            for jstor_record in jstor_records:
                if jstor_record.find('{http://www.loc.gov/MARC21/slim}datafield[@tag="655"]'
                            '/{http://www.loc.gov/MARC21/slim}subfield[@code="a"]') is not None:
                    jstor_source = jstor_record.find('{http://www.loc.gov/MARC21/slim}datafield[@tag="773"]'
                                         '/{http://www.loc.gov/MARC21/slim}subfield[@code="g"]').text
                    if jstor_source.split(', Seite')[0] in source:
                        print(source, jstor_source)
                        for field in jstor_record.findall('{http://www.loc.gov/MARC21/slim}datafield[@tag="650"]'):
                            jstor_record.remove(field)
                        for field in jstor_record.findall('{http://www.loc.gov/MARC21/slim}datafield[@tag="856"]'):
                            jstor_record.remove(field)
                        for field in jstor_record.findall('{http://www.loc.gov/MARC21/slim}datafield[@tag="URL"]'):
                            jstor_record.remove(field)
                        for field in record.findall('{http://www.loc.gov/MARC21/slim}datafield[@tag="856"]'):
                            jstor_record.append(field)
                        for field in record.findall('{http://www.loc.gov/MARC21/slim}datafield[@tag="URL"]'):
                            jstor_record.append(field)
                        for field in record.findall('{http://www.loc.gov/MARC21/slim}datafield[@tag="024"]'):
                            jstor_record.append(field)
                        review_added_root.append(jstor_record)
        else:
            review_added_root.append(record)

    review_added_tree.write(zeder_id + '_with_reviews.xml', encoding='utf-8', xml_declaration=True)


if __name__ == '__main__':
    zeder_id = input('Bitte geben Sie die Zeder-ID ein: ')
    jstor_id = input('Bitte geben Sie den Namen der JSTOR-Datei ein: ')
    get_reviews_from_jstor(zeder_id, jstor_id)