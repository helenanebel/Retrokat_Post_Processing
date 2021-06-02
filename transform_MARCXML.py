import json
import os
import xml.etree.ElementTree as ElementTree
import re


def add_jstor_links(record, jstor_dict, year, volume, issue, pagination):
    jstor_url = None
    if year in jstor_dict:
        if volume in jstor_dict[year]:
            if issue:
                if issue in jstor_dict[year][volume]:
                    if pagination in jstor_dict[year][volume][issue]:
                        jstor_url = jstor_dict[year][volume][issue][pagination]
            else:
                if pagination in jstor_dict[year][volume]:
                    jstor_url = jstor_dict[year][volume][pagination]
    if jstor_url:
        create_marc_field(record, {'tag': '856', 'ind1': '4', 'ind2': '0',
                                   'subfields': {'u': jstor_url, 'z': 'ZZ'}})
    print('JSTOR-URL added:', jstor_url)


def create_marc_field(record, field_dict: dict):
    new_datafield = ElementTree.SubElement(record, "{http://www.loc.gov/MARC21/slim}datafield",
                                           {'tag': field_dict['tag'], 'ind1': field_dict['ind1'],
                                            'ind2': field_dict['ind1']})
    for subfield in field_dict['subfields']:
        new_subfield = ElementTree.SubElement(new_datafield, "{http://www.loc.gov/MARC21/slim}subfield",
                                              {'code': subfield})
        new_subfield.text = field_dict['subfields'][subfield]


def get_subfield(record, tag, subfield_code):
    searchstring = '{http://www.loc.gov/MARC21/slim}datafield[@tag="' \
                   + tag + '"]/{http://www.loc.gov/MARC21/slim}subfield[@code="' + subfield_code + '"]'
    if record.find(searchstring) is None:
        return None
    return record.find(searchstring).text


def check_and_split_in_issues(zeder_id):
    issue_tree = ElementTree.parse('marcxml_empty.xml')
    issue_root = issue_tree.getroot()
    all_title_beginnings = {}
    missing_authors = []
    for file in os.listdir('volume_files'):
        os.unlink('volume_files/' + file)
    for file in os.listdir('result_files'):
        if file == zeder_id + '.xml':
            all_issues = []
            ElementTree.register_namespace('', "http://www.loc.gov/MARC21/slim")
            result_tree = ElementTree.parse('result_files/' + file)
            result_root = result_tree.getroot()
            records = result_root.findall('.//{http://www.loc.gov/MARC21/slim}record')
            paginations = ['-']
            reviews = 0
            current_issue = 'first'
            records = [record for record in records]
            for record in records:
                new_issue = str(get_subfield(record, '936', 'd').zfill(3)) + \
                            str(get_subfield(record, '936', 'e').zfill(2)).replace('/', '-')
                if records.index(record) == (len(records) - 1):
                    issue_tree.write('volume_files/' + current_issue + '.xml', xml_declaration=True)
                if new_issue not in all_issues:
                    with open('volume_files/' + current_issue + '.xml', 'w') as xml_file:
                        xml_file.close()
                    issue_tree.write('volume_files/' + current_issue + '.xml', xml_declaration=True)
                    all_issues.append(new_issue)
                    issue_tree = ElementTree.parse('marcxml_empty.xml')
                    issue_root = issue_tree.getroot()
                    if not (len([pagination for pagination in paginations if '-' in pagination])
                            > (len(paginations)/3)):
                        print(paginations)
                        print(current_issue, 'has problem with pagination')
                    paginations = []
                    if (not reviews) and (not current_issue == 'first'):
                        print(current_issue, 'has no reviews')
                    reviews = 0
                    current_issue = new_issue
                title = get_subfield(record, '245', 'a')
                if not record.find('{http://www.loc.gov/MARC21/slim}datafield[@tag="100"]'):
                    missing_authors.append(title)
                title_beginning = ' '.join(title.split()[:2])
                if title_beginning not in all_title_beginnings:
                    all_title_beginnings[title_beginning] = 1
                else:
                    all_title_beginnings[title_beginning] += 1
                if get_subfield(record, '655', 'a'):
                    reviews += 1
                pagination = get_subfield(record, '936', 'h')
                paginations.append(pagination)
                issue_root.append(record)
    print([beginning for beginning in all_title_beginnings if all_title_beginnings[beginning] > 3])
    print(missing_authors)


