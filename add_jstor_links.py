import re
import json
import sys
import os



def add_jstor_links(zeder_id: str):
    total_nr = 0
    total_matches = 0
    all_jstor_urls = []
    with open('W:/FID-Projekte/Team Retro-Scan/Zotero/jstor_json/' + zeder_id + '.json', 'r',
                  encoding="utf-8") as jstor_file:
            jstor_dict = json.load(jstor_file)
    with open('W:/FID-Projekte/Team Retro-Scan/Zotero/publisher_json/' + zeder_id + '.json', 'r',
              encoding="utf-8") as jstor_file:
        publisher_dict = json.load(jstor_file)
    jstor_mapping_dict = {}
    for year in publisher_dict:
        for volume in publisher_dict[year]:
            for issue in publisher_dict[year][volume]:
                for pagination in publisher_dict[year][volume][issue]:
                    if year in jstor_dict:
                        """for v in jstor_dict[year]:
                            for i in jstor_dict[year][v]:
                                for p in jstor_dict[year][v][i]:
                                    pagination_dict[p] = jstor_dict[year][v][i][p]"""
                        if volume in jstor_dict[year]:
                            # volumes werden immer gefunden.
                            if issue in jstor_dict[year][volume]:
                                if pagination in jstor_dict[year][volume][issue]:
                                    if len(jstor_dict[year][volume][issue][pagination]) == 1:
                                        for author in jstor_dict[year][volume][issue][pagination]:
                                            total_nr += len(jstor_dict[year][volume][issue][pagination][author])
                                            publisher_author = \
                                            list(publisher_dict[year][volume][issue][pagination].keys())[0]
                                            if len(jstor_dict[year][volume][issue][pagination][author]) == 1:
                                                jstor_mapping_dict[publisher_dict[year][volume][issue][pagination][publisher_author][0]] = jstor_dict[year][volume][issue][pagination][author][0]
                                                total_matches += 1
                                            else:
                                                author_publication_list_jstor = sorted(jstor_dict[year][volume][issue][pagination][author])
                                                author_publication_list_publisher = sorted(publisher_dict[year][volume][issue][pagination][publisher_author])
                                                for p in range(len(author_publication_list_publisher)):
                                                    if p < len(author_publication_list_jstor):
                                                        jstor_mapping_dict[author_publication_list_publisher[p]] = author_publication_list_jstor[p]
                                                        total_matches += 1
                                    else:
                                        # hier mehrere Autoren auf selber Seite abprüfen!
                                        for jstor_author in jstor_dict[year][volume][issue][pagination]:
                                            total_nr += len(jstor_dict[year][volume][issue][pagination][jstor_author])
                                            author_publication_list_jstor = sorted(list(set(jstor_dict[year][volume][issue][pagination][jstor_author])))
                                            for publisher_author in publisher_dict[year][volume][issue][pagination]:
                                                author_publication_list_publisher = sorted(
                                                    list(set(publisher_dict[year][volume][issue][pagination][publisher_author])))
                                                publisher_names_list = [name.lower() for name in re.findall(r'\w+', publisher_author)]
                                                names_list = [name.lower() for name in re.findall(r'\w+', jstor_author)]
                                                if len([name for name in names_list if name in publisher_names_list]) >= 2:
                                                    if len(author_publication_list_jstor) != len(author_publication_list_publisher):
                                                        print('different list length')
                                                        print(author_publication_list_publisher, author_publication_list_jstor)
                                                        # Probleme bei:
                                                        # Review by: John Habgood
                                                        # http://www.jstor.org/stable/23959547
                                                        # Review by: John S. Habgood
                                                        # https://www.jstor.org/stable/23959548
                                                        # solche Autoren evtl. zusammenlegen.
                                                    for p in range(len(author_publication_list_publisher)):
                                                        if p < len(author_publication_list_jstor):
                                                            jstor_mapping_dict[author_publication_list_publisher[p]] = \
                                                            author_publication_list_jstor[p]
                                                            total_matches += 1

                                else:

                                    total_nr += 1
                                    pagination_found = False
                                    for p in [p for p in jstor_dict[year][volume][issue]
                                              if re.findall(r'^' + p.split('-')[0] + '-', pagination)]:
                                            try:
                                                if '-' in p:
                                                    difference = abs(int(p.split('-')[1]) - int(pagination.split('-')[1]))
                                                else:
                                                    difference = abs(int(p) - int(pagination.split('-')[1]))
                                                if difference <= 5:
                                                    if len(jstor_dict[year][volume][issue][p]) == 1:
                                                        for author in jstor_dict[year][volume][issue][p]:
                                                            total_nr += len(
                                                                jstor_dict[year][volume][issue][p][author])
                                                            publisher_author = \
                                                                list(
                                                                    publisher_dict[year][volume][issue][pagination].keys())[
                                                                    0]
                                                            if len(jstor_dict[year][volume][issue][p][
                                                                       author]) == 1:
                                                                jstor_mapping_dict[
                                                                    publisher_dict[year][volume][issue][pagination][
                                                                        publisher_author][0]] = \
                                                                jstor_dict[year][volume][issue][p][author][0]
                                                                total_matches += 1
                                                                pagination_found = True
                                                            else:
                                                                author_publication_list_jstor = sorted(
                                                                    jstor_dict[year][volume][issue][p][author])
                                                                author_publication_list_publisher = sorted(
                                                                    publisher_dict[year][volume][issue][pagination][
                                                                        publisher_author])
                                                                for ap in range(len(author_publication_list_publisher)):
                                                                    if ap < len(author_publication_list_jstor):
                                                                        jstor_mapping_dict[
                                                                            author_publication_list_publisher[ap]] = \
                                                                        author_publication_list_jstor[ap]
                                                                        pagination_found = True
                                                                        total_matches += 1
                                                    else:
                                                        for jstor_author in jstor_dict[year][volume][issue][p]:
                                                            total_nr += len(
                                                                jstor_dict[year][volume][issue][p][jstor_author])
                                                            author_publication_list_jstor = sorted(list(set(
                                                                jstor_dict[year][volume][issue][p][jstor_author])))
                                                            for publisher_author in publisher_dict[year][volume][issue][
                                                                pagination]:
                                                                author_publication_list_publisher = sorted(
                                                                    list(set(
                                                                        publisher_dict[year][volume][issue][pagination][
                                                                            publisher_author])))
                                                                publisher_names_list = [name.lower() for name in
                                                                                        re.findall(r'\w+',
                                                                                                   publisher_author)]
                                                                names_list = [name.lower() for name in
                                                                              re.findall(r'\w+', jstor_author)]
                                                                if len([name for name in names_list if
                                                                        name in publisher_names_list]) >= 2:
                                                                    if len(author_publication_list_jstor) != len(
                                                                            author_publication_list_publisher):
                                                                        print('different list length')
                                                                        print(author_publication_list_publisher,
                                                                              author_publication_list_jstor)
                                                                        # Probleme bei:
                                                                        # Review by: John Habgood
                                                                        # http://www.jstor.org/stable/23959547
                                                                        # Review by: John S. Habgood
                                                                        # https://www.jstor.org/stable/23959548
                                                                        # solche Autoren evtl. zusammenlegen.
                                                                    for ap in range(len(author_publication_list_publisher)):
                                                                        if ap < len(author_publication_list_jstor):
                                                                            jstor_mapping_dict[
                                                                                author_publication_list_publisher[ap]] = \
                                                                                author_publication_list_jstor[ap]
                                                                            total_matches += 1
                                                                            pagination_found = True
                                            except Exception as e:
                                                print('Error', e, p, pagination)
                                                exc_type, exc_obj, exc_tb = sys.exc_info()
                                                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]

                                                print(exc_type, fname, exc_tb.tb_lineno)
                                    if not pagination_found:
                                        print('pagination not found')
                                        print(pagination, year, volume, issue)
                                        print([pag for pag in jstor_dict[year][volume][issue]])
                            else:
                                print('issue not found', year, volume, issue)
    '''if jstor_url:
        # create_marc_field(record, {'tag': '866', 'ind1': ' ', 'ind2': ' ',
        # 'subfields': {'x': ['JSTOR#' + jstor_url], '2': ['LOK']}})
        '''
    # in ein File schreiben und da herauslesen
    print(total_nr, 'not matched:', total_nr - total_matches)


if __name__ == '__main__':
    add_jstor_links('1350')