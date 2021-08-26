import urllib.request


def search_publication(title, author, year, publisher, place):
      title = title.replace(' ', '+')
      url = 'http://sru.k10plus.de/opac-de-627?version=1.1&operation=searchRetrieve&query=pica.tit%3D' \
            + title + '+and+pica.per%3D' + author + '+and+pica.jah%3D' + year + \
            '+and+pica.ver%3D' + place + '&maximumRecords=10&recordSchema=picaxml'
      print(url)
      xml_data = urllib.request.urlopen(url)


if __name__ == '__main__':
      print(search_publication('The Semantic Field of Cutting Tools in Biblical Hebrew', 'koller', '2012', '', 'washington'))

