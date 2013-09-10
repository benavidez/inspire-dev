$(document).ready(function() {

    // Ensure that all fields are filled as required by calling
    // prefill(). Note that this function is only defined in modify
    if(typeof prefill == 'function') {
      prefill();
    }

    var inveniobase = "/search";               // base of the search entry
    var collection  = "cc=Institutes";         // collection to search
    var searchmode  = "m1=r";                  // use regexp matching
    var searchfield = "f1=";                   // index to search
    var searchterm  = "p1";                    // how to search. No = as we
                                               // use the same parameter for the tokeninput tag
    var jsonformat  = "of=js";                 // output format to use; 
                                               // this returns plain text, we eval() it to objects
                                              
    // Tokeninput variables                   
    var toSearch    = "label";                 // tag for tokeninput to search for
    var hintTxt     = "Search for MY Institutes"; // tag for tokeninput to search for

    var srcurl = inveniobase
               + "?" + collection
               + "&" + searchmode
               + "&" + searchfield
               + "&" + jsonformat;
    var Institutes = new Object();

    //----------------------------------------------------------------------
    // if no institutes are set, popFields should be 'null' for
    // tokeninput to know that no population is necessary.
    var popField = null;

    if ($("#I9201_").val() === '') {
      // I9201_ doesn't contain anything => we do not need to
      // prepopulate the tokeninput
      popField = null;
    } else {
       var instCounter = 0;
       var fieldValue = eval($('#I9201_').val());
       var textHidden = [];  
       var prePopulateField = "";
       $.each(fieldValue, function(index, value) {
           var element = JSON.stringify(value);
           textHidden.push(element);

       });
       $.each(textHidden, function(i, value) {
           value = WashJSstr(value);
           var jsonElement = eval('[' + value + ']');
           $.each(jsonElement, function(key, value) {
               var srcurl2 = inveniobase 
                           + "?" + collection 
                           + "&" + searchterm + "=035__a:" + jsonElement[key]["0"] 
                           + "&" + searchfield
                           + "&" + jsonformat;
               $.ajax({
                   type: "GET",
                   url: srcurl2,
                   async: false,
                   success: function(text) {
                       prePopulateField = prePopulateField + text;
                       text = WashJSstr(text);
                       tmp = eval('[' + text + ']');
                       Institutes[tmp[0].I9201_0] = tmp[0];
                   }
               });
           });
       });
       popField = eval('[' + prePopulateField + ']');
    }
    //----------------------------------------------------------------------

    $("#I9201_l").tokenInput(srcurl, {
        hintText: "Search Institute",
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
        prePopulate: popField,
        onAdd: function(item) {
            Institutes[item.I9201_0] = item;
            var helpArray   = [];
            var instCounter = 0;
            $.each(Institutes, function(index, value) {
                // Inst holds all infos for a given institute, except
                // "label" which is not valid for ingest
                // Also it is indexed only by the subfield
                var Inst = new Object();
                $.each(value, function(idx, v) {
                   if (idx != "label") {
                     if (idx.substring(0, 6) == "I9201_") {
                        // get the subfield
                        var myidx = String(idx.charAt(idx.length -1));
                        Inst[myidx] = v
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
            $('#I9201_').val(JSON.stringify(helpArray))

           
        },
        onDelete: function(item) {
            var helpArrayDel = [];
            var textDel = "";
            var instCounter = 0;
            // Remove an item to the Institutes object.
            // This is easy as we used the unique ID to add it
            // so we can just delete the associated entity.
            delete Institutes[item.I9201_0];

            var helpArray   = [];
            var instCounter = 0;
            $.each(Institutes, function(index, value) {
                var Inst = new Object();
                $.each(value, function(idx, v) {
                   if (idx != "label") {
                     if (idx.substring(0, 6) == "I9201_") {
                       var myidx = String(idx.charAt(idx.length -1));
                       Inst[myidx] = v
                     }
                   }
                });
                Inst.x = String(instCounter);
                instCounter++;
                helpArray.push(Inst);
            });
            $('#I9201_').val(JSON.stringify(helpArray))

           
        }
    });
	
	  
	  //---Begin Test autopopulate_Institute(idInst) 
	
	 /* 
      var instId=["I:(DE-82)080005","I:(DE-82)jara000001","I:(DE-82)60900","	I:(DE-82)1210","I:(DE-82)56500","I:(DE-82)10840"];
	   autopopulate_Institute(instId);
	   
	 */
	   
	   
	 //--END Test
});

/*
function to autopopulate Institute if Author Field contain Author
This function need a Array with the String element (example "I:(DE-82)080005") 
*/

/******************************************/
function autopopulate_Institute(idInst) {
   
    var Inst = new Object();

    $.each(idInst, function(i, value) {
         
        var srcurl2 ="/search?ln=de&cc=Institutes&of=js&p="+value;
           
    		   $.ajax({
                   type: "GET",
                   url: srcurl2,
                   async: false,
                   success: function(text) {
                       
           text = WashJSstr(text);
					 tmp = eval('[' + text + ']');
                     
					 Inst[tmp[0].I9201_0] = tmp[0];  
					  
                    }             
    			});
				
			// Write Institute in Field	
			 $.each(Inst, function(index, value) {
               
				 $("#I9201_l").tokenInput('add', value);
                         
            });
				
				
        
      });
    
}
