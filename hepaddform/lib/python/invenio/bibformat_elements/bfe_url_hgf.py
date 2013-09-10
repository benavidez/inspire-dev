# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010 CERN.
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
This is the default format for formatting full-text URLs.
It takes 856 subfield $u as target and display $y as visible text
for the URL.
@author: arwagner
"""
__revision__ = "$Id$"

def format_element(bfo, style, separator='; '):
    """
    This is the default format for formatting full-text URLs.
    It takes 856 subfield $u as target and display $y as visible text
    for the URL.
    @param separator: the separator between urls.
    @param style: CSS class of the link
    """

    urls_u = bfo.fields("8564_u")
    lnk    = bfo.fields("8564_y")
    if style != "":
        style = 'class="'+style+'"'

    urls = []
    i    = 0
    for url in urls_u:
        publ = url
        try:
          publ = lnk[i]
        except:
          pass
        urls.append( '<a '+ style + 'href="' + url + '" title="' + publ + '">' + lnk[i] + '</a>')
        i += 1

    return separator.join(urls)

    return separator.join(urls)

def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0
