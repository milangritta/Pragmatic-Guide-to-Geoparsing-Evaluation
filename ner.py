import codecs
# noinspection PyUnresolvedReferences
from os.path import isfile
import spacy
import random
from objects_and_functions import text_to_ann, ANNOT_SOURCE_DIR, transform_tags

random.seed(1111)

annotations = text_to_ann()
m_toponyms = codecs.open("data/toponyms.txt", encoding="utf-8")
m_toponyms = [t.strip() for t in m_toponyms]
n_toponyms = codecs.open("data/noun_toponyms.txt", encoding="utf-8")
n_toponyms = [t.strip() for t in n_toponyms]
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
        sentence_output = []
        np_heads = []
        replacement = []
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
                    np_heads.append(word)
                    top = nlp(m_toponyms[random.randint(0, len(m_toponyms) - 1)])
                    for t in top:
                        # head = word.text if t.head == t else t.head.text
                        # output.append((t.text + u" [Shape]" + t.shape_ + u" [Head]" + head + u" Entity\n", True))
                        sentence_output.append((t.text + u" [Shape]" + t.shape_ + u" Entity\n", True, word.i - t.i))
                    top = nlp(n_toponyms[random.randint(0, len(n_toponyms) - 1)])
                    for t in top:
                        replacement.append((t.text + u" [Shape]" + t.shape_ + u" Entity\n", True, word.i - t.i))
            # output.append((word.text + u" [Shape]" + word.shape_ + u" [Head]" + word.head.text + u" " + label_map.get(label, u"0") + "\n", False))
            sentence_output.append((word.text + u" [Shape]" + word.shape_ + u" " + label_map.get(label, u"0") + "\n", False, word.i))
            # RAW FILES? DECODE SETUP? F-Score per class! NP AUGMENTATION? How does BMES actually work?
            if label != u"0":
                index += len(word) + 1
            if ann != 0 and index - 1 >= int(annots[ann].end):
                label = u"0"
        sentence_output.append((u"\n", False, -1))
        sentence_output = [a for (a, b, c) in sentence_output if not b] if is_augmented and is_annotated else [a for (a, b, c) in sentence_output]
        all_sentences.append((sentence_output, is_augmented and not is_annotated))
    all_files.append(all_sentences)

train = codecs.open("data/train.txt", mode="w", encoding="utf-8")
dev = codecs.open("data/dev.txt", mode="w", encoding="utf-8")
test = codecs.open("data/test.txt", mode="w", encoding="utf-8")

for all_sentences in all_files:
    r = random.random()
    for sentence, is_augmented in all_sentences:
        for word in sentence:
            if r < 0.8 or is_augmented:
                train.write(word)
            elif r > 0.9:
                dev.write(word)
            else:
                test.write(word)

transform_tags(file_name="data/train.txt", output="data/train_bmes.txt")
transform_tags(file_name="data/dev.txt", output="data/dev_bmes.txt")
transform_tags(file_name="data/test.txt", output="data/test_bmes.txt")
