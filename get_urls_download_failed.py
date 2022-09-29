import os
import re
import json


def get_urls(zeder_id):
    all_items = []
    failing_urls = []
    if zeder_id + '_failing_links.json' not in os.listdir():
        if zeder_id + '.out' not in os.listdir('W:/FID-Projekte/Team Retro-Scan/Zotero/results'):
            resulting_string = ""
            found_out_file = False
            if zeder_id + '_out' in os.listdir('W:/FID-Projekte/Team Retro-Scan/Zotero/results'):
                zid = zeder_id.replace('+', '\+')
                for file in os.listdir('W:/FID-Projekte/Team Retro-Scan/Zotero/results/' + zeder_id + '_out/'):
                    if re.findall(r'^' + zid + '_', file):
                        found_out_file = True
                        with open('W:/FID-Projekte/Team Retro-Scan/Zotero/results/' + zeder_id + '_out/' + file, 'r') as out_file:
                            text = out_file.read()
                            resulting_string += text + "\n"
            if found_out_file:
                with open('W:/FID-Projekte/Team Retro-Scan/Zotero/results/' + zeder_id + '.out', 'w') as resulting_out_file:
                    resulting_out_file.write(resulting_string)
        if zeder_id + '.out' in os.listdir('W:/FID-Projekte/Team Retro-Scan/Zotero/results'):
            with open('W:/FID-Projekte/Team Retro-Scan/Zotero/results/' + zeder_id + '.out', 'r') as out_file:
                text = out_file.read()
                successfull_urls = re.findall(r'Generated 1 record\(s\) for item (\d+) ', text)
                for successfull_url in successfull_urls:
                    all_items.append(successfull_url)
                failing_urls = re.findall(r'\| (.+?) \{.+} download failed!', text, re.IGNORECASE)
                failing_item_urls = re.findall(r'Converting item \d+ .+? \| (.+?) .+?\n.+? --> Skipping record with URL .+? because it is an undesired item type', text, re.IGNORECASE)
                failing_urls += failing_item_urls
                aborted_urls = re.findall(r'DIRECT @ ([^\s]+)\n.+\n.+\n', text, re.IGNORECASE)
                failing_urls += aborted_urls
                unsuccessfull_crawl_attempts = re.findall(r'Unsuccessful crawl attempt for (.+?)\n', text, re.IGNORECASE)
                failing_urls += unsuccessfull_crawl_attempts
                unsuccessfull_downloads = re.findall(r'\| (.+?) \{.+?\} download failed!', text, re.IGNORECASE)
                failing_urls += unsuccessfull_downloads
            with open(zeder_id + '_failing_links.json', 'w') as file:
                failing_urls = list(set(failing_urls))
                json.dump(failing_urls, file)


if __name__ == '__main__':
    zeder_id = input('Bitte geben Sie die Zeder-ID ein: ')
    get_urls(zeder_id)