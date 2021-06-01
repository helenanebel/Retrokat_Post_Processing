import os

from transform_MARCXML import transform, check_and_split_in_issues
import json

if __name__ == '__main__':
    zeder_id = input('Bitte geben Sie die ZEDER-ID ein: ')
    check_and_split_in_issues(zeder_id)
    conf_dict = {}
    if 'conf.json' in os.listdir('W:/FID-Projekte/Team Retro-Scan/Zotero/'):
        with open('W:/FID-Projekte/Team Retro-Scan/Zotero/conf.json', 'r') as conf_file:
            conf_dict = json.load(conf_file)
        period = conf_dict[zeder_id]['period']
        exclude = conf_dict[zeder_id]['exclude']
    else:
        exclude = input('Bitte geben Sie die Liste auszuschließender Titel ein: ')
        exclude = json.loads(exclude.replace("'", '"'))
        start_year = int(input('Bitte geben Sie das erste Jahr der Retrokatalogisierung ein: '))
        end_year = int(input('Bitte geben Sie das letzte Jahr der Retrokatalogisierung ein: '))
        period = (start_year, end_year)
        conf_dict[zeder_id] = {'exclude': exclude, 'period': period}
        if input('Wollen Sie diese Konfigurationsangaben speichern (j/n)') == 'j':
            with open('W:/FID-Projekte/Team Retro-Scan/Zotero/conf.json', 'w') as conf_file:
                json.dump(conf_dict, conf_file)
    transform(zeder_id, exclude, period)
