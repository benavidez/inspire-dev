$(document).ready(function() {
       
	   
    //create Select box for Result  
/*	var selectbox='<select name="titelbox"  multiple="multiple">';
	
	$("#245__a").append(selectbox);
	
	$('select').hide();
	*/	
	 //focusout field #I245__a
	$("#I1001_a,#I245__a").focusout(function() {
	
	    //prüfe, ob Titel und Author nicht leer ist
		
		
		if($('#I1001_a').val()=="" || $('#I245__a').val()==""){
		 
		 //   alert("Title and Author must not be empty, please fill it");
			$('select').hide();
		
		
		}else{   

							//create Select box for Result  
				var selectbox='<select name="titelbox"  multiple="multiple">';
				
				$("#245__a").append(selectbox);
				
				$('select').hide();
				  
		
				// calling a cgi passing on the parameters.
				// This needs to be expanded for the functionality discussed,
				// but keep stuff simple in the demo
				//var inveniobase = "/cgi-bin/AUTISearch.pl";
				var inveniobase = "/hgfImport.py?f=AUTISearch.pl";
				//var searchparam = "mode=fast&format=JSON&db=wos";
				var searchtermAutor="au=";
				var serachtermTitel="ti=";
						  
				var value1=	searchtermAutor +$('#I1001_a').val();
                var value2 =serachtermTitel+$('#I245__a').val();			
				
			//	var srcurl = inveniobase + "?" + value1+ "&" + value2+"&" +searchparam;
			    var srcurl = inveniobase + "?" + value1+ "&" + value2;
											
				// fire up the actual ajax query using a simple GET for srcurl
				$.ajax({ type: "GET",   
					url: srcurl,
					async: true,
					success : function(text) {
							// upon success we get a JSON like structure. Bracket it
							// ot an object and evalutate it to have access to the
							// values.
					    if(text==""){
						 
						}else{
							var result = eval('{[ ' + text + ' ]}');
								
							$("select").show();
					 								
							$.each( result, function(i, l){
							
								//fill Option Element Titel  
								$("select").append('<option>'+result[i].label+'</option>');  
				
															
								 $("select").change(function () {
									 // var str = "";
									 $("select option:selected").each(function () {
										
											var index=$(this).index();
										    
												$.each(result[index], function(key, value){
									  
																							  
												 $('#'+key).val(value);
														  
												});	 //each fill field with correspondent Titel
												
												//hide the selectbox after selection
												$("select").hide();
																																		
									 });  //each Select
									         								
									   })
									     //.change();

									}); 
										
						}
					}
				});  //Ajax Call close
				
				return;
				
				
				
		}//else close
	     			
	}) //focusout close
		
	
		
});

