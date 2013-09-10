import os,re,urllib2,datetime
from invenio.config import CFG_BINDIR,CFG_WEBSUBMIT_BIBCONVERTCONFIGDIR,CFG_SITE_URL
from invenio.websubmit_config import InvenioWebSubmitFunctionError
from invenio.websubmit_functions import Create_PersistentID		
from invenio.websubmit_functions.Create_hgf_record_json import washJSONinput
from invenio.webgroup_dblayer import get_groups	
from invenio.search_engine import get_fieldvalues
from invenio.access_control_config import CFG_EXTERNAL_AUTH_DEFAULT

try: import json
except ImportError: import simplejson as json	
	
global curdir,uid,sysno

def write_json(fieldname,dict):
	"""write python dictionary as json-file"""
	fw = open(os.path.join(curdir,fieldname), "w")
	json.dump(dict, fw)
	fw.close()		
	
def read_json(fieldname):
	"""read json-file and return dict"""
	fr = open(os.path.join(curdir,fieldname), "r")
	text = fr.read()
	fr.close
	#if isinstance(eval(text),list): pass
	if text.startswith("["): pass #we have a list
	else: text = '[' + text +']' ### TODOOOOOOOOOOOOOOO. really bad!!!!
	jsontext = washJSONinput(text)
	jsondict = json.loads(jsontext, 'utf8')
	marcfield = fieldname.replace("hgf_","") 
	if isinstance(jsondict,list): jsondict = {marcfield:jsondict} # if json Frormat as list 
	return jsondict
		
def read_file(filename):
	fd = open(os.path.join(curdir,filename),"r")
	text = fd.read().replace("\n","").replace("\r","")
	fd.close()
	return text
		
def write_file(fieldname,text):
	wd = open(os.path.join(curdir,filename),"w")
	wd.write(text)
	wd.close()
		
def handle_list_of_doctype_dict(doctype_dict,access=None,doctype=None,subtype=None):
	doctype_dict_list = []
	for dict in doctype_dict['I3367_']:
		d = dict
		try:
			if d['m'] == doctype:
				d['s'] = access
				d['b'] = doctype
				if subtype != '':
					d['x'] = subtype
		except:
			pass
		doctype_dict_list.append(d)
	return doctype_dict_list		
			
			
def get_usergroups():
	user_groups = get_groups(uid)
	if user_groups == []: return []
	groups = []
	[groups.append(tup[1]) for tup in user_groups]
	return groups
		
			
def get_pubtype_info(doctype):
	"""call output format for publication types and return it as dictionary (json)"""
	url_of = '%s/search?action_search=Search&cc=PubTypes&c=PubTypes&of=js&p=3367_%%3A%s' %(CFG_SITE_URL,doctype)
	f = urllib2.urlopen(url=url_of)
	text = f.read()
	f.close()
	jsontext = washJSONinput(text)
	jsondict = json.loads(jsontext, 'utf8')
	return jsondict
				
def create_handle(typ="handle"):
	form =""
	curdir = curdir
	recid_file = os.path.join(curdir,"SN")
	if not os.path.exists(recid_file): return ""
	fd = open(recid_file,"r")
	recid = fd.read().replace("\n","").replace("\r","")
	fd.close()	
	url = CFG_SITE_URL + "/record/" + recid 
	parameters = {"type":typ,"url":url}
	handle = Create_PersistentID(parameters,curdir,form) #only If fulltext + vdb relevant TODO 	
	if handle: return handle

def check_field_exists(fieldname):
	if os.path.exists(os.path.join(curdir,fieldname)): return True
	else: return None
		
def delete_fields(fieldname):
	"""delete file from curdir"""
	os.system("rm -f %s/%s?*" %(curdir,fieldname))	
		
		
def add_reportdoctype(doctype, doctype_dict_list):
	"""adds a new 3367 doctype for internal report"""
	if not "hgf_088__a" in os.listdir(curdir): return doctype_dict_list #no reportnumber
	if (doctype == "intrep" or doctype == "report"): return doctype_dict_list # we have already a report documenttype
	report_doctype_dict = get_pubtype_info("intrep")
	report_doctype_dict_list = handle_list_of_doctype_dict(report_doctype_dict)
	return doctype_dict_list + report_doctype_dict_list
			
