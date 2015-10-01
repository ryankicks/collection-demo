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
		
		$("#save").on("click", Page.save);
		
		// call from edit page
		$("#process").on("click", function(){
			
			var valid = Page.save();
			if (valid){
				var id = $(this).data("id"); 
				Page.process(id);
			}

			return false;
		});

		// call from list page
		$(".process").on("click", function(){
			
			var id = $(this).data("id"); 
			Page.process(id);

			return false;
		});

	},
	
	process : function(id){

		var url = "/collection/" + id + "/process";
		 $.ajax({
				type : "GET",
				url : url,
				dataType : "json",
				success : function(response) {
					console.log(response);
					
					var result = response.result;
					var added = result.added;
					
					alert("Added " + added.length + " tweets to collection.");
					
				},
				error : Page.handle_error 
			});	
		
		
	},
	
	save : function(){
		
		$("#list_slug").trigger("change");
		$("#collection_id").trigger("change");
		
		var valid = true;
		
		var list = $("#list_slug option:selected");
		var collection = $("#collection_id option:selected");
		
		var valid = list.val() && collection.val();
		
		if (!valid){
			console.log("valid: " + valid);
			alert("Name, list and collection are required.")
			return false;
		} else {
			return true;
		}
		
	},
	
	 handle_error :	function(request, status, error) {
		 var text = (request.responseText + " (" + request.status + ": " + error + ")");
		 alert(text);
	 }


}