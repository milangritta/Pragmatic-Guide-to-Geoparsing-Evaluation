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
from objects_and_functions import text_to_ann

# matplotlib.use('TkAgg')
# from os import listdir
# import matplotlib.pyplot as plt

# -------------------------------START OF GENERATION---------------------------------

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
# tree.write("data/GeoWebNews.xml", encoding='utf-8', pretty_print=True)

# counter = Counter(domains)
# print counter.most_common()
# print len(domains)

# plt.hist([x for (x, y) in counter.most_common()], bins=range(0, len(domains), 50))
# plt.show()

# ------------------------------------END OF CORPUS GENERATION-----------------------------------------


# -----------------------------------START OF BRAT FILES GENERATION------------------------------------

# tree = etree.parse(u'data/GeoWebNews.xml')
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

# ----------------------------------- START OF ANNOTATOR AGREEMENT ---------------------------------------

# from bratutils import agreement as a
#
# milan = a.DocumentCollection('data/IAA/milano/')
# flora = a.DocumentCollection('data/IAA/flora/')
# mina = a.DocumentCollection('data/IAA/mina/')
# milan.make_gold()

# ------------------ PLEASE READ -------------------------
# You need to paste this code change into agreement.py in BratUtils at line 650
# because we must exclude the augmentation files and Non_Toponym boundaries.
# if not line.startswith("#") and not line.startswith("A"):
#     ann = Annotation(line)
#     if ann.tag_name not in ["Non_Toponym", "Literal_Expression", "Non_Lit_Expression"]:
#         self.tags.append(ann)
# -------------------- THANKS ----------------------------


# print(flora.compare_to_gold(milan))
# print("Milan-Flora IAA")
# print(mina.compare_to_gold(milan))
# print("Milan-Mina IAA")

# milan_geo = text_to_ann("data/IAA/milano/")
# mina_geo = text_to_ann("data/IAA/mina/")
# exclude = ["Non_Toponym", "Literal_Expression", "Non_Lit_Expression"]
# agree, total = 0.0, 0.0
#
# for milan_file, mina_file in zip(milan_geo, mina_geo):
#     assert milan_file == mina_file
#     for milan_ann in milan_geo[milan_file]:
#         gold = milan_geo[milan_file][milan_ann]
#         if gold.toponym_type in exclude:
#             continue
#         for mina_ann in mina_geo[mina_file]:
#             comp = mina_geo[mina_file][mina_ann]
#             if comp.toponym_type in exclude:
#                 continue
#             if comp.start == gold.start and comp.end == gold.end:
#                 total += 1
#                 if comp.geonames_id != gold.geonames_id:
#                     print(comp.text, comp.toponym_type)
#                     print(comp.geonames_id, gold.geonames_id)
#                     print(milan_file, comp.key)
#                     print("---------------------------------")
#                 else:
#                     agree += 1
#
# print("Geocoding agreement (accuracy):", agree / total)

# ----------------------------------- END OF ANNOTATOR AGREEMENT ---------------------------------------


# ------------------------------------START OF CORPUS STATISTICS-----------------------------------------

conn = sqlite3.connect('../data/geonames.db')
c = conn.cursor()

annotations = text_to_ann()
mixed, coercion, metonymy = 0, 0, 0
embedded_lit, embedded_non_lit = 0, 0
literal_exp, non_lit_exp, literals = 0, 0, 0
literal_type, non_literal_type, total = 0, 0, 0
literal_heads, non_lit_heads, homonyms = 0, 0, 0
modifier_noun_lit, modifier_adj_lit, no_geo = 0, 0, 0
modifier_noun_non, modifier_adj_non, non_toponym = 0, 0, 0
demonym, language, has_coordinates, has_geonames = 0, 0, 0, 0

