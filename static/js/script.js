var Page = {

	user : null,
		
	init : function(user, list_slug, collection_id){
		
		Page.user = user;
		
		$('.help').popover();
		
		if (!list_slug){
			$("#link_list").hide();
		}
		
		if (!collection_id){
			$("#link_collection").hide();
		} else {
			Page.show_collection(collection_id);
		}
		
		$('.datetimepicker').datetimepicker({
	    	format: 'YYYY-MM-DD HH:mm',
	    	pickTime: true
		});
		
		$("#source_type").on("change", function(){

			var source_option = $("#source_type option:selected")
			var source_type = source_option.val();
			var source_name = source_option.html();
			
			console.log(source_type);
			console.log(source_name);
			
			if (source_type == 'search') {
				$("#search_holder").fadeIn();
				$("#link_list").hide();
			} else if (source_type == 'tweets_mine'){
				$("#search_holder").hide();
				$("#link_list").hide();
			} else if (source_type == 'new'){
				$("#search_holder").hide();
				$("#link_list").fadeIn();
				window.open("https://twitter.com/"+Page.user+"/lists", "_target");
			} else if (source_type){
				$("#search_holder").hide();
				$("#list_slug").val(source_type);
				$("#link_list").fadeIn();
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
				
				Page.show_collection(collection_id);
				
			} else {
				$("#link_collection").hide();
				$("#collection_preview").html("");
				if (collection_id == 'new'){
					window.open("https://tweetdeck.twitter.com/", "_target");
				}
				
				Page.show_collection();
				
			}

			console.log('When dynamic widgets are available, this will change the widget to preview the collection');
		});

		$("#link_list").on("click", function(){
			
			var list_slug = $("#list_slug").val();
			console.log(list_slug);
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
		
		$("#source_type").change();
		$("#collection_id").change();

	},
	
	save : function(){
		
		var name = $("#name").val();
		if (!name){
			alert("Name is required.")
			return false;
		}

		var collection = $("#collection_id option:selected").val();
		if (!collection || collection == 'new'){
			alert("Collection is required. If you recently created one, refresh this page and select it.")
			return false;
		}

		var errorMsg = "";
		var source_type = $("#source_type option:selected").val();

		if (source_type == 'search') {
			if ($("#search_term").val()){
				return true;
			} else {
				errorMsg = "Search term is required.";
			}

		} else if (source_type == 'tweets_mine'){
			return true;
		} else if (source_type == 'new'){
			errorMsg = "List is required. If you recently created one, refresh this page and select it.";
		} else if (source_type){
			if (!$("#list_name").val() && !$("#list_slug").val()){
				errorMsg = "List is required. If you recently created one, refresh this page and select it.";
			}
		}
		
		if (errorMsg){
			console.log("valid: " + errorMsg);
			alert(errorMsg)
			return false;
		} else {
			return true;
		}
		
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
					var ignored = result.ignored;
					var collection_id = result.collection_id;
					
					alert("Added " + added.length + " tweets to collection. (" + ignored.length + " ignored.)");
					
					Page.show_collection(collection_id);
					
				},
				error : Page.handle_error 
			});	
		
		
	},
	
	show_collection : function(collection_id){
		
		var output = "";
		if (collection_id){
			var template = $("#collectionTemplate").html();
			Mustache.parse(template);
			var params = {"collection_name": "", "collection_id": collection_id.substring(7)}
			output = Mustache.render(template, params);
		} else {
			output = $("#loadingTemplate").html();
		}
		console.log(output);
		$("#collection_preview").html(output);
		
		window.twttr.widgets.load();
		
	},
	
	 handle_error :	function(request, status, error) {
		 var text = (request.responseText + " (" + request.status + ": " + error + ")");
		 alert(text);
	 }


}