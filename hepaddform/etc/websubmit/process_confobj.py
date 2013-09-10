#!/usr/bin/python
# Prerequists:
#    Module configobj
#     python version >= 2.3
# Creating submission and modification forms for hgf-institutes.
# All fields and collections are defined in the 'config.cfg'.
#
# CFG_WEBSTYLE_TEMPLATE_SKIN has to be set (i.e. desy, gsi or fzj --> same
# name as in config.cfg. If not set --> take the default )
#
# Execute:
#     python process_confobj.py arg config.cfg
#
#    arg =      -c    create all submission forms
#        -d    delete all submission forms
#
from invenio.websearchadminlib import delete_col #delete webcollection
#functions for inserting into database
from invenio.websubmitadmin_dblayer import *
from configobj import ConfigObj             #module for reading config-file
from invenio.config import * #(local-conf)
import os, sys, re

##### Arguments and correct syntax ###
def check_args():
    """check arguments"""
    args = sys.argv
    if len(args) != 3:
        print "\nSyntax incorrect.\nCorrect Syntax: python process_confobj.py \
                argument conffilename\n\nargument:\n  -d delete all created\
                sbmcollections and submission forms\n  -c create sbmcollections\
                and submission forms\n"
        return 0
    global confilepath, arg, fieldlabels
    confilepath = args[2]
    arg = args[1] #argument1
    fieldlabels = []
    return 1
######################################

################# config functions ##############
def read_conf():
    """read config-file and return config-dictionary"""
    if os.path.exists(confilepath): pass
    else: sys.exit("Confile: |%s| does not exist" %(confilepath))
    try: config = ConfigObj(confilepath)
    except: sys.exit("Errors in Config-File,\
            please check for Syntax and try again. Bye, Bye.")
    return config

def get_hgf_institute(config):
    """get Variable cfg_hgf_institut from invenio-local.conf,
    if not set return default"""

    if ("CFG_WEBSTYLE_TEMPLATE_SKIN" in globals()):
        if arg == "-c": print "Creating websubmission masks for the Institute: %s" %(CFG_WEBSTYLE_TEMPLATE_SKIN)
        elif arg == "-d": print "Deleting websubmission masks for the Institute: %s" %(CFG_WEBSTYLE_TEMPLATE_SKIN)
        inst = CFG_WEBSTYLE_TEMPLATE_SKIN.lower()
        if inst in config.keys(): #inst_variable set in config.cfg
            if config[inst] == {}: #
                print "Only Variable %s is set in config.cfg" %(inst)
                inst = "default"
            else: pass
        else:
            print "no %s changes, because Variable %s not set in config.cfg --> creating default masks!" %(inst,inst)
            inst = "default"    #if global institutional variable set in local-conf, but not in config.cfg
    else:
        if arg == "-c":    print "Variable CFG_WEBSTYLE_TEMPLATE_SKIN not found in invenio.local-conf. Creating default submission masks!"
        if arg == "-d":    print "Variable CFG_WEBSTYLE_TEMPLATE_SKIN not found in invenio.local-conf. Deleting default submission masks!"
        inst = "default"

    return inst

def get_docname_from_schema(doctype,config):
    """return pretty docname for doctype"""
    for coll in config["schema"].keys():
        for doc in config["schema"][coll].keys():
            if doctype == doc: return config["schema"][coll][doc]

def get_submission_collection_fieldname(config,doctype):
    for sbmcoll in config["collection"]:
        if doctype in config["collection"][sbmcoll].keys(): return config["collection"][sbmcoll]["fieldname"]
    print "Doctype |%s| is not defined in the config-file under collection. It is not possible to add a collection into 980-field"
    return None

def get_alldoctypes(config):
    """return list of all doctypes"""
    alldoctypes = []
    for coll in config["collection"].keys():
        for doctype in config["collection"][coll]: alldoctypes.append(doctype)
    return alldoctypes

def get_marccode(config,fieldname):
    """return marccode of a specific field"""
    if fieldname in config["fielddesc"].keys():
        if  config["fielddesc"][fieldname][1] == "": return False
        else: return config["fielddesc"][fieldname][1]
    else: return False

def get_hidden_fields(config):
    """return all hidden fields but not 980"""
    hidden_fields = []
    for field in config["fielddesc"].keys():
        if config["fielddesc"][field][1] == "980__a": continue
        if config["fielddesc"][field][2].lower() == "h": hidden_fields.append(field)
    return hidden_fields

def sort_hgf_fields(default_keys, config, doctype):
    """order hgf_fields by config.cfg, but take institutional changes in order into account"""
    order_set = set(config["order"].keys())
    default_set = set(default_keys)
    intersection = order_set & default_set #only fields in order_set and in default_set
    only_default_set = default_set - order_set # fields in default_set but not in order_set. i.e. hidden fields
    if ("CFG_WEBSTYLE_TEMPLATE_SKIN" in globals()): CFG_WEBSTYLE_TEMPLATE_SKIN = globals()["CFG_WEBSTYLE_TEMPLATE_SKIN"] 
    else: CFG_WEBSTYLE_TEMPLATE_SKIN = "default"
    inst_fields = intersection
    new_order = {}
    if CFG_WEBSTYLE_TEMPLATE_SKIN in config.keys():
        if doctype in config[CFG_WEBSTYLE_TEMPLATE_SKIN].keys():
            inst_changes = config[CFG_WEBSTYLE_TEMPLATE_SKIN][doctype]
            inst = CFG_WEBSTYLE_TEMPLATE_SKIN
        else:
            inst_changes = {}
            inst = "default"
    else:
        inst_changes = config["default"][doctype]
        inst = "default"
    inst_changes_not_none = {}#sort out fields which are set None
    inst_changes_none = []
    for field in inst_changes.keys():
        if inst_changes == {}: continue
        if config[inst][doctype][field] == "None":
            inst_changes_none.append(field)
            continue
        inst_changes_not_none[field] = inst_changes[field]
    inst_changes = inst_changes_not_none
    inst_changes_but_not_order_set = set(inst_changes.keys()) - intersection #we have institutional changes, but field order under config["order"], and config["default_form"] not defined
    only_default_set = only_default_set - inst_changes_but_not_order_set # no double entries
    only_default_set = only_default_set - set(inst_changes_none) #cut out fields which are set none
    inst_fields = inst_fields | inst_changes_but_not_order_set
    inst_fields = inst_fields - set(inst_changes_none) #cut out fields which are set none
    #print inst_fields
    for field in inst_fields:

        if not (field in inst_changes.keys()): # in default, but no changes
            if field in order_set:
                new_order[field] = config["order"][field]
                continue
        if len(inst_changes[field]) > 2: #we have institutional changes in order
            if not isinstance(inst_changes[field],list): continue #bad if clause: None as a string has a length of 4
            if not inst_changes[field][2].isdigit():
                if not field in config["order"].keys():
                    new_order[field] = get_order(config["order"].values(),new_order.values(),900000) #set to the end, but before hgf_end
                    continue #field not in config["order"]
                else: new_order[field] = config["order"][field]
                continue
            else:    new_order[field] = get_order(config["order"].values(),new_order.values(),inst_changes[field][2]) #set new order
        else: continue
    new_order = sorted(new_order.items(),key=lambda x: int(x[1])) #create list with tuples sorted by value
    sorted_hgf_fields = []
    for i in new_order: sorted_hgf_fields.append(i[0])
    # add all hidden fields
    sorted_hgf_fields = sorted_hgf_fields[0:-1] + list(only_default_set) + [sorted_hgf_fields[-1]]

    return sorted_hgf_fields
