## This file is part of Invenio.
## Copyright (C) 2004, 2005, 2006, 2007, 2008, 2010, 2011 CERN.
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

__revision__ = "$Id$"

def Print_hgf_Success(parameters, curdir, form, user_info=None):
    """
    This function simply displays a text on the screen, telling the
    user the submission went fine. To be used in the 'Submit New
    Record' action.

    Parameters:

       * status: Depending on the value of this parameter, the
         function adds an additional text to the email.
         This parameter can be one of:
           - ADDED: The file has been integrated in the database.
           - APPROVAL: The file has been sent for approval to a referee.
                       or can stay empty.

       * edsrn: Name of the file containing the reference of the
                document

       * newrnin: Name of the file containing the 2nd reference of the
                  document (if any)
    """
    return "<br />Thank you!"
