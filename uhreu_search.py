"""An example program that uses the elsapy module"""

from elsapy.elsclient import ElsClient
from elsapy.elsprofile import ElsAuthor, ElsAffil
from elsapy.elsdoc import FullDoc, AbsDoc
from elsapy.elssearch import ElsSearch
import pandas as pd
import json

## Load configuration
con_file = open("config.json")
config = json.load(con_file)
con_file.close()

## Initialize client
client = ElsClient(config['apikey']['pavlidis'], config['inst_key'])
# client.inst_token = config['insttoken']

## Initialize doc search object using Scopus and execute search, retrieving
#   all results
# ALL(emotion) OR ALL(emotional) OR ALL(emotions) OR ALL(empathy) OR ALL(empathic) OR ALL(feeling) OR ALL(feelings) OR ALL(mood) OR ALL(moods) OR ALL(motivation) OR ALL(motivations) OR ALL(preference) OR ALL(preferences) OR ALL(stress) OR ALL(well-being) AND PUBYEAR < 1800
query = "TITLE-ABS-KEY(emotion) OR TITLE-ABS-KEY(emotional) OR TITLE-ABS-KEY(emotions) OR TITLE-ABS-KEY(empathy) OR TITLE-ABS-KEY(empathic) OR TITLE-ABS-KEY(feeling) " \
        "OR TITLE-ABS-KEY(feelings) OR TITLE-ABS-KEY(mood) OR TITLE-ABS-KEY(moods) OR TITLE-ABS-KEY(motivation) OR TITLE-ABS-KEY(motivations) OR TITLE-ABS-KEY(preference) " \
        "OR TITLE-ABS-KEY(preferences) OR TITLE-ABS-KEY(stress) OR TITLE-ABS-KEY(well-being) " \
        "AND PUBYEAR < 2021"
# query = "TITLE(Embeddedness) AND TITLE(multinational corporation) AND PUBYEAR = 2011"
doc_srch = ElsSearch(query, 'scopus')
doc_srch.execute(client, get_all=True)
print("doc_srch has", len(doc_srch.results), "results.")
print("doc_srch has", doc_srch.tot_num_res, " total results.")
#doc_srch.results_df.to_csv("output/test2.csv", sep=',', index=False, encoding="utf-8") # find the coverDate from the dictionary