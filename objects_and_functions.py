# coding=utf-8
from __future__ import print_function
import codecs
import os
import spacy
import sqlite3
from os import listdir
import six
# noinspection PyUnresolvedReferences
from os.path import isfile
from google.cloud import language
from google.cloud.language import enums
from google.cloud.language import types
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


# --------- COPIED WITH A TINY EDIT FROM https://github.com/jiesutd/NCRFpp TO EVALUATE NCRF++ MODEL -----------

def readSentence(input_file):
    in_lines = open(input_file,'r').readlines()
    sentences = []
    labels = []
    sentence = []
    label = []
    for line in in_lines:
        if len(line) < 2:
            sentences.append(sentence)
            labels.append(label)
            sentence = []
            label = []
        else:
            pair = line.strip('\n').split(' ')
            sentence.append(pair[0])
            label.append(pair[-1])
    return sentences,labels


def get_ner_fmeasure(golden_lists, predict_lists, label_type="BMES"):
    sent_num = len(golden_lists)
    golden_full = []
    predict_full = []
    right_full = []
    right_tag = 0
    all_tag = 0
    for idx in range(0,sent_num):
        # word_list = sentence_lists[idx]
        golden_list = golden_lists[idx]
        predict_list = predict_lists[idx]
        for idy in range(len(golden_list)):
            if golden_list[idy] == predict_list[idy]:
                right_tag += 1
        all_tag += len(golden_list)
        gold_matrix = get_ner_BMES(golden_list)
        pred_matrix = get_ner_BMES(predict_list)
        # print "gold", gold_matrix
        # print "pred", pred_matrix
        right_ner = list(set(gold_matrix).intersection(set(pred_matrix)))
        golden_full += gold_matrix
        predict_full += pred_matrix
        right_full += right_ner
    right_num = len(right_full)
    golden_num = len(golden_full)
    predict_num = len(predict_full)
    if predict_num == 0:
        precision = -1
    else:
        precision =  (right_num+0.0)/predict_num
    if golden_num == 0:
        recall = -1
    else:
        recall = (right_num+0.0)/golden_num
    if (precision == -1) or (recall == -1) or (precision+recall) <= 0.:
        f_measure = -1
    else:
        f_measure = 2*precision*recall/(precision+recall)
    accuracy = (right_tag+0.0)/all_tag
    # print "Accuracy: ", right_tag,"/",all_tag,"=",accuracy
    print("gold_num = ", golden_num, " pred_num = ", predict_num, " right_num = ", right_num)
    return accuracy, precision, recall, f_measure


def get_ner_BMES(label_list):
    # list_len = len(word_list)
    # assert(list_len == len(label_list)), "word list size unmatch with label list"
    list_len = len(label_list)
    begin_label = 'B-'
    end_label = 'E-'
    single_label = 'S-'
    whole_tag = ''
    index_tag = ''
    tag_list = []
    stand_matrix = []
    for i in range(0, list_len):
        # wordlabel = word_list[i]
        current_label = label_list[i].upper()
        if begin_label in current_label:
            if index_tag != '':
                tag_list.append(whole_tag + ',' + str(i-1))
            whole_tag = current_label.replace(begin_label,"",1) +'[' +str(i)
            index_tag = current_label.replace(begin_label,"",1)

        elif single_label in current_label:
            if index_tag != '':
                tag_list.append(whole_tag + ',' + str(i-1))
            whole_tag = current_label.replace(single_label,"",1) +'[' +str(i)
            tag_list.append(whole_tag)
            whole_tag = ""
            index_tag = ""
        elif end_label in current_label:
            if index_tag != '':
                tag_list.append(whole_tag +',' + str(i))
            whole_tag = ''
            index_tag = ''
        else:
            continue
    if (whole_tag != '')&(index_tag != ''):
        tag_list.append(whole_tag)
    tag_list_len = len(tag_list)

    for i in range(0, tag_list_len):
        if  len(tag_list[i]) > 0:
            tag_list[i] = tag_list[i]+ ']'
            insert_list = reverse_style(tag_list[i])
            stand_matrix.append(insert_list)
    # print stand_matrix
    return stand_matrix


def reverse_style(input_string):
    target_position = input_string.index('[')
    input_len = len(input_string)
    output_string = input_string[target_position:input_len] + input_string[0:target_position]
    return output_string


def fmeasure_from_file(golden_file, predict_file, label_type="BMES"):
    print("Get f measure from file:", golden_file, predict_file)
    print("Label format:",label_type)
    golden_sent,golden_labels = readSentence(golden_file)
    predict_sent,predict_labels = readSentence(predict_file)
    A,P,R,F = get_ner_fmeasure(golden_labels, predict_labels, label_type)
    print ("P:%sm R:%s, F:%s"%(P,R,F))

# ---------------- END OF CODE FROM https://github.com/jiesutd/NCRFpp TO EVALUATE NCRF++ MODEL ------------------

# run_spacy_ner(nlp=spacy.load('en_core_web_lg'))
# run_google_ner()
# print get_id_to_coordinates(sqlite3.connect('../data/geonames.db').cursor(), u"2993838")
