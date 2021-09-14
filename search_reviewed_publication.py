import urllib.request
from bs4 import BeautifulSoup
import re
import unidecode


def check_response_for_priority_of_results(xml_soup):
    # print(xml_soup.find('zs:numberofrecords'))
    SWB_ppns = []
    theo_ppns = []
    other_ppns = []
    if xml_soup.find('zs:numberofrecords').text != '0':
        for record in xml_soup.find_all('record'):
            ppn = record.find('datafield', tag='003@').find('subfield', code='0').text
            ixtheo = False
            # hier den Record auswählen, der eine 1 als SSG Zeichen hat ODER ein anderes Kennzeichen
            ssg_tags = [element.find('subfield', code='a').text for element in record.find_all('datafield', tag='045V')]
            for ssg_tag in ['1', '0', '6,22']:
                if ssg_tag in ssg_tags:
                    ixtheo = True
                    print('found ssg')
                    break
            if not ixtheo:
                cods = [element.find('subfield', code='a').text for element in record.find_all('datafield', tag='016B')]
                for cod in ['mteo', 'redo', 'DTH5', 'AUGU', 'DAKR', 'MIKA', 'BIIN', 'KALD', 'GIRA']:
                    if cod in cods:
                        ixtheo = True
                        print('found cod')
                        break
            if ixtheo:
                theo_ppns.append(ppn)
            elif record.find('datafield', tag='007G').find('subfield', code='i').text == 'BSZ':
                SWB_ppns.append(ppn)
            else:
                other_ppns.append(ppn)
    # print(theo_ppns)
    # print(SWB_ppns)
    # print(other_ppns)
    if theo_ppns:
        return theo_ppns, True
    elif SWB_ppns:
        return SWB_ppns, False
    else:
        return other_ppns, False


def encode_in_ascii_and_remove_whitespaces_and_points(string: str, is_author, is_place):
    if is_author:
        list_of_letters = re.findall(r'[\w,]+', string)
    elif is_place:
        list_of_letters = [re.findall(r'[\w]+', string)[0]]
    else:
        list_of_letters = [word if word.lower() not in ['all', 'or', 'and'] else "'" + word for word in re.findall(r'\w+', string)]
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
            if pub_dict[key] != 'null':
                url += 'pica.' + key + '%3D' + pub_dict[key].strip('.') + '+and+'
    url = url.strip('+and+') + '&maximumRecords=10&recordSchema=picaxml'
    print(url)
    xml_data = urllib.request.urlopen(url)
    xml_soup = BeautifulSoup(xml_data, features='lxml')
    ppns, is_theo = check_response_for_priority_of_results(xml_soup)
    return ppns, is_theo


def search_publication_with_isbn(isbn: str):
    url = 'http://sru.k10plus.de/opac-de-627?version=1.1&operation=searchRetrieve&query=pica.isb%3D' + isbn + '&maximumRecords=10&recordSchema=picaxml'
    print(url)
    xml_data = urllib.request.urlopen(url)
    xml_soup = BeautifulSoup(xml_data, features='lxml')
    ppns, is_theo = check_response_for_priority_of_results(xml_soup)
    return ppns, is_theo


if __name__ == '__main__':
    # search_publication('The Semantic Field of Cutting Tools in Biblical Hebrew', 'koller, aaron j.', '2012', 'washington')
    search_publication_with_isbn('Book Reviews: Three Thomist Studies. By Frederick E. Crowe, SJ (Supplementary issue of Lonergan Workshop, vol. 16, edited by Michael Vertin and Frederick Lawrence.) Boston: Boston College, 2000. Pp. xxiv+260. ISBN 0-9700862-0-2')

# prüfen, ob SSG-Kennzeichen vorhanden & in Liste schreiben, falls nicht (für Überprüfung an Herrn Faßnacht).
# mit Dubletten umgehen (immer vorzugsweise die gekennzeichnete, dann andere SWB-Aufnahmen verwenden)
# Abrufzeichen in W:\FID-Projekte\Zweitveröffentlichung\Arbeitsunterlagen_Hilfsmittel_Links
# in der Datei Abrufzeichen IxTheo.pdf prüfen, alles, was hier zutrifft, übernehmen.
