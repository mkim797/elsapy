"""An example program that uses the elsapy module"""

from elsapy.elsclient import ElsClient
from elsapy.elsprofile import ElsAuthor, ElsAffil
from elsapy.elsdoc import FullDoc, AbsDoc
from elsapy.elssearch import ElsSearch
import json

## Load configuration
con_file = open("config.json")
config = json.load(con_file)
con_file.close()

## Initialize client
client = ElsClient(config['apikey'])
# client.inst_token = config['insttoken']

## Initialize doc search object using Scopus and execute search, retrieving
#   all results
doc_srch = ElsSearch("ALL(emotion) OR ALL(emotional) OR ALL(emotions) OR ALL(empathy) OR ALL(empathic) OR ALL(feeling) OR ALL(feelings) OR ALL(mood) OR ALL(moods) OR ALL(motivation) OR ALL(motivations) OR ALL(preference) OR ALL(preferences) OR ALL(stress) OR ALL(well-being) AND PUBYEAR < 1800", 'scopus')
doc_srch.execute(client, get_all=True)
result = doc_srch.results.pop() # pop the single result...result is a dictionary
print("doc_srch has", len(doc_srch.results), "results.")
print(result['prism:coverDate']) # find the coverDate from the dictionary