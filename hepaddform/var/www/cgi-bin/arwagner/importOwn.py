#!/usr/bin/env python
# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2011, HGF
##
## CDS Invenio is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## CDS Invenio is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with CDS Invenio; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""
Allow importing data form an already existing record.
To this end we use the recid, fetch all data to a  bibformat object
and then expose those sensible fields as JSON. Then our usual GenMetadata.pl
should be able to handle it seemlessly and expose it to the frontend.
"""

import re
import sys

from invenio.bibformat_engine import BibFormatObject
import simplejson as json

recid = 108139
id = 'FZJ-2012-00307'

def GetRecord(recid):

   # TODO learn to detect a 037-Id and fetch it

   bfo = BibFormatObject(recid)

   fieldlist = [ '1001_', '7001_', '1112_', '260__', '773__', '536__', '9131_', '9201_', '041__', '082__' ]

   repfields = [ '7001_', '536__', '9131_', '9201_']
   authfields= [ '1001_', '7001_']

   res = {}

   authors = []
   authstr = ''
   for f in fieldlist:
     recval = bfo.fields(f)
     if f in authfields:
        if f == '1001_':
           authors.append(recval[0])
           authstr = recval[0]['a'] + ' [' + recval[0]['0'] + '] ; ' + authstr
        else:
           for a in recval:
             authstr += a['a'] + ' [' + a['0'] + ']' + ' ; '
             authors.append(a)
     else:
       if len(recval) > 0:
         if f == '260__':
           if 'a' in recval[0]:
             res['I'+f+'a'] = recval[0]['a']
           if 'b' in recval[0]:
             res['I'+f+'b'] = recval[0]['b']
           if 'c' in recval[0]:
             res['I'+f+'c'] = recval[0]['c']
         elif f == '773__':
           if '0' in recval[0]:
             res['I'+f+'0'] = recval[0]['0']
           if 't' in recval[0]:
             res['I'+f+'t'] = recval[0]['t']
           if 'x' in recval[0]:
             res['I'+f+'x'] = recval[0]['x']
         elif f == '1112_':
           for sf in recval[0]:
             if sf == 'd':
                res['I1112_dcs'] = re.sub(' - .*', '', recval[0][sf])
                res['I1112_dce'] = re.sub('.* - ', '', recval[0][sf])
             else:
                res['I1112_'+sf] = recval[0][sf]
         elif f == '041__':
             res['I'+f+'a'] = recval[0]['a']
         elif f == '082__':
             res['I'+f+'a'] = recval[0]['a']
         elif f in repfields:
           res['I'+f] = str(recval).replace("'", '"')
         else:
           res['I'+f] = recval[0]

   res['I1001_']  = str(authors).replace("'", '"')
   # The following doesn't really work well, all authors are red.
   res['I1001_a'] = authstr
   res['SHORTTITLE'] = 'Reusing data from record ' + str(recid)
   if bfo.field('037__a') != '':
    res['SHORTTITLE'] += ' (= ' + bfo.field('037__a') + ')'

   return(json.dumps(res, sort_keys=True, indent=2))

if __name__ == '__main__':
  recid = sys.argv[1]
  res = GetRecord(recid)
  print res
  #print res['records']

