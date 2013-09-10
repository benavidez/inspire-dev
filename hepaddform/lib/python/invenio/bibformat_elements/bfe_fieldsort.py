# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2012 HGF
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
Prints the given field of a record sorting descending by a given
subfield.
@author: arwagner
"""
__revision__ = "$Id$"

from invenio.bibformat_utils import parse_tag
from operator import itemgetter

# a = [{'a': 123, 'b': 456}, {'a': 123, 'b': 456}, {'a': 324, 'b': 357}, {'a': 243, 'b': 576}, {'a': 734, 'b': 657}, {'a': 234, 'b': 567}]
# newlist = sorted(a, key=itemgetter('b'), reversed=True)
# newlist = sorted(a, key=itemgetter('b'), reversed=False)

def format_element(bfo, tag, limit, sortfield, descending='True', instances_separator=" ",
           subfields_separator=" ", extension=""):
    """
    Prints the given field of a record sorting descending by a given
    subfield. If limit is set to 1 only the topmost entry is
    displayed. This format is meant to handle repeatable fields that
    may contain a datestamp, e.g. 371, sorted by $t limit = 1 gives
    only the most recent entry.

    @param tag: the tag code of the field that is to be printed
    @param sortfield: subfield used to sort returns
    @param descending: sort ascending (False=default) or descending (True)
    @param instances_separator: a separator between instances of field
    @param subfields_separator: a separator between subfields of an instance
    @param limit: the maximum number of values to display.
    @param extension: a text printed at the end if 'limit' has been exceeded
    """
    # Check if data or control field
    p_tag = parse_tag(tag)
    # Get values without subcode.
    # We will filter unneeded subcode later
    if p_tag[1] == '':
        p_tag[1] = '_'
    if p_tag[2] == '':
        p_tag[2] = '_'
    # Values will always be a list of dicts
    values = bfo.fields(p_tag[0]+p_tag[1]+p_tag[2]) 

    # sort the values by sortfield
    # After that we can apply the usual stuff as done in bfe_field
    # without any changes necessary.
    if descending == 'False':
      dir = False
    else:
      dir = True
    try:
       values = sorted(values, key=itemgetter(sortfield), reverse=dir) 
    except:
       # we have no sort field => no choice but leave it as it is...
       pass

    x = 0
    instances_out = [] # Retain each instance output
    sortfields    = []
    for instance in values:
      sortfields.append

    for instance in values:
        filtered_values = [value for (subcode, value) in instance.iteritems()
                          if p_tag[3] == '' or p_tag[3] == '%' \
                           or p_tag[3] == subcode]
        if len(filtered_values) > 0:
            # We have found some corresponding subcode(s)
            if limit.isdigit() and x + len(filtered_values) >= int(limit):
                # We are going to exceed the limit
                filtered_values = filtered_values[:int(limit)-x] # Takes only needed one
                if len(filtered_values) > 0: # do not append empty list!
                    instances_out.append(subfields_separator.join(filtered_values))
                    x += len(filtered_values) # record that so we know limit has been exceeded
                break # No need to go further
            else:
                instances_out.append(subfields_separator.join(filtered_values))
                x += len(filtered_values)

    ext_out = ''
    if limit.isdigit() and x > int(limit):
        ext_out = extension

    return instances_separator.join(instances_out) + ext_out
