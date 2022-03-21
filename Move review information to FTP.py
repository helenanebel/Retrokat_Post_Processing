import os
from shutil import copy2
from time import strftime

move_to_scp_server = ''
commands = ''
timestamp = strftime('%Y%m%d')
total_record_number = 0
file_nr = 0
file_nr_for_filename = 4

for file in os.listdir('review_information'):
    if timestamp in file:
        copy2('review_information/' + file, 'W:/FID-Projekte/Team Retro-Scan/Zotero/Einspielen_Sonstiges/' + file)
        move_to_scp_server += '\npython3 upload_to_bsz_ftp_server.py ' + file + ' /pub/UBTuebingen_Sonstiges/'


print('Commands:')
print('Dateien auf BENU verschieben & von BENU auf den FTP-Server legen:'
      '\nW:\ncd /FID-Projekte/Team Retro-Scan/Zotero/Einspielen_Sonstiges'
      '\nscp ' + timestamp + '_*.csv hnebel@benu.ub.uni-tuebingen.de:/home/hnebel/bsz'
      '\n\nssh hnebel@benu.ub.uni-tuebingen.de\ncd /home/hnebel/bsz' + move_to_scp_server)
