jQuery(document).ready(function($) {
        var nickname = $('.followbutton').attr('data-value')
        url = '/admin/follow/'
    $('.followbutton').click(function(){
        $.ajax({
        url: url,
        type: 'GET',
        dataType: 'json',
        data: {nickname:nickname},
        })
    .done(function(response) {
        if(response.msg==true){
            $('.followbutton').html('<b class="fa fa-check"></b>&nbsp;<span class="followed">Followed</span>')
        }else if(response.msg==false){
            $('.followbutton').html('<b class="fa fa-plus"></b>&nbsp;<span class="followed">Follow</span>')
        }
    })
    .fail(function() {
    console.log("error");
    })
    .always(function() {
    console.log("complete");
    });
    })
    });