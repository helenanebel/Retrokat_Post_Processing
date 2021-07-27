import os
import csv
import json

for file in os.listdir('W:/FID-Projekte/Team Retro-Scan/Zotero/jstor_csv'):
    jstor_dict = {}
    with open ('W:/FID-Projekte/Team Retro-Scan/Zotero/jstor_csv/' + file, 'r', encoding="utf-8") as jstor_csv_file:
        jstor_csv = csv.reader(jstor_csv_file, quotechar='"', delimiter=',')
        row_nr = 0
        for row in jstor_csv:
            row_nr += 1
            if row_nr < 2:
                continue
            if 'http://www.' not in row[0]:
                continue
            year = row[3]
            issue = row[8]
            volume = row[9]
            firstpage = row[14]
            lastpage = row[15]
            if not firstpage:
                continue
            if firstpage == lastpage:
                pages = firstpage
            else:
                pages = firstpage + '-' + lastpage
            if issue:
                if year not in jstor_dict:
                    jstor_dict[year] = {}
                if volume not in jstor_dict[year]:
                    jstor_dict[year][volume] = {}
                if issue not in jstor_dict[year][volume]:
                    jstor_dict[year][volume][issue] = {}
                if pages not in jstor_dict[year][volume][issue]:
                    jstor_dict[year][volume][issue][pages] = row[0]
                else:
                    del jstor_dict[year][volume][issue][pages]
                    print(pages in jstor_dict[year][volume][issue])
            else:
                if year not in jstor_dict:
                    jstor_dict[year] = {}
                if volume not in jstor_dict[year]:
                    jstor_dict[year][volume] = {}
                if pages not in jstor_dict[year][volume]:
                    jstor_dict[year][volume][pages] = row[0]
                else:
                    del jstor_dict[year][volume][issue][pages]
                    print(pages in jstor_dict[year][volume][issue])
    with open('W:/FID-Projekte/Team Retro-Scan/Zotero/jstor_json/' + file.replace('.csv', '.json'), 'w') as json_file:
        json.dump(jstor_dict, json_file)
