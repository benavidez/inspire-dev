# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2012 HGF
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
"""BibFormat element - Prints BibTeX meta-data
@author: arwagner
"""
__revision__ = "$Id$"

from invenio.config import CFG_SITE_LANG
from invenio.config import CFG_SITE_URL

def format_element(bfo, width="50"):
    """
    Prints a full BibTeX record.

    'width' must be bigger than or equal to 30.
    This format element is an example of large element, which does
    all the formatting by itself

    Unlike the CERN edition of this procedure this version expect more
    standard MARC. Additionally, unlike CERN it doesn't print fields
    depending on the document type, but always prints a field if we
    there is an according value in Marc. This has two reasons:
    - If it is in Marc it should mean something
    - BibTeX doesn't care if we get an additional field that the
      output formatter doesn't know for a specific doctype. But if it
      it knows it we can't pull it out of the hat if we we don't have
      it.

    @param width: the width (in number of characters) of the record
    """
    width = int(width)
    if width < 30:
        width = 30

    name_width = 19
    value_width = width-name_width
    recID = bfo.control_field('001')
 
    doctype = ''

    # In decent datasets we should have set the document type from our
    # authority mappings...
    tag = '3367_'
    fields = bfo.fields(tag)
    for f in fields:
       if f['2'] == 'BibTeX':
         doctype = f['a']
    
    # If we don't have it, try to guess it from the existence of some
    # fields. This is not perfect, but certainly better than mapping
    # everything to article.
    if doctype == '':
      if bfo.field("020__a") != '':
        doctype = 'BOOK'
      if bfo.field("490__a") != '':
        doctype = 'BOOK'
      if bfo.field("4900_a") != '':
        doctype = 'BOOK'
      if bfo.field("4901_a") != '':
        doctype = 'BOOK'
      if bfo.field("502__a") != '':
        doctype = 'PHDTHESIS'
      if bfo.field("088__a") != '':
        doctype = 'TECHREPORT'
        
    # If we didn't guess a type it was either an article or we fall
    # back to that type as the most common one.
    if doctype == '':
      doctype = 'ARTICLE'
 
    out = "@" + doctype + "{"

    #Print BibTeX key
    #
    #Try to have: author_name:recID
    #If author_name cannot be found, use primary_report_number
    #If primary_report_number cannot be found, use additional_report_number
    #If additional_report_number cannot be found, use title:recID
    #If title cannot be found, use only recID
    #
    #The construction of this key is inherited from old BibTeX format
    #written in EL, in old BibFormat.
    key = recID
    author = bfo.field("1001_a")
    if author != "":
        key = get_name(author)+":"+recID
    else:
        author = bfo.field("7001_a")
        if author != "":
            key = get_name(author)+":"+recID
        else:
          author = bfo.field("100__a")
          if author != "":
              key = get_name(author)+":"+recID
          else:
              author = bfo.field("700__a")
              if author != "":
                  key = get_name(author)+":"+recID
              else:
                  primary_report_number = bfo.field("037__a")
                  if primary_report_number != "":
                      key = primary_report_number
                  else:
                      additional_report_number = bfo.field("088__a")
                      if additional_report_number != "":
                          key = primary_report_number
                      else:
                          title = bfo.field("245__a")
                          if title != "":
                              key = get_name(title)+":"+recID

    # The bibtex key has to be ASCII, however we might have won some
    # utf-8 by the former procedure. We convert it to ascii and are
    # fine if we loose one char or the other in the process. This is
    # unavoidable.
    key = key.decode("utf-8")
    key = key.encode("ascii","ignore")

    out += key +","

    #Print authors
    #If author cannot be found, print a field key=recID
    import invenio.bibformat_elements.bfe_authors_hgf as bfe_authors
    authors = bfe_authors.format(bfo=bfo,
                                 limit="",
                                 separator=" and ",
                                 extension="",
                                 print_links="no")
    if authors == "":
        out += format_bibtex_field("key",
                                   recID,
                                   name_width,
                                   value_width)
    else:
        out += format_bibtex_field("author",
                                   authors,
                                   name_width,
                                   value_width)

    # TODO this is in principle correct, but Invenios default sets $e
    # to "ed." and this is hardcoded in the format element, while we
    # use "Editor"
    #Print editors
    import invenio.bibformat_elements.bfe_editors as bfe_editors
    editors = bfe_editors.format_element(bfo=bfo, limit="",
                                         separator=" and ",
                                         extension="",
                                         print_links="no")
    out += format_bibtex_field("editor",
                               editors,
                               name_width,
                               value_width)

    #Print title
    import invenio.bibformat_elements.bfe_title as bfe_title
    title = bfe_title.format_element(bfo=bfo, separator = ". ")
    out += format_bibtex_field("title",
                               title,
                               name_width,
                               value_width)

    #Print publisher
    publishers = []
    import invenio.bibformat_elements.bfe_publisher as bfe_publisher
    publisher = bfe_publisher.format_element(bfo=bfo)
    if publisher != "":
        publishers.append(publisher)

    #Print journal
    journals = []
    host_title = bfo.field("773__t")
    if host_title != "":
        journals.append(host_title)
    if host_title == '':
       host_title = bfo.field("440_0a")
       if host_title != "":
           journals.append(host_title)

    out += format_bibtex_field("journal",
                               ". ".join(journals),
                               name_width,
                               value_width)

    volumes = []
    host_volume = bfo.field("773__v")
    if host_volume != "":
        volumes.append(host_volume)
    if host_volume == '':
       host_volume = bfo.field("440_0v")
       if host_volume != "":
           volumes.append(host_volume)
    if host_volume == '':
       host_volume = bfo.field("490__v")
       if host_volume != "":
           volumes.append(host_volume)
    if host_volume == '':
       host_volume = bfo.field("4900_v")
       if host_volume != "":
           volumes.append(host_volume)
    if host_volume == '':
       host_volume = bfo.field("4901_v")
       if host_volume != "":
           volumes.append(host_volume)

    out += format_bibtex_field("volume",
                               ". ".join(volumes),
                               name_width,
                               value_width)

    issues = []
    host_issue = bfo.field("773__n")
    if host_issue != "":
        issues.append(host_issue)

    out += format_bibtex_field("issue",
                               ". ".join(issues),
                               name_width,
                               value_width)


    issns = []
    host_issn = bfo.field("773__x")
    if host_issn != "":
        issns.append(host_issn)
    if host_issn == '':
       host_issn = bfo.field("440_0x")
       if host_issn != "":
           issns.append(host_issn)
    if host_issn == '':
       host_issn = bfo.field("490__x")
       if host_issn != "":
           issns.append(host_issn)
    if host_issn == '':
       host_issn = bfo.field("4900_x")
       if host_issn != "":
           issns.append(host_issn)
    if host_issn == '':
       host_issn = bfo.field("4901_x")
       if host_issn != "":
           issns.append(host_issn)

    out += format_bibtex_field("issn",
                               ". ".join(issns),
                               name_width,
                               value_width)
    #Print school
    university = bfo.field("502__c")
    out += format_bibtex_field("school",
                               university,
                               name_width,
                               value_width)
    type = bfo.field("502__b")
    out += format_bibtex_field("type",
                               type,
                               name_width,
                               value_width)


    #Print address
    addresses = []
    publication_place = bfo.field("260__a")
    if publication_place != "":
        addresses.append(publication_place)

    out += format_bibtex_field("address",
                               ". ".join(addresses),
                               name_width,
                                   value_width)

    publishers = []
    publisher = bfo.field("260__b")
    if publisher != "":
        publishers.append(publisher)

    out += format_bibtex_field("publisher",
                               ". ".join(publishers),
                               name_width,
                                   value_width)

    #Print number
    numbers = []
    primary_report_number = bfo.field("037__a")
    if primary_report_number != "":
        numbers.append(primary_report_number)
    additional_report_numbers = bfo.fields("088__a")
    additional_report_numbers = ". ".join(additional_report_numbers)
    if additional_report_numbers != "":
        numbers.append(additional_report_numbers)
    out += format_bibtex_field("number",
                               ", ".join(numbers),
                               name_width,
                                  value_width)

    isbns = []
    host_isbns = bfo.field("020__a")
    if host_isbns != "":
        isbns.append(host_isbns)
    out += format_bibtex_field("isbn",
                               "=".join(isbns),
                               name_width,
                               value_width)

    series = bfo.field("490__a")
    if series == '':
      series = bfo.field("4901_a")
    if series == '':
      series = bfo.field("4900_a")
    out += format_bibtex_field("series",
                               series,
                               name_width,
                               value_width)

    #Print pages
    pages = []
    host_pages = bfo.field("773__p")
    if host_pages != "":
        pages.append(host_pages)
    phys_pagination = bfo.field("300__a")
    if phys_pagination != "":
        pages.append(phys_pagination)

    out += format_bibtex_field("pages",
                               ". ".join(pages),
                               name_width,
                               value_width)

    #Print year
    year = get_year(bfo.field("260__c"))
    if year == "":
        year = get_year(bfo.field("502__d"))

    out += format_bibtex_field("year",
                               year,
                               name_width,
                               value_width)

    #Print note
    note = []
    if bfo.field("500__a") != "":
       note.append(bfo.field("500__a"))
    if bfo.field("502__a") != "":
      note.append(bfo.field("502__a"))
    out += format_bibtex_field("note",
                               '; '.join(note),
                               name_width,
                               value_width)

    #Converted data might hold something valuable in 29510$a
    comment = bfo.field("29510a")
    out += format_bibtex_field("comment",
                               comment,
                               name_width,
                               value_width)

    #Print abstract
    abstract = bfo.field("520__a")
    out += format_bibtex_field("abstract",
                               abstract,
                               name_width,
                               value_width)

    keywords = []
    MeSH  = bfo.fields("650_2")
    Other = bfo.fields("650_7")
    for term in MeSH:
        keywords.append(term['a'])
    for term in Other:
        add = ''
        try:
          add = term['a']
        except:
          pass
        try:
          if add != '':
            add += ' (' + term['2'] + ')'
        except:
          pass
        if add != '':
          keywords.append(add)

    out += format_bibtex_field("keywords",
                               " / ".join(keywords),
                               name_width,
                               value_width)

    uniqueids = bfo.fields("0247_")
    doi = ''
    try:
       for id in uniqueids:
           if id['2'] == 'arXiv':
             out += format_bibtex_field("eprint",
                                  id['a'],
                                  name_width,
                                  value_width)
             out += format_bibtex_field("archivePrefix",
                                  "arXiv",
                                  name_width,
                                  value_width)
             out += format_bibtex_field("SLACcitation",
                                  "%%CITATION = " + id['a'] + ";%%",
                                  name_width,
                                  value_width)
           if id['2'] == 'pmid':
             out += format_bibtex_field("pubmed",
                                  id['a'],
                                  name_width,
                                  value_width)
           if id['2'] == 'pmc':
             out += format_bibtex_field("pmc",
                                  id['a'],
                                  name_width,
                                  value_width)
           if id['2'] == 'doi':
             doi = id['a']
    except:
        pass

    if doi == '':
       doi = bfo.field("773__a")

    out += format_bibtex_field("doi",
                               doi,
                               name_width,
                               value_width)

    
    url = CFG_SITE_URL + '/record/' + recID
    out += format_bibtex_field("url",
                               url,
                               name_width,
                               value_width)

    out +="\n}"

    return out


