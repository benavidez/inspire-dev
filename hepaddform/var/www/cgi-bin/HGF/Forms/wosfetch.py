#!/usr/bin/env python
# based upon
#   https://gist.github.com/2012629#file_wos.py
# with heavy extensions
# -*- coding: utf-8 -*-

from suds.client import Client
from suds.transport.http import HttpTransport as SudsHttpTransport
import urllib2
import sys
from time import time
from stat import *
import os
import re

from xml.dom.minidom import Document

class WellBehavedHttpTransport(SudsHttpTransport): 
    def u2handlers(self): 
        return []

class HTTPSudsPreprocessor(urllib2.BaseHandler):
    def __init__(self, SID):
        self.SID = SID

    def http_request(self, req):
        req.add_header('cookie', 'SID="'+self.SID+'"')
        return req

    https_request = http_request

class WOSXML(Document):

    """
    Rewrite the SearchLite structure to the usual XML-structure of WOS
    to give it transparenty to further processing tools. As we do not
    have many values in LITE search we need to fake a bunch of
    attributes to keep further processors happy.
    """

    def __init__(self):
        Document.__init__(self)
        self.records = self.createElement("records")
        self.appendChild(self.records)
        self.__NrOfRecords = 0

    def createREC(self):
        self.REC = self.createElement("REC")
        self.REC.setAttribute('inst_id', '0')     # fake value
        self.REC.setAttribute('rec_id', '0')      # fake value
        self.REC.setAttribute('hot', 'yes')       # fake value
        self.REC.setAttribute('sortkey', '0')     # fake value
        self.REC.setAttribute('timescited', '0')  # fake value
        self.REC.setAttribute('sharedrefs', '0')  # fake value
        self.REC.setAttribute('inpi', 'false')    # fake value
        self.records.appendChild(self.REC)
        self.__NrOfRecords += 1

    def createItem(self):
        self.item = self.createElement("item")
        self.item.setAttribute('issue', '0')            # fake value
        self.item.setAttribute('recid', '0')            # fake value
        self.item.setAttribute('coverdate', '150001')   # fake value yyyymm = jan. 1500
        self.item.setAttribute('sortkey', '0')          # fake value
        self.item.setAttribute('refkey', '0')           # fake value
        self.item.setAttribute('dbyear', '1500')        # fake value yyyy
        self.REC.appendChild(self.item)

    def setTextField(self, field, entry):
        self.tf = self.createElement(field)
        self.tf.appendChild(self.createTextNode(entry))
        self.item.appendChild(self.tf)

    def setSubFields(self, field, subfield, entries):
        self.f = self.createElement(field)
        self.f.setAttribute('count', str(len(entries)))
        i = 0
        for entry in entries:
                fieldtag = subfield
                # authors use the primary author flag...
                if field == 'authors':
                        if i == 0:
                                fieldtag = 'primaryauthor'
                i += 1
                self.sf = self.createElement(fieldtag)
                self.sf.appendChild(self.createTextNode(entry))
                self.f.appendChild(self.sf)
        self.item.appendChild(self.f)

    def setReferenceFields(self, source):
        issue = ''
        date  = ''
        year  = ''
        src   = ''
        vol   = ''
        pages = ''

        for s in source:
                field = s[0]
                value = s[1][0]
                if field   == 'Issue':
                        issue = value
                elif field == 'Pages':
                        pages = value
                elif field == 'Published.BiblioDate':
                        date = value
                elif field == 'Published.BiblioYear':
                        year = value
                elif field == 'SourceTitle':
                        src = value
                elif field == 'Volume':
                        vol = value

        self.f = self.createElement('bib_issue')
        txt = ''
        if vol != '':
           self.f.setAttribute('vol', str(vol))
           txt = txt + str(vol)
        if issue != '':
          txt = txt + ' (' + str(issue) + ')'
        if pages != '':
          txt = txt + ':' + pages
        if date != '':
          txt = txt + ' ' + date
        if year != '':
          self.f.setAttribute('year', str(year))
          txt = txt + ' ' + str(year)
        self.item.appendChild(self.f)
        self.f = self.createElement('bib_id')
        self.f.appendChild(self.createTextNode(txt.strip()))
        self.item.appendChild(self.f)

        if pages != '':
           self.f = self.createElement('bib_pages')
           bp = re.sub('-.*', '', pages)
           ep = re.sub('[^-]*-', '', pages)
           self.f.setAttribute('begin', str(bp))
           self.f.setAttribute('end',   str(ep))
           self.f.setAttribute('pages', str(pages))
           self.f.appendChild(self.createTextNode(pages))
           self.item.appendChild(self.f)

        if src != '':
           self.f = self.createElement('source_title')
           self.f.appendChild(self.createTextNode(src))
           self.item.appendChild(self.f)

        if issue != '':
           self.issue = self.createElement('issue')
           self.f = self.createElement('bib_vol')
           self.f.setAttribute('issue', str(issue))
           txt = '(' + str(issue) + '):'
           if vol != '':
              self.f.setAttribute('volume', str(vol))
              txt = str(vol) + txt
           self.f.appendChild(self.createTextNode(txt.strip()))
           self.issue.appendChild(self.f)

           self.f = self.createElement('bib_date')
           txt = ''
           if date != '':
               self.f.setAttribute('date', date)
               txt =  txt + date + ' '
           if year != '':
               self.f.setAttribute('year', str(year))
               txt = txt + str(year)
           self.f.appendChild(self.createTextNode(txt.strip()))
           self.issue.appendChild(self.f)

           if src != '':
               self.f = self.createElement('issue_title')
               self.f.appendChild(self.createTextNode(src))
               self.issue.appendChild(self.f)


           self.REC.appendChild(self.issue)

    def NumberOfRecords(self):
        return self.__NrOfRecords

    def InsertData(self, retdta):
        authors = retdta.records[0].authors[0].values
        # keywords= retdta.records[0].keywords[0].values
	keywords = ''
        title   = retdta.records[0].title[0].values[0]
        source  = retdta.records[0].source
        ut      = retdta.records[0].UT

        self.createREC()
        self.createItem()
        self.setTextField('ut', ut)
        self.setTextField('item_title', title)
        self.setSubFields('authors', 'author', authors)
        self.setSubFields('keywords', 'keyword', keywords)
        self.setReferenceFields(source)

