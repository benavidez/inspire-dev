#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
import urllib
try: import json
except ImportError: import simplejson as json

from invenio.config import \
  CFG_ACCESS_CONTROL_LEVEL_SITE, \
  CFG_SITE_LANG, \
  CFG_SITE_NAME, \
  CFG_SITE_URL, \
  CFG_SITE_NAME_INTL, \
  CFG_WEBSTYLE_TEMPLATE_SKIN
from invenio.dbquery import run_sql
from invenio.webpage import page
from invenio.webuser import getUid, page_not_authorized
from invenio.messages import wash_language, gettext_set_language
from invenio.urlutils import redirect_to_url

# Remove some clutter that might appear in a JSON due to Invenios
# inability to add for "only first"/"only last" records in a return
# list
from invenio.websubmit_functions.Create_hgf_record_json import washJSONinput

from invenio.search_engine import \
  perform_request_search, \
  print_record, \
  print_records
from invenio.bibformat_engine import BibFormatObject

#----------------------------------------------------------------------
# Normalize the names passed to get Lastname, Firstname separated by
# <space>;<space>
#----------------------------------------------------------------------
def NormalizeName(name):

    # Strip off superflous spaces
    newname = re.sub("\s+", " ", name)
    newname = re.sub('"', "", newname)
    newname = newname.strip()

    # if we already have a , everything is in correct order...
    if newname.find(',') > 0:
        return(newname)

    # ...else we have to sort it out

    # Split at the . We will have to add it later again.  We might win
    # some spaces so we have to .strip() all strings in the resulting
    # array.
    if (newname.count('.')) > 0:
        nameparts = newname.split('.')
    else:
        nameparts = newname.split(' ')

    if len(nameparts) >= 1:
        # Lastname
        newname = nameparts[len(nameparts)-1].strip() + ', '
        # Append all surname initials in the order given
        # H. A. Schmidt should give Schmidt, H. A.
        for i in range(len(nameparts)-1):
            newname += nameparts[i].strip()
            if name.find('.') > 0:
                newname += '. '
            else:
                newname += ' '
    newname = newname.strip()

    return(newname)

#----------------------------------------------------------------------
# The name list might contain either ; or , as separator characters.
# If we find a ; we assume that the names are like
#    Lastname, Firstname ;  Lastname, Firstname
# otherwise we assume something like
#    F. Lastname, F. Lastname
# The first mode matches old FZJ input method, the second the former
# DESY input method. We treat both as suitable
#----------------------------------------------------------------------
def SplitNameList(namelist):
    if namelist.count(';') != 0:
        namelist = re.sub('\s?;\s?', ' ; ', namelist)
    else:
        if namelist.count(',') > 1:
            namelist = re.sub('\s?,\s?', ' ; ', namelist)

    # remove the last ; to avoid an empty entry
    namelist = re.sub('\s?;\s?$', '', namelist)
    entries = namelist.split(' ; ')

    order = 0
    names = []
    for e in entries:
        name         = ''
        id           = ''
        affiliation  = ''
        role         = ''

        p = re.compile('([^\[\{]*)\s?')
        name = p.findall(e)[0]
        name = NormalizeName(name)

        p = re.compile('[^[]*(\[[^\]]*\])?\s?')
        id = p.findall(e)[0]
        id = re.sub('\[', '', id)
        id = re.sub('\]', '', id)

        p = re.compile('[^\{]*(\{[^\}]*\})?')
        affiliation = p.findall(e)[0]
        affiliation = re.sub('\{', '', affiliation)
        affiliation = re.sub('\}', '', affiliation)

        # build a marc like structure:
        # - write only subfields that have a value
        # - handle everything as a string
        marcdta = {}
        if name.strip() != '':
            marcdta['a'] = name.strip()
        if id.strip() != '':
            marcdta['0'] = id.strip()
        if affiliation.strip() != '':
            marcdta['u'] = affiliation.strip()
        marcdta['b'] = str(order)

        names.append(marcdta)

        order += 1

    return names

#----------------------------------------------------------------------
donerec = [] # Hold all ids we already found. Do not forget to empty
             # this list with del[:]
#----------------------------------------------------------------------
# Extract the $wt entries of topfield and return a list of their IDs
# from $0 subfield
#----------------------------------------------------------------------
def climbup(id, topfield='5101_'):
    rec = perform_request_search(p='035__a:'+id, cc='Institutes')
    if rec in donerec:
        return []
    else:
        donerec.append(rec)
        for r in rec:
            bfo = BibFormatObject(r)
            try:
                tops  = bfo.fields(topfield)
                topid = []
                for top in tops:
                    if top['w'] == 't':
                        try:
                            topid.append(top['0'])
                        except:
                            # we should never end up here:
                            # we have no id to follow
                            donerec.append(rec)
                            return []
                return(topid)
            except:
                return(0)

