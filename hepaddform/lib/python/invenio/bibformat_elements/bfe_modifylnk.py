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
Generate a link to modify the record via MBI masks.
@author: arwagner
"""
__revision__ = "$Id$"

from invenio.bibformat_engine import BibFormatObject
from invenio.urlutils import create_html_link
from invenio.config import CFG_SITE_URL
from invenio.access_control_config import CFG_EXTERNAL_AUTH_DEFAULT

def format_element(bfo, style=''):
    """
    Read the user info from the exposed dictionary and construct a modify link in case
    suitable. Criteria are:
    User is Editor                                   user_info.groups['EDITOR']
    The record belongs to the institute of the user  920 = user_info.groups['anyone']
    The record is in USER collection                 980 $a USER
    The record is in MAIL collection                 980 $a MAIL
    """

    # We should allow modify, if:
    # - the user owns the record: 8650_f = email
    # - the user is in EDITORS
    #   AND
    #   the record belongs to a group the user belongs as well
    groups = bfo.user_info['group']
    email  = bfo.user_info['email']

    m037a          = bfo.fields('037__a')
    doctypes       = bfo.fields('3367_')
    doccollections = bfo.fields('980__a')
    recowner       = bfo.fields('8560_f')

    out = ''

    # we can only modify the record if it has a 037__a otherwise just
    # return an empty string.
    if len(m037a) > 0:

       doctype = ''

       # The doctype for modify should be 
       for docdef in doctypes:
         if 's' in docdef:
           doctype = docdef['m']

       if doctype == '':
          # We couldn not obtain the doctype, ie. the modify mask
          # responsible for this record => the user can not modify it,
          # and thus does not get the link.
          return ''

       marc037a     = m037a[0]

       sub     = "sub=MBI"+doctype
       recRN   = 'rn=' + marc037a
       step    = 'step=1'

       baseurl = CFG_SITE_URL + '/submit/direct'

       # Add a style if we get one passed as argument
       linkattrd = {}
       if style != '':
          linkattrd['style'] = style

       # If either one of the following gets true, we should add the
       # modify link and allow modification
       allowOwner = False
       allowEditor= False
       allowStaff = False

       for owner in recowner:
         if owner == email:
           allowOwner = True

       # If we are not owner we might have additional rights. However, it
       # is enough to be owner, so check this only in case we are not.
       #if allowOwner == False:
       for group in groups:
           # + 1 for EDITOR
           if group == 'STAFF':
              allowStaff = True
           if group == 'EDITORS':
              allowEditor = True

       # we are editor, now check if we are editor for the right group
       if allowEditor:
          # by default we are not
          allowEditor = False
          for col in doccollections:
             for group in groups:
                # we get a postfix from external auth, remove it if we
                # find it. It has always the same fixed form defined in
                # invenio src.
                grp = group.replace(' ['+CFG_EXTERNAL_AUTH_DEFAULT+']', '')
                if col == grp:
                   allowEditor = True
               
       if allowOwner or allowEditor or allowStaff:
          link = baseurl + '?' + sub + '&' + recRN + '&' + step
          out += create_html_link(link,
                 {},
                 link_label = "Modify This Record",
                 linkattrd=linkattrd)
    return out

def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0

def test_format(recID):
    """
    only for testing of format
    """
    bfo = BibFormatObject(recID)
    print format_element(bfo)
 
if __name__ == '__main__': 
    test_format(recID = 124552)
    test_format(recID = 10)

