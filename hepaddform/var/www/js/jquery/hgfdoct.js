$(document).ready(function() {
    $("#I989__a").autocomplete({
        source: $.hgf_doct,
        minLength: 0,
        delay: 0
    }).focus(function() {
        if (this.value === "") $(this).trigger('keydown.autocomplete');
    });
});
