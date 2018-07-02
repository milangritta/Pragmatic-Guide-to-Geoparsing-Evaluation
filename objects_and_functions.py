

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
