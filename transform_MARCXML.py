import json
import os
import xml.etree.ElementTree as ElementTree
import re
from search_reviewed_publication import search_publication, search_publication_with_isbn
import csv


def add_jstor_links(record, jstor_dict, year, volume, issue, pagination):
    all_paginations = []
    pagination_dict = {}
    jstor_url = None
    if year in jstor_dict:
        for v in jstor_dict[year]:
            for i in jstor_dict[year][v]:
                for p in jstor_dict[year][v][i]:
                    all_paginations.append(p)
                    pagination_dict[p] = jstor_dict[year][v][i][p]
        if volume in jstor_dict[year]:
            if not issue:
                issue = 'n'
            if issue in jstor_dict[year][volume]:
                if pagination in jstor_dict[year][volume][issue]:
                    if len(jstor_dict[year][volume][issue][pagination]) == 1:
                        jstor_url = list(jstor_dict[year][volume][issue][pagination].values())[0]
                    else:
                        author_name = get_subfield(record, '100', 'a')
                        if not author_name:
                            author_name = 'nn'
                        names_list = re.findall(r'\w+', author_name)
                        for key in jstor_dict[year][volume][issue][pagination]:
                            if len(names_list) == len([name for name in names_list if name in key]):
                                jstor_url = jstor_dict[year][volume][issue][pagination][key]
                                break
                elif 'n' in jstor_dict[year][volume]:
                    if pagination in jstor_dict[year][volume]['n']:
                        if len(jstor_dict[year][volume]['n'][pagination]) == 1:
                            jstor_url = list(jstor_dict[year][volume]['n'][pagination].values())[0]
    if all_paginations.count(pagination) == 1:
        jstor_url = list(pagination_dict[pagination].values())[0]
    if jstor_url:
        create_marc_field(record, {'tag': '866', 'ind1': ' ', 'ind2': ' ',
                                   'subfields': {'x': ['JSTOR#' + jstor_url], '2': ['LOK']}})
        return 0
    # else:
        # print(get_subfield(record, '245', 'a'))
        # print(year, volume, issue, pagination)
        # print('____')
    return 1


def create_marc_field(record, field_dict: dict):
    new_datafield = ElementTree.SubElement(record, "{http://www.loc.gov/MARC21/slim}datafield",
                                           {'tag': field_dict['tag'], 'ind1': field_dict['ind1'],
                                            'ind2': field_dict['ind1']})
    for subfield_code in field_dict['subfields']:
        for subfield_text in field_dict['subfields'][subfield_code]:
            new_subfield = ElementTree.SubElement(new_datafield, "{http://www.loc.gov/MARC21/slim}subfield",
                                                  {'code': subfield_code})
            new_subfield.text = subfield_text


def get_subfield(record, tag, subfield_code):
    searchstring = '{http://www.loc.gov/MARC21/slim}datafield[@tag="' \
                   + tag + '"]/{http://www.loc.gov/MARC21/slim}subfield[@code="' + subfield_code + '"]'
    if record.find(searchstring) is None:
        return None
    return record.find(searchstring).text


def get_fields(record, tag):
    searchstring = '{http://www.loc.gov/MARC21/slim}datafield[@tag="' \
                   + tag + '"]'
    return record.findall(searchstring)


def check_abstract(record):
    abstract_tag = record.find('{http://www.loc.gov/MARC21/slim}datafield[@tag="520"]/{http://www.loc.gov/MARC21/slim}subfield[@code="a"]')
    if abstract_tag is not None:
        if re.search(r'^.{1,125}Article .+ was published on .+ in the journal .+ (.+).', abstract_tag.text, re.IGNORECASE):
            abstract_tags = get_fields(record, '520')
            for abstract_tag in abstract_tags:
                print('deleted abstract-tag')
                record.remove(abstract_tag)
        elif re.search(r'^.{1,125},\s+Volume\s+\d+,\s+Issue\s+[\d–/]+,\s+.+,\s+Pages\s+[\d–/]+,\s+https://doi\.org/', abstract_tag.text, re.IGNORECASE):
            abstract_tags = get_fields(record, '520')
            for abstract_tag in abstract_tags:
                print('deleted abstract-tag')
                record.remove(abstract_tag)
        elif 60 < len(abstract_tag.text) < 150:
            print("Short abstract:", abstract_tag.text)
        elif len(abstract_tag.text) < 60:
            abstract_tags = get_fields(record, '520')
            for abstract_tag in abstract_tags:
                record.remove(abstract_tag)
        if 'http' in abstract_tag.text:
            print("Link in abstract:", abstract_tag.text)
    return None


