import os
import xml.etree.ElementTree as ElementTree

all_issns = []
for directory in os.listdir('W:/FID-Projekte/Team Retro-Scan/Zotero/jstor_metadata/raw'):
    for file in os.listdir('W:/FID-Projekte/Team Retro-Scan/Zotero/jstor_metadata/raw/' + directory):
        tree = ElementTree.parse('W:/FID-Projekte/Team Retro-Scan/Zotero/jstor_metadata/raw/' + directory + '/' + file)
        article_xml = tree.getroot()
        recent_issn = article_xml.find('.//journal-meta/issn[@pub-type="epub"]').text
        if recent_issn not in all_issns:
            print(recent_issn)
            os.mkdir('W:/FID-Projekte/Team Retro-Scan/Zotero/jstor_metadata/' + recent_issn)
            all_issns.append(recent_issn)
        with open('W:/FID-Projekte/Team Retro-Scan/Zotero/jstor_metadata/' + recent_issn + '/' + file, 'w') as new_file:
            new_file.close()
        tree.write('W:/FID-Projekte/Team Retro-Scan/Zotero/jstor_metadata/' + recent_issn + '/' + file, encoding='utf-8', xml_declaration=True)
