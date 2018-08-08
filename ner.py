import codecs
# noinspection PyUnresolvedReferences
from os.path import isfile
import spacy
import random
# noinspection PyUnreachableCode
from objects_and_functions import text_to_ann, WORKING_DIR

if True:
    annotations = text_to_ann()
    toponyms = codecs.open("data/toponyms.txt", encoding="utf-8")
    toponyms = [t.strip() for t in toponyms]
    nlp = spacy.load('en_core_web_lg')
    # label_map = {u"Literal": u"Lit", u"Homonym": u"NonLit", u"Coercion": u"Lit", u"Mixed": u"Mixed", u"Embedded": u"Mixed",
    #              u"Metonymic": u"NonLit", u"ModifierNonLit": u"NonLit", u"ModifierLit": u"Lit"}
    label_map = {u"Literal": u"Entity", u"Homonym": u"Entity", u"Coercion": u"Entity", u"Mixed": u"Entity", u"Embedded": u"Entity",
                 u"Metonymic": u"Entity", u"ModifierNonLit": u"Entity", u"ModifierLit": u"Entity"}

    for file_name in annotations:
        text = codecs.open(WORKING_DIR + file_name + ".txt", encoding="utf-8")
        metadata = text.next()
        text = text.read()
        offset = len(metadata)
        annots = dict([(int(annotations[file_name][x].start), annotations[file_name][x]) for x in annotations[file_name]])
        for sentence in nlp(text).sents:
            label, ann, index = u"0", 0, 0
            for word in sentence:
                if word.text.strip() == "":
                    continue
                if word.idx + offset in annots:
                    label = annots[word.idx + offset].type
                    if label not in [u"Non_Lit_Expression", u"Literal_Expression"]:
                        if label == u"Modifier":
                            if annots[word.idx + offset].non_locative or \
                                    annots[word.idx + offset].mod_value in [u"Language", u"Demonym"]:
                                label = u"ModifierNonLit"
                            else:
                                label = u"ModifierLit"
                        ann = word.idx + offset
                        index = word.idx + offset
                    else:
                        top = nlp(toponyms[random.randint(0, len(toponyms) - 1)])
                        for t in top:
                            head = word.text if t.head == t else t.head.text
                            print t.text, "[POS]" + t.pos_, "[Shape]" + t.shape_, "[Head]" + head, "Entity"
                print word.text, u"[POS]" + word.pos_, "[Shape]" + word.shape_, "[Head]" + word.head.text, label_map.get(label, u"0")
                # is in geonames? # get the geonames embeddings?
                if label != u"0":
                    index += len(word) + 1
                if ann != 0 and index - 1 >= int(annots[ann].end):
                    label = u"0"
            print ""

# ---------------------------------------------------------------------------------------------------------------------


def to_bmes_tags(file_name, output):
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


# to_bmes_tags(file_name="data/train.txt", output="data/train_bmes.txt")
# to_bmes_tags(file_name="data/dev.txt", output="data/dev_bmes.txt")
# to_bmes_tags(file_name="data/test.txt", output="data/test_bmes.txt")
