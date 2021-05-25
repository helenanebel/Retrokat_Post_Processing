import csv
import urllib.request
from bs4 import BeautifulSoup

# Listen liegen hier: W:\FID-Projekte\Team Retro-Scan\ImageWare\1 Vorarbeit MyBib eDoc\Prüfung PPN-Listen

csv_file = open('2019.csv', 'r')
csv_reader = csv.reader(csv_file, delimiter=';', quotechar='"')
items_of_series_file = open('2019_Stuecktitel.csv', 'w')
csv_writer = csv.writer(items_of_series_file, delimiter=';', quotechar='"')
row_nr = -1
for row in csv_reader:
    row_nr += 1
    if row_nr < 1:
        continue
    ppn = row[0]
    if ppn:
        filedata = urllib.request.urlopen('http://sru.k10plus.de/'
                                          'opac-de-627?version=1.1&operation=searchRetrieve&query=pica.ppn%3D'
                                          + ppn + '&maximumRecords=10&recordSchema=picaxml')
        data = filedata.read()
        xml_soup = BeautifulSoup(data, "lxml")
        if xml_soup.find('datafield', tag='036F'):
            if xml_soup.find('datafield', tag='036F').find('subfield', code='R'):
                if xml_soup.find('datafield', tag='036F').find('subfield', code='R').text[1] == 'b':
                    print(ppn)
                    csv_writer.writerow([ppn])
