var Page = {

	init : function(){
		
		$('.help').popover()
		
		$("#list_slug").on("change", function(){

			var list = $("#list_slug option:selected")
			var list_name = list.html();
			if (list.val()){
				$("#list_name").val(list_name);
			}

			console.log(list_name);
		});
		

		$("#collection_id").on("change", function(){
			
			var collection = $("#collection_id option:selected")
			var collection_name = collection.html();
			if (collection.val()){
				$("#collection_name").val(collection_name);
			}

			console.log(collection_name);
			console.log('When dynamic widgets are available, this will change the widget to preview the collection');
		});
		
		$("#save").on("click", function(){
			
			var valid = true;
			
			var list = $("#list_slug option:selected")
			var collection = $("#collection_id option:selected")
			
			var valid = list.val() && collection.val(); 
			console.log("valid: " + valid);
			
//			return false;
			return valid;
		});
		
	},

}