#----------------------------------------------------------------------
# Do the actual climbing for all Ids in todo to reach their final
# top (ie the record that does not have any top anymore)
#----------------------------------------------------------------------
def climber(todo, topfield='5101_'):
    alltops = []
    mytodo  = todo

    for id in mytodo:
        newids = climbup(id, topfield)
        if newids == []:
            alltops.append(id)
        for id in newids:
            if not(id in todo):
                todo.append(id)
    return(alltops)

#----------------------------------------------------------------------
# Get the top level institutions and cound up MatchedInstitutes
#----------------------------------------------------------------------
def GetToplevels(dta, field, topfield):

    MatchedInstitutes = {}
    todo              = []
    alltops           = []

    jsfield = 'I' + field
    if jsfield in dta:
        todo = dta[jsfield].split('|')

    # empty our global
    del donerec[:]
    if todo != []:
        alltops = climber(todo, '5101_')

    for t in todo:
        if t in MatchedInstitutes:
            MatchedInstitutes[t] += 1
        else:
            MatchedInstitutes[t] = 1

    return(alltops, MatchedInstitutes)

#----------------------------------------------------------------------
# Build ip the Instituions subfield from alltops using a given
# persID and persNo (usually 1001_$0 and 1001_$b) and return the
# toplevelinsts as list + the extlabel for labeling the external
# institutes in the overall label of the person in question
#----------------------------------------------------------------------
def BuildInstitutionsSubfield (alltops, persID, persNo, tag='9101_'):
    toplevelinsts = []
    extlabel      = ''
    for id in alltops:
        rec = perform_request_search(p='035__a:'+id, cc='Institutes')
        for r in rec:
            subrec = {}
            bfo = BibFormatObject(r)
            name = bfo.field('1101_a')
            aliases = bfo.fields('4101_')
            shortcut = ''
            for alias in aliases:
                if 'w' in alias:
                    if alias['w'] == 'd':
                        shortcut = alias['a']
            subrec['6'] = persID
            subrec['b'] = str(persNo)
            subrec['0'] = id
            subrec['a'] = name
            subrec['k'] = shortcut
            subrec['label'] = shortcut + ": " + name
            extlabel = extlabel + shortcut + ", "
            toplevelinsts.append(subrec)
    extlabel = re.sub(', $', '', extlabel)
    return(toplevelinsts, extlabel)

#----------------------------------------------------------------------
# Build the label to be displayed from extlabel, inputname and several
# 37x subfields of the authority records in question if we have one.
#----------------------------------------------------------------------
def BuildLabel(inputname, extlabel, dta):

    label = inputname + ' -> ' + dta['I1001_a'].encode('utf-8', 'ignore')
    if (extlabel != '') or ('I371__m' in dta) or ('I317__c' in dta):
        label += ' ('
    if (extlabel != ''):
        label += extlabel
    if 'I371__m' in dta:
        label += ': ' + dta['I371__m'].encode('utf-8', 'ignore')

    if 'I371__c' in dta:
        label += ' / ' + dta['I371__c'].encode('utf-8', 'ignore')

    if (extlabel != '') or ('I371__m' in dta) or ('I317__c' in dta):
        label += ')'
    else:
        if 'I1001_0' in dta:
            if 'I1001_0' != 'P:(DE-HGF)0':
                label += ' [' + dta['I1001_0'].encode('utf-8', 'ignore') + ']'
            else:
                label += ' [Extern]'
    return(label)

