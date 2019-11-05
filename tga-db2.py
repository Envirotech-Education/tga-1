# Exploring the Training.gov.au Web Services
# Author: Marcus Wynwood (@MarcusTeachUs)
#
# Finds EVERY training pack, EVERY qual and EVERY unit and puts it in a SQLite Database.
# Units are duplicated if they exist in multiple quals.
# It's not normalised of efficient... yet!
# It takes a couple of hours to run too.
#
# I don't think it's quite complete, and bugs out on line 92 after about 2 hours.
# tga-db2.py", line 92, in <module>
#  for units in r.UnitGrid.UnitGridEntry:
# AttributeError: 'NoneType' object has no attribute 'UnitGridEntry'
#
# Explore tga-db2.db with SQLiteStudio or something to see what this code generates.
# 
# It would be nice to also store what Stream the elective units belong to.
# Then it could take into account Packaging Rules.
# Lots more to do, but this is a start.

import zeep
from zeep.wsse.username import UsernameToken
import sqlite3

wsdl = 'https://ws.sandbox.training.gov.au/Deewr.Tga.Webservices/TrainingComponentServiceV7.svc?wsdl'
username = "WebService.Read"
password = "Asdf098"
client = zeep.Client(wsdl=wsdl, wsse=UsernameToken(username, password))

db = sqlite3.connect('tga-db2.db')
cursor = db.cursor()

cursor.execute('''
CREATE TABLE trainingpacks(
    id INTEGER PRIMARY KEY,
    code TEXT,
    title TEXT)
''')

cursor.execute('''
CREATE TABLE quals(
    id INTEGER PRIMARY KEY,
    code TEXT,
    title TEXT,
    type TEXT,
    trainingpack TEXT)
''')

cursor.execute('''
CREATE TABLE units(
    id INTEGER PRIMARY KEY, 
    code TEXT,
    title TEXT,
    core TEXT,
    qual TEXT
)''')

db.commit()

TrainingComponentTypeFilter = {
    "IncludeAccreditedCourse": False,
    "IncludeAccreditedCourseModule": False,
    "IncludeQualification": True,
    "IncludeSkillSet": True,
    "IncludeTrainingPackage": True,
    "IncludeUnit": False,
    "IncludeUnitContextualisation": False
}

# Create a TrainingComponentSearchRequest for the search
TrainingComponentSearchRequest = {
    "ClassificationFilters": "",
    "Filter": "",  # The search term.
    "IncludeDeleted": False,
    "IncludeSuperseeded": False,
    # "PageNumber": 0,
    # "PageSize": 0,
    "SearchCode": True,
    "SearchIndustrySector": False,
    "SearchOccupation": False,
    "SearchTitle": False,
    "TaxonomyOccupationFilter": "",
    "TaxonomyIndustrySectorFilter": "",
    "TrainingComponentTypes": TrainingComponentTypeFilter,
    "IncludeLegacyData": False
}

TrainingComponentSearchResult = client.service.Search(TrainingComponentSearchRequest)
# print(TrainingComponentSearchResult)

for tp in TrainingComponentSearchResult.Results.TrainingComponentSummary:
    if (tp.ComponentType[0] == 'Qualification' or tp.ComponentType[0] == 'SkillSet') and tp.IsCurrent == True:
        # I've just used the first 3 letters of the qual as the trainingpack. Bit dodgy, but probably accurate
        cursor.execute('''INSERT INTO quals(code, title, type, trainingpack) VALUES(?,?,?,?)''', (tp.Code, tp.Title, tp.ComponentType[0], str(tp.Code)[:3]))
        db.commit()
        # Loop to grab all units in qual?
        TrainingComponentSearchRequest_qual = {
            "ClassificationFilters": "",
            "Filter": tp.Code,
            "IncludeDeleted": False,
            "IncludeSuperseeded": False,
            "SearchCode": True,
            "SearchIndustrySector": False,
            "SearchOccupation": False,
            "SearchTitle": False,
            "IncludeLegacyData": False
        }
        TrainingComponentSearchResult_qual = client.service.Search(TrainingComponentSearchRequest_qual)
        TrainingComponent_qual = client.service.GetDetails(TrainingComponentSearchResult_qual.Results.TrainingComponentSummary)
        for r in TrainingComponent_qual.Releases.Release:
            if r.Currency == 'Current':
                for units in r.UnitGrid.UnitGridEntry:
                    cursor.execute('''INSERT INTO units(code, title, core, qual) VALUES(?,?,?,?)''', (units.Code, units.Title, units.IsEssential, tp.Code))
                    db.commit()
    if tp.ComponentType[0] == 'TrainingPackage' and tp.IsCurrent == True:
        cursor.execute('''INSERT INTO trainingpacks(code, title) VALUES(?,?)''', (tp.Code, tp.Title))
        db.commit()

db.commit() # for luck

# cursor.execute('''SELECT * FROM trainingpacks''')
# for row in cursor:
#     print(row)

# cursor.execute('''SELECT * FROM quals''')
# for row in cursor:
#     print(row)

# cursor.execute('''SELECT * FROM quals WHERE trainingpack="ICT" AND type="Qualification"''')
# for row in cursor:
#     print(row)

db.close()
