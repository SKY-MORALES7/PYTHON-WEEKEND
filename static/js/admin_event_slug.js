document.addEventListener('DOMContentLoaded', function() {
    var titleInput = document.getElementById('id_title');
    var slugInput = document.getElementById('id_slug');
    var publishedCheckbox = document.getElementById('id_published');

    if (!titleInput || !slugInput) return;

    function slugify(text) {
        return text.toString().toLowerCase().trim()
            .replace(/\s+/g, '-')           // Replace spaces with -
            .replace(/[^\w\-]+/g, '')       // Remove all non-word chars
            .replace(/\-\-+/g, '-')         // Replace multiple - with single -
            .replace(/^-+/, '')             // Trim - from start of text
            .replace(/-+$/, '');            // Trim - from end of text
    }

    titleInput.addEventListener('input', function() {
        if (publishedCheckbox && publishedCheckbox.checked) {
            return; // Do not touch slug on published live events
        }
        var newSlug = slugify(titleInput.value);
        if (newSlug) {
            slugInput.value = newSlug;
        }
    });
});