def add_journaldoctype(doctype, doctype_dict_list):
	"""adds a new 3367 doctype for journal"""
	fields_set = set(["hgf_773__","hgf_773__t","hgf_440__","hgf_440"])
	files_set = set(os.listdir(curdir))
	intersection =  fields_set & files_set #only fields, which exists as files
	if len(intersection) == 0: return doctype_dict_list #no journal reference
	if (doctype == "journal"): return doctype_dict_list # we have already a journal documenttype
	report_doctype_dict = get_pubtype_info("journal")
	report_doctype_dict_list = handle_list_of_doctype_dict(report_doctype_dict)
	return doctype_dict_list + report_doctype_dict_list
	
def add_bookdoctype(doctype, doctype_dict_list):
	"""adds a new 3367 doctype for book"""
	if not "hgf_29510a" in os.listdir(curdir): return doctype_dict_list #no book reference
	if doctype == "book": return doctype_dict_list # we have already a book documenttype
	report_doctype_dict = get_pubtype_info("book")
	report_doctype_dict_list = handle_list_of_doctype_dict(report_doctype_dict)
	return doctype_dict_list + report_doctype_dict_list		
			
def add_procdoctype(doctype, doctype_dict_list):
	"""adds a new 3367 doctype for proc"""
	if not "hgf_1112_a" in os.listdir(curdir): return doctype_dict_list #no proc reference
	if doctype == "proc": return doctype_dict_list # we have already a proc documenttype
	# we have a book + a conference entry,
	# this makes us a proceedings volume
	if doctype == "book":
		report_doctype_dict = get_pubtype_info("proc")
		report_doctype_dict_list = handle_list_of_doctype_dict(report_doctype_dict)
		return doctype_dict_list + report_doctype_dict_list		
	return doctype_dict_list

def insert_email():
	"""preprocessing of emails"""
	if not os.path.exists(os.path.join(curdir,"SuE")): return
	email_file = os.path.join(curdir,"SuE")
	f = open(email_file,"r")
	email = f.read()	
	f.close()
	new_email_file = os.path.join(curdir,"hgf_8560_f")
	wd = open(new_email_file, "w")
	wd.write(email)
	wd.close()
		
def insert_date(fielddate,sdate,edate):
	"""preprocessing date into 245$f
	fielddate can be hgf_245__f, hgf_1112_d
	sdate: hgf_245__fs or hgf_1112_dcs
	edate: hgf_245__fe or hgf_1112_dce
	"""
	if sdate in os.listdir(curdir):
		fd = open(os.path.join(curdir,sdate),"r")
		hgf_sdate = fd.read().replace("\n","")
		fd.close()
	else: hgf_sdate = ""
	if edate in os.listdir(curdir): 
		fd = open(os.path.join(curdir,edate),"r")
		hgf_edate = fd.read().replace("\n","")
		fd.close()
	else: hgf_edate = ""
	if (hgf_sdate == "" and hgf_edate == "" ): return ""
	else: datestring = hgf_sdate + " - " + hgf_edate 
	date_file = os.path.join(curdir,fielddate)
	wd = open(date_file,"w")
	wd.write(datestring)
	wd.close()
	os.system("rm -f %s %s" %(os.path.join(curdir,sdate),os.path.join(curdir,edate)))	
	
def insert_reportnr():
	"""preprocessing of reportnumber"""
	rn_file = os.path.join(curdir,"rn")
	f = open(rn_file,"r")
	rn = f.read()	
	f.close()
	new_rn_file = os.path.join(curdir,"hgf_037__a")
	wd = open(new_rn_file, "w")
	wd.write(rn)
	wd.close()
		
def insert_webyear():
	try: recid = int(sysno)
	except: return
	orig_record_980 = get_fieldvalues(recid,'980__a') #create_hgf_collection was alreay active at this step and changed 980-field, so we have to get the original collections of the record from database 
	if "VDB" in orig_record_980: return # do not change web_year after it was released by library (collection tag VDB)
	web_year = None
	if os.path.exists(os.path.join(curdir,"hgf_260__c")): # publication_year exists
		fd = open(os.path.join(curdir,"hgf_260__c"),"r")
		pub_year = fd.read().replace("\n","").replace("\r","")
		fd.close()
		current_year = str(datetime.datetime.now().year)
		if pub_year == current_year: web_year = pub_year # publication year is current system year --> set web-year
	else:
		if os.path.exists(os.path.join(curdir,"hgf_245__f")): # check thesis end_date
			fd = open(os.path.join(curdir,"hgf_245__f"),"r")
			date = fd.read().replace("\n","").replace("\r","")
			fd.close()
			sdate,edate = date.split(" - ")
			if current_year in edate: web_year = current_year # ending year of thesis is current system year --> set web-year
		if os.path.exists(os.path.join(curdir,"hgf_1112_d")): # check conf end_date
			fd = open(os.path.join(curdir,"hgf_1112_d"),"r")
			date = fd.read().replace("\n","").replace("\r","")
			fd.close()
			sdate,edate = date.split(" - ")
			if current_year in edate: web_year = current_year # ending year of conference is current system year --> set web-year
				
	if web_year: #write web_year			
		wd = open(os.path.join(curdir,"hgf_9141_y"),"w")
		wd.write(web_year)
		wd.close()
			
