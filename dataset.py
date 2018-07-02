import codecs
import sqlite3
from collections import Counter
from os.path import isfile
from urlparse import urlparse
from lxml import etree, objectify
import matplotlib
from objects_and_functions import Annotation

matplotlib.use('TkAgg')
from os import listdir
import matplotlib.pyplot as plt

# -------------------------------START OF GENERATION---------------------------------

# big_tree = etree.ElementTree(etree.Element('articles'))
# big_root = big_tree.getroot()
# for i in range(1, 27):
#     tree = etree.parse(u'data/medisys' + unicode(i) + u'.xml')
#     root = tree.getroot()
#     for article in root.findall('channel/item'):
#         if article.find('{http://www.iso.org/3166}language').text == u'en':
#             big_root.append(article)
# big_tree.write("data/EMM.xml", encoding='utf-8', pretty_print=True)

# domains = set()
# tree = etree.parse(u'data/EMM.xml')
# root = tree.getroot()
# for article in root:
#     if len(domains) > 499:
#         root.remove(article)
#         continue
#     link = article.find('link').text
#     if urlparse(link)[1] not in domains and int(article.find('{http://emm.jrc.it}text').attrib['wordCount']) / 10 > 10:
#         domains.add(urlparse(link)[1])
#     else:
#         root.remove(article)
# tree.write("data/EMM.xml", encoding='utf-8', pretty_print=True)

# tree = etree.parse(u'data/EMM.xml')
# root = tree.getroot()
# for article in root:
#     etree.strip_attributes(article, '{http://emm.jrc.it}nil')
#     for attr in article.attrib:
#         article.attrib.pop(attr, None)
#     for attribute in article:
#         if attribute.tag not in ['title', 'link', 'pubDate', '{http://emm.jrc.it}text']:
#             article.remove(attribute)
#         else:
#             attribute.tag = etree.QName(attribute).localname
# tree.write("data/WebNews500.xml", encoding='utf-8', pretty_print=True)

# print model.summary()

# counter = Counter(domains)
# print counter.most_common()
# print len(domains)

# plt.hist([x for (x, y) in counter.most_common()], bins=range(0, len(domains), 50))
# plt.show()

# ------------------------------------END OF CORPUS GENERATION-----------------------------------------


# -----------------------------------START OF BRAT FILES GENERATION--------------------------------------

# tree = etree.parse(u'data/WebNews500.xml')
# c = etree.parse(u'data/EMM.xml')
# for (index, article), control in zip(enumerate(tree.getroot()), c.getroot()):
#     f = codecs.open(u"WebNews500/" + unicode(index) + u".txt", "w", "utf-8")
#     ann = codecs.open(u"WebNews500/" + unicode(index) + u".ann", "w", "utf-8")
#     ann.close()
#     f.write(u"TITLE: " + article.find('title').text + u" LINK: " + article.find("link").text + u"\n")
#     f.write(article.find('text').text)
#     f.close()
#     if article.find('text').text != control.find('{http://emm.jrc.it}text').text:
#         raise Exception("Ring Ding Ding!!!")

# ------------------------------------END OF BRAT FILES GENERATION-----------------------------------------


# ------------------------------------START OF CORPUS STATISTICS-----------------------------------------

conn = sqlite3.connect('../data/geonames.db')
c = conn.cursor()
dir_path = u"/Users/milangritta/Downloads/BRAT/data/WebNews500-Annotator-1/"
files = [f for f in listdir(dir_path) if isfile(dir_path + f)]
annotations = {}
for f in files:
    if f.endswith(".txt") or f.startswith("."):
        continue
    ann = {}
    annotations[str(f)] = ann
    f = codecs.open(dir_path + f, encoding="utf-8")
    for line in f:
        line = line.strip().split("\t")
        if line[0].startswith("T"):  # token
            if line[0] in ann:
                raise Exception("Duplicate! Check.")
            else:
                ann[line[0]] = Annotation(line[0])
                ann[line[0]].text = line[2]
                data = line[1].split(" ")
                ann[line[0]].type = data[0]
                ann[line[0]].start = data[1]
                ann[line[0]].end = data[2]
        if line[0].startswith("A"):  # attribute
            data = line[1].split(" ")
            if data[1] not in ann:
                raise Exception("No record! Check.")
            if data[0] == "Modifier_Type":
                ann[data[1]].mod_value = data[2]
            elif data[0] == "Non_Locative":
                ann[data[1]].non_locative = True
            else:
                raise Exception("This should never be triggered!")
        if line[0].startswith("#"):  # annotator note
            data = line[1].split(" ")
            if data[1] not in ann:
                raise Exception("No record! Check.")
            ann[data[1]].geonames = line[2]

c, t = 0, 0
for ann in annotations:
    for key in annotations[ann]:
        t += 1
        x = annotations[ann][key]
        if x.type == "Literal": # and x.mod_value =="Demonym":
            c += 1
print c, t

# ------------------------------------END OF CORPUS STATISTICS-----------------------------------------