################# End config functions ##############

################# Database help functions ################

def get_id_of_collection_name(collection_name):
    qstr = """SELECT id FROM sbmCOLLECTION """ \
    """WHERE name=%s """ \
    """LIMIT 1"""
    qres = run_sql(qstr, (collection_name,))
    try: return int(qres[0][0])
    except (TypeError, IndexError):return None

def get_max_id_webcollection():
    """returns maximum id value from table 'collection' """
    q = """SELECT IFNULL(MAX(id), 0) from collection"""
    return int(run_sql(q)[0][0])
def get_coll_max_collection_collection_score(id_dad):
    """returns maximum score value from table 'collection_collection' for a collection """
    q = """SELECT IFNULL(MAX(score), 0) from collection_collection where id_dad=%s""" %(id_dad)
    return int(run_sql(q)[0][0])

def get_doctype_max_collection_collection_score(id_webcoll):
    """returns maximum score value from table 'collection_collection' for a doctype """
    q = """SELECT IFNULL(MAX(score), 0) from collection_collection where id_dad=%s""" %(id_webcoll)
    return int(run_sql(q)[0][0])

def get_id_webcoll(coll):
    q = """SELECT id FROM collection where name='%s'""" % (coll)
    try: return int(run_sql(q)[0][0])
    except (TypeError, IndexError): return None

def get_fields_from_sbmfield(doctype):
    """returns list of sbi-fields for doctype"""
    q = """SELECT fidesc FROM sbmFIELD where subname='SBI%s'""" %(doctype)
    return run_sql(q)

def get_eltype_from_sbmfielddesc(hgf_field):
    """returns element type for a specific fielddescriptor"""
    q = """SELECT type FROM sbmFIELDDESC where name='%s'""" %(hgf_field)
    return run_sql(q)[0][0]

def get_field_from_sbmfielddesc(hgf_field):
    """returns field for a specific fielddescriptor"""
    q = """SELECT * FROM sbmFIELDDESC where name='%s'""" %(hgf_field)
    return run_sql(q)[0]


def update_eltype_in_sbmfielddesc(hgf_field,eltype,modification_text,fidesc):
    q = """UPDATE sbmFIELDDESC SET type='%s',modifytext='%s',fidesc='%s' where name='%s' """ %(eltype,modification_text,fidesc,hgf_field)
    run_sql(q)

def insert_coll_or_doctype_into_collection(id_webcoll,name,dbquery,nbrecs="NULL",reclist="NULL"):
    """defines collection/doctype in table 'collection'"""
    if dbquery == "NULL": q = """INSERT INTO collection (id,name,dbquery,nbrecs,reclist) VALUES (%s,'%s',%s,%s,%s)""" %(id_webcoll,name,dbquery,nbrecs,reclist) #NULL-dbquery should not be inserted as a string 'NULL'
    else: q = """INSERT INTO collection (id,name,dbquery,nbrecs,reclist) VALUES (%s,'%s','%s',%s,%s)""" %(id_webcoll,name,dbquery,nbrecs,reclist) #dbquery should be a string
    run_sql(q)

def insert_coll_or_doctype_into_collection_collection(id_dad,id_son,score,_type="r"):
    """defines collections in table 'collection_collection'. """
    q = """INSERT INTO collection_collection (id_dad,id_son,type,score) VALUES (%s,%s,'%s',%s)""" %(id_dad,id_son,_type,score)
    run_sql(q)

def insert_name_into_collectionname(id_webcoll,value,ln="en",_type="ln"):
    q = """INSERT INTO collectionname (id_collection,ln,type,value) VALUES
    (%s,'%s','%s','%s')""" %(id_webcoll,ln,_type,value)
    run_sql(q)

def insert_parameters(doctype):
    """ inserting parameters into sbmPARAMETER
    Warning: Do NOT clone parameters from DEMO-form!
    """
    if ("CFG_WEBSTYLE_TEMPLATE_SKIN" in globals()): inst = CFG_WEBSTYLE_TEMPLATE_SKIN
    else: inst = "default"
    params = {"authorfile":"hgf_1001_a","edsrn":"rn","emailFile":"SuE","fieldnameMBI":"mod_%s" %(doctype),"newrnin":"","status":"ADDED","titleFile":"hgf_245__a","createTemplate":"genecreate.tpl","sourceTemplate":"gene.tpl","modifyTemplate":"genemodify.tpl","documenttype":"fulltext","iconsize":"180>,700>","paths_and_suffixes":'{"hgf_file":""}',"rename":"<PA>file:rn</PA>","autorngen":"Y","counterpath":"lastid_%s_<PA>yy</PA>" %(inst),"rnformat":"%s-<PA>yy</PA>" %(inst.upper()),"nblength":"5","rnin":"combo%s" %(inst),"yeargen":"AUTO","files_to_be_stamped":"hgf_file","latex_template":"demo-stamp-left.tex","latex_template_vars":"{'REPORTNUMBER':'FILE:rn' ,'DATE':'FILE:hgf_245__f'}","stamp":"first"}
    if ("CFG_WEBSTYLE_TEMPLATE_SKIN" in globals()): # change to institute templates
        params["createTemplate"] = "genecreate_%s.tpl" % CFG_WEBSTYLE_TEMPLATE_SKIN.lower()
        params["modifyTemplate"] = "genemodify_%s.tpl" % CFG_WEBSTYLE_TEMPLATE_SKIN.lower()
        params["sourceTemplate"] = "gene_%s.tpl" % CFG_WEBSTYLE_TEMPLATE_SKIN.lower()
    for key in params.keys(): insert_parameter_doctype(doctype, key, params[key])

def insert_collection_fielddesc(doctype):
    """insert collection col_doctype into table sbmFIELDDESC"""
    ## col_doctype
    elname = "col_" + doctype
    elmarccode = "980__a"
    eltype = "H"
    elsize = ""
    elrows = ""
    elcols = ""
    elmaxlength = ""
    elval = doctype
    elfidesc = ""
    elmodifytext = "<br />HGF-Collection:&nbsp;"
    insert_element_details(elname, elmarccode, eltype, elsize, elrows, elcols, elmaxlength, elval, elfidesc, elmodifytext) # insert into sbmFIELDDESCR

def insert_repnr_fielddesc(inst):
    """rn_doctype #insert modification reportnumber for doctype into sbmFIELDDESC"""
    elname = "rn"
    elmarccode = "037__a"
    eltype = "I"
    elsize = "30"
    elrows = ""
    elcols = ""
    elmaxlength = ""
    elval = "%s-<YYYY>-?????" %(inst.upper())
    elfidesc = ""
    elmodifytext = ""
    insert_element_details(elname, elmarccode, eltype, elsize, elrows, elcols, elmaxlength, elval, elfidesc, elmodifytext) # insert into sbmFIELDDESCR

def insert_fielddesc(element, hgf_field):
    """insert marc-fields into table sbmFIELDDESC
    @elements: list of all values of a field
    alephcode,marccode,type,size,rows,cols,maxlength,val,fidesc,cd,md,modifytext,fddfi2,cookie
    """
    elname = hgf_field
    elmarccode = element[1]
    eltype = element[2]
    elsize = element[3]
    elrows = element[4]
    elcols = element[5]
    elmaxlength = element[6]
    elval = element[7]
    elfidesc = element[8]
    elmodifytext = element[11]
    insert_element_details(elname, elmarccode, eltype, elsize, elrows, elcols, elmaxlength, elval, elfidesc, elmodifytext) # insert into sbmFIELDDESCR

