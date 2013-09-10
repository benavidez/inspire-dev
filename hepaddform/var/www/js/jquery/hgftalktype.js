$(document).ready(function() {

  // Ensure that all fields are filled as required by calling
  // prefill(). Note that this function is only defined in modify
  if(typeof prefill == 'function') {
    prefill();
     if ($("#I3367_").val() !== '') {
       var doctypes = eval($('#I3367_').val());
       $.each(doctypes, function(index, value) {
         if (value.x != undefined) {
           $("#I3367_x").val(value.x);
         } ;
       });
     }
  }

  $("#I3367_x").autocomplete({
      source: $.hgf_talktype,
      minLength: 0,
      delay: 0
  }).focus(function() {
      if (this.value === "") $(this).trigger('keydown.autocomplete');
  });

});

