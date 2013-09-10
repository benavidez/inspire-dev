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
Generate a correction request message for the current record. This
message is prefilled with metadata and preaddressed to group STAFF
@author: arwagner
"""
__revision__ = "$Id$"

from invenio.urlutils import create_html_link
from invenio.config import CFG_SITE_URL

def format_element(bfo, style):
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
    uid    = bfo.user_info['uid']
    groups = bfo.user_info['group']
    email  = bfo.user_info['email']


    recid          =  bfo.control_field('001')
    reclnk         = CFG_SITE_URL + '/record/' + recid
    recipient      = 'STAFF'
    subject        = 'Request+correction+for+record+' + str(recid)
    body           = 'Dear+sir+or+madame!%0A%0DPlease+correct+the+following+mistakes+in+record+' + reclnk + ':%0A%0D%0A%0D'

    linkattrd = {}
    if style != '':
       linkattrd['style'] = style

    baseurl = CFG_SITE_URL + '/yourmessages/write'
    #?msg_to_group=EDITORS&msg_subject=Change+request&msg_body=Test+body
    # perform_request_write(uid, msg_to='admin', msg_subject=subject, msg_body=body)

    link = baseurl + '?msg_to_group=' + recipient \
         + '&msg_subject=' + subject \
         + '&msg_body=' + body
    out = ''
    out += create_html_link(link,
              {},
              link_label = "Request correction",
              linkattrd=linkattrd)

    return out

def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0

