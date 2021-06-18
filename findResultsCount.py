import json
from urllib.parse import quote_plus as url_encode
import csv
from elsapy.elsclient import ElsClient

con_file = open("config.json")
config = json.load(con_file)
con_file.close()

## Initialize client
client = ElsClient(config['apikey']['mark'])
codes = ['ALL','ABS','AF-ID','AFFIL','AFFILCITY','AFFILCOUNTRY','AFFILORG','AU-ID',
         'AUTHOR-NAME','AUTH','AUTHFIRST','AUTHLASTNAME', 'AUTHCOLLAB','AUTHKEY','CASREGNUMBER','CHEM',
         'CHEMNAME','CODEN','CONF','CONFLOC','CONFNAME','CONFSPONSORS',
         'DOI','EDFIRST','EDITOR','EDLASTNAME','EISSN','EXACTSRCTITLE','FIRSTAUTH','FUND-SPONSOR','FUND-ACR',
         'FUND-NO','ISBN','ISSN','ISSNP','ISSUE','KEY','LANGUAGE','MANUFACTURER',
         'PMID','PUBLISHER','REF','REFAUTH','REFTITLE',
         'REFSRCTITLE','SEQBANK','SEQNUMBER','SRCTITLE',
         'TITLE','TITLE-ABS-KEY','TITLE-ABS-KEY-AUTH','TRADENAME','VOLUME','WEBSITE']
search_count = {'ALL': 0,'ABS': 0,'AF-ID': 0,'AFFIL': 0,'AFFILCITY': 0,'AFFILCOUNTRY': 0,'AFFILORG': 0,
                'AU-ID': 0,'AUTHOR-NAME': 0,'AUTH': 0,'AUTHFIRST': 0,'AUTHLASTNAME': 0,'AUTHCOLLAB': 0,
                'AUTHKEY': 0,'CASREGNUMBER': 0,'CHEM': 0,'CHEMNAME': 0,'CODEN': 0,'CONF': 0,'CONFLOC': 0,
                'CONFNAME': 0,'CONFSPONSORS': 0,'DOI': 0,'EDFIRST': 0,'EDITOR': 0,'EDLASTNAME': 0,'EISSN': 0,
                'EXACTSRCTITLE': 0,'FIRSTAUTH': 0,'FUND-SPONSOR': 0,'FUND-ACR': 0,'FUND-NO': 0,
                'ISBN': 0,'ISSN': 0,'ISSNP': 0,'ISSUE': 0,'KEY': 0,'LANGUAGE': 0,'MANUFACTURER': 0,'PMID': 0,
                'PUBLISHER': 0,'REF': 0,'REFAUTH': 0,'REFTITLE': 0,'REFSRCTITLE': 0,'SEQBANK': 0,'SEQNUMBER': 0,
                'SRCTITLE': 0,'TITLE': 0,'TITLE-ABS-KEY': 0,'TITLE-ABS-KEY-AUTH': 0,'TRADENAME': 0,'VOLUME': 0,
                'WEBSITE': 0}
for code in codes:
    query = code + "(emotion) OR " + code + "(emotional) OR " + code + "(emotions) OR " + code + "(empathy) OR " + code + "(empathic) OR " + code + "(feeling) " \
        "OR " + code + "(feelings) OR " + code + "(mood) OR " + code + "(moods) OR " + code + "(motivation) OR " + code + "(motivations) OR " + code + "(preference) " \
        "OR " + code + "(preferences) OR " + code + "(stress) OR " + code + "(well-being) " \
        "AND PUBYEAR < 2021"
    uri = u'https://api.elsevier.com/content/search/scopus?query=' + url_encode(query) + "&count=1"
    api_response = client.exec_request(uri)
    search_count[code] = int(api_response['search-results']['opensearch:totalResults'])
with open('output/resultsCount.csv', 'w') as f:
    for key in search_count.keys():
        f.write("%s,%s\n"%(key,search_count[key]))

