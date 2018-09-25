import codecs
import spacy
import sqlite3
from collections import Counter
# noinspection PyUnresolvedReferences
from os.path import isfile
import numpy as np
from urlparse import urlparse
from lxml import etree
import matplotlib
from objects_and_functions import text_to_ann, ANNOT_SOURCE_DIR

# matplotlib.use('TkAgg')
# from os import listdir
# import matplotlib.pyplot as plt

# ----------------------------------  START OF EMM CONVERSION  ------------------------------------

# file_ids = {}
# for file_name in sorted(text_to_ann().keys()):
#     text = codecs.open(ANNOT_SOURCE_DIR + file_name + ".txt", encoding="utf-8")
#     meta = text.next()
#     link = meta.split("LINK:")[1].strip()
#     file_ids[link] = file_name + "<SEP>" + str(len(meta))
#
# tree = etree.parse(u'data/EMM.xml')
# root = tree.getroot()
# for article in root:
#     link = article.find("link").text
#     title_length = len(article.find("title").text) + 2
#     if link in file_ids:
#         f = codecs.open("data/EMM/" + file_ids[link].split("<SEP>")[0] + ".ann", mode="w", encoding="utf-8")
#         for geo in article.findall("{http://emm.jrc.it}fullgeo") + article.findall("{http://emm.jrc.it}georss"):
#             name = geo.text
#             meta = int(file_ids[link].split("<SEP>")[1])
#             for pos in geo.attrib["pos"].split(","):
#                 if int(pos) >= title_length:
#                     f.write(u"INDEX\tLOCATION " + str(int(pos) + meta - title_length) + u" "
#                             + str(int(pos) + len(name) + meta - title_length) + u"\t" + name + u"\n")

# ------------------------------------ END OF EMM CONVERSION-----------------------------------------

# ----------------------------------- START OF ANNOTATOR AGREEMENT ---------------------------------------

# milan = a.DocumentCollection('data/IAA/milano/')
# flora = a.DocumentCollection('data/IAA/flora/')
# mina = a.DocumentCollection('data/IAA/mina/')
# milan.make_gold()

# ------------------ PLEASE READ -------------------------
# You need to paste this code change into agreement.py in BratUtils at line 653
# because we must exclude the augmentation files and Non_Toponym boundaries.
# if not line.startswith("#") and not line.startswith("A"):
#     ann = Annotation(line)
#     if ann.tag_name not in ["Non_Toponym", "Literal_Expression", "Non_Lit_Expression"]:
#         self.tags.append(ann)
# Line 303, add return text, "LITERAL", start_idx, end_idx for SPacy, Google evaluation.
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

# ------------------ START F-SCORE EVALUATION -----------------
# SPACY
# from bratutils import agreement as a
# test = a.DocumentCollection('data/Spacy/')
# gold = a.DocumentCollection('data/GeoWebNews/')
# gold.make_gold()
# print(test.compare_to_gold(gold))

# GOOGLE
# from bratutils import agreement as a
# test = a.DocumentCollection('data/Google/')
# gold = a.DocumentCollection('data/GeoWebNews/')
# gold.make_gold()
# print(test.compare_to_gold(gold))

# EMM
# from bratutils import agreement as a
# test = a.DocumentCollection('data/EMM/')
# gold = a.DocumentCollection('data/GeoWebNews/')
# gold.make_gold()
# print(test.compare_to_gold(gold))

# ------------------- END F-SCORE EVALUATION ------------------

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


