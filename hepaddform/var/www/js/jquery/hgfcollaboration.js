$(document).ready(function() {
    var cleanfields = ['#I020__a', '#I260__b', '#I260__a',
                       '#I773__0', '#I915__a','#I710__g']

    // from autocomplete we get a label that is not the same as the
    // data that should get stored, as we want to give more
    // information to the user. Use storetag to replace the input upon
    // leaving the field
    var storetag  = ''; 

    var bindfield = '#I710__g'; // where we bind our events

    function CleanFormFields() {
       for (i = 0; i < cleanfields.len; i++ ) {
         $(cleanfields[i]).val("");
       }
    }

    function autocomplete_kb(that, kb_name){
       //$.getJSON("/kb/export", {kbname: kb_name, format: 'kba'})
       $.getJSON("/img/collaborations.json")
       .done(function(json) {
          that.autocomplete({
            minLength: 2,
            source: json
          });
       })
     }
     autocomplete_kb($(bindfield), "COLLABORATIONS");
}); 