def insert_thesis_note():
	"""insert 502__a --> thesis note:
	syntax: 'University, Doctype, Granted Year'
	insert 502__b (if possible)
	insert 655_7 
	"""	
	doctype = read_file("doctype")
	jsondict = get_pubtype_info(doctype)
	if "grad" in jsondict.keys(): write_file("hgf_502__b",jsondict["grad"]) #TODO
	
	all_fields = True
	all_fields = check_field_exists("hgf_502__c")
	all_fields = check_field_exists("hgf_502__d")
	if not "some_field" in jsondict.keys(): all_fields = None ## Todo
	if not all_fields: return #if some field is missing, do not create thesis_note
	norm_doctype = jsondict["some_field"] ##TODO
	thesis_note = read_file("hgf_502__c") + ", " + norm_doctype + ", " + read_file("hgf_502__d")	
	write_file("hgf_502__a",thesis_note)	
	write_file("hgf_655_7a","Hochschulschrift")
	write_file("hgf_655_7x",norm_doctype)
		
		
def insert_3367():
	"""get doctype from authorities and create 921"""		
	fd = open(os.path.join(curdir,"doctype"),"r")
	doctype = fd.read().replace("\n","").replace("\r","")
	fd.close()
	fd = open(os.path.join(curdir,"access"),"r")
	access = fd.read().replace("\n","").replace("\r","")
	fd.close()
	subtype = ''
	try:
		# Check if we have a refinement of the doctype. Usually we have
		# this only for talks which could be "Invited" or whatever. If so,
		# add it to 3367_$x
		fd = open(os.path.join(curdir,"hgf_3367_x"),"r")
		subtype = fd.read().replace("\n","").replace("\r","")
		fd.close()
	except:
	  # Usually, we do not have refinements.
		pass
	doctype_dict = get_pubtype_info(doctype)
	# Run over the dictionary and build up a list of all document types.
	# Note that not all document types have to be hgf-types, they may as
	# well stem from other vocabularies (DINI/DRIVER...)
	doctype_dict_list = handle_list_of_doctype_dict(doctype_dict,access,doctype,subtype)
	
	doctype_dict_list = add_reportdoctype(doctype, doctype_dict_list) #add intrep doctype 
	doctype_dict_list = add_journaldoctype(doctype, doctype_dict_list) #add journal doctype
	doctype_dict_list = add_bookdoctype(doctype, doctype_dict_list) #add book doctype
	doctype_dict_list = add_procdoctype(doctype, doctype_dict_list) #add proc doctype
	if os.path.exists(os.path.join(curdir,"hgf_980__")):
		dict_980 = read_json("hgf_980__")
		list_980 = dict_980["980__"]
	else: list_980 = []
	# Only add our own doctypes to 980 (ie collections)
	for dict in doctype_dict_list:
		try:
			if {"a":dict["m"]} in list_980: continue 
			list_980.append({"a":dict["m"]})
		except:
			pass
	write_json("hgf_980__",list_980)
	write_json("hgf_3367_",doctype_dict_list)
		
		
