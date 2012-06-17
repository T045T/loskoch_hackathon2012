var flickrApiKey = "c23b3fa60d0948eeb3c4c9fe43fb4dd7";
var viewModel = {
    searchTerm: ko.observable(""),
    searchTimeout: null,
    foundPhotos: ko.observableArray([]),
	tempPhoto: ko.observable(),
	selectedPhoto: ko.observable(),
    search: function(){
		viewModel.foundPhotos([]);
		
		if(this.searchTerm().length >= 3) {
			clearTimeout(viewModel.searchTimeout);
			
			this.searchTimeout = setTimeout(function(){
				var url = "http://api.flickr.com/services/rest/?method=flickr.photos.search&api_key=" + flickrApiKey + 						"&text=" + viewModel.searchTerm() + 					"&license=1%2C2%2C3%2C4%2C5%2C6&sort=interestingness_desc&per_page=100&format=json&jsoncallback=?";
				$.getJSON(url, function(data){
					if(data.stat == "ok") {
						ko.mapping.fromJS(data.photos.photo, photoMappingOptions, viewModel.foundPhotos);
					}
				});
				
			}, 1000);
		}
    }
};

var photoMappingOptions = {
    'create': function(o){
        var photo = ko.mapping.fromJS(o.data);
        photo.smallImageUrl = "http://farm"+ photo.farm() +".static.flickr.com/"+ photo.server() +"/"+ photo.id() +"_"+ photo.secret() +"_s.jpg";
        photo.mediumImageUrl = "http://farm"+ photo.farm() +".static.flickr.com/"+ photo.server() +"/"+ photo.id() +"_"+ photo.secret() +".jpg";
        photo.largeImageUrl = "http://farm"+ photo.farm() +".static.flickr.com/"+ photo.server() +"/"+ photo.id() +"_"+ photo.secret() +"_z.jpg";
		photo.select = function(){
			viewModel.selectedPhoto(this);
		}
        return photo;
    }
}



$(function(){
	ko.applyBindings(viewModel);
});

