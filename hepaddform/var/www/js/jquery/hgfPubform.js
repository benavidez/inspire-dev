$(document).ready(function() {
    $("#I245__k").autocomplete({
        source: $.hgf_pubform,
        minLength: 0,
        delay: 0
    }).focus(function() {
        if (this.value === "") $(this).trigger('keydown.autocomplete');
    });
});
