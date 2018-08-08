import codecs
from os import listdir
from os.path import isfile
WORKING_DIR = u"/Users/milangritta/Downloads/BRAT/data/milano/"


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
    files = [f for f in listdir(WORKING_DIR) if isfile(WORKING_DIR + f)]
    for f in files:
        if f.endswith(".txt") or f.startswith("."):
            continue
        ann = {}
        annotations[str(f.replace(".ann", ""))] = ann
        f = codecs.open(WORKING_DIR + f, encoding="utf-8")
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