def insert_element_details_force(elname, elmarccode, eltype, elsize, elrows, elcols, elmaxlength, elval, elfidesc, elmodifytext):
    """Insert details of a new Element into the WebSubmit database IF there are not already elements
    with the same element name (name).
    @param elname: unique Element id/name (name)
    @param elmarccode: element's MARC code
    @param eltype: type of element
    @param elsize: size of element
    @param elrows: number of rows in element
    @param elcols: number of columns in element
    @param elmaxlength: element maximum length
    @param elval: element default value
    @param elfidesc: element description
    @param elmodifytext: element's modification text
    @return: 0 (ZERO) if insert is performed; 1 (ONE) if insert not performed due to rows existing for given Element."""

    # insert new Check:
    q = """INSERT INTO sbmFIELDDESC (name, alephcode, marccode, type, size, rows, cols, maxlength, val, fidesc, cd, md, modifytext, fddfi2) VALUES(%s, NULL,%s, %s, %s, %s, %s, %s, %s, %s, CURDATE(), CURDATE(), %s, NULL)"""
    run_sql(q, ( elname, elmarccode, (eltype != "" and eltype) or (None), (elsize != "" and elsize) or (None),  (elrows != "" and elrows) or (None),  (elcols != "" and elcols) or (None),                    (elmaxlength != "" and elmaxlength) or (None),          (elval != "" and elval) or (None),                     (elfidesc != "" and elfidesc) or (None), (elmodifytext != "" and elmodifytext) or (None) ) )

def delete_collection_from_collection(name):
    q = """DELETE FROM collection WHERE name='%s'""" %(name)
    run_sql(q)

def delete_collection_from_collection_collection(id_webcoll):
    q = """DELETE FROM collection_collection WHERE id_dad=%s OR id_son=%s""" %(id_webcoll,id_webcoll)
    run_sql(q)

def delete_field_from_submissionpage(doctype, action, pagenum):
    q = """DELETE FROM sbmFIELD WHERE subname=%s AND pagenb=%s"""
    run_sql(q, ("""%s%s""" % (action, doctype), pagenum))

def delete_mbifielddescr(doctype):
    q = """DELETE FROM sbmFIELDDESC WHERE name='mod_%s'""" %(doctype)
    run_sql(q)
    q = """DELETE FROM sbmFIELDDESC WHERE name='rn_%s'""" %(doctype)
    run_sql(q)
    q = """DELETE FROM sbmFIELDDESC WHERE name='mrn_%s'""" %(doctype)
    run_sql(q)

def delete_collection_from_fielddesc(doctype):
    q = """DELETE FROM sbmFIELDDESC WHERE name='col_%s'""" %(doctype)
    run_sql(q)


def delete_hgf_field_from_fielddesc(hgf_field):
    q = """DELETE FROM sbmFIELDDESC WHERE name='%s'""" %(hgf_field)
    run_sql(q)

def delete_name_from_collectionname(name):
    q = """DELETE FROM collectionname WHERE value='%s'""" %(name)
    run_sql(q)
################### End database help functions ############

################### help functions #########################

def replace_null(a):
    if a == "NULL": return ""
    else: return a

def get_order(order_values, new_order_values, number):
    """calculate the new_order"""
    all_values_set = set(order_values) & set(new_order_values)
    if number in all_values_set:
        for i in range(int(number), int(number)+10000):
            if i in all_values_set: continue
            new_number = i
            return new_number
    else: return number

def merge_sbmfield(doctype, config, inst, field):
    """make institutianl changes in fields"""
    sbmfield = [field]
    field_parts = config[inst][doctype][field]
    for i in range(len(field_parts)): #length should be 3
        if field_parts[i] == "-":
            if i == 2: #order
                if field in config["order"].keys():
                    part = config["order"][field]
            else: part = config["default_form"][field][i] #take the default if "-"
        else: part = field_parts[i]
        sbmfield.append(part)
    return sbmfield

def make_selectbox(config,doctype):
    """create select box for modification form. All fields in select box
    appear in "to change" fields in the modification form"""
    doctype_fields = get_fields_from_sbmfield(doctype) #get doctype_fields
    default_keys = config["default_form"].keys()
    options = ""
    nr = 0
    #same field order as in submit
    fields_order = sort_hgf_fields(default_keys, config, doctype)

    for field in fields_order:
        #if field in config["fielddesc"].keys():
        #    if config["fielddesc"][field][1].lower() == "h":
        #continue # hidden fields should not be modified
        if field in ["hgf_start", "hgf_end", "hgf_coll", "hgf_report",
                "hgf_thesis", "hgf_conf", "hgf_talk", "hgf_book", "hgf_jourart",
                "hgf_patent", "hgf_unpub", "hgf_other", "hgf_master"]:
            continue # fields should not be modified
        if field.startswith("col_"): continue # collection value
        if field == "rn": continue # internal reportnr (important to modify records)
        if config["default_form"][field][0] == "hidden":  # hidden fields should not be modified
            option = '<option value="%s" selected="selected" style="display:none">%s</option>' % (field,config["default_form"][field][0])
            options += option
        else:
            option = '<option value="%s" selected="selected">%s</option>' % (field, config["default_form"][field][0])
            options += option
            nr += 1
    select_box = '<select name="mod_%s[]" size="%s" multiple><option value="Select:">Select:</option>%s</select>' %(doctype,nr+1,options)
    return select_box

def generate_css(fieldlabels):
    """create and write a list with all classes defined in the html representation of the fields.
    fieldlabels: list with all span-fieldlabels"""
    classes_unique = []
    for fieldlabel in fieldlabels:
        if not "class" in fieldlabel: continue
        class_lists = re.findall(r'class=\"([^\"]*)\"', fieldlabel)
        for cl in class_lists:
            classes = cl.split()
            for clas in classes:
                if clas in classes_unique:
                    continue
                classes_unique.append(clas)
    classes_unique.sort()
    write_css(classes_unique)

def write_css(css_classes):
    """write css-stylesheet file"""
    if ("CFG_WEBSTYLE_TEMPLATE_SKIN" in globals()):    cssfile = os.path.join(os.getcwd(), "css_file_" + CFG_WEBSTYLE_TEMPLATE_SKIN.lower())
    else: cssfile = os.path.join(os.getcwd(), "css_file")
    classtring = ""
    for clas in css_classes: classtring += "." + clas + "{}\n"
    wd = open(cssfile, "w")
    wd.write(classtring)
    wd.close()

def read_javascript_includes():
    """return javascript includes for autosuggest as text"""
    if "CFG_PREFIX" in globals():
        js_filepath = os.path.join(CFG_PREFIX, "var/www/js/jquery/jquery-lib.html")
        if os.path.exists(js_filepath):
            f = open(js_filepath, "r")
            js_text = f.read()
            f.close()
            return js_text
        else: return None
    else: return None

###################End help functions #####################


################### main functions #########################

def build_or_remove_fielddesc(config):
    """build or delete fielddescriptors"""
    for hgf_field in config["fielddesc"].keys():
        if arg == "-d": delete_hgf_field_from_fielddesc(hgf_field)
        if arg == "-c":
            values = config["fielddesc"][hgf_field]
            values = map(replace_null, values) #replace NULL by ""
            insert_fielddesc(values, hgf_field)

