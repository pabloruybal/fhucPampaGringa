var Instagram = function(elId, options) {
    
    var defaults = {
        baseUrl: "http://search.twitter.com/search.json?q=",
        searchString: "404",
        displayCount: 5,
        updateInterval: 10000,
        filters:[]
    };
	var options = $.extend(defaults, options);		

    var el = document.getElementById(elId);
    var searchURL = options.searchUrl;
    var tweetIndex = 0;
    var latestSearch;
    var intervalTimer
    
    if(!el) console.error("No Element");
    
    var init = function(){
        getData();
    }(); 
    
   function getData(){
        $.ajax({
        	type:"GET",
        	//url:options.baseUrl+encodeURIComponent(options.searchString),
        	url: "https://api.instagram.com/v1/tags/coffee/media/recent?access_token=fb2e77d.47a0479900504cb3ab4a1f626d174d2d",
        	dataType: "jsonp",
        	success: function(_data) {
        	   
            	//updateData(_data);
            	console.log("Instagram:", _data);
            	//latestSearch = _data;
            	//intervalTimer = setInterval(findLatest, options.updateInterval);
            	//findLatest();
        	}
		});
    }
    
    function buildList(){
    }
    
    function findLatest() {
        $('.tweet-list', el).addClass('transition')
        setTimeout(function(){
            $('.tweet-list', el).removeClass('transition');
            $('.tweet-list', el).empty();
            
            if(latestSearch.results[tweetIndex]){
             //var randIndex = Math.floor(Math.random()*latestSearch.results.length);
             console.log("get Tweet:", tweetIndex);
             addTweet(tweetIndex, latestSearch.results);
            }
            
            tweetIndex += 1;
            if(tweetIndex >= latestSearch.results.length-1){
                tweetIndex = 0;
                clearInterval(intervalTimer);
                setTimeout(getData, options.updateInterval)
                console.log("reset Tweet");
                //getData();
            }
           
        }, 500);
    }
    
    function addTweet(index, list) {
        var tweet = $("<li>", {'class':'tweet'});
        $(tweet).append($("<img>", {'src':list[index].profile_image_url}))
                .append($("<div>", {'class':'text'}).html(list[index].text));
        $('.tweet-list', el).append(tweet);
        //$('.text', tweet).fitText();
        $('.text', tweet).fitToHeight();
    }
    
    
}