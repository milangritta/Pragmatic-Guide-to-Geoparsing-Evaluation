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
    A simple, small container for annotations for convenience.
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


def google_NER(text, m):
    """

    :param text:
    :param m: length of metadata to add to the begin offset character
    :return:
    """
    locations = []
    client = language.LanguageServiceClient()
    document = types.Document(content=text, type=enums.Document.Type.PLAIN_TEXT, language='en')
    entities = client.analyze_entities(document, encoding_type=enums.EncodingType.UTF32).entities

    for entity in entities:
        for mention in entity.mentions:
            if mention.type == 1 and entity.type == 2:
                locations.append(u"INDEX\tLOCATION " + str(mention.text.begin_offset + m) + u" "
                + str(m + mention.text.begin_offset + len(mention.text.content)) + u"\t" + mention.text.content + u"\n")
    return locations


def run_spacy_ner(nlp):
    for file_name in text_to_ann().keys():
        print("Starting file name", file_name)
        out_spacy = codecs.open("data/Spacy/" + file_name + ".ann", mode="w", encoding="utf-8")
        text = codecs.open(ANNOT_SOURCE_DIR + file_name + ".txt", encoding="utf-8")
        meta = len(text.next())
        text = text.read()
        for entity in nlp(text).ents:
            if entity.label_ in [u"LOC", u"FAC", u"NORP", u"GPE"]:
                name = entity.text
                if name.startswith(u"the"):
                    name = name[4:]
                out_spacy.write(u"INDEX\tLOCATION " + str(entity.start_char + meta) + u" "
                                + str(entity.end_char + meta) + u"\t" + name + u"\n")


def run_google_ner():
    for file_name in text_to_ann().keys():
        print("Starting file name", file_name)
        out_google = codecs.open("data/Google/" + file_name + ".ann", mode="w", encoding="utf-8")
        text = codecs.open(ANNOT_SOURCE_DIR + file_name + ".txt", encoding="utf-8")
        meta = len(text.next())
        google = google_NER(text.read(), meta)
        for entity in google:
            out_google.write(entity)


def get_id_to_coordinates(con, id):
    """
    Access the database to retrieve coordinates from DB.
    :param con: sqlite3 database cursor i.e. DB connection
    :param id: geonames id of the place
    :return: a list of tuples [(latitude, longitude), ...]
    """
    result = con.execute(u"SELECT METADATA FROM COORD WHERE NAME = ?", (id,)).fetchone()
    if result:
        return eval(result[0])
    else:
        return []


# run_spacy_ner(nlp=spacy.load('en_core_web_lg'))
# run_google_ner()
# print get_id_to_coordinates(sqlite3.connect('../data/geonames.db').cursor(), u"2993838")
