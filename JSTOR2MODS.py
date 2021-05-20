import copy
import os
import sys
import xml.etree.ElementTree as ET
from nameparser import HumanName

if __name__ == '__main__':
    ET.register_namespace('', "http://www.loc.gov/mods/v3")
    # jeweils entsprechende ISSNs für die Zotero-Mapping-Listen aus der ISSN_to_superior_ppn.map heraussuchen!!!
    nr = 0

    template_tree = ET.parse('example.xml')

    template_root = template_tree.getroot()
    whole_xml = template_root.find('{http://www.loc.gov/mods/v3}mods')

    # immer modsCollection ersetzen und ns0: entfernen!!!
    # das ist wahrscheinlich jetzt nicht mehr notwendig!!!

    for directory in os.listdir('jstor_metadata'):
        for file in os.listdir('jstor_metadata/' + directory):
            nr += 1
            try:

                new_whole_xml = copy.deepcopy(whole_xml)
                title_tag = new_whole_xml.find(
                    "./{http://www.loc.gov/mods/v3}titleInfo/{http://www.loc.gov/mods/v3}title")

                url = new_whole_xml.find("./{http://www.loc.gov/mods/v3}location/{http://www.loc.gov/mods/v3}url")

                abstract = new_whole_xml.find("./{http://www.loc.gov/mods/v3}abstract")

                language = new_whole_xml.find(
                    "./{http://www.loc.gov/mods/v3}language/{http://www.loc.gov/mods/v3}languageTerm[@type='text']")

                journal_title_tag = new_whole_xml.find(
                    ".//{http://www.loc.gov/mods/v3}relatedItem/{http://www.loc.gov/mods/v3}titleInfo/{http://www.loc.gov/mods/v3}title")

                journal_part = new_whole_xml.find(
                    ".//{http://www.loc.gov/mods/v3}relatedItem/{http://www.loc.gov/mods/v3}part")
                volume = journal_part.find(
                    ".//{http://www.loc.gov/mods/v3}detail[@type='volume']/{http://www.loc.gov/mods/v3}number")

                issue = journal_part.find(
                    ".//{http://www.loc.gov/mods/v3}detail[@type='issue']/{http://www.loc.gov/mods/v3}number")

                firstpage = journal_part.find(
                    ".//{http://www.loc.gov/mods/v3}extent[@unit='pages']/{http://www.loc.gov/mods/v3}start")

                lastpage = journal_part.find(
                    ".//{http://www.loc.gov/mods/v3}extent[@unit='pages']/{http://www.loc.gov/mods/v3}end")

                date = new_whole_xml.find(
                    ".//{http://www.loc.gov/mods/v3}relatedItem/{http://www.loc.gov/mods/v3}originInfo/{http://www.loc.gov/mods/v3}dateIssued")

                origin_info = new_whole_xml.find(
                    ".//{http://www.loc.gov/mods/v3}relatedItem/{http://www.loc.gov/mods/v3}originInfo")

                publisher = ET.SubElement(origin_info, 'publisher')

                issn = new_whole_xml.find(
                    ".//{http://www.loc.gov/mods/v3}relatedItem/{http://www.loc.gov/mods/v3}identifier[@type='issn']")

                doi = new_whole_xml.find("./{http://www.loc.gov/mods/v3}identifier[@type='doi']")

                tree = ET.parse('jstor_metadata/' + directory + '/' + file)
                article_xml = tree.getroot()

                recent_title_tag = article_xml.find(".//article-meta/title-group/article-title")
                if recent_title_tag is None:
                    reviewed_title = article_xml.find(".//article-meta/product/source").text
                    reviewed_author = article_xml.find(".//article-meta/product/string-name")
                    if reviewed_author:
                        if (reviewed_author.find('.//surname') is not None and reviewed_author.find('.//given-names') is not None):
                            name = reviewed_author.find('.//surname').text + ', ' + reviewed_author.find('.//given-names').text
                            title_tag.text = name.strip() + ': ' + reviewed_title.strip()
                        elif reviewed_author.find('.//surname') is not None:
                            title_tag.text = reviewed_author.find('.//surname').text.strip() + ': ' + reviewed_title.strip()
                    else:
                        title_tag.text = reviewed_title
                    subject = ET.SubElement(new_whole_xml, 'subject')
                    topic = ET.SubElement(subject, 'topic')
                    topic.text = "RezensionstagPica"
                # ist das so in Ordnung oder soll ich das noch anpassen?
                #[Rezension von: [Autorenname], [Titel des Rezensierten Werkes]]
                else:
                    title_tag.text = recent_title_tag.text
                    # hier den Titel capitalizen; Ausnahmen bei welchen Fällen? z.B Römische Zahlen?
                    # ja.
                    if title_tag.text in ["Front Matter", "Back Matter", "Volume Information", "CONTRIBUTORS"]:
                        continue

                for new_name in article_xml.findall(".//article-meta/contrib-group/contrib"):
                    # type="personal"?
                    name_tag = ET.SubElement(new_whole_xml, 'name')
                    if new_name.find(".//string-name/surname") is not None:
                        givenname_tag = ET.SubElement(name_tag, 'namePart', {'type': 'given'})
                        givenname_tag.text = new_name.find(".//string-name/given-names").text
                        lastname_tag = ET.SubElement(name_tag, 'namePart', {'type': 'family'})
                        lastname_tag.text = new_name.find("./string-name/surname").text
                    elif new_name.find(".//string-name") is not None:
                        name_text = new_name.find(".//string-name").text
                        name_parts = HumanName(name_text)
                        givenname_tag = ET.SubElement(name_tag, 'namePart', {'type': 'given'})
                        givenname_tag.text = name_parts.first
                        lastname_tag = ET.SubElement(name_tag, 'namePart', {'type': 'family'})
                        lastname_tag.text = name_parts.last
                        role = ET.SubElement(name_tag, 'role')
                        roleTerm = ET.SubElement(role, "roleTerm", {'type': 'code', 'authority': 'marcrelator'})
                        roleTerm.text = 'aut'

                ns = {'xlink': "http://www.w3.org/1999/xlink"}
                recent_url = article_xml.find('.//article-meta/self-uri[@xlink:href]', ns).attrib[
                        '{http://www.w3.org/1999/xlink}href']
                url.text = recent_url
                print(url.text)
                meta_tags = article_xml.findall(".//article-meta/custom-meta-group/custom-meta")
                for meta_tag in meta_tags:
                    if meta_tag.find(".//meta-name").text == 'lang':
                        language.text = meta_tag.find(".//meta-value").text

                journal_title_tag.text = article_xml.find('.//journal-meta/journal-title-group/journal-title').text
                volume.text = article_xml.find('.//article-meta/volume').text
                if article_xml.find('.//article-meta/issue') is not None:
                    issue.text = article_xml.find('.//article-meta/issue').text

                firstpage.text = article_xml.find('.//article-meta/fpage').text
                lastpage.text = article_xml.find('.//article-meta/lpage').text
                date.text = article_xml.find('.//article-meta/pub-date/year').text
                # hier eventuell nochmal gegenchecken, of das pub-date den Typen ppub hat?

                publisher.text = article_xml.find('.//journal-meta/publisher/publisher-name').text
                recent_issn = article_xml.find('.//journal-meta/issn[@pub-type="epub"]').text
                issn.text = recent_issn[:4] + '-' + recent_issn[4:]
                # hier nach zotero_harvester.conf-Angaben anpassen über eine JSON-Datei.
                for recent_subject in article_xml.findall('.//article-meta/article-categories/subj-group/subject'):
                    subject = ET.SubElement(new_whole_xml, 'subject')
                    topic = ET.SubElement(subject, 'topic')
                    topic.text = recent_subject.text
                    # nehmen wir Schlagwortfolgen als solche auf??? mit $a trennen!!!
                    # Sollen die Topics capitalized werden?
                    # Sollen Genre-Tags rausgeworfen werden? > Nein!
                template_root.append(new_whole_xml)
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                print(exc_type, fname, exc_tb.tb_lineno)
                print(directory + '/' + file)
            if nr == 3000:
                break
        template_tree.write('example_test.xml', xml_declaration=True)

