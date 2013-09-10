# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2011, HGF
##
## Invenio is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## Invenio is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with Invenio; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
"""BibFormat element - 
Print grant information in JSON structure.
We need to follow some immediate top-elements to add data.
@author: arwagner
"""
__revision__ = "$Id$"
from invenio.config import \
  CFG_SITE_LANG, \
  CFG_SITE_NAME, \
  CFG_IGNOREPREFIX
#from invenio.dbquery import run_sql
#from invenio.webpage import page
from invenio.webuser import collect_user_info
#from invenio.messages import wash_language, gettext_set_language
#from invenio.urlutils import redirect_to_url

from invenio.bibformat_engine import BibFormatObject
from invenio.search_engine import \
  perform_request_search, \
  print_record

from invenio.websubmit_functions.Create_hgf_record_json import washJSONinput

import re
try: import json
except ImportError: import simplejson as json

import urllib
## from urllib import quote, quote_plus
## from invenio.config import CFG_SITE_URL
## from invenio.urlutils import create_html_link

#----------------------------------------------------------------------
donerec = [] # Hold all ids we already found. Do not forget to empty
             # this list with del[:]
alreadyseen = {}
#----------------------------------------------------------------------
# Extract the $wt entries of topfield and return a list of their IDs
# from $0 subfield
#----------------------------------------------------------------------
def climbdown(id, searchfield='550__', idfield='0', collection='Grants', ignoretag=None, kwfield='751_7a'):

  # avoid climbing if we were already in the branch in question. This
  # could happen if our original query produces not only parents but
  # also a bunch of children we meet again. Avoiding to climb should
  # us give some time advantage.
  if id in alreadyseen:
     alreadyseen[id] += 1
  else:
     alreadyseen[id] = 1
     q = searchfield+ idfield +':"'+id+'" '
     rec = perform_request_search(p=q, cc=collection)
     if rec == []:
       donerec.append(id)
     for r in rec:
       bfo = BibFormatObject(r)
       linking  = bfo.fields(searchfield)
       recid    = bfo.field('035__a')
       # By default we process every record, but we need to keep the
       # ignore tags in mind: if a keyword substr matches the
       # ignoretag we should not consider this record an its siblings.
       process = True
       if (ignoretag != ''):
          keywords = bfo.fields(kwfield)
          for kw in keywords:
             if kw in ignoretag:
               process = False
       if process:
          for l in linking:
            # for a record to be a child of id, it has to have our id in $wt
            if 'w' in l:
               if (l['w'] == 't') and (l['0'] == id):
                  climbdown(recid, searchfield, idfield, collection, ignoretag, kwfield)

  return

#----------------------------------------------------------------------
# Do the actual climbing for all Ids in todo to reach their final
# top (ie the record that does not have any top anymore)
#----------------------------------------------------------------------
def climber(todo, searchfield='550__', idfield='0', collection='Grants', ignoretag=None, kwfield='751_7a'):
  allchildren = []

  for id in todo:
    climbdown(id, searchfield, idfield, collection, ignoretag, kwfield)

  # remove duplicates we might have accumulated and sort by
  # identifiers to get a nice listing
  allchildren = sorted(list(set(donerec)))
  return allchildren

def JSGetAllChildren(recID, climbfield='550__', idfield='0', collection='Grants', ignoretag=None, kwfield='751_7a'):
    """
    Fetch all children from bfo
    """

    todo        = []
    try:
        # if this succeeds we got a record id
        bfo   = BibFormatObject(int(recID))
        recid = bfo.field('035__a')
        todo.append(recid)
    except:
        # otherwise we got an identifier and have to resolve it to a
        # record id first.
        #recID = urllib.unquote(recID)
        recids = recID.split('|')
        for id in recids:
          todo.append(id)

    allchildren = []
    allchildren = climber(todo, climbfield, idfield, collection, ignoretag, kwfield)

    result = []
    for id in allchildren:
      rec = perform_request_search(p='035__a:"'+id+'"', cc=collection)

      try:
         # Invenio behaves a bit strange sometimes, e.g. if we
         # accidentially uploaded non-utf8 encoded xml
         js  = washJSONinput(print_record(rec[0], format='js'))
         result.append(json.loads(js))
      except:
        pass

    return json.dumps(result, sort_keys=True, indent=2)

