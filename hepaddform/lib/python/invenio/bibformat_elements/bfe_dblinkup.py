# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2012, HGF
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
"""
Construct links to external databases to facilitate further
research.
@author: arwagner
"""
__revision__ = "$Id$"

try:
   from invenio.config import CFG_WOS_ARTICLE
except:
  pass
try:
   from invenio.config import CFG_WOS_CITING
except:
  pass
try:
   from invenio.config import CFG_WOS_RELATED
except:
  pass
try:
   from invenio.config import CFG_PUBMED
except:
  pass
try:
   from invenio.config import CFG_PMC
except:
  pass
try:
   from invenio.config import CFG_INSPEC
except:
  pass

def format_element(bfo, src, separator='; '):
    """
    Construct links to external databases to facilitate further
    research.
    This module requires several base URLs to be set in invenio.conf
      CFG_WOS_ARTICLE
      CFG_WOS_CITING
      CFG_WOS_RELATED
      CFG_PUBMED
      CFG_PMC
      CFG_INSPEC
    """

    # get an array of hashes for the identifier fields

    imgOA      = "http://upload.wikimedia.org/wikipedia/commons/5/57/Oa_80x15_orange.png"
    extid = bfo.fields('0247_')

    res = ''
    links = []
    for i in extid:
      if '2' in i:
         if (i['2'] == 'ISI') or (i['2'] == 'WOS'):
           id = i['a']
           try:
              link = '<br/><a href="' + CFG_WOS_ARTICLE + '&KeyUT=' + id + '">Web of Science (WOS)</a>'
              links.append(link)
           except:
              pass
           try:
              link = '<a href="' + CFG_WOS_CITING  + '&KeyUT=' +  id + '">Citing articles (WOS)</a>'
              links.append(link)
           except:
              pass
           try:
              link = '<a href="' + CFG_WOS_RELATED + '&KeyUT=' + id + '">Related articles (WOS)</a><br/>'
              links.append(link)
           except:
              pass
         if i['2'] == 'pmid':
           id = i['a'].replace('pmid:', '')
           try:
              link = '<a href="' + CFG_PUBMED + id + '">Pubmed</a>'
              links.append(link)
           except:
              pass
         if i['2'] == 'arXiv':
           id = i['a'].replace('arXiv:', 'http://arxiv.org/abs/')
           try:
              link = '<a href="' + id + '">'
              link = link + '<img src="' + imgOA + '"alt=OpenAcces by arXiv.org">'
              link = link + ' arXiv.org Fulltext</a>'
              links.append(link)
           except:
              pass
         if i['2'] == 'pmc':
           id = i['a'].replace('pmc:', '')
           try:
              link = '<a href="' + CFG_PMC + id + '">'
              link = link + '<img src="' + imgOA + '"alt=OpenAcces by Pubmed Central">'
              link = link + ' Pubmed Central Fulltext</a>'
              links.append(link)
           except:
              pass
         if i['2'] == 'inh':
           id = i['a'].replace('inh:', '')
           try:
              link = '<a href="' + CFG_INSPEC + '&AN=' + id + '">Inspec</a>'
              links.append(link)
           except:
              pass

    return separator.join(links)

def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0
