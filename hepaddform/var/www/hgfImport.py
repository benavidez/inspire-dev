import subprocess as sub
try:
    import json
except ImportError:
    import simplejson as json

from invenio.config import \
  CFG_SITE_LANG, \
  CFG_SITE_NAME
from invenio.webuser import getUid


def index(req, f=None, doi=None, pmid=None, ut=None, wos=None, 
          isi=None, arxiv=None, ppn=None, mode=None, format=None, 
          c=CFG_SITE_NAME, ln=CFG_SITE_LANG):
    """This interface should get parameters by URL and return names"""

    uid = getUid(req)
    docroot = req.subprocess_env['DOCUMENT_ROOT']

    # TODO these configs shouldn't live here!
    perl        = '/usr/bin/perl'
    scriptpath  = docroot+'/cgi-bin/'

    # define functions that are allowed for the f= parameter and give a
    # full definition on how to call them. Surely, we don't want to allow
    # a call of any system function ;)
    functions   = {
        'GenMetadata.pl' : scriptpath + 'GenMetadata.pl',
        'AUTISearch.pl'  : scriptpath + 'AUTISearch.pl',
        'GVKSearch.pl'   : scriptpath + 'GVKSearch.pl'
    }

    # require a login, ie a uid > 0 to work
    # TODO actually we'd like to check if we come from a submit and at
    # the end of the day we'd like not to allow to many calls from a
    # single submit either. We do not want to be a relay.
    result = ''
    #if uid > 0:
    if True:
        # Extract the proper function path
        fun  = functions["" + req.form['f']]

        # Call contains an array for Popen()
        call = []
        call.append(perl)
        call.append(fun)

        # add all parameters in proper syntax to POpen
        for par in req.form:
            if par != 'f':
                call.append(par + '='+ req.form[par])

        call.append('wwwhost=' + req.subprocess_env['HTTP_HOST'])
        # Call the external and retrieve stdout as result
        handle = sub.Popen(call, stdout=sub.PIPE, stderr=sub.PIPE)
        result, err = handle.communicate()

    return result
