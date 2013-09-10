function hgfSubmitForm() {
   document.forms[0].action="/submit";
   document.forms[0].step.value=1;
   user_must_confirm_before_leaving_page = false;
   document.forms[0].submit();
}

function hgfModifyForm() {
  document.forms[0].step.value = 2;
  user_must_confirm_before_leaving_page = false;
  document.forms[0].submit();
}

function hgf_finish(btnevent) {
   if (btnevent == 'sbirelease') {
      if ($.checked_author_input == false) {
                 if (tester2()) {
                   hgfSubmitForm();
	           return;
                 }
        var dlg = '';
        dlg += '<p class="tmp">Assigning publications to individual authors is important ';
        dlg += 'for individual publication lists (e.g. CVs, websites...).</p> ';
        dlg += '<p class="tmp">Please consider investing some seconds for this.</p> ';
        dlg += '<p class="tmp">Using the &nbsp;<img src="/img/hgftick.png">&nbsp; button ';
        dlg += 'you can confirm the systems suggestion, <strong>in case it is ';
        dlg += 'correct</strong>. If it is not, please use the  ';
        dlg += '&nbsp;<img src="/img/hgfauedit.png">&nbsp; button to correct ';
        dlg += 'the suggestion.</p>'
        dlg += '<p class="tmp">Thank you for your help!</p> ';

        $('.Lhgf_import').append('<div id="authorcheck">' + dlg + '</div>');

        $('#authorcheck').dialog({
          title : 'You did not assign this publication to any authors',
          modal : true,
          width : 'auto',
          buttons: [
             {
               text:  'Take me back, I missed something!',
               // move the import to the fields
               click: function() { 
                 $(this).dialog("close");
                 $('.tmp').remove();
               }
             },
             {
               text:  'Proceed anyway',
               // we do nothing here
               click: function() { 
                 $(this).dialog("close");
                 if (tester2()) {
                   hgfSubmitForm();
                 }
                 $('.tmp').remove();
               }
             }
          ]
        });
      }
      else if (tester2()) {
        hgfSubmitForm();
      }
   }
   if (btnevent == 'mbirelease') {
      // Modify currently has no tests
      document.forms[0].hgf_release.value='yes';
      hgfModifyForm();
   }
   if (btnevent == 'sbipostpone') {
      hgfSubmitForm();
   }
   if (btnevent == 'mbipostpone') {
      hgfModifyForm();
   }
   if (btnevent == 'sbidelete') {
      alert('sbi: Delete - You should never end up here!');
   }
   if (btnevent == 'mbidelete') {
      var answer = confirm("Are you sure that you want to DELETE this record?")
      if (answer){
        document.forms[0].hgf_delete.value='yes';
        hgfModifyForm();
      }
   }
}
