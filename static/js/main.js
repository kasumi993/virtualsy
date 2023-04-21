
(function ($) {
    "use strict";


    /*==================================================================
    [ Focus input ]*/
    $('.input100').each(function(){
        $(this).on('blur', function(){
            if($(this).val().trim() != "") {
                $(this).addClass('has-val');
            }
            else {
                $(this).removeClass('has-val');
            }
        })    
    })
  
  
    /*==================================================================
    [ Validate ]*/
    var input = $('.validate-input .input100');

    $('.validate-form').on('submit',function(e){
        e.preventDefault();
        var check = true;

        for(var i=0; i<input.length; i++) {
            if(validate(input[i]) == false){
                showValidate(input[i]);
                check=false;
            }
        }

        if (check) {
            connect(input[0].value, input[1].value);
        }

        return check;
    });


    $('.validate-form .input100').each(function(){
        $(this).focus(function(){
           hideValidate(this);
        });
    });

    function validate (input) {
        if($(input).attr('type') == 'email' || $(input).attr('name') == 'email') {
            if($(input).val().trim().match(/^([a-zA-Z0-9_\-\.]+)@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.)|(([a-zA-Z0-9\-]+\.)+))([a-zA-Z]{1,5}|[0-9]{1,3})(\]?)$/) == null) {
                return false;
            }
        }
        else {
            if($(input).val().trim() == ''){
                return false;
            }
        }
    }

    function showValidate(input) {
        var thisAlert = $(input).parent();

        $(thisAlert).addClass('alert-validate');
    }

    function hideValidate(input) {
        var thisAlert = $(input).parent();

        $(thisAlert).removeClass('alert-validate');
    }
    
    /*==================================================================
    [ Show pass ]*/
    var showPass = 0;
    $('.btn-show-pass').on('click', function(){
        if(showPass == 0) {
            $(this).next('input').attr('type','text');
            $(this).find('i').removeClass('zmdi-eye');
            $(this).find('i').addClass('zmdi-eye-off');
            showPass = 1;
        }
        else {
            $(this).next('input').attr('type','password');
            $(this).find('i').addClass('zmdi-eye');
            $(this).find('i').removeClass('zmdi-eye-off');
            showPass = 0;
        }
        
    });

    function connect(email, password) {
        const emails = [ 'nocredit@gmail.com', 'onemachine@gmail.com', 'manymachines@gmail.com'];

        if (password === 'password' && (emails.includes(email) )) {
            if (email === 'nocredit@gmail.com') {
                console.log(`connected with ${email}`);
                localStorage.setItem('user', JSON.stringify({
                    name: 'NoCredit User',
                    email: 'nocredit@gmail.com',
                    credit: 0,
                }))
            } else if (email === 'onemachine@gmail.com') {
                console.log(`connected with ${email}`);
                localStorage.setItem('user', JSON.stringify({
                    name: 'OneMachine User',
                    email: 'onemachine@gmail.com',
                    credit: 100,
                }))
            } else if (email === 'manymachines@gmail.com') {
                console.log(`connected with ${email}`);
                localStorage.setItem('user',JSON.stringify({
                    name: 'ManyMachines User',
                    email: 'manymachines@gmail.com',
                    credit: 200,
                }))
            }
            window.location.href = '/home';
        } else {
            console.log(`failed to connect with credentials : email: ${email}, password: ${password} `)
        }
    }


})(jQuery);