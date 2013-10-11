$(document).ready(function() {
	
	//
	//local vars
	//
	
	//local url for http get request
	var srcurl_search_people = "/search?cc=People&m1=r&of=js"  // for direct invenio call for prefill via id
	var srcurl_institutions = "/HandleInstitutions.py"; // for search institution authorities in order to person, orderid & query param
	
	//Link to help text for author field
	var helplink = '<a target="_blank" alt="Help" href="http://invenio-wiki.gsi.de/cgi-bin/view/Main/1001_a"><img src="/img/hgfinfo.png"></a>'
	//Link for clear all authors 
	var clearLink = '<a href="#" alt="Clear All Authors" id="clearAllAuthors"><img src="/img/hgfgroup_delete.png"></a>'      
	
	//contains results of prefill 
	var prePop = [];		//array of hashes with prepopulated results
	
	//status vars
	var onAdd = true;	//for control passive call of onAdd, for update token in list
	var escDialog	= false;
	

	//
	//tokeninput functions as js objects
	//
	
	var addFunction = function (item) {
		//add Item to tokenlist		
		//current agreement without open role dialog
		//open_role_dialog(item);
		//only check role and set/reorganise, if necessary
		if (item.checked_role !== true){ 
			if (item.I1001_e == undefined)
				item = set_general_role(item);
			var change_list = check_role(item);	
			update_tokeninput(change_list);
		}
		
		//final format into 1001_ and 7001_ here
		hidden2final_author();
	};
	
	var changeFunction = function (item) {		
		//change hiddeninput into final format to 1001_ and 7001_
	        //alert('on changeFunction');	
		hidden2final_author();
	};
	
		
	var tokenFormatterFunction = function(item) { 
		//show role in token item 
		if (typeof item.I1001_e == 'undefined')
			item.I1001_e = $.selected_role; // for initial pasted input	

		//for update total tokenlist (for role control) undefinded pasted action - use status on item	
		if ($.pasted_author_input == ""){
			if (item.pasted == true)
				return "<li style='color: red'><p>" + item.label + " " + item.I1001_e + "</p></li>"
			if (item.pasted == false)
				return "<li style='color: black'><p>" + item.label + " " + item.I1001_e + "</p></li>" 
		}
		
		// use pasted status depend on action in hgfauthor2id script
		if ($.pasted_author_input == false)  {
			item.pasted = false
			return "<li style='color: black'><p>" + item.label + " " + item.I1001_e + "</p></li>" 
		}else{
			item.pasted = true;
			return "<li style='color: red'><p>" + item.label + " " + item.I1001_e + "</p></li>" 
		}
			
	};		
	
	var resultsFormatterFunction = function(item) { 
		//show initial/last role in result list
		item['I1001_e'] = $.selected_role; 	//for initial and last role
		return "<li><p>" + item.label + " " + item.I1001_e + "</p></li>" 
	};
			
	var resultFunction = function (results) {
		//result set with guess and select hash
		//e.g. result set:[{"guess":[[{"I1001_0":"P:(DE-HGF)0","I1001_a":"Mller, H.","I1001_b":"0","I1001_u":"Extern"}],[{"I1001_0":"P:(DE-HGF)0","I1001_a":"Maier, U.","I1001_b":"1","I1001_u":"Extern"},{"I1001_0":"P:(DE-Juel1)VDB70359","I1001_a":"Maier, U.","I1001_b":"1","label":"Maier, U. ( / )"}]],"select":[[{"I1001_0":"P:(DE-HGF)0","I1001_a":"Mller, H.","I1001_b":"0","I1001_u":"Extern"}],[{"I1001_0":"P:(DE-Juel1)VDB70359","I1001_a":"Maier, U.","I1001_b":"1","label":"Maier, U. ( / )"}]]}]
		
		//differentiate between pasted and choosing authors
		if (results[0].select.length > 1){
			
			//for semi manual input & pasted input
			$.each(results[0].select, function(i, item) {
				//for semi manual input (nubmerof(Guess)== 1 == numberof(Selected))
				//e.g Plott, C. [P:(DE-Juel1)133815]; Mironov, V. P. [P:(DE-HGF)0] ; Boulyga, S. F. [P:(DE-HGF)0] ; Becker, J. S. [P:(DE-Juel1)VDB2662]
				//and check exactMatch (True/False/Unknown Identifier) (True & Unknown Identifier mark semi manual input)
				if (item.length == results[0].guess[i].length && item[0].exactMatch !== 'False'){
					$.pasted_author_input = false;
					$.checked_author_input = true	
					item = item[0];
					item = set_general_role(item);
					check_role(item);
					$($.author_field ).tokenInput("insert", item);
				}
				else {//regular pasted authors
					$.pasted_author_input = true;		// for tokenFormatterFunction
					$($.author_field ).tokenInput("add", item[0]);
				}
			});
			
		}else{	
			$.pasted_author_input = false; 		// for tokenFormatterFunction
			$.checked_author_input = true		// for alert mark authorlist as checked/manual input, if only one manual action 
			//return guess object for choosing right author in this tokeininput instance
			return results[0].guess[0];	
		}
    };
	
	var confirmFunction = function (item) {
		//set status on checked/manual input
		$.pasted_author_input = false;
		item.pasted = false;
		$.checked_author_input = true

		//final format into 1001_ and 7001_ here
		hidden2final_author();
	};
	
	var editFunction = function (item) {
		//call edit dialog
		open_edit_dialog(item);
	};
	
	var initFunction = function () {
		//add clear all author to html
		$('label[for='+$.author_field_id+']').next().append(clearLink);
	};
	
	
	//
	//prefill on modify
	//
	
	//prepopulate author field from given hidden fields before tokeninput is initialised
	if ($($.hidden_first_author_field).val() !== ""){	
		
		//get authorlist in marc syntax
		var final1001_ = jQuery.parseJSON($($.hidden_first_author_field).val());
		var final7001_ = jQuery.parseJSON($($.hidden_remain_author_field).val());		
		var all_authors = final1001_;
		
		////test output
		//console.log(JSON.stringify(final1001_));
		//console.log(JSON.stringify(final7001_));
		
		//only if final7001_ exists -> for avoiding error "a is null"
		if (final7001_ !== null){
			$.each(final7001_, function(i, entry) {
				all_authors.push(entry); 
			});
		}

		//call invenio search for complete entry with label etc.
		$.each(all_authors, function(i, entry) {
			var item = {};
			
			//set author as default role, if no "e" exist
			if (typeof entry.e == 'undefined')
				entry.e = $.default_author;				
			if (typeof entry.u == 'undefined')
				entry.u = "Extern";
				
			if (typeof entry["0"] == 'undefined'){
				//we have entries without $0 -> case no id exists  
				//query HandleNames only with name
				data = entry.a; 
			}else{
				//entries with $0 (all cases no differentiation between "P:(DE-HGF)0", own or partner id necessary)
				data = entry.a+' ['+entry["0"]+'] '; 
				//author input contains checked items
				$.checked_author_input = true;
			}
			
			//get item incl. label etc from  HandleNames with adjusted data query
			$.ajax({
				type: "GET", 
				url: $.srcurl_names,
				data: {names: data},
				dataType: "json",
				async: false,
				success: function(data) {
					if (data !== null) {
						item = data.select[0][0];
						item.I1001_e = entry.e;		//add role
						item.I1001_b = entry.b;		//add order
						if (typeof entry["0"] == 'undefined') 
							// Ensure, that items without id are treaded like they
							// were freshly added, ie. they show up in red and so on.
							item.pasted = true; 
						prePop.push(item);			//put prepop array for tokeninput	
					}
				}
			});	

		});		
				

		//set first author on false
		$.first_author_input = false;
		
		////test output
		//console.log(JSON.stringify(prePop));
		
	};
	
	//TEST of input on modify (called before initialisation of tokeninput instance)
	//prePop = [{"I1001_0":"P:(DE-HGF)0","I1001_a":"ext,","I1001_b":"0","I1001_u":"Extern","label":"ext,(Extern)","I1001_e":"author"},{"label":"Plott, Cornelia (ZB / c.plott@fz-juelich.de)","I1001_0":"P:(DE-Juel1)133815","I1001_a":"Plott, Cornelia","I371__m":"c.plott@fz-juelich.de","I9201_k":"ZB","I1001_e":"corresponding author"},{"label":"Hinz, Ulrich (G-SV / u.hinz@fz-juelich.de)","I1001_0":"P:(DE-Juel1)125388","I1001_a":"Hinz, Ulrich","I371__m":"u.hinz@fz-juelich.de","I9201_k":"G-SV","I1001_e":"author"},{"I1001_0":"P:(DE-Juel1)133832","I1001_a":"wagner,","I1001_b":"0","I371__m":"a.wagner@fz-juelich.de","I9201_k":"ZB","label":"Wagner, Alexander (ZB / a.wagner@fz-juelich.de)","I1001_e":"author"}];
	
	//for handle roles, create custom select box dialog into div #selectboxRole 
	create_role_box($.author_field , $.role_list);
	
	//
	//tokeninput for authors
	//
	
	//handle author input as tokens with autocomplete functionality
	$($.author_field).tokenInput($.srcurl_names, {
		hintText: "",
		dialogText:"&nbsp;<img src='/img/hgfauedit.png' height='16px' width='16px' alt='edit'/>&nbsp;",
		okText:"&nbsp;<img src='/img/hgftick.png' height='16px' width='16px' alt='ok'/>&nbsp;",
		method: "POST",
		queryParam: "names",
		tokenDelimiter: ";",
		propertyToSearch: "",  
		crossDomain: false,
		tokenValue:"label",
		searchDelay: 100,
		minChars: 3,
		animateDropdown: false,
		preventDuplicates: false,		
		prePopulate:prePop,		
		processpreResult: true, 
		makeSortable: true,
		allowDialog: true,
		allowOK: true,
		onAdd: addFunction,
		onDelete: changeFunction,
		tokenFormatter: tokenFormatterFunction,
		resultsFormatter: resultsFormatterFunction,
		onResult: resultFunction,
		onMove: changeFunction,
		onOK: confirmFunction,
		onDialog: editFunction,
		onInit: initFunction
	});


	
	//TEST autopopulate on hgfimport (called after initialisation of tokeninput instance)
	//autopopulate_author("Plott, C.; Maier, U.; Müller, H.");
	//autopopulate_author("Plott, C.; Hinz, W.; Kunz, U;  Maier, U.; Müller, H.");
	

	function update_tokeninput(item_list){
		//update tokeninput list e.g. after check role
		old_pasted_author_input = $.pasted_author_input;
		$.each(item_list, function(i, item) {
			$($.author_field ).tokenInput("remove", item);
			$($.author_field ).tokenInput("insert", item);
			$.pasted_author_input = ""; //for undefinded pasted action - not true/not false - depend on item
		});
		$.pasted_author_input = old_pasted_author_input;
		//make #I1001_ and #I7001_
		hidden2final_author();
		
	}
	

	
	function fill_institutions(item){
	//for prefill and update institution field from author item on edit dialog
		
		//remove old entries
		$('#editTokenInst').tokenInput("clear");
		if (typeof item.I9101_ !== 'undefined'  && item.I9101_.length){
			$.each(item.I9101_, function(i, inst_obj) {
				//add new entries
				$('#editTokenInst').tokenInput("add", inst_obj);
			});
		}	
	}

	
	function create_role_box(append_tag, list){
		
		//create select box
		var select = '<select>';
		for(var i = 0; i < list.length; i++){
			//with value (as id without spaces) for preselection
			select += '<option value='+list[i].replace(" ","")+'>'+list[i]+'</option>';
		}
		select += '</select>';
		
		//append selectbox before selecting vals
		$($.author_field ).append('<div id="selectboxRole">'+select+'</div>');
		
		//initial preselection with corresponding
		if (prePop.length == 0){
			$("#selectboxRole option[value="+$.default_cp_author.replace(" ","")+"]").attr('selected',true);
		}else { // except for prepopulate for modify, than use author as default 
			$("#selectboxRole option[value="+$.default_author.replace(" ","")+"]").attr('selected',true);
		}
		
		//for opera append box before get selecting vals
		$($.author_field).append($('#selectboxRole'));
		//than set default/selected role
		$.selected_role = $('#selectboxRole option:selected').text(); 
	
		//for ie & invenio submitmask initial load & close
		$('#selectboxRole').dialog({title: 'choose role:'});
		$('#selectboxRole').dialog("close");
	}
	
	
	function create_edit_box(item){
		//create and define edit box
		
		//define html for edit box 
		var editPerson = '<label for="editPerson">Edit Author:&nbsp;</label><br><input type="text" name="editPerson" id="editPerson" size="50"/>';
		var	selectRole = '';
		var editTokenInst = '<label for="editTokenInst">Institution:&nbsp;</label><br><input type="text" name="editTokenInst" id="editTokenInst" size="50"/>';
		var allFieldsHtml = '';
		var divHtml = '';
	
		//customize html of role selectbox
		//deselect all roles and select role of editing item	
		$('#selectboxRole option:selected').attr('selected', false);
		//for IE9 not works .attr('selected', false); .prop('selected', null); .prop('selected', false); .removeAttr('selected'); .removeProp('selected');
		//therfore additional string replace		
		var clean_html = $('#selectboxRole').html();
		clean_html = clean_html.replace('selected=""', '');
		clean_html = clean_html.replace('selected="selected"', '');
		$('#selectboxRole').html(clean_html);
		//select current role of item
		$('#selectboxRole option[value='+item.I1001_e.replace(" ","")+"]").attr('selected',true);	
		selectRole += $('#selectboxRole').html();
		
		//append dialog html to author field
//eb		allFieldsHtml += '<p>'+selectRole+'</p>';
		allFieldsHtml += '<p>'+editPerson+'</p>';
		allFieldsHtml += '<p>'+editTokenInst+'</p>';
		divHtml = '<div id="editDialog">'+allFieldsHtml+'</div>';
		//for unique editDialog replace first and/but append, too
		if ($('#editDialog').length > 0)
			$('#editDialog').replaceWith(divHtml);
		$($.author_field).append(divHtml);
	}


	function open_edit_dialog(item){		
		//open and define dialog and submit results to author token instance 
		$.pasted_author_input = false; // interactive modus

		var old_item = item; 	//save old item (with role etc) for deleting in author tokenlist
		var new_item = item; 	//if item not changed	
		
		//define edit box
		create_edit_box(item);
		//prefill autocomplete field with current item
		$('#editPerson').val(item.I1001_a);
		//define edit person input field via autocomplete
		$('#editPerson').autocomplete({		
			minLength: 2,
			source: function(request, response ) {
				//get data via ajax call 
				$.ajax({
					url: $.srcurl_names,
					data: {names: request.term},
					dataType: "json",
					success: function(data) {
						response(data.guess[0]);
					}
				});
			},
			select: function(e, ui){
				new_item = ui.item;	
				//update institution field
				fill_institutions(new_item);
			}
		}).focus(function() {
			$(this).trigger('keydown.autocomplete');
		});
		
		$('#editTokenInst').tokenInput(srcurl_institutions+'?personid='+item.I1001_0+'&ordno='+item.I1001_b+'&',{
		//$('#editTokenInst').tokenInput('/kb/export?kbname=InstitutionsCollection'+'&',{
			queryParam:'input', 
			propertyToSearch: "label",
			tokenValue:"label",
			tokenDelimiter: ";",
			minChars: 0,
			searchDelay: 100,
			zindex: 1100,
			animateDropdown: false,
			preventDuplicates: false,	
			hintText: "Search Institution",
			onResult: function (results) {
				//tokeninput need array from I9101_ for dropdown etc.
                                return results[0].I9101_;
                        }
		});
/*
		//$('#editTokenInst').tokenInput(srcurl_institutions+'?personid='+item.I1001_0+'&ordno='+item.I1001_b+'&',{
		$('#editTokenInst').autocomplete({
                   minLength: 3,
                   source: function(request, data) {
                  $.get("/kb/export",
                       {kbname: 'InstitutionsCollection', format: 'jquery', term: request.term},
                       function(data){
                          response(data);
                          //return data[0].I9101_;
                       }
                  );
                  },
                  select: function(e, ui){
                         new_item = ui.item;
                         //update institution field
                         fill_institutions(new_item);
                  }
                  
               });
*/
/*
function autocomplete_kb(that, kb_name){
    that.autocomplete({
      minLength: 3,
      source: function(request, response) {
        $.get("/kb/export",
          {kbname: kb_name, format: 'jquery', term: request.term},
          function(data){
            response(data)
            return data[0].I9101_
          }
        );
      },
    });
}
 */             //eb
              //autocomplete_kb($("#editTokenInst"), "InstitutionsCollection"); 
	      //prefill institution field
	      fill_institutions(item);	
	
		//define and open dialog and submit results to author token instance 
		$('#editDialog').dialog({
			title: 'Edit author: '+helplink,
			width: 600, //600 pixel for ok button between tokeninput field
			modal: true,
			beforeClose: function(event, ui) {
				onAdd = false;
				if (escDialog == false){
					//submit new author to tokeninput
					$($.author_field ).tokenInput("remove", old_item);
					if ($('#editPerson').val()){ //not for deleted items
						//select role				
						new_item.I1001_e = ''; //$(this).find("option:selected").html();
						//set item properties
						new_item.checked_role = false;
						new_item.pasted = false;
						//set institution
						new_item.I9101_ = $('#editTokenInst').tokenInput("get");
						//mark authorlist as checked/manual input
						$.checked_author_input = true	
						//add item to author tokeninput
						$($.author_field ).tokenInput("add", new_item);
					}
				}
				onAdd = true;
				escDialog = false;
			},
			buttons:{ "OK": function() { $(this).dialog("close"); } }
		})
		.keyup(function(e){
			//enter
			if (e.keyCode == 13)  
				$(this).dialog( "close" );
			//escape
			if (e.keyCode == 27){ 
				escDialog = true;
				$(this).dialog( "close" );
			}
		});	
	}
	
	
	$("#clearAllAuthors").click(function () {
		//clear all authors
		$($.author_field).tokenInput("clear");
		
		//set default vals
		$.pasted_author_input = false; 
		$.first_author_input = true; 
		$.checked_author_input = false; 
		
		//clear final format 1001_ and 7001_ 
		hidden2final_author();
		
        return false;
    });
	

});

