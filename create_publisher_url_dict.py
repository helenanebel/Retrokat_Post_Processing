import json
import re
import xml.etree.ElementTree as ElementTree
from transform_MARCXML import get_subfield, get_fields
from convert_roman_numbers import from_roman

month_dict = {	'January':'1',
		'February':'2',
		'March':'3',
		'April':'4',
		'May':'5',
		'June':'6',
		'July':'7',
		'August':'8',
		'September':'9',
		'October':'10',
		'November':'11',
		'December':'12'		}

def get_url_dict(zeder_id: str):
    result_tree = ElementTree.parse('result_files/' + zeder_id + '.xml')
    result_root = result_tree.getroot()
    records = result_root.findall('.//{http://www.loc.gov/MARC21/slim}record')
    publisher_url_dict = {}
    for record in records:
        url = get_subfield(record, '856', 'u')
        year = get_subfield(record, '264', 'c')
        volume = get_subfield(record, '936', 'd')
        if volume:
            if re.search(r'[^\d/]', volume):
                new_volume = re.findall(r'[^\d](\d{1,3})[^\d]', volume)
                if new_volume:
                    volume = new_volume[0]
                    volume_tag = \
                        record.find('{http://www.loc.gov/MARC21/slim}datafield[@tag="936"]'
                                    '/{http://www.loc.gov/MARC21/slim}subfield[@code="d"]')
                    volume_tag.text = volume
                else:
                    if re.findall(r'^(?=[MDCLXVI])M*(?:C[MD]|D?C*)(?:X[CL]|L?X*)(?:I[XV]|V?I*)$', volume):
                        new_volume = from_roman(
                            re.findall(r'^(?=[MDCLXVI])M*(?:C[MD]|D?C*)(?:X[CL]|L?X*)(?:I[XV]|V?I*)$', volume)[0])
                    elif re.findall(r'(?=[MDCLXVI])M*(?:C[MD]|D?C*)(?:X[CL]|L?X*)(?:I[XV]|V?I*)$', volume):
                        new_volume = from_roman(
                            re.findall(r'(?=[MDCLXVI])M*(?:C[MD]|D?C*)(?:X[CL]|L?X*)(?:I[XV]|V?I*)$', volume)[0])
                    if new_volume:
                        volume_tag = \
                            record.find('{http://www.loc.gov/MARC21/slim}datafield[@tag="936"]'
                                        '/{http://www.loc.gov/MARC21/slim}subfield[@code="d"]')
                        volume_tag.text = str(new_volume)
                        volume = new_volume
                    else:
                        print(volume, 'is not convertible to ararbic number')
        issue = get_subfield(record, '936', 'e')
        if issue:
            if re.search(r'[^\d/]', issue):
                if re.findall(r'(\d+).+?(\d+)', issue):
                    issue = re.sub(r'(\d+).+?(\d+)', r'\1/\2', issue)
                    issue_tag = \
                        record.find('{http://www.loc.gov/MARC21/slim}datafield[@tag="936"]'
                                    '/{http://www.loc.gov/MARC21/slim}subfield[@code="e"]')
                    issue_tag.text = issue
                else:
                    new_issue = ''
                    if re.findall(r'^(?=[MDCLXVI])M*(?:C[MD]|D?C*)(?:X[CL]|L?X*)(?:I[XV]|V?I*)$', issue):
                        new_issue = from_roman(
                            re.findall(r'^(?=[MDCLXVI])M*(?:C[MD]|D?C*)(?:X[CL]|L?X*)(?:I[XV]|V?I*)$', issue)[0])
                    elif re.findall(r'(?=[MDCLXVI])M*(?:C[MD]|D?C*)(?:X[CL]|L?X*)(?:I[XV]|V?I*)$', issue):
                        new_issue = from_roman(
                            re.findall(r'(?=[MDCLXVI])M*(?:C[MD]|D?C*)(?:X[CL]|L?X*)(?:I[XV]|V?I*)$', issue)[0])
                    if new_issue:
                        issue_tag = \
                            record.find('{http://www.loc.gov/MARC21/slim}datafield[@tag="936"]'
                                        '/{http://www.loc.gov/MARC21/slim}subfield[@code="d"]')
                        issue_tag.text = str(new_issue)
                        issue = new_issue
                    else:
                        if issue in month_dict:
                            issue = month_dict[issue]
                            print(issue)
                        else:
                            print('not found in dict')
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
                        pagination = fpage
        responsibles = [field.find('{http://www.loc.gov/MARC21/slim}subfield[@code="a"]').text for field in get_fields(record, '100') + get_fields(record, '700')]
        author = 'nn'
        if responsibles:
            author = responsibles[0]
        if year not in publisher_url_dict:
            publisher_url_dict[year] = {}
        if volume not in publisher_url_dict[year]:
            publisher_url_dict[year][volume] = {}
        if issue not in publisher_url_dict[year][volume]:
            publisher_url_dict[year][volume][issue] = {}
        if pagination not in publisher_url_dict[year][volume][issue]:
            publisher_url_dict[year][volume][issue][pagination] = {}
        if author not in publisher_url_dict[year][volume][issue][pagination]:
            publisher_url_dict[year][volume][issue][pagination][author] = [url]
        else:
            publisher_url_dict[year][volume][issue][pagination][author] += [url]

    with open('W:/FID-Projekte/Team Retro-Scan/Zotero/publisher_json/' + zeder_id + '.json', 'w') as json_file:
        json.dump(publisher_url_dict, json_file)


if __name__ == '__main__':
    zeder_id = input('Bitte geben Sie die Zeder-ID ein: ')
    get_url_dict(zeder_id)
