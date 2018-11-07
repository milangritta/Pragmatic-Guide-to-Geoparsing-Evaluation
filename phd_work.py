import sqlite3
from os import listdir

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

    """
    d = "/Users/milangritta/Desktop/Medisys/"
    domains, languages, locations = [], [], []
    files = [f for f in listdir(d) if isfile(d + f)]
    for f in files:
        if f.endswith(".xml"):
            tree = etree.parse(d + f)
            root = tree.getroot()
            for article in root.findall('channel/item'):
                domains.append(urlparse(article.find('link').text).hostname)
                languages.append(article.find('{http://www.iso.org/3166}language').text)
                location_count = set()
                for a in article.findall('{http://emm.jrc.it}fullgeo') + article.findall('{http://emm.jrc.it}georss'):
                    location_count.update(set(a.attrib['pos'].split(",")))  # sets avoid counting duplicates
                locations.append(len(location_count))

    # plt.hist(locations, [0, 10, 20, 30, 40, 50, 60, 70], facecolor='b')
    # plt.xlabel('Tagged Toponyms')
    # plt.ylabel('Article Count')
    # plt.title('Toponyms tagged per article (out of 10,000 news articles)')
    # plt.grid(True)
    # plt.show()
    print("Domains:", domains)
    print("Languages:", languages)
    print("Locations:", locations)
    print("No of files:", len(files))


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

    geo_location_pop, associative_outliers = dict(), dict()
    for article in root.findall("article"):
        literal, associative = [], []
        geo_location_pop[article.attrib['file']] = []
        for toponym in article.findall('toponyms/toponym'):
            norm_name = toponym.find('normalisedName').text
            norm_name = norm_name if norm_name is not None else u""
            # ------------ Toponym Resolution for each article using Population -------------
            gold_coordinates = (toponym.find('latitude').text, toponym.find('longitude').text)
            pop_coordinates = get_coordinates(conn, norm_name)
            if len(pop_coordinates) > 0 and len(gold_coordinates) > 0:
                pop_coordinates = (pop_coordinates[0][0], pop_coordinates[0][1])
                distance = great_circle(gold_coordinates, pop_coordinates)
                geo_location_pop[article.attrib['file']].append(distance)
            # -------------------- Build two lists of toponyms -------------------------
            label = toponym.find('type').text
            if label in [u"Non_Lit_Expression", u"Literal_Expression", u"Non_Toponym"]:
                continue
            if label_map[label] == u"Associative":
                associative.append(toponym)
            else:
                literal.append(toponym)
        accuracy = []
        for assoc in associative:
            min_dist = numpy.inf
            for lit in literal:
                distance = great_circle((lit.find('latitude').text, lit.find('longitude').text),
                                        (assoc.find('latitude').text, assoc.find('longitude').text))
                if distance < min_dist:
                    min_dist = distance
            accuracy.append(min_dist)
        associative_outliers[article.attrib['file']] = accuracy
    # analysis to continue here...


# emm_news_analysis()
geowebnews_analysis()
