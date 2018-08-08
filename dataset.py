import codecs
import spacy
import sqlite3
from collections import Counter
# noinspection PyUnresolvedReferences
from os.path import isfile
import numpy as np
from urlparse import urlparse
from lxml import etree, objectify
import matplotlib
from objects_and_functions import Annotation, get_coordinates, text_to_ann

# matplotlib.use('TkAgg')
# from os import listdir
# import matplotlib.pyplot as plt

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


# -----------------------------------START OF BRAT FILES GENERATION------------------------------------

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

# ------------------------------------END OF BRAT FILES GENERATION---------------------------------------


# ------------------------------------START OF CORPUS STATISTICS-----------------------------------------

conn = sqlite3.connect('../data/geonames.db')
c = conn.cursor()

annotations = text_to_ann()

embedded, homonyms, no_geo = 0, 0, 0
literal_heads, non_lit_heads = 0, 0
mixed, coercion, metonymy = 0, 0, 0
literal_exp, non_lit_exp, literals = 0, 0, 0
literal_type, non_literal_type, total = 0, 0, 0
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
        if x.type == "Coercion":
            coercion += 1
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
            embedded += 1
        if x.type == "Homonym":
            homonyms += 1
        if x.geonames is not None:
            if "," in x.geonames:
                has_coordinates += 1
            else:
                has_geonames += 1
        else:
            no_geo += 1
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
print "Coercion:", coercion, np.around(float(coercion) / total_minus_expressions, 3) * 100, "%"
print "Literal Mods (noun, adj, post):", (modifier_noun_lit, modifier_adj_lit, post_mod_lit), \
    (np.around(float(modifier_noun_lit + post_mod_lit) / total_minus_expressions, 3) * 100,
     np.around(float(modifier_adj_lit) / total_minus_expressions, 3) * 100,
     np.around(float(post_mod_lit) / total_minus_expressions, 3) * 100), "%"
group_tot = literals + mixed + coercion + modifier_noun_lit + modifier_adj_lit + post_mod_lit
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
print "Embedded:", embedded, \
     np.around(float(embedded) / total_minus_expressions, 3) * 100, "%"
group_tot = homonyms + embedded
print "Group total:", (group_tot), np.around(float(group_tot) / total_minus_expressions, 3) * 100, "%"
print "------------------------------------------------------------------"
print "Sanity Check:", demonym + language + homonyms + post_mod_lit + post_mod_non + embedded + \
                       modifier_adj_non + modifier_noun_non + modifier_adj_lit + modifier_noun_lit + metonymy + \
                       coercion + mixed + literals + literal_exp + non_lit_exp, "should equal total above!"
print "Coordinates vs Geonames vs None:", has_coordinates, has_geonames, no_geo
print "Total files annotated:", len(annotations)
print "------------------------------------------------------------------"

# Geocoding Stats? Which types, plus map, population baseline, etc.

# ------------------------------------END OF CORPUS STATISTICS-----------------------------------------


