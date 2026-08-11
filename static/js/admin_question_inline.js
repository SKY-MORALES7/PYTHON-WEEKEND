document.addEventListener('DOMContentLoaded', function() {
    // Django admin bundles jQuery as django.jQuery
    var $ = django.jQuery;

    function toggleChoicesField(row) {
        var questionTypeSelect = $(row).find('select[id$="-question_type"]');
        var choicesFieldRow = $(row).find('.field-choices');
        
        if (questionTypeSelect.length > 0) {
            if (questionTypeSelect.val() === 'choices') {
                choicesFieldRow.show();
            } else {
                choicesFieldRow.hide();
            }
        }
    }

    // Initialize all existing rows
    $('.inline-related').each(function() {
        toggleChoicesField(this);
    });

    // Listen for changes on any question_type select within the inline
    $(document).on('change', 'select[id$="-question_type"]', function() {
        var row = $(this).closest('.inline-related');
        toggleChoicesField(row);
    });
});
