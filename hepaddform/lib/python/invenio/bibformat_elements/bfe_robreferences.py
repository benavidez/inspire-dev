# -*- coding: utf-8 -*-
##
## $Id$
##
## This file is part of Invenio.
## Copyright (C) 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2010 CERN, SLAC
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

"""BibFormat element - Prints references
"""
from invenio.search_engine import search_unit
from invenio.search_engine import search_unit_refersto
from invenio.search_engine import perform_request_search
from invenio.bibformat import format_record
import re
import string
regexp = re.compile(r"(?P<j>.+)?,(?P<v>.+)?,(?P<p>\d+)?")
volregex = re.compile(r"(?P<let>[A-Z])(?P<num>.*)")
ajs = {'Astrophys.J.Suppl.': 'ApJS', 'Astron.J.': 'AJ', 'Astropart.Phys.': 'APh', 'Astrophys.J.': 'ApJ', 'Astron.Astrophys.': 'A%26A', 'Mon.Not.Roy.Astron.Soc.': 'MNRAS', 'Acta Astron.': 'AcA', 'Acta Astron.Sin.': 'AcASn', 'Acta Astronaut.': 'AcAau', 'Acta Astrophys.Sin.': 'AcApS', 'Adv.Astron.Astrophys.': 'AdA&A', 'AIAA J.': 'AIAAJ', 'Amer.Astron.Soc.Meeting': 'AAS', 'Ann.Rev.Astron.Astrophys.': 'ARA&A', 'Annales Astrophys.': 'AnAp', 'Ark.Mat.Astron.Fys.': 'ArA', 'ASP Conf.Ser.': 'ASPC', 'Astrofiz.': 'Afz', 'Astron.Astrophys.Rev.': 'A&ARv', 'Astron.Astrophys.Suppl.Ser.': 'A&AS', 'Astron.Astrophys.Trans.': 'A&AT', 'Astron.Express': 'AExpr', 'Astron.Geophys.': 'A&G', 'Astron.Nachr.': 'AN', 'Astron.Rep.': 'ARep', 'Astron.Zh.': 'AZh', 'Astrophys.Bull.': 'AstBu', 'Astrophys.Lett.': 'ApL', 'Astrophys.Lett.Commun.': 'ApL&C', 'Astrophys.Nor.': 'ApNr', 'Astrophys.Space Sci.': 'Ap&SS', 'Astrophysics': 'Ap', 'Baltic Astron.': 'BaltA', 'Bol.A.A.Astron.': 'BAAA', 'Bull.Astron.Soc.India': 'BASI', 'Celestial Mech.': 'CeMDA', 'Chin.Astron.Astrophys.': 'ChA&A', 'Comments Astrophys.': 'ComAp', 'Exper.Astron.': 'ExA', 'Geophys.Astrophys.Fluid Dynamics': 'GApFD', 'Highlights Astron.': 'HiA', 'IAU Circ.': 'IAUC', 'IAU Symp.': 'IAUS', 'Irish Astron.J.': 'IrAJ', 'J.Astronaut.Sci.': 'JAnSc', 'J.Astrophys.Astron.': 'JApA', 'J.Hist.Astron.': 'JHA', 'J.Korean Astron.Soc.': 'JKAS', 'J.Roy.Astron.Soc.Canada': 'JRASC', 'Mem.Roy.Astron.Soc.': 'MmRAS', 'Mem.Soc.Ast.It.': 'MmSAI', 'Nauchnye Inform.Astron.Sov.Akad Nauk SSR': 'NInfo', 'New Astron.': 'NewA', 'Proc.Astron.Soc.Austral.': 'PASAu', 'Publ.Astron.Soc.Austral.': 'PASA', 'Publ.Astron.Soc.Jap.': 'PASJ', 'Publ.Astron.Soc.Pac.': 'PASP', 'Publ.Dominion Astrophys.Obs.': 'PDO', 'Q.J.Roy.Astron.Soc.': 'QJRAS', 'Rev.Mex.Astron.Astrof.Ser.Conf.': 'RMxAC', 'Rev.Mex.Astron.Astrofis.': 'RMxAA', 'Rev.Mod.Astron.': 'RvMA', 'Serb.Astron.J.': 'SerAJ', 'Sov.Astron.': 'SvA', 'Vistas Astron.': 'VA'}
##  python stuff:   

