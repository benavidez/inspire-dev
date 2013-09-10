$(document).ready(function() {
    // Bind focus in to clean all data. Check if this is sensible
    // behaviour. Probably one want's to do this on focusout?
    var myItems;

    function Import() {
        if ($('#Ihgf_import').val() === '') {
            return;
        }
        // calling a cgi passing on the parameters.
        // This needs to be expanded for the functionality discussed,
        // but keep stuff simple in the demo
        var inveniobase = "/hgfImport.py?f=GenMetadata.pl";
        var searchparam = "mode=full&format=JSON";
        var searchterm = "";
        //Replace Escape with Empty String
        var urlString = $('#Ihgf_import').val().replace(/ /g, "");
        // Split : 
        var helpSplit = urlString.split(":");

        // Check if the helpString Length =2
        if (helpSplit.length == 1) {
            searchterm = "doi=" + helpSplit[0];
        } else {
            searchterm = helpSplit[0].toLowerCase() + "=" + helpSplit[1];
        }
        var srcurl = inveniobase + "&" + searchterm;
        //start spinner
        $('#Ihgf_import').after('<div id="spin"></div>');
        $('#spin').spin();
        // fire up the actual ajax query using a simple GET for srcurl
        $.ajax({
            type: "GET",
            url: srcurl,
            async: true,  // we are only triggered "on leave"
                           // or via keypress => dedicated
                           // event, wait for it's result.
            success: function(text) {
                // upon success we get a JSON like structure. Bracket it
                // ot an object and evalutate it to have access to the
                // values.
                text = WashJSstr(text);
                var res = eval('{[ ' + text + ' ]}');
                $('#spin').spin(false);

                if (res[0].SHORTTITLE == ' /  ; ') {
                   res[0].SHORTTITLE = 'DOI Not Found. Please try again.';
                }

                // Ask the user with by SHORTTITLE if she wants to
                var dlgtext = '<p class="tmp">' + res[0].SHORTTITLE + '</p>';
                if (res[0].DUPES != undefined) {
                   // The backend found some dupes. Display links to
                   // them for easy reference.
                   dlgtext = dlgtext + '<p class="tmp">';
                   dlgtext = dlgtext + 'Potential duplicate record(s):<ul>';
                   // Build up links to the dupes. Those should open
                   // in new tabs/windows!
                   var dupes = res[0].DUPES.split(", ");
                   $.each(dupes, function(index) {
                      if (dupes[index] != '') {
                         var link = '<li><a target="_blank" href="/record/' +  dupes[index] + '">';
                         link = link + dupes[index] + '</a></li>';
                         dlgtext = dlgtext + link;
                      }
                   });
                   dlgtext = dlgtext + '</ul></p>';
                }
                // import the results or not
                //$('.Lhgf_import').append('<div id="importtxt">' + dlgtext + '</div>');
                $('.Lhgf_import').before('<div id="importDialog">' + dlgtext + '</div>');
                $('#importDialog').dialog({
                  title : 'Import data:',
                  modal : true,
                  width : 'auto',
                  buttons: [
                    {
                      id  :  'importDialogImport',
                      text:  'Import',
                      // move the import to the fields
                      click: function() {
                         $(this).dialog("close");
                         $.each(res[0], function(key, value) {
                             // write data only if the field is still
                             // empty
                             if (($('#'+key)).val() === "") {
                                if ((key != 'I1001_') && (key != 'I1001_a')) {
                                   $('#' + key).val($.trim(value));
                                    //journal to short name
                                    if (key == 'I773__p'){
                                        var j = $.trim(value);
                                        j = j.toLowerCase();
                                        //alert(j);
                                        $.getJSON('/img/journalkb.json', function(data) {
                                            $.each(data, function(k, val) {
                                                var target = data[k].label;
                                                target = target.toLowerCase();
                                                if(target == j){
                                                    $('#' + key).val(data[k].value);
                                                    //alert(data[k].value);
                                                }

                                            })
                                        });
                                    }
				                    //end journal to short name
                                }
                                if (key == 'I1001_a') {
                                    autopopulate_author($.trim(value));
                                }

                            }
                         });
	                    //$('#importDialog').replaceWith('<div id="importDialog"></div>');
	                    $('.tmp').remove();
                      }
                    },
                    {
                      id  :  'importDialogDiscard',
                      text:  'Discard',
                      // we do nothing here
                      click: function() { $(this).dialog("close");
	                    $('#importDialog').replaceWith('<div id="importDialog"></div>');
	                    $('.tmp').remove();
                      }
                    },
                  ]
                });
                if (res[0].DUPES != undefined) {
                  $("#importDialogImport").button("disable");
                }
                $('#I773__a').val($('#Ihgf_import').val());
            }
        });
        $('#importDialog').replaceWith('<div id="importDialog"></div>');
        return;
    }
    // Bind focusout to the Ajax-call.
    $("#Ihgf_import").focusout(function() {
        Import();
    });
    var timeout;
    $("#Ihgf_import").keypress(function(event) {
        switch(event.keyCode) {
        case 108:         // NUM-Pad ENTER
        case 13:          // ENTER
            $('#I245__a').focus(); // trigger the event by moving the focus
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