class WokmwsSoapClient:
    """
    main steps you have to do:
        soap = WokmwsSoapClient()
        results = soap.search(...)
    """
    def __init__(self):

        self.useLiteSearch = True

        self.url = self.client = {}
        self.SID = ''
        self.SIDFILE = '/tmp/wosfetch.sid'

        self.fullsearch = 'http://search.isiknowledge.com/esti/wokmws/ws/WokSearch?wsdl'
        self.litesearch = 'http://search.isiknowledge.com/esti/wokmws/ws/WokSearchLite?wsdl'
        self.url['auth'] = 'http://search.isiknowledge.com/esti/wokmws/ws/WOKMWSAuthenticate?wsdl'

        if self.useLiteSearch:
          self.url['search'] = self.litesearch
        else:
          self.url['search'] = self.fullsearch

        self.prepare()

    def __del__(self):
        # we should not close the session as we might want to reuse
        # it to avoid senseless trouble with the throttling "service"
        #self.close()
        pass

    def prepare(self):
        # does all the initialization we need for a request
        self.initAuthClient()
        self.authenticate()
        self.initSearchClient()

    def initAuthClient(self):
        http = WellBehavedHttpTransport()
        self.client['auth'] = Client(self.url['auth'], transport = http)

    def initSearchClient(self):
        http = WellBehavedHttpTransport()
        opener = urllib2.build_opener(HTTPSudsPreprocessor(self.SID))
        http.urlopener = opener
        self.client['search'] = Client(self.url['search'], transport = http)

    def authenticate(self):
        # check how old the file is: if it is older than 3000
        # seconds we should establish a new session. Therefore, drop
        # the session file and proceed.
        # NOTE: Reasons why one hit's the throttling "service":
        # - > 10.000 requests per session
        # - > 5 (10?) established sessions per 5min
        # - > 1 request per second
        # Given the "performance" of WOS the above should keep both
        # under control still, we should sleep for 1s :S
        try:
          st = os.stat(self.SIDFILE)
          if time() - st[ST_CTIME] > 3000:
            os.remove(self.SIDFILE)
        except:
          # no session file exists, so we establish a new session
          # anyway.
          pass
        # get SID from the file to reuse the session or establish a
        # new one if no SID file survived the time stamp checking or
        # it was removed by any other means.
        try:
          f = open(self.SIDFILE, 'r')
          self.SID = f.read()
          f.close()
        except:
          self.SID = self.client['auth'].service.authenticate()
          # Store SID handle for reuse.
          f = open(self.SIDFILE, 'w')
          f.write(self.SID)
          f.close()

    def close(self):
        self.client['auth'].service.closeSession()

    def search(self, query, count=1, firstrecord=1):
        qparams = {
            'databaseID' : 'WOS',
            'userQuery' : query,
            'queryLanguage' : 'en',
            'editions' : [{
                'collection' : 'WOS',
                'edition' : 'SCI',     # Science Citation Index Expanded
            }
            ]
        }

        rparams = {
            'count' : count, # 1-100
            'firstRecord' : firstrecord,
            'fields' : [{
                'name' : 'Relevance',
                'sort' : 'D',
            }],
        }

        retdta = self.client['search'].service.search(qparams, rparams)

        if self.useLiteSearch:
           # in lite we have to recode to xml
           xmldoc = WOSXML()
           xmldoc.InsertData(retdta)
           return xmldoc.toxml()
        else:
           return retdta.records

if __name__ == '__main__':
  soap = WokmwsSoapClient()
  query = sys.argv[1]
  res = soap.search(query)
  print res
  #print res['records']