##    p=recid:1188034     str(len(search_unit_refersto('recid' + ':' + hits[0])))

##  hits = ['1234']
##  from invenio.search_engine import search_unit_refersto
##  print str(len(search_unit_refersto('recid' + ':' + hits[0])))

##  from invenio.search_engine import perform_request_search
##  print str(len(perform_request_search(p="999C5:'Proc.Am.Math.Soc.,113,11'")))
##  clean_journal = 'Proc.Am.Math.Soc.,113,11'
##  x = '999C5:' + clean_journal
##  print str(len(perform_request_search(p=x)))


def format_element(bfo, reference_prefix, reference_suffix):
    """
    Prints the references of this record

    @param reference_prefix a prefix displayed before each reference
    @param reference_suffix a suffix displayed after each reference
    """
    references = bfo.fields("999C5", escape=1, repeatable_subfields_p=True)

    out = ""
    last_o = ""

    if not references:
        return out

    out += "<table>"
    for reference in references:
        ref_out = []
        ref_out.append('<tr><td valign="top">')

        display_journal = ''
        display_report = ''
        clean_report = ''
        clean_journal = ''
        hits = []
        if reference.has_key('o') and not reference['o'][0] == last_o:
            temp_ref = reference['o'][0].replace('.', '')
            if '[' in temp_ref and ']' in temp_ref:
                ref_out.append("<small>" + temp_ref + "</small> ")
            else:
                ref_out.append("<small>[" + temp_ref + "] </small> ")
            last_o = temp_ref
        ref_out.append("</td><td>")

        if reference_prefix:
            ref_out.append(reference_prefix)
        if reference.has_key('s'):
            display_journal = reference['s'][0]
            clean_journal = reference['s'][0]
        if reference.has_key('r'):
            if "[" in reference['r'][0] and "]" in reference['r'][0]:
                breaknum = reference['r'][0].find('[')
                newreference = reference['r'][0][:breaknum].strip()
                display_report = newreference
                clean_report = newreference
            else:
                display_report = reference['r'][0]
                clean_report = reference['r'][0]
        #if reference.has_key('s') and reference.has_key('r'):
            
        if clean_report:
            hits = search_unit(f='reportnumber', p=clean_report)
        if clean_journal and len(hits)!=1:
            hits = search_unit(f='journal', p=clean_journal)
        if reference.has_key('a') and len(hits)!=1:
            hits = search_unit(f='doi', p=reference['a'][0])
        if len(hits) == 1:
            refersto_rec = str(list(hits)[0])
