# Exploring the Training.gov.au Web Services
# Author: Marcus Wynwood (@MarcusTeachUs)
#
# This program does a search, and prints/saves the results.

import zeep
from zeep.wsse.username import UsernameToken
import json
import urllib.request

wsdl = 'https://ws.sandbox.training.gov.au/Deewr.Tga.Webservices/TrainingComponentServiceV7.svc?wsdl'
username = "WebService.Read"
password = "Asdf098"
base_url_for_xml_files = 'http://training.gov.au/TrainingComponentFiles/'
client = zeep.Client(wsdl=wsdl, wsse=UsernameToken(username, password))

# Create a TrainingComponentSearchRequest for the search
TrainingComponentSearchRequest  = {
    "ClassificationFilters": "",
    "Filter": "ICTWEB201", # The search term. Put a Training Pack Code, Qual Code, or Unit Code here.
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
    # "TrainingComponentTypes": "unit",
    "IncludeLegacyData": False
}

# Once we search, we get a TrainingComponentSearchResult
TrainingComponentSearchResult = client.service.Search(TrainingComponentSearchRequest)
# Print the TrainingComponentSearchResult
print(TrainingComponentSearchResult)
# Write the TrainingComponentSearchResult to a file
with open('TrainingComponentSearchResult.xml', 'w+') as f:
    f.writelines(str(TrainingComponentSearchResult))

# From there, we can send the results to the GetDetails method to get more info
# The result is stored in a TrainingComponent
TrainingComponent = client.service.GetDetails(TrainingComponentSearchResult.Results.TrainingComponentSummary)
# Print the TrainingComponent
print(TrainingComponent)
# Write the TrainingComponent to a file
with open('TrainingComponent.xml', 'w+') as f:
    f.writelines(str(TrainingComponent))

# The actual details of the unit (elements, etc...) are stored in xml files. Go get it!
for tc in TrainingComponent.Releases.Release[0].Files.ReleaseFile:
    # If the last 4 chars are .xml, build the full URL and put the slashes around the right way
    if tc.RelativePath[-4:] == ".xml":
        full_url = base_url_for_xml_files + tc.RelativePath
        full_url = full_url.replace("\\", "/")
        # Print the full URL of the XML file
        print(full_url)
        # Write the contents of the online XML file to a local file
        # Not sure if this is the best way, but it works for now
        with urllib.request.urlopen(full_url) as response:
            html = response.read()
            filename_without_folder = tc.RelativePath[4:]
            with open(filename_without_folder, 'w+') as f:
                f.writelines(str(html)[14:].replace("\\r\\n", ""))
