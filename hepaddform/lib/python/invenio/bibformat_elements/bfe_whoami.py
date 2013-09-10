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
Try to get user info
@author: arwagner
"""
__revision__ = "$Id$"

def format_element(bfo, src):
    """
    Read the user info from the exposed dictionary and tell the user about it
    This is merely a demo on how to access session info
    """

    guest  = bfo.user_info['guest']
    uid    = bfo.user_info['uid']
    nick   = bfo.user_info['nickname']
    email  = bfo.user_info['email']
    groups = bfo.user_info['group']

    whoami = "You are: " + str(uid) + " = " + nick + " (" + email + ") "

    return whoami
