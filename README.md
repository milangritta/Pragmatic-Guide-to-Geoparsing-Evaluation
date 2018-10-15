# Pragmatic Guide to Geoparsing Evaluation

`UPDATE: 19.10.2018: The paper was submitted for peer review @ Springer's LREV. In the meantime, you can get the preprint from` -> [arxiv.org](https://arxiv.org/)

### Abstract
Empirical methods in geoparsing have thus far lacked a standard evaluation framework (1. Task, 2. Data, 3. Metrics) used for establishing state-of-the-art (SOTA) systems. Evaluation is further made inconsistent, even unrepresentative of real world usage, by the lack of distinction between the different types of toponyms. This necessitates new guidelines, a consolidation of metrics and a detailed toponym taxonomy with implications for Named Entity Recognition (NER). To address these deficiencies, our manuscript introduces such framework in three parts. Part 1) Task Definition: clarified via corpus linguistic analysis proposing a fine-grained Pragmatic Taxonomy of Toponyms with new guidelines. Part 2) Evaluation Data: shared via a dataset called GeoWebNews to provide test/train data to enable immediate use of our contributions. In addition to fine-grained Geotagging and Toponym Resolution (Geocoding), this dataset is also suitable for prototyping  machine learning NLP models. Part 3) Metrics: discussed and reviewed for a rigorous evaluation with appropriate recommendations for NER/Geoparsing practitioners.

### What's in this repository?
All resources mentioned in the paper, code, datasets, config files, annotation, outputs, models, licence, readme, etc.

***/dataset.py*** - Generation of dataset(s), IAA, Statistical Testing, Evaluation Metrics, etc.
***/ner.py*** - Generating train, test and augmentation samples/folds for the NCRF++ tagger.
***/objects_and_functions.py*** - Storing auxiliary APIs for the main scripts above.

### /brat
As we promised in the paper, we include the BRAT config files for easy, fast, consistent and extendable annotation of new datasets. The setup also lets you interactively view the annotation in [BRAT](http://brat.nlplab.org/downloads.html). Folder contains 3 files.

### /data
***/data/GWN.xml*** - This is the XML version of ***GeoWebNews***. If you wish to export it in another format, no problem, take a look at the generation code in ***/dataset.py***.

*/data/m_toponyms.txt* and */data/n_toponyms.txt* store noun and adjectival toponyms for augmentation. Required by ***/ner.py***. If you can think of better samples/augmentation, definitely have a go. Let us know how it went!

### /data/Corpora
Contains the 5 + 1 recommended datasets from the paper. We thought it would be convenient to keep them in one place. As mentioned in the paper, ***/data/Corpora/TUD-Loc2013.zip*** needs some editing but could be used for training data generation.
