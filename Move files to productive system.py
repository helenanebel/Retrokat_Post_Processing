import os
from shutil import copy2
from time import strftime
import json

move_to_scp_server = ''
commands = ''
timestamp = strftime('%y%m%d')
file_nr = 1
with open('W:/FID-Projekte/Team Retro-Scan/Zotero/Einspielen_ProduktivDB/files_renamed.json', 'r') as renamed_files_file:
    renamed_files = json.load(renamed_files_file)
    for file in os.listdir('final_files'):
        if file not in renamed_files:
            file_nr += 1
            new_filename_for_ftp = 'ixtheo_zotero_' + timestamp + '_' + str(file_nr).zfill(3) + '.xml'
            copy2('proper_files/' + file, 'W:/FID-Projekte/Team Retro-Scan/Zotero/Einspielen_ProduktivDB/' + new_filename_for_ftp)
            renamed_files[file] = new_filename_for_ftp
            move_to_scp_server += '\npython3 upload_to_bsz_ftp_server.py ' + new_filename_for_ftp + ' /pub/UBTuebingen_Default/'

with open('W:/FID-Projekte/Team Retro-Scan/Zotero/Einspielen_ProduktivDB/files_renamed.json', 'w') as renamed_files_file:
    json.dump(renamed_files, renamed_files_file)

print(str(file_nr - 1), 'files renamed and moved to folder')

print('Commands:')
print('Dateien auf BENU verschieben:\nW:\ncd /FID-Projekte/Team Retro-Scan/Zotero/Einspielen_ProduktivDB'
      '\nscp ixtheo_zotero_' + timestamp + '_*.xml hnebel@benu.ub.uni-tuebingen.de:/home/hnebel/bsz')
print('Dateien von BENU auf den FTP-Server legen:\nssh hnebel@benu.ub.uni-tuebingen.de\ncd /home/hnebel/bsz'
      + move_to_scp_server)
