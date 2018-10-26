import codecs
# noinspection PyUnresolvedReferences
from os.path import isfile
from copy import deepcopy
import spacy
import random
from objects_and_functions import text_to_ann, ANNOT_SOURCE_DIR, transform_tags

random.seed(12345)

annotations = text_to_ann()
m_toponyms = codecs.open("data/m_toponyms.txt", encoding="utf-8")
m_toponyms = [t.strip() for t in m_toponyms]
n_toponyms = codecs.open("data/n_toponyms.txt", encoding="utf-8")
n_toponyms = [t.strip() for t in n_toponyms]
nlp = spacy.load('en_core_web_lg')

label_map = {u"Literal": u"Entity", u"Homonym": u"Entity", u"Coercion": u"Entity", u"Mixed": u"Entity",
             u"Embedded_Literal": u"Entity", u"Demonym": u"Entity", u"Non_Literal_Modifier": u"Entity",
             u"Metonymic": u"Entity", u"Literal_Modifier": u"Entity", u"Embedded_Non_Lit": u"Entity",
             u"Language": u"Entity"}

# label_map = {u"Literal": u"Literal", u"Homonym": u"Associative", u"Coercion": u"Literal", u"Mixed": u"Literal",
#              u"Embedded_Literal": u"Literal", u"Demonym": u"Associative", u"Non_Literal_Modifier": u"Associative",
#              u"Metonymic": u"Associative", u"Literal_Modifier": u"Literal", u"Embedded_Non_Lit": u"Associative",
#              u"Language": u"Associative"}  # THIS LABEL MAP IS FOR BINARY SEQUENCE LABELLING (more difficult)

test_indices = sorted(annotations.keys())[80:120]
assert len(test_indices) == 40 and len(annotations.keys()) == 200

train = codecs.open("data/train.txt", mode="w", encoding="utf-8")
test = codecs.open("data/test.txt", mode="w", encoding="utf-8")

for file_name in annotations:
    text = codecs.open(ANNOT_SOURCE_DIR + file_name + ".txt", encoding="utf-8")
    metadata = text.next()
    text = text.read()
    offset = len(metadata)
    annot = dict([(int(annotations[file_name][x].start), annotations[file_name][x]) for x in annotations[file_name]
                  if annotations[file_name][x].toponym_type != u"Non_Toponym"])
    for sentence in nlp(text).sents:
        sentence_one, np_heads = [], []
        replacements, sentence_two = [], []
        is_aug = False
        label, ann, index = u"0", 0, 0
        for word in sentence:
            if word.text.strip() == "":
                continue
            if word.idx + offset in annot:
                label = annot[word.idx + offset].toponym_type
                if label not in [u"Non_Lit_Expression", u"Literal_Expression"]:
                    is_ann = True
                    ann = word.idx + offset
                    index = word.idx + offset
                # ----------- Uncomment to remove Augmentation ------------
                # elif file_name not in test_indices:
                #     is_aug = True
                #     np_heads.append(word)
                #     replacement = []
                #     top = nlp(m_toponyms[random.randint(0, len(m_toponyms) - 1)])
                #     for t in top:
                #         sentence_one.append((t.text + u" [Shape]" + t.shape_ + u" Entity\n", word.i - t.i))
                #     top = nlp(n_toponyms[random.randint(0, len(n_toponyms) - 1)])
                #     for t in top:
                #         replacement.append((t.text + u" [Shape]" + t.shape_ + u" Entity\n", word.i))
                #     replacements.append(replacement)
                # -------------------- End of Augmentation ------------------
            sentence_one.append((word.text + u" [Shape]" + word.shape_ + u" " + label_map.get(label, u"0") + "\n", word.i))
            sentence_two.append((word.text + u" [Shape]" + word.shape_ + u" " + label_map.get(label, u"0") + "\n", word.i))

            if label != u"0":
                index += len(word) + 1
            if ann != 0 and index - 1 >= int(annot[ann].end):
                label = u"0"
        sentence_one.append((u"\n", False, -1))
        sentence_two.append((u"\n", False, -1))
        for word in sentence_one:
            if file_name in test_indices:
                test.write(word[0])
            else:
                train.write(word[0])
        # ------- Uncomment to remove augmentation -------------
        # if is_aug and file_name not in test_indices:
        #     for head, replacement in zip(np_heads, replacements):
        #         left, right = head.left_edge.i, head.right_edge.i
        #         for i, word in enumerate(deepcopy(sentence_two)):
        #             if left <= word[1] <= right:
        #                 sentence_two.remove(word)
        #                 if word[1] == right:
        #                     replacement.reverse()
        #                     for r in replacement:
        #                         sentence_two.insert(i - (right - left), r)
        #         for word in sentence_two:
        #             train.write(word[0])
        # ---------------- End of Augmentation -----------------

transform_tags(file_name="data/train.txt", output="data/train_bmes.txt")
transform_tags(file_name="data/test.txt", output="data/test_bmes.txt")
