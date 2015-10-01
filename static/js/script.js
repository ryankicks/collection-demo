var Page = {

	init : function(){
		
		$('.help').popover()
		
		$("#save").on("click", function(){
			
			var list_name = $("#list_slug option:selected").html() 
			$("#list_name").val(list_name);
			
			var collection_name = $("#collection_id option:selected").html()
			$("#collection_name").val(collection_name);
			
			console.log(list_name + " " + collection_name);
			
//			return false;
			return true;
		});
		
	},

}