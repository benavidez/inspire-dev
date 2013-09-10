# -*- coding: utf-8 -*-
## This file is part of the extensions of Invenio for the HGF collaboration
##
## Provides function Make_HGF_Record()for use in WebSubmit module of Invenio
## for HGF submit masks to create MARCXML file "recmysql" to be uploaded by
## following functions.

import os
import re
try:
    import json
except ImportError:
    import simplejson as json

from invenio.textutils import wash_for_xml
#from invenio.websubmit_functions.MarcXML_hgf import MarcXMLDocument
from MarcXML_hgf import MarcXMLDocument


def getMarcTagII(fieldcode):
    """Extract marc tag and indicators from fieldcode string 'nnnij'

    Returns: Tuple (marc tag nnn, indicator i, indicator j)
    """
    mtag = fieldcode[0:3]
    ind1 = fieldcode [3]
    if ind1 == '_':
        ind1 = ""
    ind2 = fieldcode[4]
    if ind2 == '_':
        ind2 = ""
    return (mtag, ind1, ind2)


def washXMLcontrols(fieldtext):
    """First wash input with invenio.textutils.wash_for_xml()

    Then turn XML controls into respective characters
    i.e. turn &amp; into & , &lt; into < , &gt; into > and  &quot; into "

    Escaping is done afterwards in MarcXMLDocument (xml.dom.minidom)
    """

    fieldtext = wash_for_xml(fieldtext)

    fieldtext = fieldtext.replace("&amp;","&")
    fieldtext = fieldtext.replace("&lt;","<")
    fieldtext = fieldtext.replace("&gt;",">")
    fieldtext = fieldtext.replace("&quot;",'"')

    return fieldtext


def get_sfdictutf8(sfdict):
    """Transform dictionary consisting of unicode strings into dictionary
    consisting of utf8-encoded strings and washes XML control characters
    """
    sfdictutf8 = {}
    for key in sfdict:
        sfdictutf8[unicode(key).encode('utf8')] = washXMLcontrols(
                unicode(sfdict[key]).encode('utf8'))
    return sfdictutf8


def processJSfile(filename, curdir):
    """Process file containing a Marc record in JSON structure or a list of
    Marc records in JSON structure

    Returns: List of tuples containing Marc fields of record
    """

    pn = os.path.join(curdir, filename)
    frec = open(pn, "r")
    inputdata = json.load(frec, 'utf8')
    frec.close

    # If file contains dictionary of single record transform it into list
    if isinstance(inputdata, dict):
        recordlist = [inputdata]
    else:
        recordlist = inputdata

    records = []

    for recorddict in recordlist:

        rec = []

        for key in recorddict:
            fieldcode = key.encode('utf8')
            if len(fieldcode) == 3:
                # For controlfields: append tuple (Marc tag, value)
                mtag = fieldcode
                value = washXMLcontrols(recorddict[key].encode('utf8'))
                rec.append((mtag, value))

            else:
                # For datafields: append tuple
                # (Marc tag, indicator 1, indicator 2, dictionary of subfields)
                mtag, ind1, ind2 = getMarcTagII(fieldcode)
                fieldlist = recorddict[key]
                for sfdict in fieldlist:
                    rec.append((mtag, ind1, ind2, get_sfdictutf8(sfdict)))

        # Sort Tuples in record only according to first entry = Marc tag
        rec = sorted(rec, key = lambda x: int(x[0]))

        records.append(rec)

    return records


def Make_HGF_Record(parameters, curdir, form=None, user_info=None):
    """Function for use in WebSubmit module of Invenio for HGF submit masks
    to create MARCXML file "recmysql" to be uploaded by following functions.

    Arguments are defined analogously to original Make_Record() function.
    Only "curdir" (= directory where data is stored) is actually used.

    This function expects the data in "curdir" in files named
       hgf_record: JSON structure of a main record
       hgf_master: JSON structure of a master record (if present)
    Other files in curdir are not processed.
    """

    # Define JS file names for main record and master record
    mainrecordjsfile = 'hgf_record'
    masterrecordjsfile = 'hgf_master'

    # Initialize list for master record: default: no master record
    masterrecord = None

    # Initialize MarcXML object for record(s)
    xmldoc = MarcXMLDocument()

    # Create list of main record by reading and processing main record JS file
    record = processJSfile(mainrecordjsfile, curdir)

    # If masterrecordjsfile in curdir
    if masterrecordjsfile in os.listdir(curdir):
        # Create list of master record by reading and processing
        # master record JS file
        masterrecords = processJSfile(masterrecordjsfile, curdir)
        # Insert main record and master record into MarcXML object
        xmldoc.insertData(record + masterrecords)

    else:
        # Insert main record into MarcXML object
        xmldoc.insertData(record)

    # Write MarcXML object to file "recmysql" in curdir
    filename = os.path.join(curdir, 'recmysql')
    outputxmlfile = open(filename, 'w')
    xmldoc.writexml(outputxmlfile, encoding="UTF-8")
    outputxmlfile.close()

    return ""


if __name__ == '__main__':
    curdir = (
    '/cdsware/invenio/var/data/submit/storage/running/journal/1344927845_32337')
    Make_HGF_Record(None, curdir)
