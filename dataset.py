import codecs
import sqlite3
from xml.dom import minidom
# noinspection PyUnresolvedReferences
from os.path import isfile
import numpy as np
from lxml import etree
from xml.etree.ElementTree import Element, SubElement, Comment
from xml.etree import ElementTree
from geopy.distance import great_circle
from objects_and_functions import text_to_ann, ANNOT_SOURCE_DIR, get_id_to_coordinates, fmeasure_from_file
from objects_and_functions import get_coordinates

# ----------------------------------  START OF EMM CONVERSION  ------------------------------------

if False:
    file_ids = {}
    out = codecs.open("data/Geocoding/gwn_emm.txt", mode="w", encoding="utf-8")
    for file_name in text_to_ann().keys():
        text = codecs.open(ANNOT_SOURCE_DIR + file_name + ".txt", encoding="utf-8")
        meta_length = text.next()
        link = meta_length.split("LINK:")[1].strip()
        file_ids[link] = file_name + "<SEP>" + str(len(meta_length))

    tree = etree.parse(u'data/EMM.xml')
    root = tree.getroot()
    geocoding = {}
    duplicates = set()
    for article in root:
        link = article.find("link").text
        title_length = len(article.find("title").text) + 2  # (+2) is some offset that makes no sense but must be there.
        if link in file_ids:
            file_id = file_ids[link].split("<SEP>")[0]
            f = codecs.open("data/EMM/" + file_id + ".ann", mode="w", encoding="utf-8")
            if file_id not in geocoding:
                geocoding[file_id] = []
            for geo in article.findall("{http://emm.jrc.it}fullgeo") + article.findall("{http://emm.jrc.it}georss"):
                name = geo.text
                meta_length = int(file_ids[link].split("<SEP>")[1])
                for pos in geo.attrib["pos"].split(","):
                    if int(pos) >= title_length:
                        record = u"INDEX\tLOCATION " + str(int(pos) + meta_length - title_length) + u" " \
                                 + str(int(pos) + len(name) + meta_length - title_length) + u"\t" + name + u"\n"
                        if record not in duplicates:
                            f.write(record)
                            geocoding[file_id].append(geo.attrib['name'].replace(":", ",") + u",," + name + u",,"
                                                    + geo.attrib['lat'] + u",," + geo.attrib['lon'] + u",,"
                                                    + str(int(pos) - title_length) + u",," + str(int(pos) + len(name) - title_length) + u'||')
                        duplicates.add(record)
    for key in sorted(geocoding.keys()):
        for record in geocoding[key]:
            out.write(record)
        out.write(u"\n")

# ------------------------------------------ END OF EMM CONVERSION ----------------------------------------------


# --------------------------------------- START OF ANNOTATOR AGREEMENT ------------------------------------------

if False:
    from bratutils import agreement as a

    milan = a.DocumentCollection('data/IAA/milano/')
    flora = a.DocumentCollection('data/IAA/flora/')
    mina = a.DocumentCollection('data/IAA/mina/')

    # ------------------ PLEASE READ -------------------------
    # To run this code, you need to paste this code change into agreement.py in BratUtils at line 653
    # in order to exclude the augmentation annotations and the Non_Toponym types. The code starts below:
    # if not line.startswith("#") and not line.startswith("A"):
    #     if "Non_Toponym" not in line and "Literal_Expression" not in line and "Non_Lit_Expression" not in line:
    #         ann = Annotation(line)
    #         self.tags.append(ann)
    # Line 303, add -> return text, "LITERAL", start_idx, end_idx -> This is to evaluate F-Score regardless of type.
    # -------------------- THANKS ----------------------------

    print(milan.compare_to_gold(flora))
    print("Milan-Flora IAA")
    print(milan.compare_to_gold(mina))
    print("Milan-Mina IAA")

    milan_geo = text_to_ann("data/IAA/milano/")
    mina_geo = text_to_ann("data/IAA/mina/")
    exclude = ["Non_Toponym", "Literal_Expression", "Non_Lit_Expression"]
    agree, total = 0.0, 0.0

    for milan_file, mina_file in zip(milan_geo, mina_geo):
        assert milan_file == mina_file
        for milan_ann in milan_geo[milan_file]:
            gold = milan_geo[milan_file][milan_ann]
            if gold.toponym_type in exclude:
                continue
            for mina_ann in mina_geo[mina_file]:
                comp = mina_geo[mina_file][mina_ann]
                if comp.toponym_type in exclude:
                    continue
                if comp.start == gold.start and comp.end == gold.end:
                    total += 1
                    if comp.geonames_id != gold.geonames_id:
                        print(comp.text, comp.toponym_type)
                        print(comp.geonames_id, gold.geonames_id)
                        print(milan_file, comp.key)
                        print("---------------------------------")
                    else:
                        agree += 1

    print("Geocoding agreement (accuracy):", agree / total)

