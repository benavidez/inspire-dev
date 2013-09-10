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
Format RSS links from journal records properly
@author: arwagner
"""
__revision__ = "$Id$"

def format_element(bfo, style, separator='; '):
    """
    Format RSS links from journal records properly
    856 72 $u is the URL
    856 72 $x publisher supplied text
    856 72 $y display text
    @param separator: the separator between urls.
    @param style: CSS class of the link
    """
    rssimg = "/img/feed-icon-12x12.gif"

    urls_u  = bfo.fields("85672u")
    lnk     = bfo.fields("85672y")
    org     = bfo.fields("85672x")
    if style != "":
        style = 'class="'+style+'"'
    else:
        style = 'class="rssLink"'

    urls = []
    i    = 0
    for url in urls_u:
        publ = "RSS feed"
        try:
          publ = org[i]
        except:
          pass
        urls.append( '<a '+ style + 'href="' + url + '" title="' + publ + '">' + \
                    lnk[i] + '<img src="' + rssimg + '" title="' + publ + '">' + '</a>')
        i += 1

    return separator.join(urls)

def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0
