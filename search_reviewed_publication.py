import urllib.request
from bs4 import BeautifulSoup
import re
import unidecode


def encode_in_ascii_and_remove_whitespaces_and_points(string: str, is_author, is_place):
    if is_author:
        list_of_letters = re.findall(r'[\w,]+', string)
    elif is_place:
        list_of_letters = [re.findall(r'[\w]+', string)[0]]
    else:
        list_of_letters = re.findall(r'\w+', string)
    decoded_string = '+'.join(list_of_letters)
    decoded_string = unidecode.unidecode(decoded_string)
    decoded_string = decoded_string.strip('+')
    return decoded_string

# Probleme:
# Plotinus, Self and the Wo rld (Leerzeichen innerhalb führen zu Problemen)

def search_publication(title, author, year, place):
    pub_dict = {}
    pub_dict["tit"] = encode_in_ascii_and_remove_whitespaces_and_points(title, False, False)
    pub_dict["jah"] = encode_in_ascii_and_remove_whitespaces_and_points(year, False, False)
    if not pub_dict['jah']:
        pub_dict["ver"] = encode_in_ascii_and_remove_whitespaces_and_points(place, False, True)
    author = author.replace('::', ' or ')
    author = encode_in_ascii_and_remove_whitespaces_and_points(author, True, False)
    pub_dict["per"] = '"' + author + '"'
    url = 'http://sru.k10plus.de/opac-de-627?version=1.1&operation=searchRetrieve&query='
    for key in pub_dict:
        if pub_dict[key]:
            url += 'pica.' + key + '%3D' + pub_dict[key].strip('.') + '+and+'
    url = url.strip('+and+') + '&maximumRecords=10&recordSchema=picaxml'
    xml_data = urllib.request.urlopen(url)
    xml_soup = BeautifulSoup(xml_data, features='lxml')
    # print(xml_soup.find('zs:numberofrecords'))
    if xml_soup.find('zs:numberofrecords').text != '0':
        # hier den Record auswählen, der eine 1 als SSG Zeichen hat ODER ein anderes Kennzeichen
        if '1' not in [element.find('subfield', code='a').text for element in xml_soup.find_all('datafield', tag='045V')]:
            print(url)
            print(xml_soup.find('datafield', tag='007G').find('subfield', code='i').text)
            print(xml_soup.find('datafield', tag='003@').find('subfield', code='0').text)




if __name__ == '__main__':
    search_publication('The Semantic Field of Cutting Tools in Biblical Hebrew', 'koller, aaron j.', '2012', 'washington')

# Verlagsname und -ort verwenden, prüfen, ob SSG-Kennzeichen vorhanden & in Liste schreiben, falls nicht (für Überprüfung an Herrn Faßnacht).
# mit Dubletten umgehen (immer vorzugsweise die SWB-Aufnahme, als erstes unsere, verwenden)
# zuerst gekennzeichnete, dann wenn möglich SWB-Aufnahmen.
# Abrufzeichen in W:\FID-Projekte\Zweitveröffentlichung\Arbeitsunterlagen_Hilfsmittel_Links
# in der Datei Abrufzeichen IxTheo.pdf prüfen, alles, was hier zutrifft, übernehmen.