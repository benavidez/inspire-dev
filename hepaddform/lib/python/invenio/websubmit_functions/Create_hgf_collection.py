import os, re
from invenio.websubmitadmin_dblayer import get_docid_docname_alldoctypes 
from invenio.webgroup_dblayer import get_groups
try: import json
except ImportError: import simplejson as json

global uid_email,sysno,uid,curdir
#curdir = os.getcwd()

from invenio.websubmit_functions.Create_hgf_record_json import washJSONinput
from invenio.websubmit_functions.Convert_hgf_fields import write_json,read_json

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

def delete_fields(fieldname):
        """delete file from curdir"""
        os.system("rm -f %s/%s?*" %(curdir,fieldname))

def write_980(collection_list):
	#if collection_list == []: return
	write_json("hgf_980__",collection_list)
	
def get_user():
	user_groups = get_groups(uid)
	if user_groups == []: return "USER"
	groups = []
	[groups.append(tup[1]) for tup in user_groups]
	if "STAFF" in groups: return "STAFF"
	if "EDITORS" in groups: return "EDITORS"
	return "USER"		  
	
def get_technical_collections():
	return ["USER","EDITORS","VDB","VDBRELEVANT","VDBINPRINT","TEMPENTRY"]

def filter_980():
	if not os.path.exists(os.path.join(curdir,"hgf_980__")): return []
	coll_dict = read_json("hgf_980__")
	coll_list = coll_dict["980__"]
	doctype_tuples = get_docid_docname_alldoctypes()
	doctype_collections = []
	[doctype_collections.append(tup[0]) for tup in doctype_tuples]
	filter_collections = doctype_collections + get_technical_collections()
	json_filter_collections = [{"a":collection} for collection in filter_collections]
	old_collections = []
	for coll in coll_list:
		if not coll.has_key("a"): continue
		if coll["a"].startswith("I:"): continue
		if coll in json_filter_collections: continue
		old_collections.append(coll)
	return old_collections
	
			
def check_field_exists(fieldname):
	if os.path.exists(os.path.join(curdir,fieldname)): return True
	else: return None
			
def check_vdb_relevant(fieldname):
	if os.path.exists(os.path.join(curdir,fieldname)): pass
	else: return None
	fd = open(os.path.join(curdir,"hgf_vdb"),"r")
	text = fd.read()
	fd.close()
	if "yes" in text: return True
	else: return None
	 
def is_user_released(user,tag_release,tag_vdb,collection_list):
	if ((user == "USER") and tag_release): 
		collection_list.append({"a":"USER"})
		if tag_vdb: collection_list.append({"a":"VDBRELEVANT"}) 
	return collection_list
def is_user_not_released(user,tag_release,tag_vdb,collection_list):
	if ((user == "USER") and  not tag_release): 
		collection_list.append({"a":"TEMPENTRY"})
		if tag_vdb: collection_list.append({"a":"VDBRELEVANT"}) 
	return collection_list
def is_editor_released(user,tag_release,tag_vdb,collection_list):
	if ((user == "EDITORS") and tag_release): 
		collection_list.append({"a":"EDITORS"})
		if tag_vdb: collection_list.append({"a":"VDBINPRINT"}) 
	return collection_list
def is_editor_not_released(user,tag_release,tag_vdb,collection_list):
	if ((user == "EDITORS") and not tag_release): 
		collection_list.append({"a":"EDITORS"})
		collection_list.append({"a":"TEMPENTRY"})
		if tag_vdb: collection_list.append({"a":"VDBINPRINT"}) 
	return collection_list	
def is_staff_released(user,tag_release,tag_vdb,collection_list):
	if ((user == "STAFF") and tag_release): 
		if tag_vdb: collection_list.append({"a":"VDB"})
	return collection_list
def is_staff_not_released(user,tag_release,tag_vdb,collection_list):
	if ((user == "STAFF") and not tag_release): 
		collection_list.append({"a":"TEMPENTRY"})
		if tag_vdb: collection_list.append({"a":"VDBINPRINT"}) 
	return collection_list


def Create_hgf_collection(parameters, curdir, form, user_info=None):
	"""process collections by access role of the user"""
	user = get_user()
	tag_release = check_field_exists("hgf_release")
	tag_vdb = check_vdb_relevant("hgf_vdb")	
	collection_list = []
	collection_list = is_user_released(user,tag_release,tag_vdb,collection_list)
	collection_list = is_user_not_released(user,tag_release,tag_vdb,collection_list)
	collection_list = is_editor_released(user,tag_release,tag_vdb,collection_list)
	collection_list = is_editor_not_released(user,tag_release,tag_vdb,collection_list)
	collection_list = is_staff_released(user,tag_release,tag_vdb,collection_list)
	collection_list = is_staff_not_released(user,tag_release,tag_vdb,collection_list)
	
	old_collections = filter_980()
	collection_list += old_collections
	write_980(collection_list)
	
#if __name__ == "__main__":
	