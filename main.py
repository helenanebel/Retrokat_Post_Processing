import os
import add_missing_links
from transform_MARCXML import transform, check_and_split_in_issues
import json
from create_jstor_link_dict import get_jstor_links

if __name__ == '__main__':
    zeder_id = input('Bitte geben Sie die ZEDER-ID ein: ')
    conf_dict = {}
    conf_available = False
    if 'conf.json' in os.listdir('W:/FID-Projekte/Team Retro-Scan/Zotero/'):
        with open('W:/FID-Projekte/Team Retro-Scan/Zotero/conf.json', 'r') as conf_file:
            conf_dict = json.load(conf_file)
            if zeder_id in conf_dict:
                conf_available = True
                if 'eppn' not in conf_dict[zeder_id]:
                    conf_dict[zeder_id]['eppn'] = input('Bitte geben Sie die ePPN ein: ')
                    with open('W:/FID-Projekte/Team Retro-Scan/Zotero/conf.json', 'w') as conf_file:
                        json.dump(conf_dict, conf_file)
                if 'lang' not in conf_dict[zeder_id]:
                    conf_dict[zeder_id]['lang'] = input('Bitte geben Sie die Default-Sprache ein: ')
                    with open('W:/FID-Projekte/Team Retro-Scan/Zotero/conf.json', 'w') as conf_file:
                        json.dump(conf_dict, conf_file)
    if zeder_id + '.json' not in os.listdir('W:/FID-Projekte/Team Retro-Scan/Zotero/jstor_mapping'):
        get_jstor_links(zeder_id)
    record_nr = check_and_split_in_issues(zeder_id, conf_available)
    if not conf_available:
        exclude = input('Bitte geben Sie die Liste auszuschließender Titel ein: ')
        exclude = json.loads(exclude.replace("'", '"'))
        start_year = int(input('Bitte geben Sie das erste Jahr der Retrokatalogisierung ein: '))
        end_year = int(input('Bitte geben Sie das letzte Jahr der Retrokatalogisierung ein: '))
        period = (start_year, end_year)
        eppn = input('Bitte geben Sie die ePPN ein: ')
        default_lang = input('Bitte geben Sie die Default-Sprache ein: ')
        conf_dict[zeder_id] = {'exclude': exclude, 'period': period, 'eppn': eppn, 'lang': default_lang}
        if input('Wollen Sie diese Konfigurationsangaben speichern (j/n)') == 'j':
            with open('W:/FID-Projekte/Team Retro-Scan/Zotero/conf.json', 'w') as conf_file:
                json.dump(conf_dict, conf_file)
    period = conf_dict[zeder_id]['period']
    eppn = conf_dict[zeder_id]['eppn']
    add_missing_links.get_records_with_missing_links(conf_dict[zeder_id]['eppn'], zeder_id)
    with open('W:/FID-Projekte/Team Retro-Scan/Zotero/exclude.json', 'r') as exclusion_file:
        exclude_everywhere = json.load(exclusion_file)
    exclude = conf_dict[zeder_id]['exclude'] + exclude_everywhere
    default_lang = conf_dict[zeder_id]['lang']
    transform(zeder_id, exclude, period, record_nr, default_lang)