def insert_inst_into_980():
	if not os.path.exists(os.path.join(curdir,"hgf_9201_")): return
	jsondict = read_json("hgf_9201_")
	inst_list = []
	dict_980 = read_json("hgf_980__")
	list_980 = dict_980["980__"]
	for inst in jsondict["9201_"]:
		if {"a":inst["0"]} in list_980: continue 
		inst_list.append({"a":inst["0"]})
	if inst_list == []: return 0
	list_980 += inst_list
	 
	#check if users institut in 980, if not take it from user_info
	user_groups = get_usergroups()
	str_list_980 = [str(i) for i in list_980] #convert list with dicts into list with str(dicts), because python sets use list with strings
	intersection_groups = set(str_list_980) & set(user_groups) # user institute not in 980 yet
	intersection_vdb = set(["{'a':'VDB'}", "{'a':'VDBRELEVANT'}","{'a':'VDBINPRINT'}"]) & set(user_groups) # not vdb_relevant
	if intersection_groups == set([]) and  intersection_vdb == set([]): # # prevent submitting vdb irrelevant stuff for another institute
		user_inst = []
		for inst in user_groups:
			if not inst.startswith("I:"):continue
			if {"a":inst.replace(' ['+CFG_EXTERNAL_AUTH_DEFAULT+']', '')} in list_980: continue
			user_inst.append({"a":inst.replace(' ['+CFG_EXTERNAL_AUTH_DEFAULT+']', '')})
		list_980 += user_inst
	write_json("hgf_980__",list_980)
		
		
def handle_980():
	new_dict = []
	dict_980 = read_json("hgf_980__")
	list_980 = dict_980["980__"]
	fd = open(os.path.join(curdir,"doctype"),"r")
	doctype = fd.read().replace("\n","").replace("\r","")
	fd.close()
	old_index = list_980.index({"a":doctype})
	
	list_980.insert(0, list_980.pop(old_index)) #move original doctype to be first entry in 980 list, needed by invenio (more likely a bug)
	for entry in list_980: new_dict.append(entry)
	if check_field_exists("hgf_delete"): new_dict.append({"c":"DELETED"}) # user wants to delete this record
	
	write_json("hgf_980__",new_dict)	
	
	
def add_FFT():	
	"""add FFT tag into record
	if this function is used: the functions stamp_uploaded_files and move_files_to_storage should not be used in the websubmit anymore
	"""
	if not check_field_exists("hgf_file"): return None # no file submitted
	inst_dict = read_json("hgf_9201_") #read in institutes
	inst_dict_list = inst_dict["9201_"]
	inst_list = []
	for inst in inst_dict_list:
		restriction = "allow groups " + inst["0"] #@Alexander: This is the restriction string
		inst_list.append(restriction) # add institution to restriction  
	restriction = " or ".join(inst_list) # all restrictions as one string. concatenated by "or". something like (allow groups I:inst1 or allow groups I:inst2 ......)
	
	filename = read_file("hgf_file")
	file_path = os.path.join(curdir,"files","hgf_file",filename)
	if not os.path.exists("rn"): return
	rn = read_file("rn")
	
	#fill subfields for FFT 
	fft_subdict = {}
	fft_subdict["a"] = file_path
	fft_subdict["n"] = rn
	fft_subdict["r"] = restriction
	fft_dict = {"FFT__":fft_subdict}
	
	write_json("hgf_FFT__",fft_dict)
	
		
def check_9201():
	"""deleting 9201_* if vdbrelevant set in 980"""
	jsondict = read_json("hgf_980__")
	if {"a":"TEMPENTRY"} in jsondict["980__"]: os.system("rm hgf_9201_*")
	else: pass
	
def Convert_hgf_fields(parameters,curdir, form, user_info=None):
	"""converts institutional Fields (inserting of doctypes and collection tags(MAIL,EDITOR....)"""
 	pass
	insert_email() # add email
	insert_date("hgf_245__f","hgf_245__fs","hgf_245__fe") # convert date
	insert_date("hgf_1112_d","hgf_1112_dcs","hgf_1112_dce") # convert conf date
	insert_webyear() #set web-year
	insert_reportnr() #insert reportnumber
	insert_3367() #insert doctype from authorities
	delete_fields("hgf_3367_")
	delete_fields("hgf_9201_") #delete files from curdir--> hgf_9201_?*, only hgf_9201_ will survive
	delete_fields("hgf_980__") #delete files from curdir
	delete_fields("hgf_1001_") #delete files from curdir
	delete_fields("hgf_536__") #delete files from curdir
	delete_fields("hgf_9131_") #delete files from curdir
	insert_inst_into_980()
	handle_980() # make a nice json
	
	#add_FFT() # add FFT tag for inserting fulltext files with restrictions
	#check_9201() #in case of vdbirrelevant delete 9201_
	#insert_thesis_note()
	
	#create_handle() # create handle id    TODO!!!!!
		
		
#if __name__ == "__main__":
#	insert_email() # add email
#	insert_reportnr() #insert reportnumber
#	insert_3367() #insert doctype from authorities
#	insert_inst_into_980()
#	handle_980()
