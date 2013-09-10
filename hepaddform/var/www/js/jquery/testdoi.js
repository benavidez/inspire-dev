$(document).ready(function() {

	// handle the loading message. This is essentially a <div> that get
	// set to visible or not. Demo code doesn't look nice but shows how
	// to do it.
	$('#loadingMsg').hide();

	// Bind visibility to the activity of _ANY_ ajax-call on the page.
  $('#loadingMsg').bind("ajaxSend", function() {
            $(this).show();
  }).bind("ajaxComplete", function() {
            $(this).hide();
  });


	// Bind focus in to clean all data. Check if this is sensible
	// behaviour. Probably one want's to do this on focusout?
	$("#doi").focusin(function() {
			$('#id1').val("");
			$('#id2').val("");
			$('#id3').val("");
			$('#id4').val("");
			$('#id5').val("");
	})
	
	// Bind focusout to the Ajax-call.
	$("#doi").focusout(function() {
                                alert("out of focus");

				// calling a cgi passing on the parameters.
				// This needs to be expanded for the functionality discussed,
				// but keep stuff simple in the demo
				var inveniobase = "/cgi-bin/GenMetadata.pl";
				var searchterm  = "doi=";

				var srcurl = inveniobase + "?" + searchterm + $('#doi').val()

				// fire up the actual ajax query using a simple GET for srcurl
				$.ajax({ type: "GET",   
					url: srcurl,
					async: true,
					success : function(text) {
						// upon success we get a JSON like structure. Bracket it
						// ot an object and evalutate it to have access to the
						// values.
						var res = eval('{[ ' + text + ' ]}');
						// finally set the ohter fields to the values just
						// retrieved.
						$('#id1').val(res[0].hgf_master);
						$('#id2').val(res[0].hgf_300__a);
						$('#id3').val(res[0].hgf_0247_);
						$('#id4').val(res[0].hgf_588__a);
						$('#id5').val(res[0].hgf_915);
					}
				});
				return;
			}
		)
});


