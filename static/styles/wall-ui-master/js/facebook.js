
(function( $ ){
  $.fn.facebookPhotoId = function( options ) {  

		var settings = $.extend({
			'facebookAlbumId' : '126519139513',
			'photoLimit'       : '1000'
		}, options);
		
		function getArray(start, end) {
			var i, arr = [];
			for (i = start; i <= end-1; i++) {
				arr[i] = i;
			}
			return arr;
		}

		return this.each(function() {
			var albumId = settings.facebookAlbumId;
			var photoLimit = settings.photoLimit;
			var url = "https://graph.facebook.com/"+albumId+"/photos";
			var target = $(this);
			
			$.getJSON(url, function success(result) {
				var limit = photoLimit;
				
				if(result.data.length<limit) {
					limit = result.data.length;
				}
				
				var getArr = getArray(0, limit);
				
				for(i=0;i<getArr.length;i++) {
					var image = result.data[i];
					var item = "<li class='item'><img src='timthumb.php?src="+image.source+"&w=300&h=300' /></li>";
					
					//var li = "<li data-thumb='"+image.source+"'><a href='"+image.link+"' ><img src='"+image.source+"' /></a></li>";
					target.append(item);
				}
			});
		
		});
	};
	
})( jQuery );