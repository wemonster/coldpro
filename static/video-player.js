$(function(){
    $('.video').on('mouseenter',function(){
    if(this.paused) this.play();
    }).on('mouseleave',function(){
    if(this.play()) this.pause();
    })
})