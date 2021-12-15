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
            total_number = re.findall(r'Harvests:\s+(\d+)\n', text)[0]
            for number in [str(num) for num in range(1, int(total_number))]:
                if number not in all_items:
                    if 'Downloading URL ' + number + ' [' not in text:
                        failing_url = re.findall(rf'Item {number} \[.+?] \| ([^\s]+?)\s', text, re.IGNORECASE)
                        if failing_url:
                            failing_urls.append(failing_url[0])
        with open(zeder_id + '_failing_urls.json', 'w') as file:
            json.dump(failing_urls, file)


if __name__ == '__main__':
    zeder_id = input('Bitte geben Sie die Zeder-ID ein: ')
    get_urls(zeder_id)