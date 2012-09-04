## This file is part of Invenio.
## Copyright (C) 2011 CERN.
##
## Invenio is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## Invenio is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with Invenio; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

# pylint: disable=C0103
"""INSPIRE HEP Additions Form Handlers"""

import invenio.template
from invenio.bibtask import task_low_level_submission
from invenio.config import CFG_SITE_URL
from invenio.urlutils import redirect_to_url
from invenio.webinterface_handler import WebInterfaceDirectory
from invenio.bibtask import write_message
from invenio import bibcatalog


navtrail = (' <a class="navtrail" href=\"%s/inspire\">INSPIRE Utilities</a> '
            ) % CFG_SITE_URL


class WebInterfaceInspirePages(WebInterfaceDirectory):
    """Defines the set of /inspire pages."""

    _exports = ['', '/', 'hepadditions_submit','torefext']

    def __init__(self, recid=None):
        self.recid = recid

    def index(self, request):
        redirect_to_url(request, '%s' % CFG_SITE_URL)

    def torefext(self, request, form):
        ticketer = bibcatalog.BibCatalogSystemRT()
        recid = form.get('recid', '')
        content = 'recid: ' + recid + '\n\n' + form.get('refs', '')
        ticket_id = ticketer.ticket_submit(subject = 'Referece list', requestor = 'eduardob', text = 'Content: ', queue = 'Test', owner = '')

        if ticketer.ticket_comment(None, ticket_id, content) == None:
            write_message("Error: commenting on ticket %s failed." % (str(ticket_id)))
        return invenio.webpage.page(title = "To RefExtract " + str(ticket_id), body = 'Great! It was sent to RT...\n' + content, req=request)

    def hepadditions_submit(self, request, form):
        """Accept the hep additions form data"""

        marc_list = {}
        marc_list['abstract']        = '520__ $$a' 
        marc_list['author1']         = '100__ $$a' 
        marc_list['authorn']         = '700__ $$a' 
        marc_list['oai']             = '909CO $$o' 
        marc_list['citation']        = '999C5 $$s' 
        marc_list['conference']      = '111__ $$g' 
        marc_list['title']           = '245__ $$a' 
        marc_list['url']             = '8564_ $$u' 
        marc_list['completeDate']    = '269__ $$c' 
        marc_list['experiment']      = '693__ $$e' 
        marc_list['pages']           = '300__ $$a'
        marc_list['doi']             = '247__ $$2DOI$$a'
        marc_list['reference']       = '999c5 $$s'
        marc_list['dtype']           = '980__ $$a'
        tid = self._write_ticket('eduardob', 'eduardob', 'TESTING', marc_list, form)
        return invenio.webpage.page(title = "HEP Additions Form OK This is the title: " + str(tid),  
                body = 'The form seems to have gone fine. It hakks gone to a human reviewer and should appear online in a few days.',
                                        req = request)

    def __call__(self, req, form):
        """Redirect calls without final slash."""
        redirect_to_url(req, '%s/inspire/' % (CFG_SITE_URL))

    def _append_multiple_refs(self, form_dict, marc_dict):
        done = False
        i = 0    
        ret_str = ''
        while not done:
            i = i + 1        
            k = 'reference' + str(i)        
            if k in form_dict:
                if form_dict[k]:
                    ret_str = ret_str + marc_dict['reference'] + form_dict[k] + '\n'
            else:
                done = True

        return ret_str


    def _append_multiple_authors(self, form_dict, marc_dict):
        """Appends multiple authors. It concatenates last, first to create an author (2-n)"""
        done = False
        i = 1    
        ret_str = ''
        while not done:
            i = i + 1        
            last = 'last' + str(i)
            first = 'first' + str(i)        
            affiliation = 'affiliation' + str(i)        
            if last in form_dict and first in form_dict:
                if form_dict[last] and form_dict[first]:
                    ret_str = ret_str + marc_dict['authorn'] + form_dict[last] + ', ' + form_dict[first]
                    if form_dict[affiliation]:
                        ret_str += '$$u' + form_dict[affiliation] + '\n'
                    else:
                        ret_str += '\n' 
            else:
                done = True
        return ret_str
    
    def _write_ticket(self, user_email, user_name, user_comment, marc_list, form):
        ticketer = bibcatalog.BibCatalogSystemRT()
        marc_str = ''        
        #for key, value in sorted(form.iteritems(), key=lambda (k,v): (v,k)):                
        #if value:
        #all_keys = ''
        author0 = form.get('last1', '') + ', ' + form.get('first1', '') + '$$u' + form.get('affiliation1', '')
        for key in form:
            #all_keys += key + ', ' 
            value = form.get(key, '')
            if value and (marc_list.get(key, '') != ''):
                marc_str = marc_str + marc_list.get(key, '') + str(value)  + ' \n'     
        marc_str = marc_str + marc_list['author1'] + author0 + '\n'	
        marc_str = marc_str + self._append_multiple_authors(form, marc_list)    
        marc_str = marc_str + self._append_multiple_refs(form, marc_list)    
        #marc_str += '\n\n' + all_keys 
        ticket_id = ticketer.ticket_submit(subject = 'HEP Addition Submit', requestor = user_email, \
                text = 'Content: ', queue = 'Test', owner = '')

        if ticketer.ticket_comment(None, ticket_id, marc_str) == None:
            write_message("Error: commenting on ticket %s failed." % (str(ticket_id),))
        return ticket_id 
