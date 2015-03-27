(function() {
    
    var UPDATE_COMMENT_BASIC_ID = 'update-comment-';

    // Capture all the update buttons
    $("[id^=" + UPDATE_COMMENT_BASIC_ID + "]").on('click', function(e) {
        comment_id = $(this).attr('id').replace(UPDATE_COMMENT_BASIC_ID, '');
        
        // Set comment in the textarea and the ID in the hidden input
        $('#comment-id').val(comment_id);
        $('#field-comment').val($('#comment-' + comment_id).text().trim());

        // Hide and show buttons
        $('#suggest-comment-update-discard').removeClass('hide');
        $('#suggest-comment-update').removeClass('hide');
        $('#suggest-comment-add').addClass('hide');
    });

    // Capute the discard button
    $('#suggest-comment-update-discard').on('click', function(e) {
        // Remove the values
        $('#comment-id').val('');
        $('#field-comment').val('');

        // Hide and show buttons
        $('#suggest-comment-update-discard').addClass('hide');
        $('#suggest-comment-update').addClass('hide');
        $('#suggest-comment-add').removeClass('hide');

        // Prevent default
        e.preventDefault();
    })
})();