def format_bibtex_field(name, value, name_width=20, value_width=40):
    """
    Formats a name and value to display as BibTeX field.

    'name_width' is the width of the name of the field (everything before " = " on first line)
    'value_width' is the width of everything after " = ".

    6 empty chars are printed before the name, then the name and then it is filled with spaces to meet
    the required width. Therefore name_width must be > 6 + len(name)

    Then " = " is printed (notice spaces).

    So the total width will be name_width + value_width + len(" = ")
                                                               (3)

    if value is empty string, then return empty string.

    For example format_bibtex_field('author', 'a long value for this record', 13, 15) will
    return :
    >>
    >>      name    = "a long value
    >>                 for this record",
    """
    if name_width < 6 + len(name):
        name_width = 6 + len(name)
    if value_width < 2:
        value_width = 2
    if value is None or value == "":
        return ""

    #format name
    name = "\n      "+name
    name = name.ljust(name_width)

    #format value
    value = '"'+value+'"' #Add quotes to value
    value_lines = []
    last_cut = 0
    cursor = value_width -1 #First line is smaller because of quote
    increase = False
    while cursor < len(value):
        if cursor == last_cut: #Case where word is bigger than the max
                               #number of chars per line
            increase = True
            cursor = last_cut+value_width-1

        if value[cursor] != " " and not increase:
            cursor -= 1
        elif value[cursor] != " " and increase:
            cursor += 1
        else:
            value_lines.append(value[last_cut:cursor])
            last_cut = cursor
            cursor += value_width
            increase = False
    #Take rest of string
    last_line = value[last_cut:]
    if last_line != "":
        value_lines.append(last_line)

    tabs = "".ljust(name_width + 2)
    value = ("\n"+tabs).join(value_lines)

    return name + ' = ' + value + ","

