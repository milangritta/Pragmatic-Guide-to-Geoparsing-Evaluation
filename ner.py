import codecs
# noinspection PyUnresolvedReferences
from os.path import isfile
from copy import deepcopy
import spacy
import random
from objects_and_functions import text_to_ann, ANNOT_SOURCE_DIR, transform_tags, strip_sentence

random.seed(12345)

annotations = text_to_ann()
m_toponyms = codecs.open("data/m_toponyms.txt", encoding="utf-8")
m_toponyms = [t.strip() for t in m_toponyms]
n_toponyms = codecs.open("data/n_toponyms.txt", encoding="utf-8")
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
    all_sents = []
    annot = dict([(int(annotations[file_name][x].start), annotations[file_name][x]) for x in annotations[file_name]])
    for sentence in nlp(text).sents:
        sentence_out = []
        np_heads = []
        replacements = []
        is_aug = False
        is_ann = False
        label, ann, index = u"0", 0, 0
        for word in sentence:
            if word.text.strip() == "":
                continue
            if word.idx + offset in annot:
                label = annot[word.idx + offset].type
                if label not in [u"Non_Lit_Expression", u"Literal_Expression"]:
                    is_ann = True
                    if label == u"Modifier":
                        if annot[word.idx + offset].non_locative or \
                                annot[word.idx + offset].mod_value in [u"Language", u"Demonym"]:
                            label = u"ModifierNonLit"
                        else:
                            label = u"ModifierLit"
                    ann = word.idx + offset
                    index = word.idx + offset
                else:
                    is_aug = True
                    np_heads.append(word)
                    replacement = []
                    top = nlp(m_toponyms[random.randint(0, len(m_toponyms) - 1)])
                    for t in top:
                        # head = word.text if t.head == t else t.head.text
                        # output.append((t.text + u" [Shape]" + t.shape_ + u" [Head]" + head + u" Entity\n", True))
                        sentence_out.append((t.text + u" [Shape]" + t.shape_ + u" Entity\n", True, word.i - t.i))
                    if label == u"Literal_Expression":
                        top = nlp(n_toponyms[random.randint(0, len(n_toponyms) - 1)])
                        for t in top:
                            replacement.append((t.text + u" [Shape]" + t.shape_ + u" Entity\n", True, word.i))
                        replacements.append(replacement)
            # output.append((word.text + u" [Shape]" + word.shape_ + u" [Head]" + word.head.text + u" " + label_map.get(label, u"0") + "\n", False))
            sentence_out.append((word.text + u" [Shape]" + word.shape_ + u" " + label_map.get(label, u"0") + "\n", False, word.i))
            # DECODE SETUP? How does BMES actually work? Replace SGD? Merge multiple train files? Is in Geonames feature?
            if label != u"0":
                index += len(word) + 1
            if ann != 0 and index - 1 >= int(annot[ann].end):
                label = u"0"
        sentence_out.append((u"\n", False, -1))
        all_sents.append((strip_sentence(sentence_out, is_aug, is_ann, False), is_aug and not is_ann))
        if is_aug and not is_ann:
            for head, replacement in zip(np_heads, replacements):
                sentence_augmented = deepcopy(sentence_out)
                sentence_augmented = strip_sentence(sentence_augmented, True, True, True)
                left, right = head.left_edge.i, head.right_edge.i
                for i, word in enumerate(deepcopy(sentence_augmented)):
                    if left <= word[2] <= right:
                        sentence_augmented.remove(word)
                        if word[2] == right:
                            replacement.reverse()
                            for r in replacement:
                                sentence_augmented.insert(i - (right - left), r)
                all_sents.append((strip_sentence(sentence_augmented, is_aug, is_ann, False), is_aug and not is_ann))
        # http://scikit-learn.org/stable/modules/generated/sklearn.metrics.classification_report.html
    all_files.append((all_sents, file_name))

train = codecs.open("data/train.txt", mode="w", encoding="utf-8")
test = codecs.open("data/test.txt", mode="w", encoding="utf-8")
raw = codecs.open("data/raw.txt", mode="w", encoding="utf-8")

test_indices = sorted(annotations.keys())[0:40]
assert len(test_indices) == 40 and len(annotations.keys()) == 200
for all_sents, file_name in all_files:
    for sentence, is_aug in all_sents:
        for word in sentence:
            if file_name not in test_indices or is_aug:
                train.write(word)
            else:
                test.write(word)
            word = word.split(" ")
            raw.write(word[0] + u" " + word[-1])

transform_tags(file_name="data/train.txt", output="data/train_bmes.txt")
transform_tags(file_name="data/test.txt", output="data/test_bmes.txt")
transform_tags(file_name="data/raw.txt", output="data/raw_bmes.txt")
# http://www.nltk.org/api/nltk.tag.html#module-nltk.tag.stanford

# Fold 1: 86.6 part-augmented
# Fold 2: 88.1 part-augmented
# Fold 3: 87.6 part-augmented
# Fold 4: 90.2 part-augmented
# Fold 5: 89.1 part-augmented
