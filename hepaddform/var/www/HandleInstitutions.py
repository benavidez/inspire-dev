#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
try:
    import json
except ImportError:
    import simplejson as json

from invenio.config import \
    CFG_ACCESS_CONTROL_LEVEL_SITE, \
    CFG_SITE_LANG, \
    CFG_SITE_NAME, \
    CFG_SITE_URL, \
    CFG_SITE_NAME_INTL, \
    CFG_WEBSTYLE_TEMPLATE_SKIN
from invenio.bibformat_engine import BibFormatObject
from invenio.dbquery import run_sql
from invenio.webpage import page
from invenio.webuser import getUid, page_not_authorized
from invenio.messages import wash_language, gettext_set_language
from invenio.urlutils import redirect_to_url
from invenio.bibformat_elements import bfe_title
from invenio.websubmit_functions.Create_hgf_record_json import washJSONinput
from invenio.bibknowledge import get_kbd_values
from invenio.search_engine import \
    perform_request_search, \
    print_record, \
    print_records



#----------------------------------------------------------------------
# Build ip the Instituions subfield from alltops using a given
# persID and persNo (usually 1001_$0 and 1001_$b) and return the
# top_level_insts as list + the extlabel for labeling the external
# institutes in the overall label of the person in question
#----------------------------------------------------------------------
def BuildInstitutionsSubfield (alltops, persID='1', persNo='0', tag='9101_'):
    """ comment goes here """

    top_level_insts = []
    extlabel      = ''
    for id in alltops:
        #rec = perform_request_search(p='035__a:'+id, cc='Institutes')
        rec = perform_request_search(cc='Institutes')
        for r in rec:
            subrec = {}
            bfo = BibFormatObject(r)
            name = bfe_title.format_element(bfo) #bfo.field('1101_a')
            aliases = bfo.fields('4101_')
            shortcut = ''
            for alias in aliases:
                if 'w' in alias:
                    if alias['w'] == 'd':
                        shortcut = alias['a']
            subrec['6'] = persID
            subrec['b'] = persNo
            subrec['0'] = id
            subrec['a'] = name
            subrec['k'] = shortcut
            subrec['label'] = shortcut + ": " + name
            extlabel = extlabel + shortcut + ", "
            top_level_insts.append(subrec)
    extlabel = re.sub(', $', '', extlabel)
    return(top_level_insts, extlabel)

def IdentifyInstitutions(personid, ordno, input):
    """ comment goes here """

    dta  = {}
    todo = []
    # effectively, we want to have all top level entries from
    # the Institution collection here, as HandleNames already evaluates
    # the authors associations.
    #rec = perform_request_search(cc='Institution') eb
    rec = get_kbd_values('InstitutionsCollection', input)
    for rec in rec:
        subrec = {}
        #bfo = BibFormatObject(r)
        subrec['a'] =  rec #bfe_title.format_element(bfo)
        subrec['label'] =  rec #bfe_title.format_element(bfo)
        todo.append(subrec)

    dta['I9101_'] = todo
    return (json.dumps(dta, sort_keys=True, indent=2))


def index(req, personid, ordno, input, c=CFG_SITE_NAME, ln=CFG_SITE_LANG):
    """This interface should get parameters by URL and return names"""

    if req != None:
        uid = getUid(req)
        # names should be urlencoded! DO NOT USE ";" HERE.
        personid = str(req.form['personid'])
        ordno    = str(req.form['ordno'])
        input    = str(req.form['input'])

    result = IdentifyInstitutions(personid, ordno, input)
    return result


#if __name__ == '__main__':
#   personid= 'P:(DE-Juel1)133832'
#   ordno = 0
#   input = 'Meine schoene Uni Irgendwo'
#   input = 'Gau'
#   personid= 'P:(DE-HGF)0'
#   print IdentifyInstitutions(personid, ordno, input)
