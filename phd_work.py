import sqlite3
from collections import Counter
from os import listdir
import matplotlib.pyplot as plt
import numpy
from lxml import etree
# noinspection PyUnresolvedReferences
from os.path import isfile
from urlparse import urlparse
from geopy.distance import great_circle
from objects_and_functions import get_coordinates


############################################################################################################
#                                                                                                          #
# This code only applies to my PhD thesis. If you liked the Springer paper, then read my thesis as well :) #
#  It does make sense to package it here since it's a natural extension of the work in our latest paper.   #
#                                                                                                          #
# Unfortunately, some data for these analyses is proprietary and not in the open-source domain, one of the #
# few pieces that I'm not at liberty to publish. Sorry about that, if you do need it, please get in touch. #
#                                                                                                          #
############################################################################################################


def emm_news_analysis():
    """
    An analysis of the sources of news articles, their language types, tagged locations, etc.
    """
    d = "/Users/milangritta/Desktop/Medisys/"
    domains, languages, locations, word_counts = [], [], [], []
    files = [f for f in listdir(d) if isfile(d + f)]
    print("No of files:", len(files))
    for f in files:
        if f.endswith(".xml"):  # no hidden files...
            tree = etree.parse(d + f)
            root = tree.getroot()
            for article in root.findall('channel/item'):
                domains.append(urlparse(article.find('link').text).hostname.split(".")[-1])
                languages.append(article.find('{http://www.iso.org/3166}language').text)
                location_count = set()
                for a in article.findall('{http://emm.jrc.it}fullgeo') + article.findall('{http://emm.jrc.it}georss'):
                    location_count.update(set(a.attrib['pos'].split(",")))  # sets avoid counting duplicates
                locations.append(len(location_count))
                word_counts.append(int(article.find('{http://emm.jrc.it}text').attrib['wordCount']))

    # c = Counter(domains).most_common()
    # c = Counter(languages).most_common()
    # for k in c:
    #     print k[0], ",", k[1]
    # hist = numpy.histogram(word_counts, range=(0, 2000))
    hist = numpy.histogram(locations, range=(0, 70))
    for count, bucket in zip(hist[0], hist[1]):
        print(count, ",", bucket)


def geowebnews_analysis():
    """

    :return:
    """
    label_map = {u"Literal": u"Literal", u"Homonym": u"Associative", u"Coercion": u"Literal", u"Mixed": u"Literal",
                 u"Embedded_Literal": u"Literal", u"Demonym": u"Associative", u"Non_Literal_Modifier": u"Associative",
                 u"Metonymic": u"Associative", u"Literal_Modifier": u"Literal", u"Embedded_Non_Lit": u"Associative",
                 u"Language": u"Associative"}
    tree = etree.parse(u'data/GWN.xml')
    root = tree.getroot()
    conn = sqlite3.connect('../data/geonames.db').cursor()

    geo_location_pop, associative_outliers = dict(), []
    toponym_feature_types = {u"Associative": [], u"Literal": []}
    for article in root.findall("article"):
        literal, associative = [], []
        for toponym in article.findall('toponyms/toponym'):
            label = toponym.find('type').text
            if toponym.find('latitude') is None:
                continue
            name = toponym.find('extractedName').text
            name = name if name is not None else u""
            # ------------ Toponym Resolution for each article using Population -------------
            gold_coordinates = (toponym.find('latitude').text, toponym.find('longitude').text)
            pop_coordinates = get_coordinates(conn, name)
            if len(pop_coordinates) > 0 and len(gold_coordinates) > 0:
                feature_type = pop_coordinates[0][3]
                pop_coordinates = (pop_coordinates[0][0], pop_coordinates[0][1])
                distance = great_circle(gold_coordinates, pop_coordinates).km
                if name + u":::" + feature_type not in geo_location_pop:
                    geo_location_pop[name + u":::" + feature_type] = []
                geo_location_pop[name + u":::" + feature_type].append(distance)
                toponym_feature_types[label_map[label]].append(feature_type)
            # -------------------- Build two lists of toponyms -------------------------
            if label_map[label] == u"Associative":
                associative.append(toponym)
            else:
                literal.append(toponym)
        accuracy = []
        for assoc in associative:
            if len(literal) == 0:
                continue
            min_dist = numpy.inf
            for lit in literal:
                distance = great_circle((lit.find('latitude').text, lit.find('longitude').text),
                                        (assoc.find('latitude').text, assoc.find('longitude').text)).km
                if distance < min_dist:
                    min_dist = distance
            accuracy.append(min_dist)
        associative_outliers.extend(accuracy)
    # ---------------- Compute Associative Outliers -----------------
    print(u"Total measurements:", len(associative_outliers))
    hist = numpy.histogram(associative_outliers, bins=[0, 100, 200, 300, 400, 500, 750, 1000, 2000, 5000, 10000, 20000])
    for count, bucket in zip(hist[0], hist[1]):
        print(count, ",", bucket)
    # ---------------- Compute Geocoding by Population and Type ----------------
    sorted_by_type = {}
    total = 0
    print(u"Number of unique toponyms:", len(geo_location_pop))
    for toponym in geo_location_pop:
        the_type = toponym.split(u":::")[1]
        if the_type not in sorted_by_type:
            sorted_by_type[the_type] = []
        sorted_by_type[the_type].append(numpy.mean(geo_location_pop[toponym]))
        # print(toponym, geo_location_pop[toponym])  # SANITY CHECK!
        total += len(geo_location_pop[toponym])
    for the_type in sorted(sorted_by_type.items(), key=lambda (x, y): numpy.mean(y)):
        if len(the_type[1]) > 4:
            print(the_type[0], ",", numpy.mean(the_type[1]))
    print(u"Total resolved toponyms:", total)
    # ------------------ Compute Feature Types per Pragmatic Type --------------------
    hist_lit = Counter(toponym_feature_types[u"Literal"])
    hist_ass = Counter(toponym_feature_types[u"Associative"])
    for key in set(hist_ass.keys() + hist_lit.keys()):
        if hist_lit.get(key, 0) > 4 and hist_ass.get(key, 0) > 4:
            print(key, u",", float(hist_lit.get(key, 0)) / len(toponym_feature_types[u"Literal"]),
                       u",", float(hist_ass.get(key, 0)) / len(toponym_feature_types[u"Associative"]))


# emm_news_analysis()
geowebnews_analysis()
