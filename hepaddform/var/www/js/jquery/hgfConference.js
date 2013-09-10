$(document).ready(function() {
   
	$("#I1112_").autocomplete({
		
		source: function(input, response) {
				// build the URL for the query. 
				// Note: it has to be a local URL, do NOT use the full
				//       qualified URL (considered cross site scripting)
				// Also this type of URL is portable and will work on every
				// invenio installation

				var inveniobase = "/search";         // base of the search entry
				var collection  = "cc=Conferences";  // collection to search
				var searchterm  = "p1=";             // search parameter
				var searchmode  = "m1=r";            // use regexp matching
				var searchfield = "f1=";             // index to search
				var jsonformat  = "of=js";       // output format to use; 
								     // this has to return plain text.

				// Build the URL for the search. Notice to use substring search by 
				// regexp .*term.*
				var srcurl = inveniobase
					   + "?" + collection
					   + "&" + searchmode
					   + "&" + searchterm + input.term  
					   + "&" + searchfield + "title"
					   + "&" + jsonformat;

				//--// For debugging uncomment the following line
				// log("URL: " + srcurl);

				// fire up the actual ajax query using a simple GET for srcurl
				$.ajax({ type: "GET",   
					url: srcurl,
					async: true,
			        success : function(text) {
						
            text = WashJSstr(text);
						response(eval('{[ ' + text + ' ]}'));
						
						
						
					}
				});
				return;
			},
		
		select: function(input, response) {
				// we have a select!
				// Now fill in the values into the proper form fields
				// Each field is addressed by its #<id>, then use the val() method
				// to set it's value. The latter is given via the response object
				// where item.<hashindex> signifies the value to use.
				if (response.item) {
							        
				
				    $.each( response.item, function(key, value){
								 
						 $('#'+key).val(value);
						 
										 
                });	
						
					
					
				} 
			},
			
		
		
			
			minLength: 3
			

			
			
	});
});