def index(req, record, src, id, col, query=None, groups=None, grpfield='751_7a', c=CFG_SITE_NAME, ln=CFG_SITE_LANG):
    """
    This interface should get parameters by URL and return names
    """

    ignoreprefix = CFG_IGNOREPREFIX

    if req != None:
       record   = str(req.form['record'])
       src      = str(req.form['src'])
       id       = str(req.form['id'])
       col      = str(req.form['col'])
       grpfield = urllib.unquote(str(req.form['grpfield']))
       query    = urllib.unquote(str(req.form['query']))
       groups   = collect_user_info(req)['group']

       record = urllib.unquote(record)

    query = query.strip()

    # add a search term prefixed by CFG_IGNOREPREFIX and consisting of
    # all groups a user belongs ot, that will ommit all records that
    # contain this keyword in any field. This allows us to show a bit
    # more selectively.
    # 
    # Note: if a higher level collection sets this keyword, but the
    # query emmitted results in children that do NOT set the keyword,
    # they will still show up as we do not climb up first and then
    # down again.
    grplimit = ''
    if (groups != None) and (len(groups) > 0):
       grplimit = ' AND NOT ('
       for g in groups:
         grplimit += '"' + ignoreprefix + g + '"' + ' OR '

       grplimit = grplimit[:-4]

       grplimit += ')'

    # if we have a non-empty query use it to find the top level(s),
    # otherwise record should hold an id/record number

    if (query != None) and (query != ''):
       # Beware of invenios advanced search behaviours compared to
       # structured search query simple search. Especially mind the
       # quotes and the minor differences between "" and '' in simple
       # search...
       # NOTE there is some comment that this might change in
       # Invenio > 1.0!
       marctag = re.compile('^[0-9_]{5}[a-z0-9]{1}:')
       if (record != ''):
          if marctag.search(record) == None:
            # if we do not have a leading marc tag, which signifies to
            # search a specific subfield only, we quote record as string,
            # otherwise we leave it as it is.
            record = "'" + record + "'"

       q = ''
       if ((query  != None) and (query  != '')) and \
          ((record != None) and (record != '')):
          q = "'" + query + "' AND " + record
       else:
         if (query  != None) and (query  != ''):
           q = "'" + query + "'"
         if (record != None) and (record != ''):
           q = record

       if grplimit != '':
          q = '(' + q + ')' + grplimit

       rec = perform_request_search(p=q, cc=col)
       record = ''
       for r in rec:
         bfo   = BibFormatObject(r)
         recid = bfo.field('035__a')
         record += recid + '|'
       record = record[:-1]
    else:
       marctag = re.compile('^[0-9_]{5}[a-z0-9]{1}:')
       if marctag.search(record) != None:
          record = record[7:]
          # remove quoting and wildcarding. From tokeninput frontends
          # we can not rewrite the search url depending on user input,
          # so we might get a search for a IDs subrecords, but we have
          # empty user input...
          record = record.strip('"').strip('*')

    if (record != None) and (record != ''): 
       return JSGetAllChildren(record, src, id, col, grplimit, grpfield)
    else:
       return ''

if __name__ == '__main__': 
    grp = []
    grp.append("I:(DE-Juel1)ZB-20090406 [FZJ eMail-Account]") 
    grp.append("DESY [DESY]") 

    # print index(req=None, record='', query='Photo', src='550__', id='0', col='Grants')
    #print index(req=None, record='035__a:"G:(DE-HGF)POF2*"', query='', src='550__', id='0', col='Grants')
    #print index(req=None, record='035__a:"G:(DE-HGF)POF2*"', query='110', src='550__', id='0', col='Grants')
    #print index(req=None, record='', query='294810', src='550__', id='0', col='Grants')

    # print index(req=None, record='035__a:"G:(DE-HGF)POF2*"', query='thin',   groups=grp, grpfield='751_7a', src='550__', id='0', col='Grants')
    # print index(req=None, record='035__a:"G:(DE-HGF)POF2*"', query='energy', groups=grp, grpfield='751_7a', src='550__', id='0', col='Grants')
    # print index(req=None, record='035__a:"G:(DE-HGF)POF2*"', query='',       groups=grp, grpfield='751_7a', src='550__', id='0', col='Grants')
    # print index(req=None, record='035__a:"G:(DE-HGF)POF2*"', query='pof',    groups=grp, grpfield='751_7a', src='550__', id='0', col='Grants')