//
//define global vars
//

//global url for http get request
$.srcurl_names = "/HandleNames.py"; 					// for call with one or more name

//global, for change status on autopopulate_author
$.pasted_author_input = false; 
//global, for first author input via autopopulate_author
$.first_author_input = true; 
//global, for select and check role for autopopulate_author, too
$.selected_role;
//global, for checked/manual author import 
$.checked_author_input = false; 

//contains element ids of autor fields
$.author_field_id = 'I1001_a';
$.author_field = '#I1001_a';
$.hidden_first_author_field = '#I1001_';
$.hidden_remain_author_field = '#I7001_';
$.hidden_inst_author_field = '#I9101_';


function set_general_role(item){
//set role of general role box and add to json result item	
	$.selected_role = $('#selectboxRole option:selected').text(); 	
	item.I1001_e = $.selected_role;		
	return item
} 

function check_role(current_item){
//check only one corresponding exists and change if necessary
	var change_list = [];
	
	//for pasted input, let first author on 'corresponding' and set second+n on 'author' via defaut
	//for first input, let first author on 'corresponding', but change input box to 'autor'
	if ($.pasted_author_input || $.first_author_input){
		//set 'author' on defaut
		$("#selectboxRole option[value="+$.default_author.replace(" ","")+"]").attr('selected',true);
		$.selected_role = $('#selectboxRole option:selected').text(); 
		$.first_author_input = false;
		return [];
	}
		
	//if new role 'corresponding', set all existing 'corresponding' on 'author'
	if (current_item.I1001_e == $.default_cp_author){
		all_tokens = $($.author_field).tokenInput("get");
		$.each(all_tokens, function(i, item) {
			//change 'corresponding' to 'author', but not for current item
			if (item.label !== current_item.label && item.I1001_e == $.default_cp_author ){
				item.I1001_e = $.default_author;
			}
		//put all items in change list for keeping order
		item.checked_role = true;
		change_list.push(item);
		});
		return change_list;
	}
	return [];
} 

