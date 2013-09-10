$(document).ready(function() {
    $("#I041__a").autocomplete({
        source: $.hgf_languages,
        minLength: 0,
        delay: 0
    }).focus(function() {
        if (this.value === "") $(this).trigger('keydown.autocomplete');
    });
});
