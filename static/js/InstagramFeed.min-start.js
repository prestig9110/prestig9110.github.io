(function(){
    new InstagramFeed({
        'username': 'gmgameserver',
        'container': document.querySelector(".instagram-post"),
        'display_profile': false,
        'display_biography': true,
        'display_gallery': true,
        'display_captions': true,
        'max_tries': 80,
        'callback': null,
        'styling': true,
        'items': 8,
        'items_per_row': 4,
        'margin': 1,
        'lazy_load': true,
        'on_error': console.error
    });
})();