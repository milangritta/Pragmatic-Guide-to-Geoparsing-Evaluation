import codecs
from os import listdir
# noinspection PyUnresolvedReferences
from os.path import isfile
import xml.etree.ElementTree as ET
ANNOT_SOURCE_DIR = u"/Users/milangritta/Downloads/BRAT/data/milano/"


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
    type = None
    start = None
    end = None
    text = None
    mod_value = None
    non_locative = False
    geonames = None

    # def change_name(self, argument):
    #     self.name = argument


def text_to_ann():
    """

    :return:
    """
    annotated = 0
    annotations = {}
    files = [f for f in listdir(ANNOT_SOURCE_DIR) if isfile(ANNOT_SOURCE_DIR + f)]
    for f in files:
        if f.endswith(".txt") or f.startswith("."):
            continue
        ann = {}
        annotations[str(f.replace(".ann", ""))] = ann
        f = codecs.open(ANNOT_SOURCE_DIR + f, encoding="utf-8")
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
    tree = ET.parse('data/GeoVirus.xml')
    toponyms = set()
    for article in tree.getroot():
        for location in article.findall("locations/location"):
            name = location.find("name").text
            toponyms.add(name)
    tree = ET.parse("data/WikToR.xml")
    for page in tree.getroot():
        name = page.find("toponymName").text
        toponyms.add(name)
    out = codecs.open("data/noun_toponyms.txt", mode="w", encoding="utf-8")
    for top in toponyms:
        out.write(top + "\n")

