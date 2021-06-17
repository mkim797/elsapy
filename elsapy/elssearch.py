"""The search module of elsapy.
    Additional resources:
    * https://github.com/ElsevierDev/elsapy
    * https://dev.elsevier.com
    * https://api.elsevier.com"""
import xmltodict

from . import log_util
from urllib.parse import quote_plus as url_encode
import pandas as pd, json
from .utils import recast_df
import string
from pathlib import Path
import os

logger = log_util.get_logger(__name__)

class ElsSearch():
    """Represents a search to one of the search indexes accessible
         through api.elsevier.com. Returns True if successful; else, False."""

    # static / class variables
    _base_url = u'https://api.elsevier.com/content/search/'
    _cursored_indexes = [
        'scopus',
    ]

    def __init__(self, query, index):
        """Initializes a search object with a query and target index."""
        self.query = query
        self.index = index
        self.num_records = 25
        self._cursor_supported = (index in self._cursored_indexes)
        self._uri = self._base_url + self.index + '?query=' + url_encode(
                self.query) + '&count=' + str(self.num_records)
        columns = ['@_fa','link','prism:url','dc:identifier','eid','dc:title','prism:aggregationType','subtype',
                   'subtypeDescription','citedby-count','prism:publicationName','prism:isbn','prism:issn',
                   'prism:volume','prism:issueIdentifier','prism:pageRange','prism:coverDate','prism:coverDisplayDate',
                   'prism:doi','pii','pubmed-id','orcid','dc:creator','openaccess','affiliation','author','dc:description',
                   'authkeywords','article-number','fund-acr','fund-no','fund-sponsor','prism:eIssn', 'abstract_text']
        self.results_df = pd.DataFrame(columns=columns)
        self.max_file_size = 100 * 1000 # first number in KB

    # properties
    @property
    def query(self):
        """Gets the search query"""
        return self._query

    @query.setter
    def query(self, query):
        """Sets the search query"""
        self._query = query

    @property
    def index(self):
        """Gets the label of the index targeted by the search"""
        return self._index

    @index.setter
    def index(self, index):
        """Sets the label of the index targeted by the search"""
        self._index = index

    @property
    def results(self):
        """Gets the results for the search"""
        return self._results

    @property
    def tot_num_res(self):
        """Gets the total number of results that exist in the index for
            this query. This number might be larger than can be retrieved
            and stored in a single ElsSearch object (i.e. 5,000)."""
        return self._tot_num_res

    @property
    def num_res(self):
        """Gets the number of results for this query that are stored in the 
            search object. This number might be smaller than the number of 
            results that exist in the index for the query."""
        return len(self.results)

    @property
    def uri(self):
        """Gets the request uri for the search"""
        return self._uri

    def _upper_limit_reached(self):
        """Determines if the upper limit for retrieving results from of the
            search index is reached. Returns True if so, else False. Upper 
            limit is 5,000 for indexes that don't support cursor-based 
            pagination."""
        if self._cursor_supported:
            return False
        else:
            return self.num_res >= 5000

    
    def execute(self, els_client = None, get_all = False):
        """Executes the search. If get_all = False (default), this retrieves
            the default number of results specified for the API. If
            get_all = True, multiple API calls will be made to iteratively get 
            all results for the search, up to a maximum of 5,000."""
        ## TODO: add exception handling
        api_response = els_client.exec_request(self._uri)
        abstracts_index = 0
        self._tot_num_res = int(api_response['search-results']['opensearch:totalResults'])
        self._results = api_response['search-results']['entry']
        self.add_abstracts(els_client, abstracts_index)
        self.results_df = self.results_df.append(recast_df(pd.DataFrame(self._results)))
        # breakpoint()
        csv_filename_number = 0
        csv_filename = "output/test"+ str(csv_filename_number) + ".csv"
        self.results_df.to_csv(csv_filename, mode='a', sep=',', index=False, encoding="utf-8", header=not os.path.exists(csv_filename))
        if get_all is True:
            while (self.num_res < self.tot_num_res): #and not self._upper_limit_reached():
                # breakpoint()
                for e in api_response['search-results']['link']:
                    if e['@ref'] == 'next':
                        next_url = e['@href']
                        # next_url = next_url.replace('scopus?start=', 'scopus?cursor=')
                api_response = els_client.exec_request(next_url)
                self._results = api_response['search-results']['entry']
                self.add_abstracts(els_client, abstracts_index)
                self.results_df = self.results_df.append(recast_df(pd.DataFrame(self._results)))
                self.results_df.to_csv(csv_filename, mode='a', sep=',', index=False, encoding="utf-8", header=not os.path.exists(csv_filename))
                filesize = Path(csv_filename).stat().st_size
                if filesize >= self.max_file_size:
                    csv_filename_number += 1
                    csv_filename = "output/test" + str(csv_filename_number) + ".csv"
        with open('dump.json', 'w') as f:
            f.write(json.dumps(self._results))

    def add_abstracts(self, els_client, start = 0):
        """Finds abstracts of document from Scopus Search and adds them to results"""
        end = start + self.num_records - 1
        for i in range(start, end):
            if 'prism:doi' not in self._results[i] or 'pii' not in self._results[i]:
                continue
            if 'prism:doi' in self._results[i]:
                get_abstract_url = "https://api.elsevier.com/content/article/doi/" + self._results[i]['prism:doi']
            elif 'pii' in self._results[i]:
                get_abstract_url = "https://api.elsevier.com/content/article/pii/" + self._results[i]['pii']
            get_abstract_response = els_client.exec_request(get_abstract_url)
            if 'full-text-retrieval-response' in get_abstract_response \
                    and 'coredata' in get_abstract_response['full-text-retrieval-response'] \
                    and 'dc:description' in get_abstract_response['full-text-retrieval-response']['coredata'] \
                    and get_abstract_response['full-text-retrieval-response']['coredata']['dc:description'] is not None:
                abstract = get_abstract_response['full-text-retrieval-response']['coredata']['dc:description'].translate(str.maketrans('', '', string.punctuation))
                abstract = " ".join(abstract.split())
                self._results[i]['abstract_text'] = abstract

    def output_csv(self, file_number=0, max_file_size = 100000):
        csv_filename = "output/test" + str(file_number) + ".csv"
        self.results_df.to_csv(csv_filename, mode='a', sep=',', index=False, encoding="utf-8",
                               header=not os.path.exists(csv_filename))
        filesize = Path(csv_filename).stat().st_size
        if filesize >= max_file_size:
            file_number += 1
        return file_number

    def hasAllResults(self):
        """Returns true if the search object has retrieved all results for the
            query from the index (i.e. num_res equals tot_num_res)."""
        return (self.num_res is self.tot_num_res)
