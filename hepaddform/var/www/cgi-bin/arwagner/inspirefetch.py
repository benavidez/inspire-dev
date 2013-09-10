#!/usr/bin/env python
# based upon
#   https://gist.github.com/2012629#file_wos.py
# with heavy extensions
# -*- coding: utf-8 -*-

import urllib2
import sys
from time import time
from stat import *
import os
import re

from invenio.bibrecord import create_record, record_get_field_values, record_get_field_instances

# URL: http://inspirehep.net/search?ln=en&ln=en&p=10.1016%2Fj.physletb.2006.11.038&of=xm

baseurl  = 'http://inspirehep.net/search'
querypar = 'p='
format   = 'of=xm'

from xml.dom.minidom import Document

class RecXML(Document):

    def __init__(self):
        Document.__init__(self)
        self.collection= self.createElement("collection")
        self.appendChild(self.collection)
        self.createREC()

    def createREC(self):
        self.record = self.createElement("record")
        self.collection.appendChild(self.record)

    def AddRecID(self, recid):
        self.id = self.createElement("controlfield")
        self.id.setAttribute("tag", "001")
        self.id.appendChild(self.createTextNode(str(recid)))
        self.record.appendChild(self.id)

    def AddKeywords(self, kwlst):
        for id in kwlst:
          self.datafield = self.createElement("datafield")
          self.datafield.setAttribute("tag", "650")
          self.datafield.setAttribute("ind1", " ")
          self.datafield.setAttribute("ind2", "7")
          for sf in id:
             self.sf = self.createElement('subfield')
             self.sf.setAttribute("code", sf)
             self.sf.appendChild(self.createTextNode(id[sf]))
             self.datafield.appendChild(self.sf)
          self.record.appendChild(self.datafield)

    def AddIDlst(self, idlst, reclst):
        for id in idlst:
          self.datafield = self.createElement("datafield")
          self.datafield.setAttribute("tag", "024")
          self.datafield.setAttribute("ind1", "7")
          self.datafield.setAttribute("ind2", " ")
          for sf in id:
             self.sf = self.createElement('subfield')
             self.sf.setAttribute("code", sf)
             self.sf.appendChild(self.createTextNode(id[sf]))
             self.datafield.appendChild(self.sf)
          self.record.appendChild(self.datafield)
        for id in reclst:
          try:
            if id['9'] == 'arXiv':
              self.datafield = self.createElement("datafield")
              self.datafield.setAttribute("tag", "024")
              self.datafield.setAttribute("ind1", "7")
              self.datafield.setAttribute("ind2", " ")

              self.sf = self.createElement('subfield')
              self.sf.setAttribute("code", "a")
              self.sf.appendChild(self.createTextNode('arXiv:' + id['a']))
              self.datafield.appendChild(self.sf)
              self.sf = self.createElement('subfield')
              self.sf.setAttribute("code", "2")
              self.sf.appendChild(self.createTextNode(id['9']))
              self.datafield.appendChild(self.sf)
              self.record.appendChild(self.datafield)
          except:
              pass
              # self.datafield = self.createElement("datafield")
              # self.datafield.setAttribute("tag", "024")
              # self.datafield.setAttribute("ind1", "7")
              # self.datafield.setAttribute("ind2", " ")
              # for sf in id:
              #    print sf
              #    self.sf = self.createElement('subfield')
              #    self.sf.setAttribute("code", sf)
              #    self.sf.appendChild(self.createTextNode(id[sf]))
              #    self.datafield.appendChild(self.sf)
              # self.record.appendChild(self.datafield)


def GetFieldVals(fieldlst):
  retlist = []
  for aufields in fieldlst:
    hash = {}
    for au in aufields[0]:
       sf  = au[0]
       val = au[1]
       hash[sf] = val
    retlist.append(hash)
  return retlist

if __name__ == '__main__':
  query  = querypar + '10.1016/j.physletb.2006.11.038'


  # '10.1142/S0217751X07035756'
  # '10.1103/PhysRevLett.100.113001'
  # '10.1016/j.physletb.2006.11.038'

  search = baseurl + '?' + query + '&' + format

  response = urllib2.urlopen(search)
  xml = response.read()

  rec = create_record(xml)
  
  print len(rec)
  print rec
  if len(rec) == 3:
     # we have one answer, so all values are in rec[0]
     r = rec[0]
     recid = 5;

     data = {}
     try:
        data['AB'] = record_get_field_values(r, '520', code='a')[0]
     except:
      pass
     au1        = record_get_field_instances(rec[0], tag='100', ind1=' ', ind2=' ')
     au7        = record_get_field_instances(rec[0], tag='700', ind1=' ', ind2=' ')
     ids        = record_get_field_instances(rec[0], tag='024', ind1='7', ind2=' ')
     keywords   = record_get_field_instances(rec[0], tag='695', ind1=' ', ind2=' ')
     repnos     = record_get_field_instances(rec[0], tag='037', ind1=' ', ind2=' ')

     firstau = GetFieldVals(au1)
     aulst   = GetFieldVals(au7)
     idlst  = GetFieldVals(ids)
     kwlst  = GetFieldVals(keywords)
     replst = GetFieldVals(repnos)

     print firstau
     print aulst
     print idlst
     print replst
     print kwlst
     print data


     newxml = RecXML()
     newxml.AddRecID(recid)
     newxml.AddIDlst(idlst, replst)
     newxml.AddKeywords(kwlst)
     print newxml.toprettyxml()
  else:
    print "no unique match."