def get_name(string):
    """
    Tries to return the last name contained in a string.

    In fact returns the text before any comma in 'string', whith
    spaces removed. If comma not found, get longest word in 'string'

    Behaviour inherited from old GET_NAME function defined as UFD in
    old BibFormat. We need to return the same value, to keep back
    compatibility with already generated BibTeX records.

    Eg: get_name("سtlund, عvind B") returns "سtlund".
    """
    names = string.split(',')

    if len(names) == 1:
        #Comma not found.
        #Split around any space
        longest_name = ""
        words = string.split()
        for word in words:
            if len(word) > len(longest_name):
                longest_name = word
        return longest_name
    else:
        return names[0].replace(" ", "")


def get_year(date, default=""):
    """
    Returns the year from a textual date retrieved from a record

    The returned value is a 4 digits string.
    If year cannot be found, returns 'default'
    Returns first value found.

    @param date: the textual date to retrieve the year from
    @param default: a default value to return if year not fount
    """
    import re
    year_pattern = re.compile(r'\d\d\d\d')
    result = year_pattern.search(date)
    if result is not None:
        return result.group()

    return default

def get_month(date, ln=CFG_SITE_LANG, default=""):
    """
    Returns the year from a textual date retrieved from a record

    The returned value is the 3 letters short month name in language 'ln'
    If year cannot be found, returns 'default'

    @param date: the textual date to retrieve the year from
    @param default: a default value to return if year not fount
    """
    import re
    from invenio.dateutils import get_i18n_month_name
    from invenio.messages import language_list_long

    #Look for textual month like "Jan" or "sep" or "November" or "novem"
    #Limit to CFG_SITE_LANG as language first (most probable date)
    #Look for short months. Also matches for long months
    short_months = [get_i18n_month_name(month).lower()
                    for month in range(1, 13)] # ["jan","feb","mar",...]
    short_months_pattern = re.compile(r'('+r'|'.join(short_months)+r')',
                                      re.IGNORECASE) # (jan|feb|mar|...)
    result = short_months_pattern.search(date)
    if result is not None:
        try:
            month_nb = short_months.index(result.group().lower()) + 1
            return get_i18n_month_name(month_nb, "short", ln)
        except:
            pass

    #Look for month specified as number in the form 2004/03/08 or 17 02 2004
    #(always take second group of 2 or 1 digits separated by spaces or - etc.)
    month_pattern = re.compile(r'\d([\s]|[-/.,])+(?P<month>(\d){1,2})([\s]|[-/.,])')
    result = month_pattern.search(date)
    if result is not None:
        try:
            month_nb = int(result.group("month"))
            return get_i18n_month_name(month_nb, "short", ln)
        except:
            pass

    #Look for textual month like "Jan" or "sep" or "November" or "novem"
    #Look for the month in each language

    #Retrieve ['en', 'fr', 'de', ...]
    language_list_short = [x[0]
                           for x in language_list_long()]
    for lang in language_list_short: #For each language
        #Look for short months. Also matches for long months
        short_months = [get_i18n_month_name(month, "short", lang).lower()
                        for month in range(1, 13)] # ["jan","feb","mar",...]
        short_months_pattern = re.compile(r'('+r'|'.join(short_months)+r')',
                                          re.IGNORECASE) # (jan|feb|mar|...)
        result = short_months_pattern.search(date)
        if result is not None:
            try:
                month_nb = short_months.index(result.group().lower()) + 1
                return get_i18n_month_name(month_nb, "short", ln)
            except:
                pass

    return default


