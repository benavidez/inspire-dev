/*
 * function to autopopulate Grants
 * This function need a Array with the String element and has to live
 * outside of the $(document).ready-scope
 *
*/
function autopopulate_Grants(idGrants, id, tkfield) {
    var Grants = new Object();
    if (idGrants != null) {
       $.each(idGrants, function(i, value) {
           var srcurl2 = '/search?ln=de&cc=Grants&of=js&p=035__a:%22' + value + '%22';
           $.ajax({
               type: "GET",
               url: srcurl2,
               async: false,
               success: function(text) {
                   if (text != '') {
                      text = WashJSstr(text);
                      tmp = eval('[' + text + ']');
                      Grants[tmp[0][id]] = tmp[0];
                   }
               }
           });
           // Write Grants in Field	
           $.each(Grants, function(index, value) {
               $(tkfield).tokenInput('add', value);
           });
       });
    }
}

$(document).ready(function() {

    // Ensure that all fields are filled as required by calling
    // prefill(). Note that this function is only defined in modify
    if(typeof prefill == 'function') {
      prefill();
    }

    // general search parameters required to buil up urls
    var inveniobase = "/search";            // base of the search entry
    var collection  = "cc=Grants";          // collection to search
    var jsonformat  = "of=js";              // output format to use; 
                                            // this returns plain
                                            // text, we eval() it to
                                            // objects

    // parameters used for grant field (536). This search should
    // result in _all_ grants to be selectable.
    var searchmode  = "m1=r";               // use regexp matching
    var searchfield = "f1=";                // index to search
    var searchterm  = "p1";                 // how to search. No = as we
                                            
    // Tokeninput variables                 
    var toSearch    = "label";              // tag for tokeninput to search for
    var hintTxt     = "Search for Grants";  // tag for tokeninput to search for

    var srcurl = inveniobase
               + "?" + collection
               + "&" + searchmode
               + "&" + searchfield
               + "&" + jsonformat;
    var Grants = new Object();

    // Build up a search, that returns only HGF-projects ie. POF and
    // friends. This uses a two step search, and we identify all POF
    // grants by their ID (035__$a) to start with G:(DE-HGF)*
    // use phrase search for the * operator to work!
    var p1  = 'p1=G:(DE-HGF)*';
    var f1  = 'f1=035__a';
    var m1  = 'm1=p'
    var op1 = 'op1=a'
    var m2  = 'm2=r'
    var f2  = 'f2='
    var rg  = 'rg=100';
    var pofurl = inveniobase
               + "?" + collection
               + "&" + jsonformat
               + "&" + p1
               + "&" + f1
               + "&" + m1
               + "&" + op1
               + "&" + m2
               + "&" + rg
               + "&" + f2;
    var pofsearchterm = 'query';

    // Note that the ID has to be URLencoded!!!
    pofurl = '/JSGetAllChildren.py?record='
           + escape('035__a:"G:(DE-HGF)POF2*"')
           + '&src=550__&id=0&col=Grants&grpfield=751_7a';

    //----------------------------------------------------------------------
    // build the json string that gets store in 536__ and ends up
    // later on in the 536 grant categories of our record.
    // src allows to specify another field that should be handled the
    // same way.
    function BuildGrantStr(Grants, src, useonly) {
       // grantJS is an array of hashes, one hash per grant, keyed
       // by subfields of, usually, 536.
       var grantJS = [];
       var i = 0;
       // make sure that we have each grant exactly once and build up
       // the hashes for each grant.
       $.each(Grants, function(index, value) {
          // build up a hash for each grant, where the subfields
          // form the keys. 'useonly' is prevents 913 to be filled
          // with grants that are Non-HGF.
          // The returns we write here contain all subfields for 536
          // and 913.
          if ((useonly === '') || (index.search(useonly) > -1)) {
             var hlp = new Object;
             $.each(value, function(tag, field) {
               if (tag.indexOf(src) !== -1) {
                 var key = tag.charAt(tag.length-1);
                 if (field !== '') {
                   hlp[key] = field;
                 }
               } 
             });
             hlp['x'] = i.toString();
             i++;
             grantJS.push(hlp);
          }
       });
       return(JSON.stringify(grantJS));
    }

    function tokenOnAdd(item) {
       Grants[item.I536__0] = item;

       // 536 holds all grants regardless of the funder
       $('#I536__').val(BuildGrantStr(Grants, 'I536', ''));
       // 9131_ holds only additional, HGF specific informations for
       // grants, mainly for POF and the like structures that can not
       // be modeled in 536 easily.
       $('#I9131_').val(BuildGrantStr(Grants, 'I913', 'G:\\(DE-HGF\\)'));
    }
    //----------------------------------------------------------------------
    function tokenOnDelete(item) {
       // Remove an item to the Grants object.
       // This is easy as we used the unique ID to add it
       // so we can just delete the associated entity.
       delete Grants[item.I536__0];

       $('#I536__').val(BuildGrantStr(Grants, 'I536', ''));
       $('#I9131_').val(BuildGrantStr(Grants, 'I913', 'G:\\(DE-HGF\\)'));
    }

    //----------------------------------------------------------------------
    $("#I536__a").tokenInput(srcurl, {
        animateDropdown: false,
        crossDomain: false,
        hintText: hintTxt,
		    makeSortable: true,
        // append to the URL after concatenating with searchterm=
        propertyToSearch: toSearch,
        queryParam: searchterm,
        searchDelay: 300,
        tokenValue: toSearch,
        onAdd: function(item) {
          // if we add something to 536 it is not necessarily be added
          // to 9131_, we have it as a real grant already
          tokenOnAdd(item);
        },
        onDelete: function(item) {
          tokenOnDelete(item);
          // if we remove something from I536, remove it from 9131_ as
          // well
          $("#I9131_v").tokenInput('remove', item);
        }
    });

    //----------------------------------------------------------------------
    // For POF we want to search only grants issued by DE-HGF
    $("#I9131_v").tokenInput(pofurl, {
        animateDropdown: false,
        crossDomain: false,
        hintText: hintTxt,
		    makeSortable: true,
        propertyToSearch: toSearch,
        queryParam: pofsearchterm,
        searchDelay: 300,
        // searchOnEnter: we want to fly out a result list upon
        // entering the field.
        // searching for a space is effectively searching everyhting
        // cf. construction of search url.
        searchOnEnter: ' ',
        tokenValue: toSearch,
        onAdd: function(item) {
          tokenOnAdd(item);
          // if we add something to 9131_ we should add it to the real
          // grants as well
          $("#I536__a").tokenInput('add', item);
        },
        onDelete: function(item) {
          tokenOnDelete(item);
          // if we delete something from 9131_ we should remove it
          // from the real grants as well
          $("#I536__a").tokenInput('remove', item);
        }
    });

    // extract ID values from a technical field
    function GetIDs(src) {
       if ($(src).val() === '') {
         return(null);
       } else {
          var fieldValue = eval($(src).val());
          var ids = [];
          $.each(fieldValue, function(index, value) {
            var id = value['0'];
            ids.push(id);
          });
          return(ids);
        }
    }

   // instead of using prepopulate values call autopopulate which does
   // the same but also builds up internal infrastrcuture as it
   // generates onAdd events
   var I9131_ = $('#I9131_').val();
   var I536__ = $('#I536__').val();
   autopopulate_Grants(GetIDs('#I9131_'), 'I9131_0', '#I9131_v');
   // reset the value of I536__ to its original value as otherwise we
   // come into conflict with the split entity.
   $('#I536__').val(I536__);
   autopopulate_Grants(GetIDs('#I536__'), 'I536__0', '#I536__a');
   
});

