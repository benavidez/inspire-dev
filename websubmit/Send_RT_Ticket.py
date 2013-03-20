from configobj import ConfigObj             #module for reading config-file
from invenio.config import * #(local-conf)
import os, sys, re
try: import json
except ImportError: import simplejson as json
from invenio import bibcatalog_system_rt

#global curdir
#curdir = '/opt/invenio/var/data/submit/storage/running/journal/1360004080_1102'
		 
############# Functions ###################################
def read_file(fieldname):
 	"""read a text-file (marcdata) and return text"""
  	fr = open(os.path.join(curdir,fieldname), "r")
    	text = fr.read()
      	fr.close
      	return text

def read_json(fieldname):
        """read json-file and return dict"""
        fr = open(os.path.join(curdir,fieldname), "r")
        text = fr.read()
        fr.close
        jsondict = json.loads(text, 'utf8')
        return jsondict

def get_hgf_files():
	"""get all hgf_files from curdir"""
	hgf_files = []
	for f in os.listdir(curdir):
		if not f.startswith("hgf_"): continue
		hgf_files.append(f)
	return hgf_files

def washJSONinput(jsontext):
    """Wash string jsontext intended for processing with json.loads()

    Removes newlines and commas before closing brackets and at the end of 
    the string. 
    Returns: String suitable for processing with json.loads()
    """
    jsontext = re.sub('\n', '', jsontext)
    jsontext = re.sub(',\s*]', ']', jsontext)
    jsontext = re.sub(',\s*}', '}', jsontext)
    jsontext = re.sub(',\s*$', '', jsontext)
    return jsontext

def get_recordid():
	"""get_record_id"""
	f = open(os.path.join(curdir,"SN"),"r")
	recid = f.read().replace("\n","").replace("\r","")
	f.close()
	return recid

def check_hgf_field(fieldname):
	"""check if regular marcfield"""
	if len(fieldname) < 7: return 0, ""
	if fieldname == "hgf_master": return True, "master"
	if re.search('\d\d\d', fieldname):
		if len(fieldname) == 9: return True, "json"
		else: return True, "asci" 
	else: return 0, ""
	
def backup_file(fieldname):
	"""create bak-file"""
	bak_file = os.path.join(curdir,fieldname + ".bak")
	orig_file = os.path.join(curdir,fieldname) 	
	os.system("cp %s %s" %(orig_file,bak_file)) 


def get_authors(fieldname, mylist, inst):
        """ format authors 700 or 100"""
	""" return string with the author and the institute"""
        ret = ''
        mylistj = json.loads(washJSONinput(mylist))
        for o in mylistj:
                i = int(o["b"])
                ret = ret + fieldname + ' $$a' + o["a"] + '$$u' +  inst[i]["a"] + '\n'

        return ret

# -------------------------- PUBLIC FUNCTION -----------------------------------------  
def Send_RT_Ticket(parameters, curdir, form, user_info=None):
        """run over all hgf_fields and create hgf_record in json-format"""
	"""Then, convert to marc21 and send to RT as a ticket """
        ret = ''
        hgf_files = get_hgf_files()
	#read the institutes
        inst = read_file('hgf_9101_')
        instj = json.loads(washJSONinput(inst))

        for fieldname in hgf_files:
		#don't need these fields, so skip them
                if fieldname in ['hgf_record', 'hgf_jourart', 'hgf_release', 'hgf_9101_', 'hgf_1001_a']: continue
                mylist = read_file(fieldname)
                fieldname = fieldname.replace('hgf_', '')

		#get the subfield if there is one.
                subfield = ''
                if len(fieldname) == 6:
                        subfield = fieldname[5]

                if fieldname in ['1001_', '7001_']:
			#special case for the multiple authors. Not sure why the 1, so remove it
			fieldname = fieldname.replace('1_', '__')
                        ret = ret + get_authors(fieldname, mylist, instj)
                else:
                        fieldname = fieldname[:5]
                        ret = ret + fieldname + ' $$' + subfield + mylist + '\n'

	#print ret
 	ticketer = bibcatalog_system_rt.BibCatalogSystemRT()
        ticket_id = ticketer.ticket_submit(subject = 'HEP Addition Submit', requestor = 'eduardob', text = 'Content: ', queue = 'Test', owner = '') 

        #if ticketer.ticket_comment(None, ticket_id, ret) == None:
        ticketer.ticket_comment(None, ticket_id, str(ret))
       		#print 'commentiong on ticket failed' #write_message("Error: commenting on ticket %s failed." % (str(ticket_id),))
	


 
#if __name__ == "__main__":
#	Send_RT_Ticket()
