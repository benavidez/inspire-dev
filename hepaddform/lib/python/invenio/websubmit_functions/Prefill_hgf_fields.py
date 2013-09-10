import os, re
global sysno,rn,curdir,doctype
from pprint import pprint
#curdir = os.getcwd()
from invenio.config import * #(local-conf)
from invenio.search_engine import get_record
from invenio.websubmitadmin_dblayer import get_details_and_description_of_all_fields_on_submissionpage

#curdir = os.getcwd()
#doctype = "journal"
try: import json
except ImportError: import simplejson as json

def delete_fields(fieldname):
        """delete file from curdir"""
	fieldname = "hgf_"+ fieldname
	if not os.path.exists(os.path.join(curdir,fieldname)): return
	cmd = "rm -f %s?*" % os.path.join(curdir,fieldname)
	os.system(cmd)
	
def write_json(fieldname,dict):
	"""write python dictionary as json-file"""
	fw = open(os.path.join(curdir,fieldname), "w")
	field = fieldname.replace("hgf_","")
	json.dump(dict[field], fw)
	fw.close()		

def read_json(fieldname):
	"""read json-file and return dict"""
	fr = open(os.path.join(curdir,fieldname), "r")
	text = fr.read()
	fr.close
	jsondict = json.loads(text, 'utf8')
	return jsondict

def wash_db_record_dict(record_dict):
	"""create nice json dictionary
	record_dict = output of search_engine.get_record
	"""
	json_dict = {}
	for marccode in record_dict.keys():
		#loop 1: all fields 100,200,300
		ct_fields = len(record_dict[marccode]) # field counter
		#print marccode
		for marcfield in record_dict[marccode]:
			#loop2:	all 700 fields
			#print marcfield
			ind1 = marcfield[1]	
			ind2 = marcfield[2]
			if not ind1 in map(lambda w: str(w),range(0,10)): ind1 = "_" #ind1 is blank
			if not ind2 in map(lambda w: str(w),range(0,10)): ind2 = "_" #ind2 is blank		
			fullmarccode = str(marccode) + ind1 + ind2
			#print fullmarccode, marcfield
			dict ={}
			for subfield in marcfield[0]:
				#loop3: all subfields
				dict[subfield[0]]=subfield[1]
			if dict == {}: continue
			if not fullmarccode in json_dict.keys(): json_dict[fullmarccode] = []
			json_dict[fullmarccode].append(dict)
			
	
	return json_dict
	
def get_autosuggest_keys():
	autosuggest_keys = ["9201_","1001_","7001_","9131_","536__"]
	return autosuggest_keys	
	
def delete_for_autosuggest_fields():
	for key in get_autosuggest_keys(): delete_fields(key)
		
def add_non_json_fields(json_dict):
	"""add single input fields if field non repeatable"""
	autosuggest_keys = get_autosuggest_keys()
	for key in json_dict.keys():
		if not len(json_dict[key])==1: continue
		for subfield in json_dict[key][0].keys():
			fieldname = key + subfield 
			json_dict[fieldname] = json_dict[key][0][subfield]
		if key in autosuggest_keys:
			#fieldname = "hgf_" + key
			#delete_fields(fieldname) 
			continue #do not delete autosuggest fields
		del json_dict[key] #prevent double entries
	return json_dict	
			  	
	

def write_all_fields(json_dict):
	for field in json_dict.keys():
		fieldname = "hgf_" + field 
		if len(fieldname)==9: write_json(fieldname,json_dict)
		else: write_file(fieldname,json_dict[field])
		
def write_done_file():
	done_file = open(os.path.join(curdir,"Create_Modify_Interface_DONE"),"w")
	done_file.write("DONE")
	done_file.close()

def write_file(filename,text):
	wd = open(os.path.join(curdir,filename),"w")
	wd.write(text)
	wd.close()
	

def handle_url():
	if os.path.exists(os.path.join(curdir,"hgf_8564_")): 
		os.system("rm -f %s" %os.path.join(curdir,"hgf_8564_u"))
		os.system("cp %s %s" %(os.path.join(curdir,"hgf_8564_"),os.path.join(curdir,"test")))
		
		jsondict_list = read_json("hgf_8564_")
		for i in jsondict_list:
			if CFG_SITE_URL in i["u"]: continue # skip internal file
			wd = open(os.path.join(curdir,"hgf_8564_u"),"w")
			wd.write(i["u"])
			wd.close
			os.system("rm -f %s" %os.path.join(curdir,"hgf_8564_")) #remove technical field
			return # write only one URL
	if os.path.exists(os.path.join(curdir,"hgf_8564_u")):
		fd = open(os.path.join(curdir,"hgf_8564_u"),"r")
		text = fd.read()
		fd.close()
		if CFG_SITE_URL in text: os.system("rm -f %s" %os.path.join(curdir,"hgf_8564_u")) #skip internal file
		
def handle_date():
	if not os.path.exists(os.path.join(curdir,"hgf_245__f")): return
	fd = open(os.path.join(curdir,"hgf_245__f"),"r")
	date = fd.read().replace("\n","")
	fd.close()
	try: sdate,edate = date.split(" - ")
	except: return
	if sdate != "": write_file("hgf_245__fs",sdate)
	if edate != "": write_file("hgf_245__fe",edate)
	  			
def write_mod_doctype():
	"""write mod_doctype file to automatically connect to modification page"""
	mod_doctype_path = os.path.join(curdir,"mod_"+doctype)
	mod_file = open(mod_doctype_path,"w")
	tuple_fields = get_details_and_description_of_all_fields_on_submissionpage(doctype, "SBI", 1)
	for _tuple in tuple_fields:
		field = _tuple[0]
		if field in ["hgf_start","hgf_end","hgf_master"]: continue
		mod_file.write( field + "\n")
	mod_file.close()
def prefill_vdb_relevant():
	if not os.path.exists(os.path.join(curdir,"hgf_980__")): return
	fd = open(os.path.join(curdir,"hgf_980__"),"r")
	text = fd.read()
	fd.close()
	if (('VDBRELEVANT' in text) or ('"VDB"' in text) or ('VDBINPRINT' in text)): value = "yes"
	else: value = "no"
	wd = open(os.path.join(curdir,"hgf_vdb"),"w")
	wd.write(value)
	wd.close()
		
def Prefill_hgf_fields(parameters, curdir, form, user_info=None):
	"""extract all information from DB-record as json dict and write files into curdir"""
	record_dict = get_record(sysno) #get record
	json_dict = wash_db_record_dict(record_dict) #create nice json dictionary
	json_dict = add_non_json_fields(json_dict) #add single input fields
	write_all_fields(json_dict) # write all values to files
	delete_for_autosuggest_fields()
	write_done_file() #write done file--> cheat invenio
	handle_url()
	handle_date()
	write_mod_doctype()
	prefill_vdb_relevant()
	#os.system("cp %s/hgf_9201_ %s/out" %(curdir,curdir))
	
#if __name__ == "__main__":
	#record_dict = get_record("332") #get record
	#pprint(record_dict)
	#json_dict = wash_db_record_dict(record_dict) #create nice json dictionary
	#json_dict = add_non_json_fields(json_dict)
	#pprint(json_dict)
	#write_all_fields(json_dict) # write all values to files
	#delete_for_autosuggest_fields()
	#write_done_file() #write done file--> cheat invenio
	#handle_url()
	#handle_date()
	#write_mod_doctype()
	
