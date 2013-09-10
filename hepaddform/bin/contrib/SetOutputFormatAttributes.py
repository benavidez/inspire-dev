#!/usr/bin/env python
#=========================================================================
#
#    SetOutputFormatAttributes.py
#
#    Output formats that do not return HTML need their content/type to 
#    be set explicitly. Unlike format templates this needs to be done
#    by setting several values on the database instead of embedded in 
#    the respective file.
#   
#    Therefore, work through all files in the output_formats folder and 
#    set it's content type. To ease up things a naming convention is
#    implemented.
#
#     Nameing convention:
#     - JS*.bfo   : JSON output formats           => content type = text/plain
#     - ZZ*.bfo   : automatic dump output formats => content type = text/plain
#     - T*.bfo    : general Text output           => content type = text/plain
#
#    $Id: $
#    Last change: <Mo, 2011/09/26 22:32:53  ZB0063>
#    Author     : Alexander Wagner
#    Language   : Python
#
#-------------------------------------------------------------------------
#
#    Copyright (C) 2011 by Alexander Wagner
#
#    This is free software; you can redistribute it and/or modify it
#    under the terms of the GNU Genereal Public License as published
#    by the Free Software Foundation; either version 2, or (at your
#    option) any later version.
#
#    This program is distributed in the hope that it will be usefull,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
#    General Public License for more details.
#
#    You should have recieved a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
#
#=========================================================================

import sys
import os
import re

# import getter and setter from bibformat_dblayer as this allows
# for individual elements to be set. 'code' just refers to the file
# name without extension (ie. the code passed on the URL.)
from invenio.bibformat_dblayer import   \
    set_output_format_description,  \
    set_output_format_content_type, \
    set_output_format_visibility,   \
    set_output_format_name,         \
    get_output_format_content_type, \
        get_output_format_description,  \
        get_output_format_id,           \
    get_output_format_names

bfopath = "etc/bibformat/output_formats"

files = os.listdir(bfopath)

for file in files:
    if os.path.isdir(file) : continue
    code = file.replace(".bfo", "")
    description = ""

    if (file[0] == "Z") and (file[1] == "Z") : 
        print "ZZ : " + code
        content_type = "text/plain"
        description  = "Text export for automatic processing"
        set_output_format_description(code, description)
        set_output_format_content_type(code, content_type)
        set_output_format_name(code, code, lang="generic")
    if (file[0] == "J") and (file[1] == "S") : 
        print "JS : " + code
        content_type = "text/plain"
        description  = "JSON like structure for Web applications"
        set_output_format_description(code, description)
        set_output_format_content_type(code, content_type)
        set_output_format_name(code, code, lang="generic")
    if (file[0] == "T") :
        print "T_ : " + code 
        content_type = "text/plain"
        description  = "Text export for automatic processing"
        set_output_format_description(code, description)
        set_output_format_content_type(code, content_type)
        set_output_format_name(code, code, lang="generic")

## print get_output_format_names(code)
## 
## set_output_format_description(code, description)
## set_output_format_content_type(code, content_type)
## set_output_format_visibility(code, visibility)
## set_output_format_name(code, name, lang="generic")
## 
## print get_output_format_content_type(code)
## print get_output_format_description(code)
## print get_output_format_id(code)
## print get_output_format_names(code)