def build_or_remove_schema(config):
    """Build or delete submission-collections"""
    sbmcollections = config["schema"].keys()
    for sbmcoll in sbmcollections:
        #if not sbmcoll == "Thesis": continue
        if arg == "-d": #deleting
            collection_id = get_id_of_collection_name(sbmcoll)
            delete_submission_collection_details(collection_id) #sbmCOLLECTION
            delete_submission_collection_from_submission_tree(collection_id)#sbmCOLLECTION_sbmCOLLECTION

        if arg == "-c": #creating
            id_son = insert_submission_collection(sbmcoll) #sbmCOLLECTION
            ## get the maximum catalogue score of the existing collection children:
            max_child_score = \
            get_maximum_catalogue_score_of_collection_children_of_submission_collection(0) # 0: highest collection
            ## add it to the collection, at a higher score than the others have:
            new_score = max_child_score + 1
            insert_collection_child_for_submission_collection(0, id_son, new_score) #sbmCOLLECTION_sbmCOLLECTION
            collection_id = get_id_of_collection_name(sbmcoll)
        doctypes = config["schema"][sbmcoll]
        for doctype in doctypes:
            if arg == "-c":
                ## insert the submission-collection/doctype link:
                ## get the maximum catalogue score of the existing doctype children:
                max_child_score = get_maximum_catalogue_score_of_doctype_children_of_submission_collection(collection_id)
                ## add it to the new doctype, at a higher score than the others have:
                new_score = max_child_score + 1
                insert_doctype_child_for_submission_collection(collection_id, doctype, new_score) #sbmCOLLECTION_sbmDOCTYPE
            elif arg == "-d": delete_doctype_children_from_submission_collection(collection_id) #sbmCOLLECTION_sbmDOCTYPE


