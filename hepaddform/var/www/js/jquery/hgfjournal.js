$(document).ready(function() {
    var cleanfields = ['#I020__a', '#I260__b', '#I260__a',
                       '#I773__0', '#I915__a' ]

    // from autocomplete we get a label that is not the same as the
    // data that should get stored, as we want to give more
    // information to the user. Use storetag to replace the input upon
    // leaving the field
    var storetag  = ''; 

    var bindfield = '#I773__p'; // where we bind our events

    function CleanFormFields() {
       for (i = 0; i < cleanfields.len; i++ ) {
         $(cleanfields[i]).val("");
       }
    }
/*
    $(bindfield).autocomplete({
         source: "/img/journals.json"
    });
*/

function autocomplete_kb(that, kb_name){
 //$.getJSON("/kb/export", {kbname: kb_name, format: 'kba'})
 $.getJSON("/img/journalkb.json")
  .done(function(json) {
    that.autocomplete({
    minLength: 2,
    source: json
    });
  })
}

   autocomplete_kb($(bindfield), "JOURNALS");

    /*EB-This function is from Sebastian. It replaces the code below it*/
/*   function autocomplete_kb(that, kb_name){
      that.autocomplete({
        minLength: 2,
        source: function(request, response) {
          $.getJSON("/img/journalkb.json", {term: request.term}, 
            function(json){
              //response(JSON.parse(json))
              response(json)
            }
          );
        }
      });
   }
*/
  
  
/*$(bindfield).autocomplete({
        source: function(input, response) {
            // build the URL for the query. 
            // Note: it has to be a local URL, do NOT use the full
            //       qualified URL (considered cross site scripting)
            // Also this type of URL is portable and will work on every
            // invenio installation
            var inveniobase = "/kb/export"; // base of the search entry
            var kbname = "JOURNALS"; // output format to use; 
            var of = "kba"; 
            // this has to return plain text.
            // Build the URL for the search. Notice to use substring search by 
            // regexp .*term.*
           // JOURNALS&format=kba
            var srcurl = inveniobase 
                       + "?kbname=" + kbname
                       + "&format=" + of
                       //+ "&of=" + of
            // the following would limit the search to the title
            // TODO is this sensible or not?
            // + "&" + searchfield + "title"
            //--// For debugging uncomment the following line

            // fire up the actual ajax query using a simple GET for srcurl
            $.ajax({
                type: "GET",
                url: srcurl,
                async: true,
                success: function(text) {
                    var res = text.split('\n');
                    var t = '';
                    for (var i = 0; i < res.length; i++){
                        t = t + '\"' + res[i] + '\"' + ',';
                    } 
                    //text = WashJSstr(text);
                    //alert(text);
                    response(eval('{[' +t +']}'));
                }
            });
            return;
        },
        open: function(input, response) {
            // if the selection menu is open, clean all other fields
            CleanFormFields();
        },
        select: function(input, response) {
            // we have a select!
            // Now fill in the values into the proper form fields
            // Each field is addressed by its #<id>, then use the val() method
            // to set it's value. The latter is given via the response object
            // where item.<hashindex> signifies the value to use.
            if (response.item) {
                $.each(response.item, function(key, value) {
                    //alert('xx:' + key + ': ' + value);
                    $('#' + key).val(value);
                    $(bindfield).val(value);
                    storetag = value;
                    if ('#'+key == bindfield) {
                      // store what we really want to write to the
                      // field
                      storetag = value;
                    }
                });
            } else {
              CleanFormFields();
            }
        },
        minLength: 4
    });*/

    // store the real value as soon as we leave the field
    /*$(bindfield).focusout(function(){
      $(bindfield).val(storetag);
    });*/
    

});
