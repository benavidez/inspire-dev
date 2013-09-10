$(document).ready(function() {
    $("#getURL").click(function() {
        var instfield = '9201_';
        var statfield = '915__';
        var typefield = '3367_';
		var grantfield = '536__';
        
        // read the structured fields
        var Institut = eval($("#I" + instfield).val());
        var StatID   = eval($("#I" + statfield).val());
        var PubTypes = eval($("#I" + typefield).val());
		var Grants =  eval($("#I" + grantfield).val());
	
		
        // Marc has distinctive values for first and other authors, so
        // we get them passed on in two bunches. However, we do not
        // want to keep this distinction in the final search.
        var Author1  = eval($("#I1001_").val());
        var Author7  = eval($("#I7001_").val());
        
        // query will hold the final query we need to build up by
        // concating all entries made by the user
        var query = "";

        function buildTerm(Field, prefix) {
            // loop over all entries of Field and collect their IDs
            var term = '';
            if (Field !== undefined) {
                $.each(Field, function(idx, value) {
                    var ID = value['0'];
                    // concat a search properly prefixed and concatted
                    // with logical OR
                    term += " " + prefix + ":'" + ID + "' OR";
                });
                // remove the superflous last one
                term = $.trim(term.replace(/ OR$/, ''));
                // Invenio doesn't like brackets if we have only one term
                // within, so set them only if we have at least one OR
                if (term.indexOf('OR') != -1) {
                    term = '(' + term + ')';
                }
                // add AND for the next query concatted
                return term + ' AND ';
            } else {
                return '';
            }
        }
        // build up search queries for all normal fields
        query += buildTerm(Institut, instfield);
        query += buildTerm(PubTypes, typefield);
        query += buildTerm(StatID, statfield);
		query += buildTerm(Grants, grantfield);
        // Authors add some complexity due to the distinction of
        // 100/700 in Marc
        if (Author1 !== undefined) {
            var authorSearch = '';
            $.each(Author1, function(idx, value) {
                var ID = value['0'];
                // for authors we need to search 100 AND 700 as we have
                // distinct first and other authors in Marc.
                authorSearch += " " + '100' + ":'" + ID + "' OR";
                authorSearch += " " + '700' + ":'" + ID + "' OR";
            });
            if (Author7 !== undefined) {
                $.each(Author7, function(idx, value) {
                    var ID = value['0'];
                    authorSearch += " " + '100' + ":'" + ID + "' OR";
                    authorSearch += " " + '700' + ":'" + ID + "' OR";
                });
            }
            authorSearch = $.trim(authorSearch.replace(/ OR$/, ''));
            if (authorSearch.indexOf('OR') != -1) {
                authorSearch = '(' + authorSearch + ')';
            }
            if (authorSearch !== '') {
                query += authorSearch + ' AND ';
            }
        }
        query = $.trim(query.replace(/ AND $/, ''));
        var inveniobase = "/search"; // base of the search entry
        var searchterm = "p=";       // initiate a simple search, we have IDs
        var srcurl = inveniobase + '?' + searchterm + query;
        alert(window.location.protocol +"//"+ window.location.hostname+srcurl);
		
    });
});
