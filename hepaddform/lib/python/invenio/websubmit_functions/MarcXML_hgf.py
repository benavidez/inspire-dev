## This file is part of the extensions of Invenio for the HGF collaboration
##
## Provides class MarcXMLDocument() with methods to easily create 
## MARC XML documents.

from xml.dom.minidom import Document

class MarcXMLDocument(Document):
    """Based on class Document from module xml.dom.minidom.
    Provides methodes to easily create MARC XML documents.

    Usage:
    doc = MarcXMLDocument() initializes MARC XML Document doc
    doc.insertData(marcdata) inserts Marc data
       where marcdata is list of Marc records being a list of tuples
       containing Marc fields. Tuples may be (tag, entry) for controlfields
       and (tag, ind1, ind2, sfdict) for datafields with Indicators ind1
       and ind2 and a dictionary sfdict of the form {code: entry, ...}
       for its subfields.

    or
    
    doc = MarcXMLDocument() initializes MARC XML Document doc
    (<collection> ... </collection>)

       doc.createRecord() adds record to doc
       (<record> ... </record>)

          doc.createControlfield(nnn, entry) adds control field to record
          (<controlfield tag=nnn>entry</controlfield>)

          ...

          doc.createDatafield(nnn, i, j) adds data field to record
          (<datafield ind1=i ind2=j tag=nnn> ... /datafield>

             doc.createSubfield(c, entry) adds subfield to data field
             (<subfield code=c>entry</subfield>)

             ...

          ...

       ...
    """

    def __init__(self):
        Document.__init__(self)
        self.coll = self.createElement("collection")
        self.appendChild(self.coll)
        self.__NrOfRecords = 0

    def createRecord(self):
        self.record = self.createElement("record")
        self.coll.appendChild(self.record)
        self.__NrOfRecords += 1

    def createControlfield(self, tag, entry):
        self.controlfield = self.createElement("controlfield")
        self.controlfield.setAttribute("tag", tag)
        self.controlfield.appendChild(self.createTextNode(entry))
        self.record.appendChild(self.controlfield)

    def createDatafield(self, tag, ind1, ind2):
        self.datafield = self.createElement("datafield")
        self.datafield.setAttribute("tag", tag)
        self.datafield.setAttribute("ind1", ind1)
        self.datafield.setAttribute("ind2", ind2)
        self.record.appendChild(self.datafield)

    def createSubfield(self, code, entry):
        self.subfield = self.createElement("subfield")
        self.subfield.setAttribute("code", code)
        self.subfield.appendChild(self.createTextNode(entry))
        self.datafield.appendChild(self.subfield)

    def NumberOfRecords(self):
        return self.__NrOfRecords

    def insertData(self, marcdata):
        """Inserts Marc data into MARC XML document

        Input: marcdata: List of Marc records.
                         Record is list of tuples containing Marc fields.
                         Tuples may be (tag, entry) for controlfields and
                         (tag, ind1, ind2, sfdict) for datafields with
                         Indicators ind1 and ind2 and a dictionary sfdict
                         of the form {code: entry, ...} for its subfields.
        """

        # Loop over records in marcdata
        for record in marcdata:
            # Create record in XML document
            self.createRecord()

            # Loop over fields (= tuples) in record
            for field in record:
                # len(field) == 2 => Controlfield
                if len(field) == 2:
                    tag, entry = field
                    # Add controlfield to record
                    self.createControlfield(tag, entry)
                # len(f) == 4 => Datafield
                else:
                    tag, ind1, ind2, sfdict = field
                    # Add datafield to record
                    self.createDatafield(tag, ind1, ind2)
                    for key in sfdict:
                        # Add subfield to datafield
                        self.createSubfield(key, sfdict[key])