def create_review_link(record):
    tags = record.findall('{http://www.loc.gov/MARC21/slim}datafield[@tag="650"]/{http://www.loc.gov/MARC21/slim}subfield[@code="a"]')
    keywords = get_fields(record, '650')
    ppns = []
    is_theo = []
    for tag in tags:
        if re.search(r'^#reviewed_pub#', tag.text, re.IGNORECASE):
            pub_title = re.findall(r'#title::([^#]+)#', tag.text, re.IGNORECASE)[0] if re.findall(r'#title::([^#]+)#', tag.text, re.IGNORECASE) else ''
            pub_author = re.findall(r'#name::([^#]+)#', tag.text, re.IGNORECASE)[0] if re.findall(r'#name::([^#]+)#', tag.text, re.IGNORECASE) else ''
            pub_year = re.findall(r'#year::([^#]+)#', tag.text, re.IGNORECASE)[0] if re.findall(r'#year::([^#]+)#', tag.text, re.IGNORECASE) else ''
            pub_place = re.findall(r'#place::([^#]+)#', tag.text, re.IGNORECASE)[0] if re.findall(r'#place::([^#]+)#', tag.text, re.IGNORECASE) else ''
            tag_ppns, tag_is_theo = search_publication(pub_title, pub_author, pub_year, pub_place)
            ppns.append(tag_ppns)
            is_theo.append(tag_is_theo)
            for keyword in keywords:
                if keyword.find('{http://www.loc.gov/MARC21/slim}subfield[@code="a"]').text == tag.text:
                    record.remove(keyword)
    return ppns, is_theo


def check_and_split_in_issues(zeder_id, conf_available):
    issue_tree = ElementTree.parse('marcxml_empty.xml')
    issue_root = issue_tree.getroot()
    all_title_beginnings = {}
    missing_authors = []
    record_nr = 0
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
            with open('W:/FID-Projekte/Team Retro-Scan/Zotero/exclude.json', 'r') as exclusion_file:
                exclude_everywhere = json.load(exclusion_file)
            for record in records:
                record_nr += 1
                new_issue = str(get_subfield(record, '936', 'd').zfill(3)) + \
                            str(get_subfield(record, '936', 'e').zfill(2)).replace('/', '-')
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
                        print(current_issue, 'has no reviews! example:', get_subfield(record, '856', 'u'))
                    reviews = 0
                    current_issue = new_issue
                title = get_subfield(record, '245', 'a')
                found = False
                for exclude_regex in exclude_everywhere:
                    if re.search(exclude_regex, title, re.IGNORECASE):
                        found = True
                if not record.find('{http://www.loc.gov/MARC21/slim}datafield[@tag="100"]'):
                    if title not in missing_authors:
                        if not found:
                            missing_authors.append(title)
                title_beginning = ' '.join(title.split()[:3])
                if not found:
                    if title_beginning not in all_title_beginnings:
                        all_title_beginnings[title_beginning] = 1
                    else:
                        all_title_beginnings[title_beginning] += 1
                if get_subfield(record, '655', 'a'):
                    reviews += 1
                pagination = get_subfield(record, '936', 'h')
                if pagination:
                    paginations.append(pagination)
                issue_root.append(record)
                if records.index(record) == (len(records) - 1):
                    issue_tree.write('volume_files/' + current_issue + '.xml', xml_declaration=True)
    if conf_available:
        if input("Show titles with multiple occurence and missing authors? (y/n) ") == 'y':
            conf_available = False
    if not conf_available:
        print([beginning for beginning in all_title_beginnings if all_title_beginnings[beginning] > 3])
        print(missing_authors)
    return record_nr


