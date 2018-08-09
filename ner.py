import codecs
# noinspection PyUnresolvedReferences
from os.path import isfile
import spacy
import random
from objects_and_functions import text_to_ann, ANNOT_SOURCE_DIR, transform_tags

random.seed(111111)

annotations = text_to_ann()
toponyms = codecs.open("data/toponyms.txt", encoding="utf-8")
toponyms = [t.strip() for t in toponyms]
nlp = spacy.load('en_core_web_lg')
all_files = []
# label_map = {u"Literal": u"Lit", u"Homonym": u"NonLit", u"Coercion": u"Lit", u"Mixed": u"Mixed", u"Embedded": u"Mixed",
#              u"Metonymic": u"NonLit", u"ModifierNonLit": u"NonLit", u"ModifierLit": u"Lit"}
label_map = {u"Literal": u"Entity", u"Homonym": u"Entity", u"Coercion": u"Entity", u"Mixed": u"Entity", u"Embedded": u"Entity",
             u"Metonymic": u"Entity", u"ModifierNonLit": u"Entity", u"ModifierLit": u"Entity"}

for file_name in annotations:
    text = codecs.open(ANNOT_SOURCE_DIR + file_name + ".txt", encoding="utf-8")
    metadata = text.next()
    text = text.read()
    offset = len(metadata)
    all_sentences = []
    annots = dict([(int(annotations[file_name][x].start), annotations[file_name][x]) for x in annotations[file_name]])
    for sentence in nlp(text).sents:
        output = []
        is_augmented = False
        is_annotated = False
        label, ann, index = u"0", 0, 0
        for word in sentence:
            if word.text.strip() == "":
                continue
            if word.idx + offset in annots:
                label = annots[word.idx + offset].type
                if label not in [u"Non_Lit_Expression", u"Literal_Expression"]:
                    is_annotated = True
                    if label == u"Modifier":
                        if annots[word.idx + offset].non_locative or \
                                annots[word.idx + offset].mod_value in [u"Language", u"Demonym"]:
                            label = u"ModifierNonLit"
                        else:
                            label = u"ModifierLit"
                    ann = word.idx + offset
                    index = word.idx + offset
                else:
                    is_augmented = True
                    top = nlp(toponyms[random.randint(0, len(toponyms) - 1)])
                    for t in top:
                        head = word.text if t.head == t else t.head.text
                        output.append(t.text + u" [POS]" + t.pos_ + u" [Shape]" + t.shape_ + u" [Head]" + head + u" Entity\n")
            output.append(word.text + u" [POS]" + word.pos_ + u" [Shape]" + word.shape_ + u" [Head]" + word.head.text + u" " + label_map.get(label, u"0") + "\n")
            # RAW FILE? DECODE SETUP? NP AUGMENTATION?
            if label != u"0":
                index += len(word) + 1
            if ann != 0 and index - 1 >= int(annots[ann].end):
                label = u"0"
        output.append(u"\n")
        all_sentences.append((output, is_augmented and not is_annotated))
    all_files.append(all_sentences)

train = codecs.open("data/train.txt", mode="w", encoding="utf-8")
dev = codecs.open("data/dev.txt", mode="w", encoding="utf-8")
test = codecs.open("data/test.txt", mode="w", encoding="utf-8")

for all_sentences in all_files:
    r = random.random()
    for sentence, is_augmented in all_sentences:
        for word in sentence:
            if r < 0.6 or is_augmented:
                train.write(word)
            elif r > 0.8:
                dev.write(word)
            else:
                test.write(word)

transform_tags(file_name="data/train.txt", output="data/train_bmes.txt")
transform_tags(file_name="data/dev.txt", output="data/dev_bmes.txt")
transform_tags(file_name="data/test.txt", output="data/test_bmes.txt")
