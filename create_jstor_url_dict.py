import os
import csv
import json
import re


for file in os.listdir('W:/FID-Projekte/Team Retro-Scan/Zotero/jstor_csv'):
    #if file == '237.csv':
    total_nr = 0
    jstor_dict = {}
    print(file)
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
            author = row[11]
            if not firstpage:
                continue
            if firstpage == lastpage:
                pages = firstpage
            else:
                pages = firstpage + '-' + lastpage
            issue = re.sub(r'[^\d]', '-', issue)
            volume = re.sub(r'[^\d]', '-', volume)
            year = re.sub(r'[^\d]', '-', year)
            if not issue:
                issue = 'n'
            if year not in jstor_dict:
                jstor_dict[year] = {}
            if volume not in jstor_dict[year]:
                jstor_dict[year][volume] = {}
            if issue not in jstor_dict[year][volume]:
                jstor_dict[year][volume][issue] = {}
            if pages not in jstor_dict[year][volume][issue]:
                jstor_dict[year][volume][issue][pages] = {}
            if not author:
                author = 'nn'
            if author not in jstor_dict[year][volume][issue][pages]:
                jstor_dict[year][volume][issue][pages][author] = row[0]
                total_nr +=1
            else:
                del jstor_dict[year][volume][issue][pages]
    with open('W:/FID-Projekte/Team Retro-Scan/Zotero/jstor_json/' + file.replace('.csv', '.json'), 'w') as json_file:
        json.dump(jstor_dict, json_file)
    print(total_nr)