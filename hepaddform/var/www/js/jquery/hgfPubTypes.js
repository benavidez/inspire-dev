$(document).ready(function() {

    var inveniobase = "/search";     // base of the search entry
    var collection  = "cc=PubTypes"; // collection to search
    var searchfield = "f=";          // we perform a simple search
    var jsonformat  = "of=js";       // returning js format
    var searchterm  = "p";

    var srcurl = inveniobase
               + "?" + collection
               + "&" + searchfield
               + "&" + jsonformat;

    var toSearch   = "label";      // tag for tokeninput to search for
    var retstruct  = "I3367_";     // structure we expect
    var srcfield   = "2";          // subfield specifying the src of the values
    var labelfield = "a";          // subfield used for display
    var srcval     = "PUB:(DE-HGF)"; // we only need our own in the final result

    var pubtypes   = new Object; 

    $("#I3367_a").tokenInput(srcurl, {
        hintText: "Search for Publication Types",
        queryParam: searchterm,
        propertyToSearch: toSearch,
        crossDomain: false,
        tokenValue: toSearch,
        searchDelay: 300,
        animateDropdown: false,
        shortSearch: 3,
        minChars: 3,
        shortSearchPrefix: '^',
        onResult: function (results) {
           // we get a higher structure which we need to flatten
           // frist by extracting all own document types from it.
           var newres = [];
           $.each(results, function (index, value) {
               $.each(value.I3367_, function(index, val) { 
                  if (val[2] == srcval) {
                    var arr = [];
                    arr = val;
                    arr ['label'] = val[labelfield];
                    newres.push(arr);
                  }
               })
           });
           // now we have an array of hashes suitable for tokeninput
           results = newres;
           return results;
        },
        onAdd: function(item) {
          pubtypes[item['0']] = item;
          var hlp = [];
          $.each(pubtypes, function(index, value) {
            hlp.push(value);
          });
          var str = JSON.stringify(hlp);
          $('#I3367_').val(str);
        },
        onDelete: function(item) {
          var toremove = item['0'];
          var hlp = [];
          $.each(pubtypes, function(index, value) {
            if (index != toremove) {
              hlp[index] = value;
            }
          });
          pubtypes = hlp;
          hlp = [];
          $.each(pubtypes, function(index, value) {
            hlp.push(value);
          });
          var str = JSON.stringify(hlp);
          $('#I3367_').val(str);
        }
    });
});
