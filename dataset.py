import codecs
import spacy
import sqlite3
from collections import Counter
from os.path import isfile
import numpy as np
from urlparse import urlparse
from lxml import etree, objectify
import matplotlib
from objects_and_functions import Annotation, get_coordinates

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
annotations, annotated = {}, 0
for f in files:
    if f.endswith(".txt") or f.startswith("."):
        continue
    ann = {}
    annotations[str(f.replace(".ann", ""))] = ann
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
    if len(ann) > 0:
        annotated += 1

literal_type, non_literal_type, total = 0, 0, 0
literal_exp, non_lit_exp, literals = 0, 0, 0
literal_heads, non_lit_heads = 0, 0
mixed, pragmatics, metonymy = 0, 0, 0
embedded_assoc, embedded_non, homonyms = 0, 0, 0
modifier_noun_lit, modifier_adj_lit, post_mod_lit = 0, 0, 0
modifier_noun_non, modifier_adj_non, post_mod_non = 0, 0, 0
demonym, language, has_coordinates, has_geonames = 0, 0, 0, 0

for ann in annotations:
    for key in annotations[ann]:
        x = annotations[ann][key]
        if x.type == "Literal_Expression":
            literal_exp += 1
            if x.non_locative:
                non_lit_heads += 1
            else:
                literal_heads += 1
        if x.type == "Non_Lit_Expression":
            non_lit_exp += 1
            if x.non_locative:
                non_lit_heads += 1
            else:
                literal_heads += 1
        if x.type == "Literal":
            literals += 1
        if x.type == "Mixed":
            mixed += 1
        if x.type == "Facilities":
            pragmatics += 1
        if x.type == "Metonymic":
            metonymy += 1
        if x.type == "Modifier":
            if x.non_locative:
                if x.mod_value == "Noun" or x.mod_value == "Possessive":
                    modifier_noun_non += 1
                if x.mod_value == "Adjective":
                    modifier_adj_non += 1
                if x.mod_value == "Appositional":
                    post_mod_non += 1
            else:
                if x.mod_value == "Noun" or x.mod_value == "Possessive":
                    modifier_noun_lit += 1
                if x.mod_value == "Adjective":
                    modifier_adj_lit += 1
                if x.mod_value == "Appositional":
                    post_mod_lit += 1
            if x.mod_value == "Demonym":
                demonym += 1
            if x.mod_value == "Language":
                language += 1
        if x.type == "Embedded":
            if x.non_locative:
                embedded_non += 1
            else:
                embedded_assoc += 1
        if x.type == "Homonym":
            homonyms += 1
        if x.geonames is not None:
            if "," in x.geonames:
                has_coordinates += 1
            else:
                has_geonames += 1
        total += 1

print "------------------------------------------------------------------"
print "Total Annotations:", total
print "Literal Expressions:", literal_exp
print "Non_Lit Expressions:", non_lit_exp
print "Heads (literal, non_literal):", (literal_heads, non_lit_heads)
total_minus_expressions = total - literal_exp - non_lit_exp
print "Total excluding Expressions:", total_minus_expressions
print "------------------------------------------------------------------"
print "Literals:", literals, np.around(float(literals) / total_minus_expressions, 3) * 100, "%"
print "Mixed:", mixed, np.around(float(mixed) / total_minus_expressions, 3) * 100, "%"
print "Facilities:", pragmatics, np.around(float(pragmatics) / total_minus_expressions, 3) * 100, "%"
print "Literal Mods (noun, adj, post):", (modifier_noun_lit, modifier_adj_lit, post_mod_lit), \
    (np.around(float(modifier_noun_lit + post_mod_lit) / total_minus_expressions, 3) * 100,
     np.around(float(modifier_adj_lit) / total_minus_expressions, 3) * 100,
     np.around(float(post_mod_lit) / total_minus_expressions, 3) * 100), "%"
group_tot = literals + mixed + pragmatics + modifier_noun_lit + modifier_adj_lit + post_mod_lit
print "Group total:", (group_tot), np.around(float(group_tot) / total_minus_expressions, 3) * 100, "%"
print "------------------------------------------------------------------"
print "Metonymy:", metonymy, np.around(float(metonymy) / total_minus_expressions, 3) * 100, "%"
print "Non_Lit Mods (noun, adj, post):", (modifier_noun_non, modifier_adj_non, post_mod_non), \
    (np.around(float(modifier_noun_non) / total_minus_expressions, 3) * 100,
     np.around(float(modifier_adj_non) / total_minus_expressions, 3) * 100,
     np.around(float(post_mod_non) / total_minus_expressions, 3) * 100), "%"
print "Demonyms:", demonym, np.around(float(demonym) / total_minus_expressions, 3) * 100, "%"
print "Language:", language, np.around(float(language) / total_minus_expressions, 3) * 100, "%"
group_tot = metonymy + modifier_noun_non + modifier_adj_non + post_mod_non + demonym + language
print "Group total:", (group_tot), np.around(float(group_tot) / total_minus_expressions, 3) * 100, "%"
print "------------------------------------------------------------------"
print "Homonyms:", homonyms, np.around(float(homonyms) / total_minus_expressions, 3) * 100, "%"
print "Embedded (assoc, non-loc):", (embedded_assoc, embedded_non), \
    (np.around(float(embedded_assoc) / total_minus_expressions, 3) * 100,
     np.around(float(embedded_non) / total_minus_expressions, 3) * 100), "%"
group_tot = homonyms + embedded_assoc + embedded_non
print "Group total:", (group_tot), np.around(float(group_tot) / total_minus_expressions, 3) * 100, "%"
print "------------------------------------------------------------------"
print "Sanity Check:", demonym + language + homonyms + post_mod_lit + post_mod_non + embedded_non + embedded_assoc + \
                       modifier_adj_non + modifier_noun_non + modifier_adj_lit + modifier_noun_lit + metonymy + \
                       pragmatics + mixed + literals + literal_exp + non_lit_exp, "should equal total above!"
print "Coordinates vs Geonames:", has_coordinates, has_geonames
print "Total files annotated:", annotated
print "------------------------------------------------------------------"

# Geocoding Stats? Which types, plus map, population baseline, etc.

# ------------------------------------END OF CORPUS STATISTICS-----------------------------------------

# ------------------------------------START OF 100% TOPONYM RECALL---------------------------------------

nlp = spacy.load(u'en_core_web_lg')
files = [f for f in listdir(dir_path) if isfile(dir_path + f)]
conn = sqlite3.connect('../data/geonames.db')
c = conn.cursor()
stopwords = nlp.Defaults.stop_words
# add plural and singular
adjectival_tops = set([annotations[x][y].text for x in annotations for y in annotations[x]
                       if annotations[x][y].mod_value == 'Adjective' or annotations[x][y].mod_value == 'Demonym'])

for f in files:
    if f.endswith(".ann") or f.startswith("."):
        continue
    file_id = f.replace(".txt", "")
    f = codecs.open(dir_path + f, encoding="utf-8")
    doc = nlp(f.read())
    print doc
    print "ID:", file_id
    indices = dict([(annotations[file_id][ann].start, annotations[file_id][ann].end) for ann in annotations[file_id]])
    for word in doc:
        if word.text.istitle() and word.text.lower() not in stopwords:
            coord = get_coordinates(c, word.text)
            if len(coord) > 0 or word.text in adjectival_tops:
                if unicode(word.idx) not in indices:
                    print word, word.i

# ------------------------------------END OF 100% TOPONYM RECALL-----------------------------------------