def build_or_remove_doctypes(config,inst):
    """build doctypes for submission collection"""
    doctypes = config[inst].keys() #reading in config file, if Variable hgf_institute --> take defined doctypes by institute, else take the default
    b1 = set(doctypes) #all inst_doctypes
    b2 = set(config["default"].keys()) #all default_doctypes
    diff = b2.difference(b1) # doctypes which are in default but not in institutional changes
    if not diff == []: doctypes = doctypes + list(diff) # loop default doctypes at the end
    for doctype in doctypes:
        #if not doctype == "journal":continue
        if doctype == "specialfields":continue
        docname = get_docname_from_schema(doctype,config)
        doctypedescr = "This is a %s submission form." %(docname)
        if arg == "-d":
            print "deleting Doctype: %s" %(doctype)
            delete_all_functions_foraction_doctype(doctype, "SBI") #sbmFUNCTIONS
            delete_all_functions_foraction_doctype(doctype, "MBI") #sbmFUNCTIONS
            delete_doctype(doctype) #sbmDOCTYPE
            delete_all_submissions_doctype(doctype) #sbmIMPLEMENT
            delete_all_parameters_doctype(doctype) #sbmPARAMETERS
            delete_field_from_submissionpage(doctype, "SBI", "1") #sbmFIELD
            delete_field_from_submissionpage(doctype, "MBI", "1") #sbmFIELD
            delete_mbifielddescr(doctype) #sbmFIELDDESC
            delete_collection_from_fielddesc(doctype) #sbmFIELDDESC
            continue
        if (get_number_doctypes_docid(doctype) >0): continue #check if doctype already exists
        if doctype in diff:
            print "creating Doctype: %s (default)" %(doctype)
            inst = "default" # this can be done, because we loop over default doctypes at the end
        else: print "creating Doctype: %s" %(doctype)

        insert_doctype_details(doctype,docname,doctypedescr) #create doctype

        numrows_function = get_number_functions_action_doctype(doctype="DEMOTHE", action="SBI")

        #clone_functions_foraction_fromdoctype_todoctype("DEMOTHE", doctype, "SBI") #clone actions/functions from DEMOTHE
        #clone_functions_foraction_fromdoctype_todoctype("DEMOTHE", doctype, "MBI") #clone actions/functions from DEMOTHE

        #SBI without cloning --add function parameter
        #add_function_parameter("Report_Number_Generation", "autorngen")
        #add_function_parameter("Report_Number_Generation", "counterpath")
        #add_function_parameter("Report_Number_Generation", "edsrn")
        #add_function_parameter("Report_Number_Generation", "nblength")
        #add_function_parameter("Report_Number_Generation", "rnformat")
        #add_function_parameter("Report_Number_Generation", "rn")
        #add_function_parameter("Report_Number_Generation", "yeargen")

        #add_function_parameter("Stamp_Uploaded_Files", "files_to_be_stamped")
        #add_function_parameter("Stamp_Uploaded_Files", "latex_template")
        #add_function_parameter("Stamp_Uploaded_Files", "latex_template_vars")
        #add_function_parameter("Stamp_Uploaded_Files", "layer")
        #add_function_parameter("Stamp_Uploaded_Files", "stamp")
        #add_function_parameter("Stamp_Uploaded_Files", "switch_file")

        #add_function_parameter("Move_Files_to_Storage", "documenttype")
        #add_function_parameter("Move_Files_to_Storage", "iconsize")
        #add_function_parameter("Move_Files_to_Storage", "paths_and_doctypes")
        #add_function_parameter("Move_Files_to_Storage", "paths_and_restrictions")
        #add_function_parameter("Move_Files_to_Storage", "paths_and_suffixes")
        #add_function_parameter("Move_Files_to_Storage", "rename")

        #add_function_parameter("Print_Success", "edsrn")
        #add_function_parameter("Print_Success", "newrnin")
        add_function_parameter("Print_Success", "status")

        #add_function_parameter("Mail_Submitter", "authorfile")
        #add_function_parameter("Mail_Submitter", "edsrn")
        #add_function_parameter("Mail_Submitter", "emailFile")
        #add_function_parameter("Mail_Submitter", "newrnin")
        #add_function_parameter("Mail_Submitter", "status")
        #add_function_parameter("Mail_Submitter", "titleFile")

        #MBI without cloning --add function parameter
        add_function_parameter("Get_Report_Number","edsrn")
        add_function_parameter("Get_Recid","record_search_pattern")
        add_function_parameter("Create_Modify_Interface_hgf", "fieldnameMBI")
        add_function_parameter("Send_Modify_Mail_hgf", "fieldnameMBI")
        add_function_parameter("Send_Modify_Mail_hgf", "addressesMBI")
        add_function_parameter("Send_Modify_Mail_hgf", "emailFile")
        add_function_parameter("Send_Modify_Mail_hgf", "sourceDoc")
        #email_params={"addressesMBI":"","emailFile":"SuE","fieldnameMBI":"mod_%s" %doctype,"sourceDoc":doctype}

        #SBI without cloning --insert function details
        #insert_function_details("Create_Recid", "Creating Record-ID")
        #insert_function_details("Report_Number_Generation", "Generate Report number")
        #insert_function_details("Stamp_Uploaded_Files", "Stamp some of the files that were uploaded during a submission")
        #insert_function_details("Move_Files_to_Storage", "Attach files received from chosen file input element(s)")
        #insert_function_details("Create_hgf_collection", "create workflow collections")
        #insert_function_details("Convert_hgf_fields", "postprocessing of the record data. convert email,date,collections...")
        insert_function_details("Create_hgf_record_json", "create hgf record in json format")
        insert_function_details("Send_hgf_RT_Ticket", "Sends an RT Ticket")
        #insert_function_details("Make_HGF_Record", "convert HGF-record into MARCxml")
        #insert_function_details("Insert_Record", "insert record into database")
        insert_function_details("Print_hgf_Success", "inform the user about the successful submission")
        #insert_function_details("Mail_Submitter", "mail to the submitter of the record")
        #insert_function_details("Move_to_Done", "backup curdir")

        #MBI without cloning --insert function details
        insert_function_details("Get_Report_Number", "get the report number")
        insert_function_details("Get_Recid", "get the record-id")
        insert_function_details("Is_Submitter_Or_Editor", "check for modify permissions")
        insert_function_details("Prefill_hgf_fields", "prefill hgf fields in modify form")
        insert_function_details("Create_Modify_Interface_hgf", "new create modify interface function for hgf")
        insert_function_details("Insert_hgf_modify_record", "replace old record by new one completely")
        insert_function_details("Send_Modify_Mail_hgf", "replace old modify mail by new hgf mail")

        #SBI without cloning --insert function into websubmit steps
        #insert_function_into_submission_at_step_and_score(doctype, "SBI", "Create_Recid", "1", "10")
        #insert_function_into_submission_at_step_and_score(doctype, "SBI", "Report_Number_Generation", "1", "20")
        #insert_function_into_submission_at_step_and_score(doctype, "SBI", "Stamp_Uploaded_Files", "1", "30")
        #insert_function_into_submission_at_step_and_score(doctype, "SBI", "Move_Files_to_Storage", "1", "40")
        #insert_function_into_submission_at_step_and_score(doctype, "SBI", "Create_hgf_collection", "1", "50")
        #insert_function_into_submission_at_step_and_score(doctype, "SBI", "Convert_hgf_fields", "1", "60")
        insert_function_into_submission_at_step_and_score(doctype, "SBI", "Create_hgf_record_json", "1", "70")
        insert_function_into_submission_at_step_and_score(doctype, "SBI", "Send_hgf_RT_Ticket", "1", "80")
        #insert_function_into_submission_at_step_and_score(doctype, "SBI", "Make_HGF_Record", "1", "80")
        #insert_function_into_submission_at_step_and_score(doctype, "SBI", "Insert_Record", "1", "90")
        insert_function_into_submission_at_step_and_score(doctype, "SBI", "Print_hgf_Success", "1", "100")
        #insert_function_into_submission_at_step_and_score(doctype, "SBI", "Mail_Submitter", "1", "110")
        #insert_function_into_submission_at_step_and_score(doctype, "SBI", "Move_to_Done", "1", "120")

        #MBI without cloning --insert function into websubmit steps
        #insert_function_into_submission_at_step_and_score(doctype, "MBI", "Get_Report_Number", "1", "10")
        #insert_function_into_submission_at_step_and_score(doctype, "MBI", "Get_Recid", "1", "20")
        #insert_function_into_submission_at_step_and_score(doctype, "MBI", "Is_Submitter_Or_Editor", "1", "30")
        #insert_function_into_submission_at_step_and_score(doctype, "MBI", "Prefill_hgf_fields", "1", "40")
        #insert_function_into_submission_at_step_and_score(doctype, "MBI", "Create_Modify_Interface_hgf", "1", "50")
        #insert_function_into_submission_at_step_and_score(doctype, "MBI", "Get_Report_Number", "2", "10")
        #insert_function_into_submission_at_step_and_score(doctype, "MBI", "Get_Recid", "2", "20")
        #insert_function_into_submission_at_step_and_score(doctype, "MBI", "Is_Submitter_Or_Editor", "2", "30")
        #insert_function_into_submission_at_step_and_score(doctype, "MBI", "Create_hgf_collection", "2", "40")
        #insert_function_into_submission_at_step_and_score(doctype, "MBI", "Convert_hgf_fields", "2", "50")
        #insert_function_into_submission_at_step_and_score(doctype, "MBI", "Create_hgf_record_json", "2", "60")
        #insert_function_into_submission_at_step_and_score(doctype, "MBI", "Make_HGF_Record", "2", "70")
        #insert_function_into_submission_at_step_and_score(doctype, "MBI", "Insert_hgf_modify_record", "2", "80")
        #insert_function_into_submission_at_step_and_score(doctype, "MBI", "Move_Files_to_Storage", "2", "90")
        #insert_function_into_submission_at_step_and_score(doctype, "MBI", "Print_Success_MBI", "2", "100")
        #insert_function_into_submission_at_step_and_score(doctype, "MBI", "Send_Modify_Mail_hgf", "2", "110")
        #insert_function_into_submission_at_step_and_score(doctype, "MBI", "Move_to_Done", "2", "120")

        ## add action in sbmIMPLEMENT for doctype
        #insert_submission_details_clonefrom_submission(doctype,"SBI","DEMOTHE")
        #insert_submission_details_clonefrom_submission(doctype,"MBI","DEMOTHE")

        # add action in sbmIMPLEMENT for doctype --without cloning
        insert_submission_details(doctype, "SBI", "Y", "1", "1", "", "1", "1", "0", "")
        insert_submission_details(doctype, "MBI", "Y", "1", "2", "", "", "0", "0", "")

        ## add sbmParameters (i.e. bibconvert template name for marc-fields)
        insert_parameters(doctype)

        ## create institutes defined fields
        create_mask(config, doctype, inst)

