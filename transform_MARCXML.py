import json
import os
import xml.etree.ElementTree as ElementTree
import re


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


def check_and_split_in_issues():
    issue_tree = ElementTree.parse('marcxml_empty.xml')
    issue_root = issue_tree.getroot()
    all_title_beginnings = {}
    missing_authors = []
    for file in os.listdir('result_files'):
        all_issues = []
        ElementTree.register_namespace('', "http://www.loc.gov/MARC21/slim")
        result_tree = ElementTree.parse('result_files/' + file)
        result_root = result_tree.getroot()
        records = result_root.findall('.//{http://www.loc.gov/MARC21/slim}record')
        paginations = ['-']
        reviews = 0
        current_issue = 'first'
        for record in records:
            new_issue = str(get_subfield(record, '936', 'd').zfill(3)) + \
                        str(get_subfield(record, '936', 'e').zfill(2)).replace('/', '-')
            if new_issue not in all_issues:
                with open('volume_files/' + current_issue + '.xml', 'w') as xml_file:
                    xml_file.close()
                issue_tree.write('volume_files/' + current_issue + '.xml', xml_declaration=True)
                all_issues.append(new_issue)
                issue_tree = ElementTree.parse('marcxml_empty.xml')
                issue_root = issue_tree.getroot()
                if not (len([pagination for pagination in paginations if '-' in pagination]) > (len(paginations)/3)):
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


def transform(zeder_id: str, exclude: list[str], volumes_to_catalogue: tuple[int, int]):
    volumes_discarded = []
    post_process_nr = 0
    discarded_nr = 0
    proper_nr = 0
    volume_list = [str(year) for year in range(volumes_to_catalogue[0], volumes_to_catalogue[1] + 1)]
    with open('present_records.json', 'r') as present_record_file:
        present_record_list = json.load(present_record_file)
        present_record_lookup_years = [present_record['year'] for present_record in present_record_list[zeder_id]]
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
            pagination = get_subfield(record, '936', 'h')
            if '-' in pagination:
                fpage, lpage = re.findall(r'(\d+)-(\d+)', pagination)[0]
                if fpage == lpage:
                    pagination_tag = \
                        record.find('{http://www.loc.gov/MARC21/slim}datafield[@tag="936"]'
                                    '/{http://www.loc.gov/MARC21/slim}subfield[@code="h"]')
                    pagination_tag.text = fpage
            if pagination is None:
                append_to_postprocess = True
            if present_record_list[zeder_id]:
                delete_entries = []
                if [year in present_record_lookup_years]:
                    volume = get_subfield(record, '936', 'd')
                    issue = get_subfield(record, '936', 'e')
                    for entry in [entry for entry in present_record_list[zeder_id] if entry['year'] == year]:
                        if (entry['volume'] == volume) and (entry['issue'] == issue):
                            title = get_subfield(record, '245', 'a')
                            found = re.match('^' + entry['title'], title, re.IGNORECASE)
                            if found is not None:
                                delete_entries.append(entry)
                                discard = True
                    for entry in delete_entries:
                        present_record_list[zeder_id].remove(entry)
            for exclude_regex in exclude:
                if re.match(exclude_regex, get_subfield(record, '245', 'a'), re.IGNORECASE):
                    discard = True
            if discard:
                discarded_nr += 1
                continue
            elif append_to_postprocess:
                post_process_root.append(record)
                post_process_nr += 1
            else:
                create_marc_field(record, {'tag': '935', 'ind1': ' ', 'ind2': ' ',
                                           'subfields': {'a': 'zota', '2': 'LOK'}})
                proper_root.append(record)
                proper_nr += 1

    proper_tree.write(zeder_id + '_proper.xml', xml_declaration=True)
    post_process_tree.write(zeder_id + '_post_process.xml', xml_declaration=True)
    print('missing doublets:', present_record_list[zeder_id])
    print('proper:', proper_nr)
    print('post_process:', post_process_nr)
    print('discard:', discarded_nr)
    print('volumes discarded:', volumes_discarded)