'https://sru.bsz-bw.de/swb?version=1.1&query=pica.all%3Deaster+and+pica.per%3Dmueller&operation=searchRetrieve&maximumRecords=10&recordSchema=marcxmlk10os'
# URL für Dublettenkontrolle
# Verlag wird bei Artikeln nicht gesetzt, ist deshalb okay, dass er fehlt!
# hier steht, wie man Kinder suchen kann:
'https://wiki.k10plus.de/display/K10PLUS/SRU'
# vorher schauen, wo überhaupt was dranhängt
# nach Jahreszahlen +- 1 filtern.

# in ZEDER prüfen, ab wann katalogisiert wurde Und dann die restlichen ODER alles mit Dublettenprüfung?

# Nachrufe sind ohne Seitenzahlen! Wie sollen diese verarbeitet werden?

# Nachrufe ausgeben lassen zur Kontrolle.

# welche Abrufzeichen müssten dann im MARCXML noch gesetzt werden?




'''

<Element 'fn-group' at 0x000001C769374130>
<Element 'title' at 0x000001C769374180>
<Element 'fn' at 0x000001C7693741D0>
<Element 'label' at 0x000001C769374220>
<Element 'p' at 0x000001C769374270>
<Element 'mixed-citation' at 0x000001C769374310>
'''

# eventuell noch bearbeiten:
# <Element '{http://www.loc.gov/mods/v3}modsCollection' at 0x000001F129964F90>
# <Element '{http://www.loc.gov/mods/v3}mods' at 0x000001F129975040>
# <Element '{http://www.loc.gov/mods/v3}genre' at 0x000001F1299752C0>
# <Element '{http://www.loc.gov/mods/v3}role' at 0x000001F129975450>
# <Element '{http://www.loc.gov/mods/v3}roleTerm' at 0x000001F1299754F0>
# {http://www.loc.gov/mods/v3}abstract
# {http://www.loc.gov/mods/v3}identifier[@type='doi']