from hashlib import blake2b
from datetime import datetime

test_record = '''<record>
<leader>00000nab a22004452  4500</leader>
<controlfield tag="001">IxTheo#2021-12-29#1E3B6BDB882867F28E2ADB3434329917075B2B65</controlfield>
<controlfield tag="003">DE-Tue135</controlfield>
<controlfield tag="007">cr|||||</controlfield>
<datafield tag="024" ind1="7" ind2=" ">
<subfield code="a">10.1017/S002204692000305X</subfield>
<subfield code="2">doi</subfield>
</datafield>
<datafield tag="040" ind1=" " ind2=" ">
<subfield code="a">DE-627</subfield>
<subfield code="b">ger</subfield>
<subfield code="c">DE-627</subfield>
<subfield code="e">rda</subfield>
</datafield>
<datafield tag="041" ind1=" " ind2=" ">
<subfield code="a">eng</subfield>
</datafield>
<datafield tag="084" ind1=" " ind2=" ">
<subfield code="a">1</subfield>
<subfield code="2">ssgn</subfield>
</datafield>
<datafield tag="100" ind1="1" ind2=" ">
<subfield code="0">(DE-588)103882950X</subfield>
<subfield code="4">aut</subfield>
<subfield code="a">Hoover, Jesse</subfield>
<subfield code="e">VerfasserIn</subfield>
</datafield>
<datafield tag="245" ind1="0" ind2="0">
<subfield code="a">The Apocalyptic Number 616 and the Donatist Church</subfield>
</datafield>
<datafield tag="264" ind1=" " ind2=" ">
<subfield code="c">2021</subfield>
</datafield>
<datafield tag="520" ind1=" " ind2=" ">
<subfield code="a">The apocalyptic number 616 is attested as a variant for the more common 666 in Revelation xiii.18 as early as Irenaeus as well as in several ancient Greek manuscripts. Surprisingly, however, all known exegetical interpretations of the number in late antiquity and the early medieval era can be traced back to just two sources derived from the Donatist Church in North Africa: Tyconius’ Expositio apocalypseos and the anonymous Liber genealogus. After reviewing these sources and the exegetical traditions predicated on them, this article will introduce a third witness to the 616 variant within the Donatist communion and comment on its implications.</subfield>
</datafield>
<datafield tag="650" ind1=" " ind2="4">
<subfield code="a">Berlin 1826–</subfield>
</datafield>
<datafield tag="650" ind1=" " ind2="4">
<subfield code="a">Auctores Antiquissimi</subfield>
</datafield>
<datafield tag="650" ind1=" " ind2="4">
<subfield code="a">Monumenta Germaniae Historica</subfield>
</datafield>
<datafield tag="650" ind1=" " ind2="4">
<subfield code="a">DC 1948–</subfield>
</datafield>
<datafield tag="650" ind1=" " ind2="4">
<subfield code="a">Washington</subfield>
</datafield>
<datafield tag="650" ind1=" " ind2="4">
<subfield code="a">Fathers of the Church</subfield>
</datafield>
<datafield tag="650" ind1=" " ind2="4">
<subfield code="a">Turnhout 1954–</subfield>
</datafield>
<datafield tag="650" ind1=" " ind2="4">
<subfield code="a">Series Latina</subfield>
</datafield>
<datafield tag="650" ind1=" " ind2="4">
<subfield code="a">Corpus Christianorum</subfield>
</datafield>
<datafield tag="773" ind1="0" ind2="8">
<subfield code="i">In: </subfield>
<subfield code="t">The journal of ecclesiastical history : JEH</subfield>
<subfield code="x">1469-7637</subfield>
<subfield code="w">(DE-627)265785375</subfield>
<subfield code="g">72 (2021), 4, Seite 709-725</subfield>
</datafield>
<datafield tag="852" ind1=" " ind2=" ">
<subfield code="a">DE-Tue135</subfield>
</datafield>
<datafield tag="856" ind1="4" ind2="0">
<subfield code="u">https://doi.org/10.1017/S002204692000305X</subfield>
<subfield code="z">ZZ</subfield>
</datafield>
<datafield tag="856" ind1="4" ind2="0">
<subfield code="u">https://www.cambridge.org/core/journals/journal-of-ecclesiastical-history/article/apocalyptic-number-616-and-the-donatist-church/0775DE1C87F329E3270E5A34AF356069</subfield>
<subfield code="z">ZZ</subfield>
</datafield>
<datafield tag="887" ind1=" " ind2=" ">
<subfield code="a">Autor in der Zoterovorlage [Hoover, Jesse] maschinell zugeordnet</subfield>
<subfield code="2">ixzom</subfield>
</datafield>
<datafield tag="935" ind1=" " ind2=" ">
<subfield code="a">mteo</subfield>
</datafield>
<datafield tag="935" ind1=" " ind2=" ">
<subfield code="a">ixzs</subfield>
<subfield code="2">LOK</subfield>
</datafield>
<datafield tag="935" ind1=" " ind2=" ">
<subfield code="a">zota</subfield>
<subfield code="2">LOK</subfield>
</datafield>
<datafield tag="936" ind1="u" ind2="w">
<subfield code="d">72</subfield>
<subfield code="e">4</subfield>
<subfield code="h">709-725</subfield>
<subfield code="j">2021</subfield>
</datafield>
<datafield tag="JOU" ind1=" " ind2=" ">
<subfield code="a">The journal of ecclesiastical history : JEH</subfield>
</datafield>
<datafield tag="URL" ind1=" " ind2=" ">
<subfield code="a">https://www.cambridge.org/core/journals/journal-of-ecclesiastical-history/article/apocalyptic-number-616-and-the-donatist-church/0775DE1C87F329E3270E5A34AF356069</subfield>
</datafield>
<datafield tag="ZID" ind1=" " ind2=" ">
<subfield code="a">1347</subfield>
<subfield code="b">ixtheo</subfield>
</datafield>
</record>'''


def get_hash(record_string: str):
    time = datetime.now()
    timestamp = time.strftime("%Y-%m-%d")
    h = blake2b(digest_size=20)
    record_string = record_string.encode('utf8')
    h.update(record_string)
    value = h.hexdigest()
    hash_value = value.upper()
    complete_hash = "IxTheo#" + timestamp + "#" + hash_value
    return complete_hash


if __name__ == "__main__":
    print(get_hash(test_record))
    # IxTheo#2022-01-05#7C9388591D815D72818F85BDFA758C6F7B81934C
