function build_tooltip() {
        /*Purpose: Append a tooltip on all the help icons.*/

        var tt = {};    
        tt['hgf_import'] = 'If a DOI for this article was deposited and is available at CrossRef, enter it here, and then click “Finish Submission” without filling out other fields.  Data will be imported from CrossRef. If the DOI was never deposited, or was deposited through an agency other than CrossRef, this form will not automatically fill in the various fields.'//doi import
        tt['245__a'] = 'Enter the article title here. TeX coding is strongly encouraged for special symbols. Unicode is supported.';//title
        tt['035__a'] = 'Provide the arXiv number here, if the article was originally deposited at arXiv. If so, no additional information about the article itself is required, as this will be drawn directly from arXiv.'; //arXiv (eprint)
        tt['269__c'] = 'If the article originally appeared on arXiv, enter the date it was deposited here.'; //preprint date
        tt['773__p'] = 'If the article appeared in a journal, enter the standard abbreviation for journal name used in citations, or the journal coden.'; //journal
        tt['773__v'] = 'If the article was published in a journal, enter the volume number or name here'; //volume
        tt['773__c'] = 'Please provide the page range for the article. If a journal uses article IDs instead of page numbers, enter that instead.'; //page range
        tt['989__a'] = 'Please select the paper types that apply to this submission.'; //Doc-type
        tt['300__a'] = 'If the article appears in full in a publication, enter the total number of pages on which this article appears. If the article does not appear in print, a count of PDF pages is acceptable.'; //number of pages
        tt['111__g'] = 'If the article is part of a conference proceedings, enter the INSPIRE conference number. You can search for these in the “Conferences” section of <a href="#">test</a>'; //conference number
        tt['693__e'] = 'If the article is the product of an experimental collaboration, please provide the experiment name here. You can search for experiment names in the “Experiments” section of this site.'//experiment
        tt['260__c'] = 'Enter the date the article was published or first made available.'; //publication date
        tt['8564_u'] = 'Please provide the URL for the article, if a version of it is available on line.'; //url
        tt['1001_a'] = ' ';//author 
        tt['520__a'] = 'Enter the abstract for the article here.'; //abstract
        tt['999C5'] = 'In this box, copy and paste the references for the article. References can be complete text citations or a list of INSPIRE bibtex keys. References provided as text must use standard journal abbreviations, and standard citation formatting.\n Use the “Try INSPIRE\’s Reference Extractor” link to see how your references will appear in INSPIRE.'; //references
        tt['500__a'] = 'Provide any additional information you believe would be helpful here.  Examples include [provide examples??]'; //additional info
        tt['hgf_relevance'] = 'Please provide a few words on why this article is relevant to high energy physics.';//relevance 
        tt['65017'] = 'Please indicate which subject categories apply to this submission. Check all that directly apply.';//INSPIRE Subject Categories
        tt['hgf_email'] = 'Please provide an e-mail address at which we can contact you if we have questions about this requested addition.';//email 
        tt['710__g'] = 'If the article is the product of an experimental collaboration, enter the name of the collaboration here.';//Collaboration 

        //multi-line field 

        $(".Helptext").each(function () {
            var originalSrc = $(this).attr('id');
            var to = originalSrc.length - 13;
            originalSrc = originalSrc.substring(0, to);
            if (tt[originalSrc]) {
                $(this).attr('title', tt[originalSrc]);    
            }else {
                $(this).attr('title', originalSrc);    
            }
        });
}

//contains possible roles for persons in field 100/700
$.default_author = ''//#"Author";
$.default_cp_author = '' //#"Corresponding author";
$.role_list = [ $.default_author, $.default_cp_author , "Editor",
"Collaboration Author", "Gutachter", "Gastherausgeber", "Gefeierter",
"Illustrator", "Redakteur", "Rezensent", "Serienherausgeber",
"Übersetzer" ];

// List of languages for a given work
$.hgf_languages = ["English", "Czech", "Dutch", "Finnish", "French",
"German", "Greek", "Hungarian", "Italian", "Norwegian", "Polish",
"Portuguese", "Russian", "Slovak", "Spanish", "Swedish", "Other",
"Multiple"];

// List of Doc types
//$.hgf_doct = ["Book", "Thesis", "ConferencePaper", "Proceedings", "Published", "Review"];


// List of Publicationform for a given work
$.hgf_pubform = ["Druck", "Online", "Datenträger", "Digitalisat", "Medienkombination"];


// (Sub-)Types a talk may have
$.hgf_talktype = ["Invited", "Plenary/Keynote", "After Call", "Other"]

function WashJSstr(jsstr) {
    jsstr = jsstr.replace(/\n/g, '');
    jsstr = jsstr.replace(/,\s*]/g, ']');
    jsstr = jsstr.replace(/,\s*}/g, '}');
    jsstr = jsstr.replace(/,\s*$/g, '');
    return jsstr
}
//this is used to clear all fields when the arXiv field is not empty
function resetForm($form) {
    $form.find('input:text, input:password, input:file, select, textarea').not('#I035__a, #Ihgf_email').val('');
    $form.find('input:radio, input:checkbox')
    .removeAttr('checked').removeAttr('selected');
}
$(document).ready(function() {

//arXiv or Eprint
  $('#I035__a').change(function() {
    if( $(this).val().length > 0 ) {
        $("#clearAllAuthors").trigger("click");
        resetForm($('#submissionfields'));
	    $( "span" ).each(function( index ) {
		   $(this).hide();
	    });
        //show email 
        $(".G035__a").show();
        $(".MG").show();
    }else{
	$( "span" ).each(function( index ) {
		$(this).show();
	});
    }
  });
  	
	// hide the AJAX notifier
 	$('#loadingMsg').hide();

	// Bind visibility of the AJAX notifier to the activity of _ANY_ ajax-call on the page.
  $('#loadingMsg').bind("ajaxSend", function() {
            //$(this).show();
  }).bind("ajaxComplete", function() {
            $(this).hide();
  });

  $('label[for="Ihgf_email"]').before('<p id="status-message"></p>');
  
$('label[for="I999C5"]').after('<div><a href="http://inspirehep.net/textmining/" target="blank_"> - Try Inspire\'s Reference Extractor</a></div>');

  $("#Ihgf_email").verimail({
      messageElement: "p#status-message"
  });

  build_tooltip();
//static text for title
  $('label[for="I1001_a"]').before('<div class="Lhgf_import"></div>');
  $("#I1001_a").before('<div id="author-msg"> After entering each author name, please click on its edit icon to add the institution.</div>');

// mapping F1 does not really work well, as some strange browsers seem
// to block it and it also causes strange effects. Another keyboard
// binding does not seem sensible either as it is just not initutive
// and non SAA/CUA.
//
//  // Links to our online help system are constructed by the wiki base
//  // + the ID of the field in question added. Additionally, we might
//  // have individual subsections to call up, those live in the ID as
//  // well.
//  var wikibase = 'http://invenio-wiki.gsi.de/cgi-bin/view/Main/'
//  var helptags = $('span.Helptext');
//  $.each(helptags, function(key, value){
//    // Get the ID of the field. This coincides with the help link to
//    // be constructed
//    var id = value.id;
//    // construct the fields ID for the acutal binding
//    var field = '#I' + id.replace(/#.*/g, '').toLowerCase();
//    // bind F1 to call the help link
//    $(field).keypress(function(event){
//      switch(event.keyCode) {
//        case 112:
//          window.open(wikibase + id, '_blank')
//          break;
//      }
//    })
//  });
});