# ----------------------------------- END OF ANNOTATOR AGREEMENT ---------------------------------------

# ------------------ PLEASE READ -------------------------
# To run the code below, you need to paste this code change into agreement.py in BratUtils at line 653
# in order to exclude the augmentation annotations and the Non_Toponym types. The code starts below:

# if not line.startswith("#") and not line.startswith("A"):
#     if "Non_Toponym" not in line and "Literal_Expression" not in line and "Non_Lit_Expression" not in line:
#         ann = Annotation(line)
#         self.tags.append(ann)
# Uncomment line 302, start a new line 303, add this -> return text.lower(), "LITERAL", start_idx, end_idx
# This is to evaluate F-Score regardless of toponym type.
# -------------------- THANKS ----------------------------

# ------------------ START F-SCORE EVALUATION -----------------
# Take a look at the official MUC-7 Guide at http://www.aclweb.org/anthology/M98-1024

# SPACY NER
# from bratutils import agreement as a
# test = a.DocumentCollection('data/Spacy/')
# gold = a.DocumentCollection('data/GeoWebNews/')
# gold.make_gold()
# print(test.compare_to_gold(gold))

# GOOGLE NLP
# from bratutils import agreement as a
# test = a.DocumentCollection('data/Google/')
# gold = a.DocumentCollection('data/GeoWebNews/')
# gold.make_gold()
# print(test.compare_to_gold(gold))

# EMM ONLY
# from bratutils import agreement as a
# test = a.DocumentCollection('data/EMM/')
# gold = a.DocumentCollection('data/GeoWebNews/')
# gold.make_gold()
# print(test.compare_to_gold(gold))

# Precision -> cor / pos
# Recall -> cor / 2,720 (SIZE OF GeoWebNews DATASET or the size of your particular dataset if different)
# F-Score -> 2 * Precision * Recall / (Precision + Recall)

# The MUC-7 table has multiple interpretations depending on the task, please read the paper I cited above. Thanks!
# ------------------- END F-SCORE EVALUATION ------------------


# --------------------------------- Statistical Testing Code Block ------------------------------------

if False:
    #  McNemar's Test for Geotagging
    google_ann = text_to_ann("data/Google/")  # Comparing Google Cloud NLP
    spacy_ann = text_to_ann("data/Spacy/")  # with Spacy NLP
    gold_ann = text_to_ann()  # These are the gold answers/labels
    table = [[0, 0], [0, 0]]  # stored in this table.
    for file_name in gold_ann:
        for gold in gold_ann[file_name]:
            toponym = gold_ann[file_name][gold]
            print(toponym)
    # stat = statsmodels.stats.contingency_tables.mcnemar(table, exact=False, correction=True)
    # WORK IN PROGRESS...

# --------------------------------- End of Statistical Testing Code Block ------------------------------------


# ------------------------------------START OF CORPUS STATISTICS-----------------------------------------

if False:
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

# ------------------------------------END OF CORPUS STATISTICS-----------------------------------------

# -------------------------------GENERATE INPUTS FOR CAMCODER & OUTPUT THE XML DATASET---------------------------------