function hidden2final_author(){
		// format and write hidden stuff into json 1001_ 7001_ structure
		
		// get hiddeninput array of hashes [{"label":<label>,"I1001_0":<I1001_0>,"I1001_a":<I1001_a>,...},{...},...]
		var hiddeninput =  $($.author_field).tokenInput("get");
		////test output
		//console.log(JSON.stringify(hiddeninput));
		
		// first author into hidden field I1001_ [{ 'a':'first Author, H', '0':'P(DE..', 'b':'0'}]
		// second to n authors into hidden field I7001_ [{ 'a':'Author, H', '0':'P(DE..', 'b':'0'}, {'a':'Beta, H', '0':'P(DE...', 'b':'1'}]
		var final1001_ = []
		var final7001_ = [];
		var final9101_ = [];
		
		//for order don't use counter in 1001_b, not ok for manual input
		var i = 0;		
		$.each(hiddeninput, function(index, person) {
			var item = {};
			var inst_item = {};
			
			//save (all) keys with syntax Ix001_x 	
			$.each(person, function(key, val) {
				//for order like displayed list, for marc better as string
				item['b'] = String(i);
				
				//save all marc vals (without subfields 0ub)
				var match =  key.match(/I[17]001_[^0ub]/i);
				if (match !== null  && val !== $.role_list[0])
					item[key.substring(6,7)] = val;	
					//key[6] works not in ie compatibility mode
					//item[key[6]] = val;	
				
				//for checked (ok/manual typing) add $0 and $u(?)
				if (person.pasted == false){
					var match =  key.match(/I[17]001_[0u]/i);
					if (match !== null && val !== $.role_list[0])
						//item[key[6]] = val;	
						item[key.substring(6,7)] = val;	
					
					//add all insitutions fields with one character joined with $b from author field
					if (key == 'I9101_' && val.length) {
						$.each(val, function(i, inst_obj) {
							inst_item = {};
							$.each(inst_obj, function(inst_key, inst_val) {
								if (inst_key.length == 1)
									inst_item[inst_key] = inst_val;
							});
							//overwrite "b"
							inst_item["b"] = item["b"];
							final9101_.push(inst_item);
						});
					}
				}
			});
			//first author into I1001_ 
			if (i==0){
				final1001_.push(item);
			//second to n authors into I7001_ 
			}else{
				final7001_.push(item);
			}					
			i = i+1; 
		});
		
		////test output
		//console.log(JSON.stringify(final1001_));
		//console.log(JSON.stringify(final7001_));
		//console.log(JSON.stringify(final9101_));
		//console.log('checked_author_input:'+$.checked_author_input);
		
		
		//set into hidden fields as string 
		$($.hidden_first_author_field).val(JSON.stringify(final1001_));
		$($.hidden_remain_author_field).val(JSON.stringify(final7001_));
		$($.hidden_inst_author_field).val(JSON.stringify(final9101_));
		
	
	}

function autopopulate_author(author_str) {
	//prepopulate results from eg. hgfImport after tokeninput is initialized
	$($.author_field ).tokenInput("clear");
	$.ajax({
		type: "POST",
		url: $.srcurl_names,
		data: "names="+encodeURIComponent(author_str),
		dataType: "json",
		async: false,
		success: function(data) {
				$.pasted_author_input = true; // for tokenFormatterFunction				
				$($.author_field ).tokenInput("clear");
				$.each(data.select, function (i, item) {
					item = item[0];
					item = set_general_role(item);
					check_role(item);
					$($.author_field ).tokenInput("insert", item);
				});
				//make #I1001_ and #I7001_
				hidden2final_author();
				
		}						
	});	
}


