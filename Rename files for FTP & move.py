import os
from shutil import copy2
from time import strftime

move_to_scp_server = ''
commands = ''
files_renamed = ''
timestamp = strftime('%y%m%d')
file_nr = 1
for file in os.listdir('proper_files'):
    if file not in os.listdir('W:/FID-Projekte/Team Retro-Scan/Zotero/Einspielen_TestDB'):
        file_nr += 1
        copy2('proper_files/' + file, 'W:/FID-Projekte/Team Retro-Scan/Zotero/Einspielen_TestDB/' + file)
        new_filename_for_ftp = 'ixtheo_zotero_' + timestamp + '_' + str(file_nr).zfill(3) + '.xml'
        copy2('proper_files/' + file, 'W:/FID-Projekte/Team Retro-Scan/Zotero/Einspielen_TestDB/' + new_filename_for_ftp)
        files_renamed += file.ljust(16) + '=     ' + new_filename_for_ftp + '\n'
        move_to_scp_server += '\npython3 upload_to_bsz_ftp_server.py ' + new_filename_for_ftp + ' /pub/UBTuebingen_Default_Test/'
with open('W:/FID-Projekte/Team Retro-Scan/Zotero/Einspielen_TestDB/files_renamed_on_' + timestamp + '.txt', 'w') as doku_file:
    doku_file.write(files_renamed)

print(str(file_nr - 1), 'files renamed and moved to folder')

print('Commands:')
print('Dateien auf BENU verschieben:\nW:\ncd /FID-Projekte/Team Retro-Scan/Zotero/Einspielen_TestDB'
      '\nscp ixtheo_zotero_' + timestamp + '_*.xml hnebel@benu.ub.uni-tuebingen.de:/home/hnebel/bsz')
print('Dateien von BENU auf den FTP-Server legen:\nssh hnebel@benu.ub.uni-tuebingen.de\ncd /home/hnebel/bsz'
      + move_to_scp_server)