if False:
    line_no = 0
    annotations = text_to_ann()
    conn = sqlite3.connect('../data/geonames.db').cursor()
    f = codecs.open("data/Geocoding/gwn_full.txt", mode="w", encoding="utf-8")
    root = Element('articles')
    boolean = {True: u'Yes', False: u'No'}
    comment = Comment('GeoWebNews Dataset by Milan Gritta et al. 2019 accompanying the publication "A Pragmatic Guide to Geoparsing Evaluation"')
    root.append(comment)
    for file_name in sorted(annotations.keys()):
        source = codecs.open("data/GeoWebNews/" + file_name + ".txt", encoding="utf-8")
        meta = source.next()  # discard the first line but remember its length
        meta_length = len(meta)
        source = source.read()  # grab the rest of the text
        destination = codecs.open("data/Geocoding/files/" + str(line_no), mode="w", encoding="utf-8")
        destination.write(source)

        article = SubElement(root, 'article')
        article.set('file', file_name)
        title = SubElement(article, 'title')
        title.text = meta.split("LINK:")[0].replace(u"TITLE:", u"").strip()
        link = SubElement(article, 'link')
        link.text = meta.split("LINK:")[1].strip()
        text = SubElement(article, 'text')
        text.text = source
        toponyms = SubElement(article, 'toponyms')

        for ann in annotations[file_name]:
            annotation = annotations[file_name][ann]
            toponym = SubElement(toponyms, 'toponym')
            extName = SubElement(toponym, 'extractedName')
            normName = SubElement(toponym, 'normalisedName')
            topType = SubElement(toponym, 'type')
            modType = SubElement(toponym, 'modifierType')
            nonLoc = SubElement(toponym, 'nonLocational')
            start = SubElement(toponym, 'start')
            end = SubElement(toponym, 'end')
            extName.text = annotation.text
            topType.text = annotation.toponym_type
            nonLoc.text = boolean[annotation.non_locational]
            start.text = str(int(annotation.start) - meta_length)
            end.text = str(int(annotation.end) - meta_length)
            modType.text = annotation.modifier_type

            if annotation.toponym_type not in ["Non_Toponym", "Non_Lit_Expression", "Literal_Expression", "Demonym",
                                               "Homonym", "Language"] and annotation.geonames_id is not None:
                assert len(annotation.geonames_id) >= 5
                geonames = SubElement(toponym, 'geonamesID')
                lat = SubElement(toponym, 'latitude')
                lon = SubElement(toponym, 'longitude')
                if u"," not in annotation.geonames_id:
                    data = get_id_to_coordinates(conn, annotation.geonames_id)
                    out = data[2] + ",," + annotation.text + ",," + str(data[0]) + ",," + str(data[1]) + ",," \
                          + str(int(annotation.start) - meta_length) + ",," + str(int(annotation.end) - meta_length) + "||"
                    f.write(out)
                    normName.text = data[2]
                    geonames.text = annotation.geonames_id
                    lat.text = str(data[0])
                    lon.text = str(data[1])
                else:
                    # IF YOU WOULD LIKE TO GEOCODE ALL 2,601 POSSIBLE TOPONYMS, UNCOMMENT THE CODE BELOW
                    # Our paper evaluates 2,401 toponyms, the ones below are REALLY HARD!!! Have a go if you wish!
                    # data = annotation.geonames_id.split(",")
                    # out = annotation.text + ",," + annotation.text + ",," + str(data[0]) + ",," + str(data[1]) + ",," \
                    #       + str(int(annotation.start) - meta) + ",," + str(int(annotation.end) - meta) + "||"
                    # f.write(out)
                    normName.text = ""
                    coord = annotation.geonames_id.split(",")
                    lat.text = str(coord[0].strip())
                    lon.text = str(coord[1].strip())
        f.write(u"\n")
        line_no += 1
    xml = minidom.parseString(ElementTree.tostring(root, 'utf-8')).toprettyxml(indent="\t")
    codecs.open("data/GWN.xml", mode="w", encoding="utf-8").write(xml)
    f.close()

# ------------------------------------       END OF GENERATION       -----------------------------------------


# ----- This is the Ensemble Setup for Geotagging Evaluation of the NCRF++ trained model -------------
if False:
    fold = "1stFold.out"
    full = codecs.open("data/NCRFpp/full" + fold, encoding="utf-8")
    partial = codecs.open("data/NCRFpp/partial" + fold, encoding="utf-8")
    none = codecs.open("data/NCRFpp/no" + fold, encoding="utf-8")
    out = codecs.open("data/NCRFpp/ensemble" + fold, mode="w", encoding="utf-8")
    for f, p, n in zip(full, partial, none):
        if f.strip() == u"":
            out.write(f)
            continue
        f, p, n = f.split(" "), p.split(" "), n.split(" ")
        assert f[0] == p[0] == n[0]
        result = [f[1], p[1], n[1]]
        label = max(set(result), key=result.count)
        out.write(f[0] + u" " + label)
    out.close()
    fmeasure_from_file('data/NCRFpp/gold' + fold, 'data/NCRFpp/no' + fold)


# ----------------- DATABASE ALIGNMENT - CONVERTING TOPONYM COORDINATES TO GEONAMES COORDINATES ----------------

def align_database_with_geonames(file_name):
    db = sqlite3.connect('../data/geonames.db').cursor()
    inp = codecs.open(file_name, encoding="utf-8")
    out = codecs.open(file_name + "_geonames.txt", mode="w", encoding="utf-8")
    for inp_line in inp:
        for annotation in inp_line.split("||")[:-1]:
            annotation = annotation.split(",,")
            candidates = get_coordinates(db, annotation[0].split(",")[0])
            if len(candidates) == 0:
                out.write(u',,'.join(annotation))
                out.write(u'||')
                print("No Geonames record for:", annotation[0])
                continue
            minDist = np.inf
            lat, lon = 0, 0
            for cand in candidates:
                distance = great_circle((cand[0], cand[1]), (annotation[2], annotation[3])).km
                if distance < minDist:
                    minDist = distance
                    lat = str(cand[0])
                    lon = str(cand[1])
            annotation[2] = lat
            annotation[3] = lon
            out.write(u',,'.join(annotation))
            out.write(u'||')
        out.write(u'\n')


# ------------- END OF DATABASE ALIGNMENT - CONVERTING TOPONYM COORDINATES TO GEONAMES COORDINATES -------------

# align_database_with_geonames("data/Geocoding/gwn_emm.txt")
