import os
from shutil import copy2
from time import strftime
import json
import xml.etree.ElementTree as ElementTree
from termcolor import colored


move_to_scp_server = ''
commands = ''
timestamp = strftime('%y%m%d')
total_record_number = 0
file_nr = 0
file_nr_for_filename = 1
with open('W:/FID-Projekte/Team Retro-Scan/Zotero/Einspielen_TestDB/files_renamed.json', 'r') as renamed_files_file:
    renamed_files = json.load(renamed_files_file)
    file_nr_for_filename += len([renamed_files[filename] for filename in renamed_files if timestamp + '_' in renamed_files[filename]])
    for file in os.listdir('proper_files'):
        if file not in renamed_files:
            ElementTree.register_namespace('', "http://www.loc.gov/MARC21/slim")
            result_tree = ElementTree.parse('final_files/' + file)
            result_root = result_tree.getroot()
            records = result_root.findall('.//{http://www.loc.gov/MARC21/slim}record')
            total_record_number += len(records)
            if total_record_number > 20000:
                print(colored('total record number exceeds maximum capazity of ftp-server.', 'red'))
                continue
            file_nr_for_filename += 1
            file_nr += 1
            new_filename_for_ftp = 'ixtheo_zotero_' + timestamp + '_' + str(file_nr_for_filename).zfill(3) + '.xml'
            copy2('proper_files/' + file, 'W:/FID-Projekte/Team Retro-Scan/Zotero/Einspielen_TestDB/' + new_filename_for_ftp)
            renamed_files[file] = new_filename_for_ftp
            move_to_scp_server += '\npython3 upload_to_bsz_ftp_server.py ' + new_filename_for_ftp + ' /pub/UBTuebingen_Default_Test/'

with open('W:/FID-Projekte/Team Retro-Scan/Zotero/Einspielen_TestDB/files_renamed.json', 'w') as renamed_files_file:
    json.dump(renamed_files, renamed_files_file)

print(str(file_nr), 'files renamed and moved to folder')

print('Commands:')
print('Dateien auf BENU verschieben & Dateien von BENU auf den FTP-Server legen:\nW:\ncd /FID-Projekte/Team Retro-Scan/Zotero/Einspielen_TestDB'
      '\nscp ixtheo_zotero_' + timestamp + '_*.xml hnebel@benu.ub.uni-tuebingen.de:/home/hnebel/bsz')
print('\nssh hnebel@benu.ub.uni-tuebingen.de\ncd /home/hnebel/bsz'
      + move_to_scp_server)