def transform(zeder_id: str, exclude: list[str], volumes_to_catalogue: list[int, int], record_nr):
    total_jstor_fails = 0
    total_jstor_links = 0
    review_links_created = 0
    volumes_discarded = []
    post_process_nr = 0
    discarded_nr = 0
    discarded_by_volume_nr = 0
    proper_nr = 0
    volume_list = [str(year) for year in range(volumes_to_catalogue[0], volumes_to_catalogue[1] + 1)]
    non_ixtheo_ppns = []
    with open('W:/FID-Projekte/Team Retro-Scan/Zotero/missing_links/' + zeder_id + '.json', 'r') as missing_link_file:
        records_with_missing_links = json.load(missing_link_file)
        missing_link_lookup_years = [missing_link_record['year'] for missing_link_record in records_with_missing_links]
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
                discarded_by_volume_nr += 1
                if year not in volumes_discarded:
                    volumes_discarded.append(year)
                continue
            discard = False
            append_to_postprocess = False
            for datafield in record.findall('{http://www.loc.gov/MARC21/slim}datafield'):
                if datafield.attrib['tag'] == '935':
                    record.remove(datafield)
            for retrieve_sign in ['ixzs', 'ixrk', 'zota']:
                create_marc_field(record, {'tag': '935', 'ind1': ' ', 'ind2': ' ', 
                                           'subfields': {'a': [retrieve_sign], '2': ['LOK']}})
            create_marc_field(record, {'tag': '935', 'ind1': ' ', 'ind2': ' ',
                                       'subfields': {'a': ['mteo']}})
            volume = get_subfield(record, '936', 'd')
            issue = get_subfield(record, '936', 'e')
            pagination = get_subfield(record, '936', 'h')
            if pagination:
                if '-' in pagination:
                    if re.findall(r'(\d+)-(\d+)', pagination):
                        fpage, lpage = re.findall(r'(\d+)-(\d+)', pagination)[0]
                        if fpage == lpage:
                            pagination_tag = \
                                record.find('{http://www.loc.gov/MARC21/slim}datafield[@tag="936"]'
                                            '/{http://www.loc.gov/MARC21/slim}subfield[@code="h"]')
                            pagination_tag.text = fpage
                    else:
                        append_to_postprocess = True
            else:
                append_to_postprocess = True
            title = get_subfield(record, '245', 'a')
            if zeder_id in present_record_list:
                delete_entries = []
                if [year in present_record_lookup_years]:
                    for entry in [entry for entry in present_record_list[zeder_id] if entry['year'] == year]:
                        if (entry['volume'] == volume) and (entry['issue'] == issue):
                            if entry['title'] == '*all*':
                                print('Alle Titel in', issue, volume, year, 'werden gelöscht.')
                                discard = True
                            else:
                                found = re.search(entry['title'], title, re.IGNORECASE)
                                if found is not None:
                                    delete_entries.append(entry)
                                    discard = True
                    for entry in delete_entries:
                        present_record_list[zeder_id].remove(entry)
            if [year in missing_link_lookup_years]:
                for entry in [entry for entry in records_with_missing_links if entry['year'] == year]:
                    if ('volume' in entry)  and ('issue' in entry) and ('pages' in entry):
                        if (entry['volume'] == volume) and (entry['issue'] == issue) and (entry['pages'] == pagination):
                            print('found link for record')
            for exclude_regex in exclude:
                if re.search(exclude_regex, get_subfield(record, '245', 'a'), re.IGNORECASE):
                    discard = True
            if discard:
                discarded_nr += 1
                continue
            if any([re.search(regex, title, re.IGNORECASE) for regex in [r'^errat*', r'^corrigend*', r'^correct*', r'^berichtigung*', r'^omission*',
                                                                         r'\berrat((um)|(a))\b', r'\bcorrigend((um)|(a))\b', r'\bcorrections?\b', r'\bberichtigung\b']]):
                create_marc_field(record, {'tag': '935', 'ind1': ' ', 'ind2': ' ',
                                           'subfields': {'a': ['erco'], '2': ['LOK']}})
                # Abrufzeichen für die Nachbearbeitung von Errata/Corrigenda!
            responsibles = get_fields(record, '100') + get_fields(record, '700')
            url = get_subfield(record, '856', 'u')
            for responsible in responsibles:
                if re.match(r'^, ?$', responsible.find('{http://www.loc.gov/MARC21/slim}subfield[@code="a"]').text):
                    record.remove(responsible)
                if re.match(r'^\w\., \w\.$', responsible.find('{http://www.loc.gov/MARC21/slim}subfield[@code="a"]').text):
                    gnd_link = responsible.find('{http://www.loc.gov/MARC21/slim}subfield[@code="0"]')
                    if gnd_link is not None:
                        responsible.remove(gnd_link)
            ppns = []
            is_theo = False
            form_tag = record.find('{http://www.loc.gov/MARC21/slim}datafield[@tag="655"][@ind2="7"]'
                                   '/{http://www.loc.gov/MARC21/slim}subfield[@code="a"]')
            if form_tag is None:
                if re.search(r'[^\d]((?:\d{3}[\- ])?(?:\d[\- ]?){10})', title):
                    create_marc_field(record, {'tag': '655', 'ind1': ' ', 'ind2': '7',
                                               'subfields': {'a': ['Rezension'], '0': ['(DE-588)4049712-4', '(DE-627)106186019'], '2': ['gnd-content']}})
                    print('created tag Rezension for url', url)
            elif form_tag.text == "Rezension":
                ppns, is_theo = create_review_link(record)
                if not ppns:
                    isbn_list = re.findall(r'[^\d]((?:\d{3}[\- ])?(?:\d[\- ]?){10})', title)
                    for isbn in isbn_list:
                        isbn = re.sub(r'[\- ]', '', isbn)
                        isbn = isbn + 'x' if len(isbn) == 10 else isbn
                        isbn_ppns, isbn_is_theo = search_publication_with_isbn(isbn)
                        ppns.append(isbn_ppns)
                        is_theo.append(isbn_is_theo)
                ppn_list_nr = 0
                for ppn_list in ppns:
                    if ppn_list:
                        for ppn in ppn_list:
                            create_marc_field(record, {'tag': '787', 'ind1': '0', 'ind2': '8',
                                                       'subfields': {'i': ['Rezension von'], 'w': ['(DE-627)' + ppn]}})
                            create_marc_field(record, {'tag': '935', 'ind1': ' ', 'ind2': ' ',
                                                       'subfields': {'a': ['aurl'], '2': ['LOK']}})
                            print('link created to ppn', ppn)
                            review_links_created += 1
                            if not is_theo[ppn_list_nr]:
                                non_ixtheo_ppns.append(ppn)
                    ppn_list_nr += 1
            check_abstract(record)
            journal_link_tag = record.find('{http://www.loc.gov/MARC21/slim}datafield[@tag="773"]'
                                            '/{http://www.loc.gov/MARC21/slim}subfield[@code="t"]')
            journal_link_tag.text = journal_link_tag.text.strip('+')
            journal_name_tag = record.find('{http://www.loc.gov/MARC21/slim}datafield[@tag="JOU"]'
                                           '/{http://www.loc.gov/MARC21/slim}subfield[@code="a"]')
            journal_name_tag.text = journal_name_tag.text.strip('+')
            if append_to_postprocess:
                '''if form_tag is not None:
                    if form_tag.text == 'Rezension':
                        create_marc_field(record, {'tag': '650', 'ind1': ' ', 'ind2': '4',
                                                   'subfields': {'a': ['RezensionstagPica']}})'''
                post_process_root.append(record)
                post_process_nr += 1
            else:
                if zeder_id + '.json' in os.listdir('W:/FID-Projekte/Team Retro-Scan/Zotero/jstor_json'):
                    with open('W:/FID-Projekte/Team Retro-Scan/Zotero/jstor_json/' + zeder_id + '.json', 'r',
                              encoding="utf-8") as jstor_file:
                        jstor_dict = json.load(jstor_file)
                        if add_jstor_links(record, jstor_dict, year, volume, issue, pagination):
                            total_jstor_fails += 1
                        else:
                            total_jstor_links += 1
                proper_root.append(record)
                proper_nr += 1
    if non_ixtheo_ppns:
        with open(zeder_id + '_rezensierte_werke_nicht_ixtheo.csv', 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile, delimiter=';',
                                    quotechar='"', quoting=csv.QUOTE_MINIMAL)
            for non_ixtheo_ppn in non_ixtheo_ppns:
                csv_writer.writerow([non_ixtheo_ppn])
    proper_tree.write(zeder_id + '_proper.xml', encoding='utf-8', xml_declaration=True)
    if post_process_nr > 0:
        post_process_tree.write(zeder_id + '_post_process.xml', encoding='utf-8', xml_declaration=True)
    if zeder_id in present_record_list:
        print('missing doublets:', present_record_list[zeder_id])
    print('total number of records harvested:', record_nr)
    print('proper:', proper_nr)
    print('post_process:', post_process_nr)
    print('discarded:', discarded_nr + discarded_by_volume_nr)
    print('discarded by volume:', discarded_by_volume_nr)
    print('volumes discarded:', volumes_discarded)
    print('total jstor fails:', total_jstor_fails)
    print('total jstor links:', total_jstor_links)
    print('review links created:', review_links_created)


# announcement, books and media received