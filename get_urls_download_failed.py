import os
import re
import json


def get_urls(zeder_id):
    all_items = []
    failing_urls = []
    if zeder_id + '.out' in os.listdir():
        with open(zeder_id + '.out', 'r') as out_file:
            text = out_file.read()
            successfull_urls = re.findall(r'Generated 1 record\(s\) for item (\d+) ', text)
            for successfull_url in successfull_urls:
                all_items.append(successfull_url)
            failing_urls = re.findall(r'\| (.+?) \{.+} download failed!', text, re.IGNORECASE)
            failing_item_urls = re.findall(r'Converting item \d+ .+? \| (.+?) .+?\n.+? --> Skipping record with URL .+? because it is an undesired item type', text, re.IGNORECASE)
            failing_urls += failing_item_urls
            aborted_urls = re.findall(r'DIRECT @ ([^\s]+)\n.+\n.+\n', text, re.IGNORECASE)
            failing_urls += aborted_urls
        with open(zeder_id + '_failing_links.json', 'w') as file:
            json.dump(failing_urls, file)


if __name__ == '__main__':
    zeder_id = input('Bitte geben Sie die Zeder-ID ein: ')
    get_urls(zeder_id)