for ann in annotations:
    for key in annotations[ann]:
        x = annotations[ann][key]
        total += 1
        if x.toponym_type == "Literal_Expression":
            literal_exp += 1
            if x.non_locational:
                non_lit_heads += 1
            else:
                literal_heads += 1
        elif x.toponym_type == "Non_Lit_Expression":
            non_lit_exp += 1
            if x.non_locational:
                non_lit_heads += 1
            else:
                literal_heads += 1
        elif x.toponym_type == "Literal":
            literals += 1
        elif x.toponym_type == "Mixed":
            mixed += 1
        elif x.toponym_type == "Embedded_Literal":
            embedded_lit += 1
        elif x.toponym_type == "Embedded_Non_Lit":
            embedded_non_lit += 1
        elif x.toponym_type == "Coercion":
            coercion += 1
        elif x.toponym_type == "Metonymic":
            metonymy += 1
        elif x.toponym_type == "Literal_Modifier":
            if x.modifier_type == "Noun":
                modifier_noun_lit += 1
            if x.modifier_type == "Adjective":
                modifier_adj_lit += 1
        elif x.toponym_type == "Non_Literal_Modifier":
            if x.modifier_type == "Noun":
                modifier_noun_non += 1
            if x.modifier_type == "Adjective":
                modifier_adj_non += 1
        elif x.toponym_type == "Demonym":
            demonym += 1
        elif x.toponym_type == "Language":
            language += 1
        elif x.toponym_type == "Homonym":
            homonyms += 1
        elif x.toponym_type == "Non_Toponym":
            non_toponym += 1
        if x.geonames_id is not None:
            if "," in x.geonames_id:
                has_coordinates += 1
            else:
                has_geonames += 1
        else:
            no_geo += 1

print("------------------------------------------------------------------")
print("Total Annotations:", total)
print("Literal Expressions:", literal_exp)
print("Non_Lit Expressions:", non_lit_exp)
print("Heads (literal, non_literal):", (literal_heads, non_lit_heads))
total_minus_expressions = total - literal_exp - non_lit_exp - non_toponym
print("Total excluding Expressions and Non_Toponyms:", total_minus_expressions)
print("------------------------------------------------------------------")
print("Literals:", literals, np.around(float(literals) / total_minus_expressions, 5) * 100, "%")
print("Mixed:", mixed, np.around(float(mixed) / total_minus_expressions, 5) * 100, "%")
print("Coercion:", coercion, np.around(float(coercion) / total_minus_expressions, 5) * 100, "%")
print("Embedded Lit:", embedded_lit, np.around(float(embedded_lit) / total_minus_expressions, 5) * 100, "%")
print("Literal Mods (noun, adj):", (modifier_noun_lit, modifier_adj_lit),
    (np.around(float(modifier_noun_lit) / total_minus_expressions, 5) * 100,
     np.around(float(modifier_adj_lit) / total_minus_expressions, 5) * 100), "%")
group_tot = literals + mixed + coercion + modifier_noun_lit + modifier_adj_lit + embedded_lit
print("Group total:", group_tot, np.around(float(group_tot) / total_minus_expressions, 5) * 100, "%")
print("------------------------------------------------------------------")
print("Metonymy:", metonymy, np.around(float(metonymy) / total_minus_expressions, 5) * 100, "%")
print("Non_Lit Mods (noun, adj):", (modifier_noun_non, modifier_adj_non),
    (np.around(float(modifier_noun_non) / total_minus_expressions, 5) * 100,
     np.around(float(modifier_adj_non) / total_minus_expressions, 5) * 100), "%")
print("Demonyms:", demonym, np.around(float(demonym) / total_minus_expressions, 5) * 100, "%")
print("Language:", language, np.around(float(language) / total_minus_expressions, 5) * 100, "%")
print("Homonyms:", homonyms, np.around(float(homonyms) / total_minus_expressions, 5) * 100, "%")
print("Embedded Non_Lit:", embedded_non_lit, np.around(float(embedded_non_lit) / total_minus_expressions, 5) * 100, "%")
group_tot = homonyms + embedded_non_lit + metonymy + modifier_noun_non + modifier_adj_non + demonym + language
print("Group total:", group_tot, np.around(float(group_tot) / total_minus_expressions, 5) * 100, "%")
print("------------------------------------------------------------------")
print("Sanity Check:", demonym + language + homonyms + embedded_lit + embedded_non_lit + non_toponym +
                       modifier_adj_non + modifier_noun_non + modifier_adj_lit + modifier_noun_lit + metonymy +
                       coercion + mixed + literals + literal_exp + non_lit_exp, "should equal total above.")
print("Coordinates vs Geonames vs None:", has_coordinates, has_geonames, no_geo)
print("Non_Toponyms", non_toponym, "should equal", coercion + embedded_non_lit + embedded_lit)
print("Total files annotated:", len(annotations))
print("------------------------------------------------------------------")

# Geocoding Stats? Which types, plus map, population baseline, etc.

# ------------------------------------END OF CORPUS STATISTICS-----------------------------------------


