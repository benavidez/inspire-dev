$(document).ready(function() {
    var notrigger = 0;

    function Import() {
        // Search if Input Field ISBN not empty
        if (($("#I020__a").val() !== "") && (notrigger === 0)) {
            notrigger = 1;
            // calling a cgi passing on the parameters.
            // This needs to be expanded for the functionality discussed,
            // but keep stuff simple in the demo
            var inveniobase = "/hgfImport.py?f=GVKSearch.pl";
            var searchparam = "mode=full&format=JSON";
            var searchtermISBN = "isbn=";
            //var serachtermTitel="ti=&db=wos";
            var ISBN = searchtermISBN + $('#I020__a').val();
            var srcurl = inveniobase + "&" + ISBN;
            //alert(srcurl);
            // fire up the actual ajax query using a simple GET for srcurl
            $.ajax({
                type: "GET",
                url: srcurl,
                async: false,  // we are only triggered "on leave"
                               // or via keypress => dedicated
                               // event, wait for it's result.
                success: function(text) {
                    // upon success we get a JSON like structure. Bracket it
                    // ot an object and evalutate it to have access to the
                    // values.
                    if (text === "") {} else {
                        notrigger = 1;

                        text = WashJSstr(text);
                        var result = eval('{[ ' + text + ' ]}');
                        var list = result.length;
                        if (list > 10){ list = 10; }
                        if (list == 1){ list = 2; }
                        var selectbox = '<br><select name="titelbox" id="L020__aselect" size="'+ list +  '">';
                        $(".L020__a").append(selectbox);
                        $('#L020__aselect').focus();
                        
                        // build up the selectbox
                        $.each(result, function(i, l) {
                            $("select").append('<option>' + result[i].label + '</option>');

                        });

                        //--------------------------------------------------
                        function fillFields(result, index) {
                           $.each(result[index], function(key, value) {
                               // write data only if the field is still empty
                               if (($('#'+key)).val() === "") {
                                  if ((key != 'I1001_') && (key != 'I1001_a')) {
                                      $('#' + key).val($.trim(value));
                                  }
                                  if (key == 'I1001_a') {
                                      autopopulate_author($.trim(value));
                                  }
                               }
                           }); //each fill field with correspondent Titel
                        }
                        //--------------------------------------------------

                        //--------------------------------------------------
                        function dupeCheck(result, index) {
                           var dlgtext = '<p>' + result[index].SHORTTITLE + '</p>';
                           if (result[index].DUPES != undefined) {
                              // The backend found some dupes. Display links to
                              // them for easy reference.
                              dlgtext = dlgtext + '<p>';
                              dlgtext = dlgtext + 'Potential duplicate record(s):<ul>';
                              // Build up links to the dupes. Those should open
                              // in new tabs/windows!
                              var dupes = result[index].DUPES.split(", ");
                              $.each(dupes, function(idx) {
                                 if (dupes[idx] != '') {
                                    var link = '<li><a target="_blank" href="/record/' +  dupes[idx] + '">';
                                    link = link + dupes[idx] + '</a></li>';
                                    dlgtext = dlgtext + link;
                                 }
                              });
                              dlgtext = dlgtext + '</ul></p>';
                              // import the resultults or not
                              $('.Lhgf_import').append('<div id="importDialog">' + dlgtext + '</div>');
                              $('#importDialog').dialog({
                                 title : 'Duplicate entry?',
                                 modal : true,
                                 width : 'auto',
                                 buttons: [
                                   {
                                     text:  'Import',
                                     // move the import to the fields
                                     click: function() { 
                                        $(this).dialog("close");
                                        fillFields(result, index);
                                     }
                                   },
                                   {
                                     text:  'Discard',
                                     click: function() { $(this).dialog("close"); }
                                   },
                                 ]
                              });
                           }
                           //--// //we get several selects?
                           else {
                              fillFields(result, index);
                           }
                        }
                        //--------------------------------------------------


                        $("select").click(function() {
                           // after the initial setup we always get
                           // two options selected. Work around this
                           // by incrementing done.
                           var done = 0;
                           $("select").find("option:selected").each(function() {
                                var idx = $(this).index();
                                done++;
                                if (done == 1) {
                                  dupeCheck(result, idx);
                                }
                           })
                           //hide the selectbox after selection
                           $('select').remove();
                           $('#Ihgf_import').focus();
                        })

                        $("select").keyup(function(event) {
                            var done = 0;
                            if (event.which == 13) {
                               // On enter fill in the values
                               $("select").find("option:selected").each(function() {
                                   //hide the selectbox after selection
                                   done++;
                                   if (done == 1) {
                                      dupeCheck(result, $(this).index());
                                   }
                              })
                              $('select').remove();
                              $('#Ihgf_import').focus();
                            }
                            if (event.which == 27) {
                              // On Esc remove the list
                              $("select").remove();
                              $('#I020__a').focus();
                            }
                        })
                    }
                }
            }); //Ajax Call close
            return;
        } // if not empty	
    }
    $("#I020__a").focusout(function() {
        if (notrigger === 0) {
            Import();
        }
    });

    // use keyup events as we handle non-printable keys
    var timeout;
    $("#I020__a").keyup(function(event) {
        switch(event.keyCode) {
        case 108:         // NUM-Pad ENTER
        case 13:          // ENTER
            notrigger = 0;
            $('#Ihgf_import').focus();
            break;
        default:
            // If we got any key not handled till now, assume that the
            // user is sitting and waiting for Godot. => give Godot a
            // helping hand...
            if(String.fromCharCode(event.which)) {
              clearTimeout(timeout)
              timeout = setTimeout(function(){$('#I245__a').focus();}, 3000);
            }
            break;
        }
    });
});
