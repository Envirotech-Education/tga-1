# Exploring the Training.gov.au Web Services
# Author: Marcus Wynwood (@MarcusTeachUs)
#
# Finds all the units in a qual

import zeep
from zeep.wsse.username import UsernameToken
import urllib
import xmltodict

wsdl = 'https://ws.sandbox.training.gov.au/Deewr.Tga.Webservices/TrainingComponentServiceV7.svc?wsdl'
username = "WebService.Read"
password = "Asdf098"
client = zeep.Client(wsdl=wsdl, wsse=UsernameToken(username, password))
base_url_for_xml_files = 'http://training.gov.au/TrainingComponentFiles/'



#########################################
# xml_url_to_dict(xml_url)
# Give this bad boy a URL to an XML file, and it'll
# give you a dictionary populated form that XML file.
# xmltodict doesn't seem to make it that nice...
def xml_url_to_dict(xml_url):
    file = urllib.request.urlopen(xml_url)
    data = file.read()
    file.close()
    data = xmltodict.parse(data)
    return data



#########################################
# get_qualification(code)
# Given a Qual Code string, return a list of units
# The returned list will contain dictionaries with: code, title, core
def get_qualification(code):

    list_of_units = []

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
    # for tcs in TrainingComponentSearchResult.Results.TrainingComponentSummary:
    #     if tcs.ComponentType[0] == 'Qualification' and tcs.IsCurrent == True:
    #         print(tcs.Code, tcs.Title)

    # Loop through every unit in the Qual to get the CODE, TITLE, and if it is a CORE UNIT.
    for r in TrainingComponent.Releases.Release:
        if r.Currency == 'Current':
            for units in r.UnitGrid.UnitGridEntry:
                # print(units.Code, units.Title, units.IsEssential)
                list_of_units.append({"code":units.Code, "title":units.Title, "core":units.IsEssential})

    return list_of_units



#########################################
# get_competence(code)
# Given a Unit Code string, return a list with the elements, ke, pe, etc...
def get_competence(code):
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

    for tc in TrainingComponent.Releases.Release[0].Files.ReleaseFile:
        # If the last 4 chars are .xml, build the full URL and put the slashes around the right way
        if tc.RelativePath[-4:] == ".xml":
            full_url = base_url_for_xml_files + tc.RelativePath
            full_url = full_url.replace("\\", "/")
            # Print the full URL of the XML file
            # print(full_url)
            return xml_url_to_dict(full_url)



#########################################
# list_to_html(the_list, html_filename)
# Takes a list of dictionaries, and creates a HTML table from it
def list_of_dicts_to_html(the_list_of_dicts, html_filename):
    html_output = "<table>"
    for u in the_list_of_dicts:
        html_output = html_output + "<tr>"
        for d in u.values():
            html_output = html_output + "<td>" + str(d) + "</td>"
        html_output = html_output + "</tr>"
    html_output = html_output + "</table>"

    with open(html_filename, 'w+') as f:
        f.writelines(html_output)

    # print(html_output)



#########################################

# qual = get_qualification("ICT30118")
# for unit in qual:
#     print(unit['core'], unit['code'], unit['title'])

list_of_dicts_to_html(get_qualification("ICT30118"), "out.html")

unit = get_competence("ICTWEB201")
# print(unit)
with open("unit.json", 'w+') as f:
    f.write(str(unit))