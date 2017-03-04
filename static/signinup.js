jQuery(document).ready(function($) {
    $('#sign-name').change(function(){
        var username = $('#sign-name').val();
        if (username.length <6){
            $('#msg').text('用户名必须至少6位').css('color','red')
        }
        else{
        $.ajax({
            url: '/admin/checkname/',
            type: 'GET',
            dataType: 'json',
            data: {username:username},
        })
        .done(function(response) {
           if (response.msg == true){
            $('#msg').text('用户名可用').css('color','green')
           }else{
            $('#msg').text('用户名已存在').css('color','red')
           }
        })
        .fail(function() {
            console.log("error");
        })
        .always(function() {
            console.log("complete");
        }); 
        }   
    })
    $('#nickname').change(function(){
        var nickname = $('#nickname').val();
        if (nickname.length>3){
            $.ajax({
                url: '/admin/check-nickname/',
                type: 'GET',
                dataType: 'json',
                data: {nickname:nickname},
            })
        .done(function(response) {
            if (response.msg == true){
                $('#nick').text('昵称可用').css('color','green')
            }else{
                $('#nick').text('昵称已存在').css('color','red')
            }
        })
        .fail(function() {
            console.log("error");
        })
        .always(function() {
            console.log("complete");
        }); 
        } 
    })
    $('.closepanel').click(function(){
        $(this).parent().addClass('hide');
        $('.login-shadow').addClass('hide')
        $('body').css('overflow','visible')
        $('.medium').css('filter','blur(0px)')
    })
    $('#login').click(function(){
        $.ajax({
            url: '/admin/login/',
            type: 'GET',
            dataType: 'html',
            async:false
            })
            .done(function(content) {
            $('.panel-cover').html(content);
            $('.login-shadow').removeClass('hide')
            $('body').css('overflow','hidden')
            $('.medium').css('filter','blur(2px)')
            console.log('ok')
            })
            .fail(function() {
            console.log("error");
            })
            .always(function() {
            console.log("complete");
        });
    });
    $('#signup').click(function(){
        $.ajax({
            url: '/admin/signup/',
            type: 'GET',
            dataType: 'html',
        })
        .done(function(content) {
            $('.panel-cover').html(content);
            $('.login-shadow').removeClass('hide')
            $('body').css('overflow','hidden')
            $('.medium').css('filter','blur(2px)')
        })
        .fail(function(){
            console.log("error");
        })
        .always(function() {
            console.log("complete");
        });       
    })
        $('.panel-login').click(function(){
            $.ajax({
                url: '/admin/login/',
                type: 'GET',
                dataType: 'html',
            })
            .done(function(content) {
                $('.panel-cover').html(content)
            })
            .fail(function() {
                console.log("error");
            })
            .always(function() {
                console.log("complete");
            });       
        })
        $('.panel-signup').click(function(){
            $.ajax({
                url: '/admin/signup/',
                type: 'GET',
                dataType: 'html',
                async:true
            })
            .done(function(content) {
                $('.panel-cover').html(content)
            })
            .fail(function() {
                console.log("error");
            })
            .always(function() {
                console.log("complete");
            });
        })
});

// fb login
// window.fbAsyncInit = function() {
//   FB.init({
//     appId      : '1266851933359601',
//     cookie     : true,  // enable cookies to allow the server to access 
//                         // the session
//     xfbml      : true,  // parse social plugins on this page
//     version    : 'v2.7' // use graph api version 2.5
//   });
// }
//     FB.getLoginStatus(function(response){
//         console.log(response)
//         statusChangeCallback(response)
//     })
//   // This is called with the results from from FB.getLoginStatus().
//   function statusChangeCallback(response) {
//     console.log('statusChangeCallback');
//     console.log(response);
//     // The response object is returned with a status field that lets the
//     // app know the current login status of the person.
//     // Full docs on the response object can be found in the documentation
//     // for FB.getLoginStatus().
//     if (response.status === 'connected') {
//       // Logged into your app and Facebook.
//       testAPI();
//     } else if (response.status === 'not_authorized') {
//       // The person is logged into Facebook, but not your app.
//       document.getElementById('status').innerHTML = 'Please log ' +
//         'into this app.';
//     } else {
//       // The person is not logged into Facebook, so we're not sure if
//       // they are logged into this app or not.
//       document.getElementById('status').innerHTML = 'Please log ' +
//         'into Facebook.';
//     }
//   }

//   // This function is called when someone finishes with the Login
//   // Button.  See the onlogin handler attached to it in the sample
//   // code below.
//   function checkLoginState() {
//     FB.getLoginStatus(function(response) {
//       statusChangeCallback(response);
//     })
//   }


//   // Now that we've initialized the JavaScript SDK, we call 
//   // FB.getLoginStatus().  This function gets the state of the
//   // person visiting this page and can return one of three states to
//   // the callback you provide.  They can be:
//   //
//   // 1. Logged into your app ('connected')
//   // 2. Logged into Facebook, but not your app ('not_authorized')
//   // 3. Not logged into Facebook and can't tell if they are logged into
//   //    your app or not.
//   //
//   // These three cases are handled in the callback function.


//   // Load the SDK asynchronously
//   (function(d, s, id) {
//     var js, fjs = d.getElementsByTagName(s)[0];
//     if (d.getElementById(id)) return;
//     js = d.createElement(s); js.id = id;
//     js.src = "//connect.facebook.net/en_US/sdk.js";
//     fjs.parentNode.insertBefore(js, fjs);
//   }(document, 'script', 'facebook-jssdk'));

//   // Here we run a very simple test of the Graph API after login is
//   // successful.  See statusChangeCallback() for when this call is made.
//   function testAPI() {
//     console.log('Welcome!  Fetching your information.... ');
//     FB.api('/me', function(response) {
//       console.log('Successful login for: ' + response.name);
//       document.getElementById('status').innerHTML =
//         'Thanks for logging in, ' + response.name + '!';
//     });
//   }