def transform(zeder_id: str, exclude: list[str], volumes_to_catalogue: list[int, int]):
    volumes_discarded = []
    post_process_nr = 0
    discarded_nr = 0
    proper_nr = 0
    volume_list = [str(year) for year in range(volumes_to_catalogue[0], volumes_to_catalogue[1] + 1)]
    with open('W:/FID-Projekte/Team Retro-Scan/Zotero/present_records.json', 'r') as present_record_file:
        present_record_list = json.load(present_record_file)
        if zeder_id in present_record_list:
            present_record_lookup_years = [present_record['year'] for present_record in present_record_list[zeder_id]]
        else:
            present_record_lookup_years = []
    post_process_tree = ElementTree.parse('marcxml_empty.xml')
    post_process_root = post_process_tree.getroot()
    proper_tree = ElementTree.parse('marcxml_empty.xml')
    proper_root = proper_tree.getroot()
    for file in os.listdir('volume_files'):
        ElementTree.register_namespace('', "http://www.loc.gov/MARC21/slim")
        result_tree = ElementTree.parse('volume_files/' + file)
        result_root = result_tree.getroot()
        records = result_root.findall('.//{http://www.loc.gov/MARC21/slim}record')
        for record in records:
            year = get_subfield(record, '264', 'c')
            if year not in volume_list:
                if year not in volumes_discarded:
                    volumes_discarded.append(year)
                continue
            discard = False
            append_to_postprocess = False
            for datafield in record.findall('{http://www.loc.gov/MARC21/slim}datafield'):
                if datafield.attrib['tag'] == '935':
                    record.remove(datafield)
            for retrieve_sign in ['ixzs', 'ixrk']:
                create_marc_field(record, {'tag': '935', 'ind1': ' ', 'ind2': ' ', 
                                           'subfields': {'a': retrieve_sign, '2': 'LOK'}})
            create_marc_field(record, {'tag': '935', 'ind1': ' ', 'ind2': ' ',
                                       'subfields': {'a': 'mteo'}})
            volume = get_subfield(record, '936', 'd')
            issue = get_subfield(record, '936', 'e')
            pagination = get_subfield(record, '936', 'h')
            if '-' in pagination:
                if re.findall(r'(\d+)-(\d+)', pagination):
                    fpage, lpage = re.findall(r'(\d+)-(\d+)', pagination)[0]
                    if fpage == lpage:
                        pagination_tag = \
                            record.find('{http://www.loc.gov/MARC21/slim}datafield[@tag="936"]'
                                        '/{http://www.loc.gov/MARC21/slim}subfield[@code="h"]')
                        pagination_tag.text = fpage
                else:
                    print(get_subfield(record, '856', 'u'))
                    pagination_tag = \
                        record.find('{http://www.loc.gov/MARC21/slim}datafield[@tag="936"]'
                                    '/{http://www.loc.gov/MARC21/slim}subfield[@code="h"]')
                    pagination_tag.text = input('Bitte geben Sie die Seitenzahl des Artikels ein: ')
            if pagination is None:
                append_to_postprocess = True
            if zeder_id in present_record_list:
                delete_entries = []
                if [year in present_record_lookup_years]:
                    for entry in [entry for entry in present_record_list[zeder_id] if entry['year'] == year]:
                        if (entry['volume'] == volume) and (entry['issue'] == issue):
                            if entry['title'] == '*all*':
                                print('Alle Titel in', issue, volume, year, 'werden gelöscht.')
                                discard = True
                            else:
                                title = get_subfield(record, '245', 'a')
                                found = re.search(entry['title'], title, re.IGNORECASE)
                                if found is not None:
                                    delete_entries.append(entry)
                                    discard = True
                    for entry in delete_entries:
                        present_record_list[zeder_id].remove(entry)
            for exclude_regex in exclude:
                if re.search(exclude_regex, get_subfield(record, '245', 'a'), re.IGNORECASE):
                    discard = True
            if discard:
                discarded_nr += 1
                continue
            elif append_to_postprocess:
                form_tag = record.find('{http://www.loc.gov/MARC21/slim}datafield[@tag="655"][@ind2="7"]'
                                       '/{http://www.loc.gov/MARC21/slim}subfield[@code="a"]')
                if form_tag is not None:
                    if form_tag.text == 'Rezension':
                        create_marc_field(record, {'tag': '650', 'ind1': ' ', 'ind2': '4',
                                                   'subfields': {'a': 'RezensionstagPica'}})
                post_process_root.append(record)
                post_process_nr += 1
            else:
                if zeder_id + '.json' in os.listdir('W:/FID-Projekte/Team Retro-Scan/Zotero/jstor_csv'):
                    with open('W:/FID-Projekte/Team Retro-Scan/Zotero/jstor_csv/' + file, 'r',
                              encoding="utf-8") as jstor_file:
                        jstor_dict = json.load(jstor_file)
                        add_jstor_links(record, jstor_dict, year, volume, pagination, issue)
                create_marc_field(record, {'tag': '935', 'ind1': ' ', 'ind2': ' ',
                                           'subfields': {'a': 'zota', '2': 'LOK'}})
                proper_root.append(record)
                proper_nr += 1

    proper_tree.write(zeder_id + '_proper.xml', encoding='utf-8', xml_declaration=True)
    post_process_tree.write(zeder_id + '_post_process.xml', encoding='utf-8', xml_declaration=True)
    if zeder_id in present_record_list:
        print('missing doublets:', present_record_list[zeder_id])
    print('proper:', proper_nr)
    print('post_process:', post_process_nr)
    print('discard:', discarded_nr)
    print('volumes discarded:', volumes_discarded)

    {"issue": "5", "volume": "38", "title": "23. Reception", "year": "2016"},
    {"issue": "5", "volume": "38", "title": "22. Textual Criticism", "year": "2016"},
    {"issue": "5", "volume": "38", "title": "21. language", "year": "2016"},
    {"issue": "5", "volume": "38", "title": "Early Christianity", "year": "2016"},
    {"issue": "5", "volume": "38", "title": "19.Graeco-Roman", "year": "2016"},
    {"issue": "5", "volume": "38", "title": "18. Judaism", "year": "2016"},
    {"issue": "5", "volume": "38", "title": "17.Revelation", "year": "2016"},
    {"issue": "5", "volume": "38", "title": "16. Non-Pauline Letters", "year": "2016"},
    {"issue": "5", "volume": "38", "title": "15. Pastoral Epistles", "year": "2016"},
    {"issue": "5", "volume": "38", "title": "14. Philippians & Thessalonians", "year": "2016"},
    {"issue": "5", "volume": "38", "title": "13. Ephesians, Colossians & Philemon", "year": "2016"},
    {"issue": "5", "volume": "38", "title": "12. Galatians", "year": "2016"},
    {"issue": "5", "volume": "38", "title": "11. Corinthians", "year": "2016"},
    {"issue": "5", "volume": "38", "title": "10. Romans", "year": "2016"},
    {"issue": "5", "volume": "38", "title": "9. Paul", "year": "2016"},
    {"issue": "5", "volume": "38", "title": "8. John", "year": "2016"},
    {"issue": "5", "volume": "38", "title": "7. Luke-Acts", "year": "2016"},
    {"issue": "5", "volume": "38", "title": "6. Mark", "year": "2016"},
    {"issue": "5", "volume": "38", "title": "5. Matthew", "year": "2016"},
    {"issue": "5", "volume": "38", "title": "4. Gospels", "year": "2016"},
    {"issue": "5", "volume": "38", "title": "3. Jesus", "year": "2016"},
    {"issue": "5", "volume": "38", "title": "2. New Testaments Topics", "year": "2016"},
    {"issue": "5", "volume": "38", "title": "1. New Testament General", "year": "2016"}
