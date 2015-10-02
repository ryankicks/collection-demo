var Page = {

	user : null,
		
	init : function(user){
		
		Page.user = user;
		
		$('.help').popover();
		$("#link_list").hide();
		$("#link_collection").hide();
		
		$("#list_slug").on("change", function(){

			var list = $("#list_slug option:selected")
			var list_slug = list.val();
			var list_name = list.html();
			
			if (list.val()){
				$("#list_name").val(list_name);
			}
			if (list_slug && list_slug != 'new'){
				$("#list_name").val(list_name);
				$("#link_list").fadeIn();
			} else {
				$("#link_list").hide();
				if (list_slug == 'new'){
					window.open("https://twitter.com/"+Page.user+"/lists", "_target");
				} 				
			}

			console.log(list_name);
		});
		

		$("#collection_id").on("change", function(){
			
			var collection = $("#collection_id option:selected")
			var collection_id = collection.val();
			var collection_name = collection.html();
			
			if (collection_id && collection_id != 'new'){
				$("#collection_name").val(collection_name);
				$("#link_collection").fadeIn();
			} else {
				$("#link_collection").hide();
				if (collection_id == 'new'){
					window.open("https://tweetdeck.twitter.com/", "_target");
				} 				
			}

			console.log(collection_name);
			console.log('When dynamic widgets are available, this will change the widget to preview the collection');
		});

		$("#link_list").on("click", function(){
			
			var list = $("#list_slug option:selected")
			var list_slug = list.val();
			if (list_slug && list_slug != 'new'){
				var url = "https://twitter.com/"+Page.user+"/lists/" + list_slug;
				window.open(url);
			}

		});
		
		$("#link_collection").on("click", function(){
			
			var collection = $("#collection_id option:selected")
			var collection_id = collection.val();
			if (collection_id && collection_id != 'new'){
				var url = "https://twitter.com/"+Page.user+"/timelines/" + collection_id.substring(7)
				window.open(url);
			}

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