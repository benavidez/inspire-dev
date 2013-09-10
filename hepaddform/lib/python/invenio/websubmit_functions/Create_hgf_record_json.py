#from configobj import ConfigObj             #module for reading config-file
#from invenio.config import * #(local-conf)
import os, re
try:
    import json
except ImportError:
    import simplejson as json
#from Make_HGF_Record import processJSfile
#global curdir
#curdir = os.getcwd()
############## Classes #################################
class Create_json_hgf_record:
    """build hgf_record as json-structure"""

    def __init__(self): self.data = {}

    def add_jsondict(self, fieldname):
        """add field structure (json structure)"""

        jsondict = self.read_json(fieldname)
        for key in jsondict.keys():
            if key in self.data.keys():
                return
            else:
                if isinstance(jsondict[key], list): \
                        self.data[key] = jsondict[key] #value is already a list
                elif isinstance(jsondict[key], str): #value is string
                    if isinstance(eval(jsondict[key]), list): self.data[key] =\
                            eval(jsondict[key]) #value is a list in a string
                    else: self.data[key] = \
                            [eval(jsondict[key])] #value is just a string
                else: return

    def add_one_field(self, marcfield, subfield, value):
        """add field, no json structure"""

        if marcfield in self.data.keys():
            if subfield in self.data[marcfield][0].keys():\
                    self.data[marcfield].append({subfield:value})
            else: self.data[marcfield][0][subfield] = value
        else: self.data[marcfield] = [{subfield:value}]

    def add_field(self, fieldname):
        """add a field  (no json structure) to dictionary. """

        text = self.read_file(fieldname)
        fieldname = fieldname.replace("hgf_", "")
        marcfield = fieldname[0:5]
        subfield = fieldname[5:]
        self.add_one_field(marcfield, subfield, text)

    def write_json(self, fieldname="hgf_record"):
        """write python dictionary as json-file"""

        fw = open(os.path.join(curdir, fieldname), "w")
        json.dump(self.data, fw)
        fw.close()

    def read_json(self, fieldname):
        """read json-file and return dict"""

        fr = open(os.path.join(curdir, fieldname), "r")
        text = fr.read()
        fr.close
        if isinstance(eval(text), list):
            pass
        else:
            text = "[" + text +"]"
        jsontext = washJSONinput(text)
        jsondict = json.loads(jsontext, 'utf8')
        marcfield = fieldname.replace("hgf_", "")
        if isinstance(jsondict, list):
            jsondict = {marcfield:jsondict} # if json Frormat as list
        return jsondict

    def read_file(self, fieldname):
        """read a text-file (marcdata) and return text"""

        fr = open(os.path.join(curdir, fieldname), "r")
        text = fr.read()
        fr.close
        return text
        ## in case we have repeatable fields without
        ## subfields return a list of values
        #values = []
        #for line in lines:
        #    field = line.strip().replace("\n","").replace("\r","")
        #    if (field == "" or field == None): continue
        #    values.append(field)
        #return values

    def add_key_value(self, key, value):
        """set value to key"""

        self.data[key] = value

    def transform_values_into_list(self):
        """convert values of keys into lists for Make_HGF_Record"""

        for key in self.data.keys():
            if isinstance(self.data[key], list): continue
            self.data[key] = [self.data[key]]

    def process_master(self, fieldname):
        """write python dictionary as json-file for field hgf_master"""

        master = Create_json_hgf_record()
        master.add_jsondict(fieldname)
        master.write_json(fieldname)

    def print_values(self):    print self.data

############# End Classes #################################

############# Functions ###################################
def get_hgf_files():
    """get all hgf_files from curdir"""

    hgf_files = []
    for f in os.listdir(curdir):
        if not f.startswith("hgf_"):
            continue
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

    f = open(os.path.join(curdir, "SN"), "r")
    recid = f.read().replace("\n", "").replace("\r", "")
    f.close()
    return recid

def check_hgf_field(fieldname):
    """check if regular marcfield"""

    if len(fieldname) < 7: 
        return 0, ""
    if fieldname == "hgf_master": 
        return True, "master"
    if re.search('\d\d\d', fieldname):
        if len(fieldname) == 9: 
            return True, "json"
        else: 
            return True, "asci"
    else: return 0, ""

def backup_file(fieldname):
    """create bak-file"""

    bak_file = os.path.join(curdir, fieldname + ".bak")
    orig_file = os.path.join(curdir, fieldname)
    os.system("cp %s %s" %(orig_file, bak_file))

def Create_hgf_record_json(parameters, curdir, form, user_info=None):
    """run over all hgf_fields and create hgf_record in json-format"""

    hgf_files = get_hgf_files()
    hgf_rec = Create_json_hgf_record()
    for fieldname in hgf_files:
        #TODO: add 999C5 and 65017 to record
        if fieldname == 'hgf_999C5' or fieldname == 'hgf_65017':
            continue
        flag, ident = check_hgf_field(fieldname)
        if not flag:
            continue # no standard marc-field (e.g. hgf_vdb)
        if ident == "json":
            hgf_rec.add_jsondict(fieldname) #add json structure
        elif ident == "asci":
            hgf_rec.add_field(fieldname) #add non json structure
        elif ident == "master":
            backup_file(fieldname)
            hgf_rec.process_master(fieldname) #process master record
        else:
            continue
    recid = 1 #get_recordid()
    #convert values into lists for Make_HGF_Record
    hgf_rec.transform_values_into_list()
    hgf_rec.add_key_value("001", recid) #add recid to json-dict
    hgf_rec.write_json()
    #hgf_rec.print_values()
    #reclist = processJSfile('hgf_record', curdir)


#if __name__ == "__main__":
#Create_hgf_record_json()