def create_user_defined_fielddesc(sbmfield,field,config):
    """create institutional defined fielddescriptor
    sbmfield: [fieldname,fielddesc,m/o,r/d]
    element: alephcode,marccode,type,size,rows,cols,maxlength,val,fidesc,cd,md,modifytext,fddfi2,cookie
    """
    hgf_field = sbmfield[0]
    if hgf_field.startswith("hgf"):
        element = config["fielddesc"][hgf_field]
    else:
        if hgf_field in config["default_form"]: element = get_field_from_sbmfielddesc(hgf_field)[1:]
        else: return "","O" #non hgf-fields (defined collections,...)

    if hgf_field == "hgf_start":
        ### fieldlabel = '<TABLE class="submission" WIDTH="100%" BGCOLOR="#99CC00" ALIGN="center" CELLSPACING="2" CELLPADDING="2" BORDER="1"><TR><TD ALIGN="left"><br /><b style="font-size: 1.4em;">dummy:</b><br /><br />' #define html-Table
    # define a fieldset which can then be used for internal element
    # placement relative to that div so we end up with a table-less
    # form doing arrangement entirely in CSS
        if read_javascript_includes():
            fieldlabel = '%s<fieldset id="submissionfields"><legend id="submissionlegend">dummy</legend><div id="loadingMsg"><img src="/img/search.png" alt="Loading..." />Loading data. Please stand by...</div>' %read_javascript_includes()
        else:
            fieldlabel = '<fieldset id="submissionfields"><legend id="submissionlegend">dummy</legend><div id="loadingMsg"><img src="/img/search.png" alt="Loading..." />Loading data. Please stand by...    </div>'
        fieldlabel = fieldlabel.replace("dummy",sbmfield[1])
        return fieldlabel,sbmfield[2].upper()
    if hgf_field == "hgf_end":
        ### fieldlabel = '<br /><br /></td></tr></table><br />'
    # close the main fieldset
        fieldlabel = '</fieldset>'
        return fieldlabel,sbmfield[2].upper()
    if hgf_field == "hgf_comment": #technical field
        if sbmfield[1] == "hidden": pass# 'hidden' is generated by create_mask function
        else:
            fieldlabel = "<span class=\"Comment\" id=\"hgf_comment\">%s</span>" % sbmfield[1]
            return fieldlabel,sbmfield[2].upper()
    if element[1] == "": #no marccode
        unique_id = sbmfield[0] # i.e. hgf_import is Input-field, but not MARC
        id1 = ""
        id2 = ""
    else :
        id1 = element[1][0:3]
        id2 = element[1]
        unique_id = hgf_field.replace("hgf_","")
    size,rows,cols = element[3:6]
    value = element[7]
    if value == "NULL": value = ""
    fieldtext = sbmfield[1]
    fieldtype = None

    if ("CFG_WEBSTYLE_TEMPLATE_SKIN" in globals()): # suffix for twiki page at GSI
        suffix = "#" + CFG_WEBSTYLE_TEMPLATE_SKIN.upper() + "_font"
    else: suffix = ""
    #Insert Helptext#
    if ("CFG_HGF_WIKI_BASE_URL" in globals()):
        # Twiki needs all page titles to start with a capital letter.
        # Therefore, capitalize() the uniq_id when constructing the URL.
        help_text = "<span class=\"Helptext\" id=\"%(unique_id)s%(suffix)s\"><a href=\"%(CFG_HGF_WIKI_BASE_URL)s%(unique_id)s%(suffix)s\" alt=\"Help\" target=\"_blank\"><img src=\"/img/hgfinfo.png\"></a></span>" %{'unique_id':unique_id.capitalize(),"CFG_HGF_WIKI_BASE_URL":CFG_HGF_WIKI_BASE_URL,"suffix":suffix}
    else:
        #help_text = "<span class=\"Helptext\" id=\"%(unique_id)s%(suffix)s\"><a href=\"http://invenio-wiki.gsi.de/cgi-bin/view/Main/%(unique_id)s%(suffix)s\" alt=\"Help\" target=\"_blank\"><img src=\"/img/hgfinfo.png\"></a></span>" %{'unique_id':unique_id,"suffix":suffix}
        help_text = "<span class=\"Helptext\" id=\"%(unique_id)s%(suffix)s\"><img src=\"/img/hgfinfo.png\"></span>" %{'unique_id':unique_id,"suffix":suffix}

    if element[2] == "I": #Input text box
        fieldtype = "D" # set user defined input
        if sbmfield[2] == "m":#fieldlevel
            fieldlabel = '<span class="MG%(id2)s G%(id2)s MG%(id1)s G%(id1)s MG G"><label for="I%(unique_id)s" class="L%(unique_id)s ML%(id2)s L%(id2)s ML%(id1)s L%(id1)s ML L">%(fieldtext)s</label> %(help_text)s <input name="%(hgf_name)s" id="I%(unique_id)s" class="MI%(id2)s I%(id2)s MI%(id1)s I%(id1)s MI I"></input></span>' % {'id1':id1,'id2':id2,'unique_id':unique_id,'size':size,'fieldtext':fieldtext,'hgf_name':hgf_field,'help_text':help_text}
        else:
            if unique_id == sbmfield[0]: #no marccode but Input-field
                fieldlabel = '<span class="G G%(unique_id)s"> <label for="I%(unique_id)s" class="L%(unique_id)s L">%(fieldtext)s</label> %(help_text)s <input name="%(hgf_name)s" id="I%(unique_id)s" class="I"></input> </span>' % {'unique_id':unique_id,'size':size,'fieldtext':fieldtext,'hgf_name':hgf_field,'help_text':help_text}
            else:
                fieldlabel = '<span class="G%(id2)s G%(id1)s G"> <label for="I%(unique_id)s" class="L%(id2)s L%(id1)s L">%(fieldtext)s</label> %(help_text)s <input name="%(hgf_name)s" id="I%(unique_id)s" class="I%(id2)s I%(id1)s I"></input> </span>' % {'id1':id1,'id2':id2,'unique_id':unique_id,'size':size,'fieldtext':fieldtext,'hgf_name':hgf_field,'help_text':help_text}
    elif element[2] == "T":    # Textarea
        fieldtype = "D"
        if sbmfield[2] == "m":#fieldlevel
            fieldlabel = '<span class="MG%(id2)s G%(id2)s MG%(id1)s G%(id1)s MG G"> <label for="I%(unique_id)s" class="ML%(id2)s L%(id2)s ML%(id1)s L%(id1)s ML L" >%(fieldtext)s</label> %(help_text)s <textarea name="%(hgf_name)s" id="I%(unique_id)s" class="MI%(id2)s I%(id2)s MI%(id1)s I%(id1)s MI I" cols="%(cols)s" rows="%(rows)s"></textarea> </span>' % {'id1':id1,'id2':id2,'unique_id':unique_id,'size':size,'rows':rows,'cols':cols,'fieldtext':fieldtext,'hgf_name':hgf_field,'help_text':help_text}
        else:
            fieldlabel = '<span class="G%(id2)s G%(id1)s G G%(unique_id)s"> <label for="I%(unique_id)s" class="L%(id2)s L%(id1)s L">%(fieldtext)s</label> %(help_text)s <textarea name="%(hgf_name)s" id="I%(unique_id)s" class="I%(id2)s I%(id1)s I" cols="%(cols)s" rows="%(rows)s"></textarea> </span>' % {'id1':id1,'id2':id2,'unique_id':unique_id,'size':size,'rows':rows,'cols':cols,'fieldtext':fieldtext,'hgf_name':hgf_field,'help_text':help_text}
    elif element[2].lower() == "h": #hidden field
        fieldtype = "D"
        if unique_id == sbmfield[0]:
            fieldlabel = '<span class="G"> <label for="I%(unique_id)s" class="L%(unique_id)s L"></label> <input type="hidden" name="%(hgf_name)s" id="I%(unique_id)s" value="%(value)s" class="I"></input> </span>' % {'unique_id':unique_id,'value':value,'hgf_name':hgf_field}
        else:
            fieldlabel = '<span class="G%(id2)s G%(id1)s G"> <label for="I%(unique_id)s" class="L%(unique_id)s L%(id2)s L%(id1)s L"></label> <input type="hidden" name="%(hgf_name)s" id="I%(unique_id)s" value="%(value)s" class="I%(id2)s I%(id1)s I"></input> </span>' % {'id1':id1,'id2':id2,'unique_id':unique_id,'value':value,'hgf_name':hgf_field}
    elif element[2] == "C": #check box
        fieldtype = "D" # set user defined input
        fieldlabel = make_specialfields(unique_id,id1,id2,size,fieldtext,hgf_field,help_text,sbmfield,config,"checkbox")
    elif element[2] == "F": #File field
        fieldtype = "D" # set user defined input
        if sbmfield[2] == "m":#fieldlevel
            if unique_id == sbmfield[0]: #no marccode but Input-field
                fieldlabel = '<span class="MG MG%(unique_id)s"> <label for="I%(unique_id)s" class="L%(unique_id)s ML">%(fieldtext)s</label> %(help_text)s <input type="file" name="%(hgf_name)s" id="I%(unique_id)s" class="MI"></input> </span>' % {'unique_id':unique_id,'size':size,'fieldtext':fieldtext,'hgf_name':hgf_field,'help_text':help_text}
            else:
                fieldlabel = '<span class="MG%(id2)s G%(id2)s MG%(id1)s G%(id1)s MG G"><label for="I%(unique_id)s" class="ML%(id2)s L%(id2)s ML%(id1)s L%(id1)s ML L">%(fieldtext)s</label> %(help_text)s <input type="file" name="%(hgf_name)s" id="I%(unique_id)s" class="MI%(id2)s I%(id2)s MI%(id1)s I%(id1)s MI I"></input></span>' % {'id1':id1,'id2':id2,'unique_id':unique_id,'size':size,'fieldtext':fieldtext,'hgf_name':hgf_field,'help_text':help_text}
        else:
            if unique_id == sbmfield[0]: #no marccode but Input-field
                fieldlabel = '<span class="G G%(unique_id)s"> <label for="I%(unique_id)s" class="L%(unique_id)s L">%(fieldtext)s</label> %(help_text)s <input type="file" name="%(hgf_name)s" id="I%(unique_id)s" class="I"></input> </span>' % {'unique_id':unique_id,'size':size,'fieldtext':fieldtext,'hgf_name':hgf_field,'help_text':help_text}
            else:
                fieldlabel = '<span class="G%(id2)s G%(id1)s G"> <label for="I%(unique_id)s" class="L%(id2)s L%(id1)s L">%(fieldtext)s</label> %(help_text)s <input name="%(hgf_name)s" type="file" id="I%(unique_id)s" class="I%(id2)s I%(id1)s I"></input> </span>' % {'id1':id1,'id2':id2,'unique_id':unique_id,'size':size,'fieldtext':fieldtext,'hgf_name':hgf_field,'help_text':help_text}
    elif element[2] == "R": #Radio button
        fieldtype = "D" # set user defined input
        fieldlabel = make_specialfields(unique_id, id1, id2, size, fieldtext, hgf_field, help_text, sbmfield, config, "radio")
    else:     return "","O" #other hgf-field with marccode (if exists)
    if fieldtype: #change fieldtype to user defined input. IMPORTANT: whole information about the field (spans, fieldname, input-field, textarea) are stored in the fieldlabel in the sbmFIELD herefore fidesc in sbmFIELDDESC has to be "" and eltype "D")
        eltype = get_eltype_from_sbmfielddesc(hgf_field)
        fidesc = ""
        modification_text = fieldlabel #modification text
        if eltype != fieldtype: update_eltype_in_sbmfielddesc(hgf_field, fieldtype, modification_text, fidesc) #
    return fieldlabel, sbmfield[2].upper()

