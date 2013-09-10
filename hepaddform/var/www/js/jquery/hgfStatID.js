$(document).ready(function() {

    var inveniobase = "/search"; // base of the search entry
    var collection = "cc=StatID"; // collection to search
    var searchmode = "m1=r"; // use regexp matching
    var searchfield = "f1="; // index to search
    var searchterm = "p1"; // how to search. No = as we
    // use the same parameter for the tokeninput tag
    var jsonformat = "of=js"; // output format to use;   // this returns plain text, we eval() it to objects

    var Institutes = new Object();

    // Tokeninput variables                   
    var srcurl = inveniobase 
               + "?" + collection
               + "&" + searchmode
               + "&" + searchfield
               + "&" + jsonformat;

    var toSearch = "label"; // tag for tokeninput to search for
    //   alert(srcurl);	
    $("#I915__a").tokenInput(srcurl, {

        hintText: "Search for StatID",
        queryParam: searchterm,
        //wird an der url angehängt mit dem suchTerm 
        propertyToSearch: toSearch,
        crossDomain: false,
        tokenValue: toSearch,
        searchDelay: 300,
        animateDropdown: false,
        makeSortable: true,
        shortSearch: 3,
        shortSearchPrefix: '^',

        onAdd: function(item) {
            Institutes[item.I915__0] = item;
            var helpArray = [];
            var instCounter = 0;
            $.each(Institutes, function(index, value) {
                // Inst holds all infos for a given institute, except
                // "label" which is not valid for ingest
                // Also it is indexed only by the subfield
                var Inst = new Object();
                $.each(value, function(idx, v) {
                    if (idx != "label") {
                        if (idx.substring(0, 5) == "I915_") {
                            // get the subfield
                            var myidx = String(idx.charAt(idx.length - 1));
                            Inst[myidx] = v;
                        }
                    }
                });
                // add the counter
                Inst.x = String(instCounter);
                instCounter++;
                // push to the array that gets inserted
                helpArray.push(Inst);
            });
            // Insert to structured field
            $('#I915__').val(JSON.stringify(helpArray))
        },
        onDelete: function(item) {
            var helpArrayDel = [];
            var textDel = "";
            var instCounter = 0;
            // Remove an item to the Institutes object.
            // This is easy as we used the unique ID to add it
            // so we can just delete the associated entity.
            delete Institutes[item.I915__0];

            var helpArray = [];
            var instCounter = 0;
            $.each(Institutes, function(index, value) {
                var Inst = new Object();
                $.each(value, function(idx, v) {
                    if (idx != "label") {
                        if (idx.substring(0, 5) == "I915_") {
                            var myidx = String(idx.charAt(idx.length - 1));

                            Inst[myidx] = v
                        }
                    }
                });
                Inst.x = String(instCounter);
                instCounter++;
                helpArray.push(Inst);
            });
            $('#I915__').val(JSON.stringify(helpArray));
        }
    });
});
