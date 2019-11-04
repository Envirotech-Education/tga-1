# Exploring the Training.gov.au Web Services
# Author: Marcus Wynwood (@MarcusTeachUs)
#
# Finds all the units in a qual, and puts it in a SQLite Database

import zeep
from zeep.wsse.username import UsernameToken
import sqlite3

wsdl = 'https://ws.sandbox.training.gov.au/Deewr.Tga.Webservices/TrainingComponentServiceV7.svc?wsdl'
username = "WebService.Read"
password = "Asdf098"
client = zeep.Client(wsdl=wsdl, wsse=UsernameToken(username, password))

code = "ICT30118"

db = sqlite3.connect(':memory:')
cursor = db.cursor()
cursor.execute('''CREATE TABLE units(id INTEGER PRIMARY KEY, qual_code TEXT, unit_code TEXT, unit_title TEXT, core TEXT)''')

# Create a TrainingComponentSearchRequest for the search
TrainingComponentSearchRequest = {
    "ClassificationFilters": "",
    "Filter": code,
    "IncludeDeleted": False,
    "IncludeSuperseeded": False,
    "SearchCode": True,
    "SearchIndustrySector": False,
    "SearchOccupation": False,
    "SearchTitle": False,
    "IncludeLegacyData": False
}
# Run a search with the TrainingComponentSearchRequest 
TrainingComponentSearchResult = client.service.Search(TrainingComponentSearchRequest)

# Use the search results to get more details about the TrainingComponent
TrainingComponent = client.service.GetDetails(TrainingComponentSearchResult.Results.TrainingComponentSummary)

# Get the CODE and the TITLE from the TrainingComponentSearchResult
for tcs in TrainingComponentSearchResult.Results.TrainingComponentSummary:
    if tcs.ComponentType[0] == 'Qualification' and tcs.IsCurrent == True:
        # print(tcs.Code, tcs.Title)
        qual = tcs.Code

# Loop through every unit in the Qual to get the CODE, TITLE, and if it is a CORE UNIT.
for r in TrainingComponent.Releases.Release:
    if r.Currency == 'Current':
        for units in r.UnitGrid.UnitGridEntry:
            cursor.execute('''INSERT INTO units(qual_code, unit_code, unit_title, core) VALUES(?,?,?,?)''', (qual, units.Code, units.Title, units.IsEssential))
db.commit()

cursor.execute('''SELECT * FROM units WHERE core=1 ORDER BY unit_code''')
for row in cursor:
    print(row)

db.close()