def get_input(values, inputclass, typ):
    """make multiple radio buttons/ checkboxes """
    if typ == "radio": inputfield = '<input type="radio" name="%(hgf_name)s" checked="checkedvalue"  value="value2" %(inputclass)s></input>value1'
    if typ == "checkbox": inputfield = '<input type="checkbox" name="%(hgf_name)s" id="inputid" checked="checkedvalue"  value="value2" %(inputclass)s></input>'
    inputlabel = '<label for="inputid">value1</label>'
    inp_fields = ""
    values_count = 0
    values = eval(values)
    if isinstance(values[0], str): values = [values] #workaround for one checkbox/radio
    for tupl in values:
        values_count += 1
        value1 = tupl[0]
        value2 = tupl[1]
        if len(tupl) == 3: checkedvalue = tupl[2]
        else: checkedvalue = ""
        field = inputfield.replace("inputid", str(values_count)).replace("value2",value2).replace("checked=\"checkedvalue\"",checkedvalue)
        labelfield = inputlabel.replace("value1", value1).replace("inputid", str(values_count))
        inp_fields = inp_fields + field + labelfield
    return inp_fields

def make_specialfields(unique_id, id1, id2, size, fieldtext, hgf_field, help_text, sbmfield, config, typ):
    """create radio buttons and checkboxes"""
    if ("CFG_WEBSTYLE_TEMPLATE_SKIN" in globals()): inst = CFG_WEBSTYLE_TEMPLATE_SKIN
    else: inst = "default"
    if not "specialfields" in config[inst].keys():
        return  '<input name="%s">Please define %s in specialfields</input>' %(hgf_field,hgf_field)
    if not hgf_field in config[inst]["specialfields"].keys():
        return  '<input name="%s">Please define %s in specialfields</input>' %(hgf_field,hgf_field)
    values = config[inst]["specialfields"][hgf_field] #get special values for radio buttons
    if sbmfield[2] == "m": #fieldlevel
        if unique_id == sbmfield[0].replace("hgf_", ""): #no marccode but Input-field
            spanclass = '<span class="MG MG%(unique_id)s"> <label for="I%(unique_id)s" class="L%(unique_id)s ML">%(fieldtext)s</label> %(help_text)s'
            inputclass = 'class="MI"'
            inputfield = get_input(values, inputclass, typ)
        else:
            spanclass = '<span class="MG%(id2)s G%(id2)s MG%(id1)s G%(id1)s MG G"><label for="I%(unique_id)s" class="ML%(id2)s L%(id2)s ML%(id1)s L%(id1)s ML L">%(fieldtext)s</label> %(help_text)s'
            inputclass = 'class="MI%(id2)s I%(id2)s MI%(id1)s I%(id1)s MI I"'
            inputfield = get_input(values, inputclass, typ)
    else:
        if unique_id == sbmfield[0].replace("hgf_", ""): #no marccode but Input-field
            spanclass = '<span class="G G%(unique_id)s"> <label for="I%(unique_id)s" class="L%(unique_id)s L">%(fieldtext)s</label> %(help_text)s'
            inputclass = 'class="I"'
            inputfield = get_input(values, inputclass, typ)
        else:
            spanclass = '<span class="G%(id2)s G%(id1)s G"> <label for="I%(unique_id)s" class="L%(id2)s L%(id1)s L">%(fieldtext)s</label> %(help_text)s'
            inputclass = 'class="I%(id2)s I%(id1)s I"'
            inputfield = get_input(values, inputclass, typ)
    end = '</span>'
    span_field = spanclass + inputfield + end
    span_field = span_field %{'id1':id1, 'id2':id2, 'unique_id':unique_id, 'size':size, 'fieldtext':fieldtext, 'hgf_name':hgf_field, 'help_text':help_text, 'inputclass':inputclass}
    return span_field


