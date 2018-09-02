# coding=utf-8
from __future__ import print_function
import codecs
import os
import random

import spacy
import sqlite3
from os import listdir
import six
# noinspection PyUnresolvedReferences
from os.path import isfile
from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types
import xml.etree.ElementTree as ET
ANNOT_SOURCE_DIR = u"data/GeoWebNews/"
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/milangritta/Downloads/GeoWebNews-0dca974782b0.json"


def get_coordinates(con, loc_name):
    """
    Access the database to retrieve coordinates and other data from DB.
    :param con: sqlite3 database cursor i.e. DB connection
    :param loc_name: name of the place
    :return: a list of tuples [(latitude, longitude, population, feature_code), ...]
    """
    result = con.execute(u"SELECT METADATA FROM GEO WHERE NAME = ?", (loc_name.lower(),)).fetchone()
    if result:
        result = eval(result[0])  # Do not remove the sorting, the function below assumes sorted results!
        return sorted(result, key=lambda (a, b, c, d): c, reverse=True)
    else:
        return []


class Annotation:
    """
    A small container for annotations, a convenient object for queries.
    """
    def __init__(self, key):
        self.key = key

    key = None
    toponym_type = None
    start = None
    end = None
    text = None
    modifier_type = None
    non_locational = False
    geonames_id = None


def text_to_ann(directory=ANNOT_SOURCE_DIR):
    """

    :return:
    """
    annotations = {}
    files = [f for f in listdir(directory) if isfile(directory + f)]
    for f in files:
        if f.endswith(".txt") or f.startswith("."):
            continue
        ann = {}
        annotations[str(f.replace(".ann", ""))] = ann
        f = codecs.open(directory + f, encoding="utf-8")
        for line in f:
            line = line.strip().split("\t")
            if line[0].startswith("T"):  # token
                if line[0] in ann:
                    raise Exception("Duplicate! Check.")
                else:
                    ann[line[0]] = Annotation(line[0])
                    ann[line[0]].text = line[2]
                    data = line[1].split(" ")
                    ann[line[0]].toponym_type = data[0]
                    ann[line[0]].start = data[1]
                    ann[line[0]].end = data[2]
            if line[0].startswith("A"):  # attribute
                data = line[1].split(" ")
                if data[1] not in ann:
                    raise Exception("No record! Check.")
                if data[0] == "Modifier_Type":
                    ann[data[1]].modifier_type = data[2]
                elif data[0] == "Non_Locational":
                    ann[data[1]].non_locational = True
                else:
                    raise Exception("This should never be triggered!")
            if line[0].startswith("#"):  # annotator note
                data = line[1].split(" ")
                if data[1] not in ann:
                    raise Exception("No record! Check.")
                ann[data[1]].geonames_id = line[2]
    return annotations


def transform_tags(file_name, output):
    """

    :param file_name:
    :param output:
    :return:
    """
    inp = codecs.open(file_name, encoding="utf-8")
    out = codecs.open(output, mode="w", encoding="utf-8")
    last = inp.next()
    current = inp.next()
    if last.split(" ")[-1].strip() != u"0":
        o = last.split(" ")
        if current.split(" ")[-1].strip() == u"0":
            o[-1] = u"S-" + last.split(" ")[-1]
        else:
            o[-1] = u"B-" + last.split(" ")[-1]
        out.write(u" ".join(o))
    else:
        out.write(last)

    for line in inp:
        if current.strip() == u"":
            out.write(current)
        elif current.split(" ")[-1].strip() != u"0":
            o = current.split(" ")
            if last.split(" ")[-1].strip() == u"0" or last.strip() == u"":
                if line.split(" ")[-1].strip() == u"0":
                    o[-1] = u"S-" + current.split(" ")[-1]
                else:
                    o[-1] = u"B-" + current.split(" ")[-1]
            elif line.split(" ")[-1].strip() == u"0":
                o[-1] = u"E-" + current.split(" ")[-1]
            else:
                o[-1] = u"M-" + current.split(" ")[-1]
            out.write(u" ".join(o))
        else:
            out.write(current)
        last = current
        current = line

    if current.strip() == u"":
        out.write(current)
    elif current.split(" ")[-1].strip() != u"0":
        o = current.split(" ")
        if last.split(" ")[-1].strip() == u"0" or last.strip() == u"":
            o[-1] = u"S-" + current.split(" ")[-1]
        else:
            o[-1] = u"E-" + current.split(" ")[-1]
        out.write(u" ".join(o))
    else:
        out.write(current)


