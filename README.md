# Pragmatic Guide to Geoparsing Evaluation

UPDATE: 31.10.2018: The paper was submitted for peer review @ Springer's LREV. In the meantime, you can get the preprint from -> ["A Pragmatic Guide to Geoparsing Evaluation."](https://arxiv.org/abs/1810.12368) We welcome any comments and suggestions!

### Abstract
Empirical methods in geoparsing have thus far lacked a standard evaluation framework described as the task, data and metrics used to establish state-of-the-art systems. Evaluation is further made inconsistent, even unrepresentative of real world usage, by the lack of distinction between the \textit{different types of toponyms}. This necessitates new guidelines, a consolidation of metrics and a detailed toponym taxonomy with implications for Named Entity Recognition (NER). To address these deficiencies, our manuscript introduces such framework in three parts. Part 1) Task Definition: clarified via corpus linguistic analysis proposing a fine-grained \textit{Pragmatic Taxonomy of Toponyms} with new guidelines. Part 2) Evaluation Data: shared via a dataset called \textit{GeoWebNews} to provide test/train data to enable immediate use of our contributions. In addition to fine-grained Geotagging and Toponym Resolution (Geocoding), this dataset is also suitable for prototyping  machine learning NLP models. Part 3) Metrics: discussed and reviewed for a rigorous evaluation with appropriate recommendations for NER/Geoparsing practitioners.

### Resources for training the NCRF++ Tagger
You can download them from ...

#### What's in this repository?
All resources mentioned in the paper, code, datasets, config files, annotation, outputs, models, licence, readme, etc.

***/dataset.py*** - Generation of dataset(s), IAA, Statistical Testing, Evaluation Metrics, etc.

***/ner.py*** - Generating train, test and augmentation samples/folds for the NCRF++ tagger.

***/objects_and_functions.py*** - Storing auxiliary APIs for the main scripts above.

#### /brat
As we promised in the paper, we include the BRAT config files for easy, fast, consistent and extendable annotation of new datasets. The setup also lets you interactively view the annotation in [BRAT](http://brat.nlplab.org/downloads.html). Folder contains 3 files.

#### /data
***/data/GWN.xml*** - This is the XML version of ***GeoWebNews***. If you wish to export it in another format, no problem, take a look at the generation code in ***/dataset.py***.

***/data/m_toponyms.txt*** and ***/data/n_toponyms.txt*** store noun and adjectival toponyms for augmentation. Required by ***/ner.py***. If you can think of better samples/augmentation, definitely have a go. Let us know how it went!

#### /data/Corpora
Contains the 5 + 1 recommended datasets from the paper. We thought it would be convenient to keep them in one place. As mentioned in the paper, ***/data/Corpora/TUD-Loc2013.zip*** needs some editing but could be used for data generation.

#### /data/Geocoding
***/data/Geocoding/files/*** contains the raw text files required to generate machine-readable test data for Toponym Resolution.
***/data/Geocoding/gwn_full.txt*** contains the gold labels and indices for GeoWebNews. Required by ***/dataset.py***. The CamCoder model referenced in the paper can be downloaded [here](https://github.com/milangritta/Geocoding-with-Map-Vector).

#### /data/GeoWebNews
Contains the 200 + 200 BRAT annotation + raw text files. These are used to compute F-Scores during Geotagging comparisons.

#### /data/Google
Contains the 200 BRAT-compatible annotation files used for benchmarking of Google Cloud NLP/NER as described in the paper.

#### /data/IAA
Contains the Inter Annotator Agreement files. 3 subfolders for each annotator. IAA computed with [BRATUTILS](https://github.com/savkov/bratutils), see ***/dataset.py*** for details.

#### /data/NCRFpp
These are the output files from the 5-Fold Cross-Validation reported in the paper. The format is different from BRAT as [NCRF++](https://github.com/jiesutd/NCRFpp) uses the CoNLL format. The F-Score was computed using their utility functions, see ***/objects_and_functions.py***.

#### /data/Spacy
Contains the 200 BRAT-compatible annotation files used for benchmarking of SPacy NLP/NER as described in the paper.

***
*If there are any issues or you need some help/clarification, do not hesitate do contact me using the email in my profile description :)*
***