##            ref_out.append('whats in refersto_rec: ' + str(refersto_rec) + 'real stuff: ')
            c_count = str(len(search_unit_refersto('recid' + ':' + refersto_rec)))
            ref_out.append('<small>' + format_record(list(hits)[0],'hs2') + '  [' + "<a href=\"/search?ln=en&amp;p=refersto%3Arecid%3A" + refersto_rec + "\">" + c_count + "</a>"  + ' citations in HEP]</small>')
            ## + '[' + str(len(search_unit_refersto('recid' + ':' + c_count))) + ' citations in HEP]' + '</small>')
        else:

            if reference.has_key('a'):
                ref_out.append("<small> <a href=\"http://dx.doi.org/" + reference['a'][0] + "\">" + reference['a'][0]+ "</a></small>")
            if reference.has_key('h'):
                ref_out.append("<small> " + reference['h'][0] + ",</small>")
            if reference.has_key('t'):
                ref_out.append("<small> " + reference['t'][0] + "</small> -")
            if reference.has_key('p'):
                ref_out.append("<small> " + reference['p'][0] + ".</small>")
            if reference.has_key('y'):
                ref_out.append("<small> " + reference['y'][0] + ".</small>")
            if reference.has_key('m'):
                ref_out.append("<small> "+ reference['m'][0].replace(']]', ']') + ".</small>")

            if reference.has_key('u'):
                ref_out.append("<small> <a href=" + reference['u'][0] + ">" + \
                reference['u'][0] + "</a></small>")
            if reference.has_key('i'):
                for r in reference['i']:
                    ref_out.append("<small> <a href=\"/search?ln=en&amp;p=020__a%3A"+r+"\">"+r+"</a></small>")
            ref_out.append('<small>')

            if display_journal:
                search_arg = '999C5:' + clean_journal
                c_count = str(len(perform_request_search(p=search_arg)))
                ref_out.append(display_journal)
                ref_out.append('  [' + "<a href=\"/search?ln=en&amp;p=fin" + "+" + "c" + "+" + clean_journal + "\">" + c_count + "</a>" + ' citations in HEP]')
                jname = regexp.search(clean_journal)
                jn = str(jname.group('j'))
                vol = str(jname.group('v'))
                pp  = str(jname.group('p'))
                if ajs.has_key(jn):
                    ads_name = str(ajs[jn])
                    ref_out.append('  [' + "<a href=\"http://adsabs.harvard.edu/cgi-bin/nph-abs_connect?bibstem=" + ads_name + "&amp;volume=" + vol + "&amp;page=" + pp + "\">" + 'ADS' + "</a>" + ']')
                if re.search("^Phys\.Rev\.$", jn) or re.search("^Phys\.Rev\.Lett\.$", jn) or re.search("$Rev\.Mod\.Phys\.$", jn):
                    letnum = volregex.search(vol)
                    apsjn = jn.replace('.','')                        
                    if letnum:
                        l = letnum.group('let')
                        n = letnum.group('num')
                        ref_out.append('  [' + "<a href=\"http://dx.doi.org/10.1103/" + apsjn + l + '.' + n + '.' + pp + "\">" + 'DOI' + "</a>" + ']')
                    else:
                        ref_out.append('  [' + "<a href=\"http://dx.doi.org/10.1103/" + apsjn + '.' + vol + '.' + pp + "\">" + 'DOI' + "</a>" + ']')
                else:
                    letnum = volregex.search(vol)
                    if letnum:
                        l = letnum.group('let')
                        n = letnum.group('num')
                        ref_out.append('  [' + "<a href=\"http://crossref.org/guestquery/?title=" + str(jn) + l + "&amp;volume=" + n + "&amp;page=" + pp + "\">" + 'CrossRef' + "</a>" + ']')
                    else:
                        ref_out.append('  [' + "<a href=\"http://crossref.org/guestquery/?title=" + str(jn) + "&amp;volume=" + vol + "&amp;page=" + pp + "\">" + 'CrossRef' + "</a>" + ']')

            if display_report:
                ref_out.append(' ' + display_report)
                if not display_journal:
                   search_arg = '999C5:' + clean_report
                   c_count = str(len(perform_request_search(p=search_arg)))
                   ref_out.append('  [' + "<a href=\"/search?ln=en&amp;p=fin" + "+" + "c" + "+" + clean_report + "\">" + c_count + "</a>" + ' citations in HEP]')
                if re.search("\d{4}\.\d{4}", clean_report) or re.search("\/\d{7}", clean_report): 
                   ref_out.append('  [' + "<a href=\"http://arxiv.org/abs/" + clean_report + "\">" + 'arXiv' + "</a>" + ']')
                else:
                   ref_out.append('  [' + "<a href=\"http://www.google.com/&#35;hl=en&amp;output=search&amp;sclient=psy-ab&amp;q=%22" + clean_report + "%22\">" + 'Google' + "</a>" + ']')
                   
            ref_out.append("</small>")
        if reference_suffix:
            ref_out.append(reference_suffix)
        ref_out.append("</td></tr>")
        out += ' '.join(ref_out)

    return out + "</table>"

#if re.search("^[A-Z].*", vol):

# we know the argument is unused, thanks
# pylint: disable-msg=W0613
def escape_values(bfo):
    """
    Called by BibFormat in order to check if output of this element
    should be escaped.
    """
    return 0
# pylint: enable-msg=W0613