def build_noun_toponyms():
    """

    :return:
    """
    # toponyms = set()
    for line in codecs.open(u"../data/allCountries.txt", u"r", encoding=u"utf-8"):
        line = line.split("\t")
        name = line[2]
        # if line[7] in ["BCH", "DSRT", "ISL", "MT", "VAL", "FRST", "ST", "RD", "AIRP", "BLDG", "CH", "CSTL", "FCL", "RES",
        #                "BAY", "FRM", "HSP", "MAR", "MKT", "QUAY", "SCH", "UNIV", "SQR", "STDM", "TMPL", "ZOO", "CST",
        #                "PRK", "RGN", "CNL", "GULF", "LK", "LKS", "OCN", "SEA"]:
        #     toponyms.add(name)
        #     if random.random() > 0.9999:
        #         print(name)
        if line[6] in ["A", "P"] and int(line[14]) > 500000:
            # toponyms.add(name)
            if random.random() > 0.9:
                print(name)
    # out = codecs.open("data/n_toponyms.txt", mode="w", encoding="utf-8")
    # for top in toponyms:
    #     out.write(top + "\n")
    # print("Saved:", len(toponyms), "toponyms.")


def google_NER(text, nlp):
    """

    :param text:
    :return:
    """
    locations = []
    client = language.LanguageServiceClient()
    document = types.Document(content=text, type=enums.Document.Type.PLAIN_TEXT, language='en')
    entities = client.analyze_entities(document, encoding_type=enums.EncodingType.UTF32).entities

    for entity in entities:
        for mention in entity.mentions:
            if mention.type == 1 and entity.type == 2:
                last_offset = mention.text.begin_offset
                for word in nlp(mention.text.content):
                    if word.is_punct:
                        locations.append((last_offset - 1, word.text))
                        last_offset += len(word) - 1
                    else:
                        locations.append((last_offset, word.text))
                        last_offset += len(word) + 1
    return dict(locations)


def strip_sentence(s, is_augmented, is_annotated, keep_tags):
    """

    :param s:
    :param is_augmented:
    :param is_annotated:
    :param keep_tags:
    :return:
    """
    if is_augmented and is_annotated:
        return [(a, b, c) for (a, b, c) in s if not b] if keep_tags else [a for (a, b, c) in s if not b]
    else:
        return [(a, b, c) for (a, b, c) in s] if keep_tags else [a for (a, b, c) in s]


# build_noun_toponyms()

# nlp = spacy.load('en_core_web_lg')
# raw = codecs.open("data/raw.txt", mode="w", encoding="utf-8")
# spacy_o = codecs.open("data/spacy.txt", mode="a", encoding="utf-8")
# google_o = codecs.open("data/google.txt", mode="a", encoding="utf-8")

# for file_name in sorted(annotations.keys()):
#     print("Starting file name", file_name)
#     text = codecs.open(ANNOT_SOURCE_DIR + file_name + ".txt", encoding="utf-8")
#     metadata = text.next()
#     text = text.read()
#     google = google_NER(text, nlp)            ---USE BRAT FILES AND BRAT UTILS---
#     for sentence in nlp(text).sents:
#         for word in sentence:
#             spacy_label = u"Entity" if word.ent_type_ in [u"LOC", u"FAC", u"NORP", u"GPE"] else u"0"
#             spacy_label = spacy_label if word.text != u"the" else u"0"
#             google_label = u"Entity" if word.idx in google else u"0"
#             if word.idx in google:
#                 if google[word.idx] != word.text:
#                     print(u"ERR: google[word.idx] != word.text", google[word.idx], word.text, word.idx)
#             spacy_o.write(word.text + u" " + spacy_label + u"\n")
#             google_o.write(word.text + u" " + google_label + u"\n")
#             raw.write(word)
#         spacy_o.write("\n")
#         google_o.write("\n")
# transform_tags(file_name="data/raw.txt", output="data/raw_bmes.txt")

# print(metrics.flat_classification_report(y_test, y_pred, labels=sorted_labels, digits=3))
