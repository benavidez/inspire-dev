$(document).ready(function() {

	$("#I000__a").autocomplete({
		source: function(input, response) {
				var inveniobase = "/search";        // base of the search entry
				var collection  = "cc=Institution"; // collection to search
				var searchterm  = "p=";             // search parameter
				var jsonformat  = "of=js";          // output format to use; 

				var srcurl = inveniobase
					   + "?" + collection
					   + "&" + searchterm + input.term  
					   + "&" + jsonformat;
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
				if (response.item) {
				   // $.each( response.item, function(key, value){
					 //    $('#'+key).val(value);
           // });	
				}
			},
			minLength: 0
	}).focus(function(){
      if (this.value === '') $(this).trigger('keydown.autocomplete');
  });
});


