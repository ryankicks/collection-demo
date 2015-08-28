var Page = {

	init : function(){
		
		$("#refresh").on("click", function(){
			Page.toggleRefresh($(this).val());
		});
		
	},
		
	setRefresh : function(interval){
		setTimeout(function () {
			window.location.reload();
		}, interval);
	},
	
	toggleRefresh : function(interval){
		var url = $("#share_url").val();
		var refresh = "&refresh=" + interval; 
		if (url.indexOf(refresh) > 0){
			url = url.replace(refresh, "");
		} else {
			url = url + refresh;
		}
		$("#share_url").val(url);
	}

}