#----------------------------------------------------------------------
# normalize and split the list of names into a python
# array of hashes with hash keys corresponding to marc tags
#----------------------------------------------------------------------
def IdentifyPeople(namelist, onlylast=False):
    names = SplitNameList(namelist)

    if onlylast:
        lastname = names[len(names)-1]
        names    = []
        names.append(lastname)

    result = {}
    Select = []
    Guess  = []

    MatchedInstitutes = {}
    mostlikelyinst    = ''

    for person in names:
        try:
            mostlikelyinst = sorted(MatchedInstitutes,
                key=MatchedInstitutes.get, reverse=True)[0]
        except:
            mostlikelyinst = ''
        select = []
        guess  = []

        # Check if we have an ID. If so we enrich data from our local
        # database. If the ID is the same as CFG_WEBSTYLE_TEMPLATE_SKIN
        # it is no real ID so we treat it by guessing.
        if ('0' in person) and \
            (person['0'].upper() != CFG_WEBSTYLE_TEMPLATE_SKIN.upper()):

            # Ask the database for the ID
            res = perform_request_search(p=person['0'], cc='People')
            if len(res) == 1:
                for r in res:
                    js = washJSONinput(print_record(r, format='js'))
                    dta = json.loads(js)
                    alltops = []  # all top level institute ids
                    todo    = []  # institutes to search for top level and add
                                # to counting for most likely

                    alltops, MatchedInstitutes = GetToplevels(dta,
                            '373__0', '5101_')

                    # Address information
                    todo = []
                    if 'I371__0' in dta:
                        todo = dta['I371__0'].split('|')

                    # counting institutes of this author to get
                    # the most likely one.
                    for t in todo:
                        if t in MatchedInstitutes:
                            MatchedInstitutes[t] += 1
                        else:
                            MatchedInstitutes[t] = 1
                    try:
                        mostlikelyinst = sorted(MatchedInstitutes,
                            key=MatchedInstitutes.get, reverse=True)[0]
                    except:
                        mostlikelyinst = ''

                    # remove empty Marc fields
                    dta['I9101_'], extlabel = BuildInstitutionsSubfield(alltops,
                            dta['I1001_0'], person['b'], '9101_')
                    dta['label'] = BuildLabel(person['a'], extlabel, dta)
                    todel = []
                    for k in dta:
                        if k == 'I373__0':
                            todel.append(k)
                        if k == 'I371__0':
                            todel.append(k)
                        if k == 'I371__m':
                            todel.append(k)
                        if k == 'I371__c':
                            todel.append(k)
                        if dta[k] == '':
                            todel.append(k)
                    for k in todel:
                        del dta[k]
                    dta['I1001_b'] =  person['b']
                    # searching with an ID is unique so we can enrich what we
                    # have But we preserve the name as it was written, unless
                    # len(names) == 1 indicates interactive input.
                    # Additionally if we have no full name we should return
                    # the full name resolved from an authority record if
                    # possible.
                    marcdta = {}
                    if 'a' in person:
                        if len(names) == 1:
                            marcdta['I1001_a'] = dta['I1001_a']
                        else:
                            marcdta['I1001_a'] = person['a']
                    if 'b' in person:
                        marcdta['I1001_b'] = person['b']
                    if 'I1001_0' in dta:
                        marcdta['I1001_0'] = dta['I1001_0']
                    if 'I9101_' in dta:
                        marcdta['I9101_'] = dta['I9101_']
                    if 'label' in dta:
                        marcdta['label'] = dta['label']
                    marcdta['exactMatch'] = 'True'
                    guess.append(marcdta)
                    select.append(marcdta)
            else:
                # We should actually never end up here!
                # In this case we have an ID but it does NOT resolve
                # on our local system. (This could be e.g. a GND number we
                # did not yet store locally to our authors.)
                marcdta = {}
                marcdta['I1001_0'] = person['0']
                if 'a' in person:
                    marcdta['I1001_a'] = person['a']
                if 'b' in person:
                    marcdta['I1001_b'] = person['b']
                marcdta['label'] = person['a'] + ' [' + person['0'] + ']'
                marcdta['exactMatch'] = 'Unknown Identifier'
                select.append(marcdta)
                guess.append(marcdta)
        else:
            # mostlikely will finally hold our most likely match, ie.
            # the entry for the selected array.
            mostlikely = {}

            # Setup a guess-set from what we have already
            marcdta    = {}
            if 'a' in person:
                marcdta['I1001_a'] = person['a']
            if 'b' in person:
                marcdta['I1001_b'] = person['b']
            # we have 0 but it is CFG_WEBSTYLE_TEMPLATE_SKIN: Store it in
            # $u and do not assign a $0 as we don't have one.
            # This case may happen by copy&paste, e.g. "Müller, H [FZJ]"
            if '0' in person:
                marcdta['label'] = (person['a'] + ' ('
                        + extlabel + ' ; ' + person['0'].upper() + ')')
                marcdta['I1001_u'] = person['0'].upper()
            else:
                marcdta['label'] = person['a']#ebv + ' (Extern)'
                marcdta['I1001_0'] = 'P:(DE-HGF)0'
                marcdta['exactMatch'] = 'False'
            mostlikely = marcdta
            guess.append(marcdta)

            # replace . by * and remove , to search for people

            # Use m1='p' for "partial phrase". This does all we need here
            # with a lower footprint that regexping it. Thanks to Ludmila
            # Marian for the pointer.
            # Why is  f1='author',  not good?
            if len(person['a'].split(' ')) > 1:
                # TODO in case it doesn't work properly, things to try would
                # be resorting to regexp again and brushing up the searchterm
                # like:
                # searchterm = searchterm + '*'
                # searchterm = '^' + searchterm + '.*'
                ##res = perform_request_search(p1=searchterm,
                #m1='a',cc='People', rg=50)
                # resort to a simple search with the literal input
                searchterm = person['a'].replace('.', ' ').strip()
                searchterm = "'" + searchterm + "'"
                res = perform_request_search(p=searchterm, cc='People', rg=50)
            else:
                searchterm = person['a'].replace('.', ' ').replace(',', ' ').strip()
                res = perform_request_search(p1=searchterm, m1='p',
                        f1='author', cc='People', rg=50)

            for r in res:
                alltops = []  # all top level institute ids
                todo    = []  # institutes to search for top level and add
                                # to counting for most likely

                js = washJSONinput(print_record(r, format='js'))
                dta = json.loads(js)

                alltops, MatchedInstitutes = GetToplevels(dta, '373__0',
                        '5101_')

                # Address information
                todo = []
                if 'I371__0' in dta:
                    todo = dta['I371__0'].split('|')

                # counting institutes of this author to get the most likely one.
                for t in todo:
                    if t in MatchedInstitutes:
                        MatchedInstitutes[t] += 1
                    else:
                        MatchedInstitutes[t] = 1
                try:
                    mostlikelyinst = sorted(MatchedInstitutes,
                        key=MatchedInstitutes.get, reverse=True)[0]
                except:
                    mostlikelyinst = ''


                # Marc does not contain empty fields, so drop them
                # todel = ['I373__0']
                dta['I1001_b'] = person['b']

                dta['I9101_'], extlabel = BuildInstitutionsSubfield(alltops,
                        dta['I1001_0'], person['b'], '9101_')
                inputname = person['a']
                dta['label'] = BuildLabel(inputname, extlabel, dta)

                todel = []
                for k in dta:
                    if k == 'I373__0':
                        todel.append(k)
                    if k == 'I371__0':
                        todel.append(k)
                    if k == 'I371__m':
                        todel.append(k)
                    if k == 'I371__c':
                        todel.append(k)
                    if dta[k] == '':
                        todel.append(k)
                for k in todel:
                    del dta[k]

                # If our record belongs to the most likely institute return
                # it as best match
                if mostlikelyinst in todo:
                    mostlikely = dta
                else:
                    # if not check if it is an internal author
                    # and then prefer her
                    if 'I1001_0' in dta:
                        if dta['I1001_0'] != 'P:(DE-HGF)0':
                            mostlikely = dta

                if  len(names) > 1:
                    # we suspect that a names list was pasted, and we are not in
                    # interactive input mode
                    if len(person['a'].split(' ')) > 1:
                        # The name contains more then one word, we should
                        # preserve it.
                        dta['I1001_a'] = person['a']
                dta['exactMatch'] = 'False'
                guess.append(dta)

            select.append(mostlikely)

        Select.append(select)
        Guess.append(guess)

    result['select'] = Select
    result['guess']  = Guess

    return (json.dumps(result, sort_keys=True, indent=2))