def insert_mbifields(config, doctype):
    """defines the fields in sbmFIELD to appear in the modification form. hidden fields are already skipped in the create_mask function"""

    docname = get_docname_from_schema(doctype, config)
    fieldtext = '<table width="100%" bgcolor="#99CC00" align="center" cellspacing="2" cellpadding="2" border="1"><tr><td align="left"><br /><b>Modify a docname bibliographic information:</b><br /><br /><span style="color: red;">*</span>Reference Number:&nbsp;&nbsp;'
    fieldtext = fieldtext.replace("docname", docname)
    fieldlevel = "O"
    action = "MBI"
    pagenum = "1"
    fieldname = "rn"
    fieldshortdesc = fieldname.replace("hgf_", "")
    fieldcheck = ""
    insert_field_onto_submissionpage(doctype, action, pagenum, fieldname, fieldtext, fieldlevel, fieldshortdesc, fieldcheck) #insert into sbmFIELD

    ## hgf_change
    select_box = make_selectbox(config, doctype)
    elname = "mod_" + doctype
    elmarccode = ""
    eltype = "S"
    elsize = ""
    elrows = ""
    elcols = ""
    elmaxlength = ""
    elval = ""
    elfidesc = select_box # select box for modification form
    elmodifytext = ""
    insert_element_details(elname, elmarccode, eltype, elsize, elrows, elcols, elmaxlength, elval, elfidesc, elmodifytext) # inserrt into sbmFIELDDESCR


    fieldtext = '<br /><br /><span style="color: red;">*</span>Choose the fields to be modified:<br />'
    fieldlevel = "M"
    action = "MBI"
    pagenum = "1"
    fieldname = elname
    fieldshortdesc = elname.replace("hgf_", "")
    fieldcheck = ""
    insert_field_onto_submissionpage(doctype, action, pagenum, fieldname, fieldtext, fieldlevel, fieldshortdesc, fieldcheck) #insert into sbmFIELD

    #mbi_end
    fieldtext = '<br /><br /></td></tr></table><br />'
    fieldlevel = "O"
    action = "MBI"
    pagenum = "1"
    fieldname = "mbi_end"
    fieldshortdesc = fieldname.replace("hgf_","")
    fieldcheck = ""
    insert_field_onto_submissionpage(doctype, action, pagenum, fieldname, fieldtext, fieldlevel, fieldshortdesc, fieldcheck) #insert into sbmFIELD

def create_mask(config, doctype, inst):
    """"""
    #if fields to add, which are not in default_form, we have to add them now to the default_form before iterating over its fields:
    default_keys = config["default_form"].keys()
    a1 = set(default_keys) #all fields in default form
    if doctype in config[inst].keys(): #check if doctype defined for institional changes
        a2 = set(config[inst][doctype].keys()) #all fields for institutional form
    else: a2 = set([])
    diff = a2.difference(a1) # new fields which are not in default_form
    sbmcoll = get_submission_collection_fieldname(config, doctype) #get collection name for 980-Field
    diff.add(sbmcoll) #add 980-Field (submission collection)
    sbmcoll = "col_" + doctype #TTT
    #create sbmcoll FIELDDESC   TTT
    insert_collection_fielddesc(doctype)
    diff.add(sbmcoll) #add 980-Field (doctype collection)

    #add hidden fields
    hidden_fields = get_hidden_fields(config)
    diff |= set(hidden_fields)
    for new_field in diff:
        default_keys = default_keys[0:-1] + [new_field] + [default_keys[-1]] #update the list of default_keys with new_fields and add hgf_end to the end of list
        if new_field  == sbmcoll:
            config["default_form"].update({new_field:["hidden", "o"]}) #adding hidden collection
            continue
        if config["fielddesc"][new_field][2].lower() == "h":
            config["default_form"].update({new_field:["hidden", "o"]}) #adding hidden field
        else: config["default_form"].update({new_field:config[inst][doctype][new_field]}) #Warning adding to dictionary (we want to add only for current doctype, so we have to delete it at the end of this functions. TODO)

    default_keys = sort_hgf_fields(default_keys, config, doctype)   # create new field order
    for field in default_keys: #fields
        if doctype in config[inst].keys(): #check if doctype defined for institional changes
            if field in config[inst][doctype].keys():
                if config[inst][doctype][field] == "None": continue #field is None and will not appear on submissionpage
                else: sbmfield = merge_sbmfield(doctype, config, inst, field)# we have institutional changes
            else: sbmfield = [field] + config["default_form"][field]#field unchanged
        else:  sbmfield = [field] + config["default_form"][field]#field unchanged
        fieldtext_visible = sbmfield[1]
        fieldtext, fieldlevel = create_user_defined_fielddesc(sbmfield, config["default_form"][field], config)
        action = "SBI"
        pagenum = "1"
        fieldname = field
        fieldshortdesc = fieldtext_visible
        fieldcheck = ""
        insert_field_onto_submissionpage(doctype, action, pagenum, fieldname, fieldtext, fieldlevel, fieldshortdesc, fieldcheck) #sbmFIELD
        fieldlabels.append(fieldtext)
    insert_mbifields(config, doctype) # insert mbi-fields for modification mask

    for new_field in diff: del config["default_form"][new_field] #deleting added fields for current doctype. The next doctype starts with the default fields again



def webcollection(config):
    """make our collections visible at startpage and delete demo-collections"""
    webcolls = config["collection"].keys()
    webcolls.sort() #strange behavior, list is sorted Z-->A ??
    webcolls.reverse()
    for coll in webcolls:
        id_webcoll = get_max_id_webcollection() + 1 #
        if arg == "-c":
            coll_id = get_id_webcoll(coll)
            if coll_id: delete_col(coll_id) # delete existing collection
            insert_name_into_collectionname(id_webcoll, coll) #insert name of our collection into table 'collectionname'
            insert_coll_or_doctype_into_collection(id_webcoll, coll, dbquery="NULL") #insert collection into table 'collection'
            id_dad = 1
            id_son = id_webcoll
            score = get_coll_max_collection_collection_score(id_dad) + 10
            insert_coll_or_doctype_into_collection_collection(id_dad, id_son, score) #insert collection into 'collection_collection'
        if arg == "-d":
            delete_name_from_collectionname(coll)
            id_webcoll = get_id_webcoll(coll)
            if not (id_webcoll): continue
            delete_collection_from_collection_collection(id_webcoll)
            delete_collection_from_collection(coll)
        doccolls = config["collection"][coll].keys()
        doccolls.sort()
        doccolls.reverse()
        for doctype in doccolls:
            if doctype == "fieldname": continue #skip fieldname- its not a document type
            id_webcoll = get_max_id_webcollection() + 1
            if arg == "-c":
                dbquery = "collection:%s" %(doctype)
                docname = get_docname_from_schema(doctype, config)
                coll_id = get_id_webcoll(docname)
                if coll_id: delete_col(coll_id) # delete existing collection
                insert_name_into_collectionname(id_webcoll, docname) #insert name of our doctype into table 'collectionname'
                insert_coll_or_doctype_into_collection(id_webcoll, docname, dbquery) #insert doctype into table 'collection'
                id_dad = get_id_webcoll(coll)
                id_son = get_id_webcoll(docname)
                score = get_doctype_max_collection_collection_score(id_dad) + 10
                insert_coll_or_doctype_into_collection_collection(id_dad, id_son, score, _type="r") #insert doctype into 'collection_collection'
            if arg == "-d":
                docname = get_docname_from_schema(doctype, config)
                delete_name_from_collectionname(docname)
                delete_collection_from_collection(doctype)
                delete_collection_from_collection(docname)
################### end main functions ################################################

def process_all():
    """main-function to insert all Collections, Documenttypes, Fields into database (and everything needed to get instituts-defined submission and modification forms) """
    if check_args():  #check arguments
        config = read_conf() #read config-file
        inst = get_hgf_institute(config) #check which hgf-institute
        build_or_remove_fielddesc(config) #create/delete fielddescriptors (fields + marctags)
        insert_repnr_fielddesc(inst) #report number as hidden input in submit
        build_or_remove_doctypes(config, inst) #create/delete doctypes
        build_or_remove_schema(config) #create/delete collections for submit form
        generate_css(fieldlabels) #create css_file
        #webcollection(config)
    else: pass

if __name__ == "__main__":
    process_all()
    pass
