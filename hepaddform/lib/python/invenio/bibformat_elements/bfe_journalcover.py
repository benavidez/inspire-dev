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
"""
Genearate an image link for the journal cover
@author: arwagner
"""
__revision__ = "$Id$"

import os.path
from invenio.config import \
    CFG_WEBDIR


def format_element(bfo, src="ZDBID", search="PERI:(DE-600)", replace="", subfield='2', tag='0247_', printfield='a', separator=' ; ', onlyfirst='yes'):
    """
    Genearate an image link for the journal cover

    @param src: value in subfield to select
    @param search: value to replace by replace argument
    @param replace: replacement value
    @param subfield: subfield to search for src
    @param tag: field to check for src. By default use 0247_ according to Marc
    @printfield: subfield to print
    @param separator: a separator between keywords
    """

    # get an array of hashes for the identifier fields

    imgpath = "/img/jcover/"
    noimg   = "NoCover.png"
    fields = bfo.fields(tag)
    ids    = []
    

    imgsrc  = imgpath + noimg

    for i in fields:
        if i[subfield] == src:
           id = i[printfield]
           id = id.replace(search, replace) 
           ids.append( id )

    if os.path.isfile(CFG_WEBDIR + imgpath + ids[0] + '.jpg'):
      imglnk = '<img src="/img/jcover/' + ids[0] + '.jpg">'
    else:
      imglnk = '<img src="' + imgsrc + '">'

    return imglnk

def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0
