jQuery(document).ready(function($) {
	//验证表单
	$('#regForm').validate({
		rules:{
			// username:{required:true,minlength:6},
			password:{required:true,minlength:6},
			repeat:{required:true,equalTo:'#sign-password'},
			email:{required:true,email:true},
			agree:{required:true}
		},
		messages:{
			// username:{required:'用户名必填！',minlength:'用户名不得少于6位！'},
			password:{required:'密码必填！',minlength:'密码最少6位'},
			repeat:{required:'重复密码必填',equalTo:'两次密码输入不一致'},
			email:{required:'邮箱必填！',email:"邮箱格式不正确"},
			agree:{required:'必须同意协议才可以注册！'}
		},
	});
});