def index(req, names, c=CFG_SITE_NAME, ln=CFG_SITE_LANG):
    """
    This interface should get parameters by URL and return names
    """
    uid = getUid(req)
    # names should be urlencoded! DO NOT USE ";" HERE.
    if 'names' in req.form:
        people   = str(req.form['names'])
        #print req
        onlylast = False
        try:
            if req.form['onlylast'] == 'True':
                onlylast = True
        except:
            onlylast = False
        result = IdentifyPeople(people, onlylast)
        return result
    else:
        return ''

#if __name__ == '__main__':
   #print perform_request_search(
   #c='P', p='B*', f='author', of='js', cc='People', verbose=9)
   #print perform_request_search(
   #c='P', p='', f='author', of='js', cc='People', verbose=9)
   #result = perform_request_search(p='*', cc='People')
   # for r in result:
   #   print print_record(r, format='js')
   #
   # print result

   #print NormalizeName("H.A.   Schmidt")

   # print IdentifyPeople(
   #"H.    Mueller   {Uni. Aachen }    [   P:(DE-Juel1)123]")
   # print IdentifyPeople("Schmitz, H.; R. Schmitz;Schmitz, Achim", False)
   # print IdentifyPeople("Heinz Schmitz , Ralf Schmitz , Achim Schmitz", False)
   # # print IdentifyPeople("Schmidt, B.")

   #namelst = ("Wagner ; Maier, H. ; Plott C.")
   #namelst = ("Plott")
   #namelst = ("Wagner, A.")
   #namelst = ("A. Wagner, H. Maier, Plo")
   #namelst = ("Wagner, A.")
   #namelst = ("Wagner, A.;")
   #namelst = ("Maier, U.;")
   #namelst = ("Wagner, A ; Becker, J. S. [P:(DE-Juel1)133838]")
   #namelst = ("Plo")
   #namelst = "Müller-Gärtner"
#   namelst = "Stöcker"
   #namelst = "Wagner, A"
#   namelst = "Müller, M"
#   print IdentifyPeople(namelst, False)

