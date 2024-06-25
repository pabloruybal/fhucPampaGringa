
$(document).ready(function(){
   
   
		
    var Clock = function(elId) {
        var el = document.getElementById(elId);
     
        if(el) {
            $(el).append($("<ul>", {'class': 'clock-group'}));
            $(".clock-group", el).append($("<li>", {'class': 'sec'})).append($("<li>", {'class': 'hour'})).append($("<li>", {'class': 'min'}))
             setInterval( function() {
              var seconds = new Date().getSeconds();
              var sdegree = seconds * 6;
              var srotate = "rotate(" + sdegree + "deg)";
              
              $(".sec", el).css({"-moz-transform" : srotate, "-webkit-transform" : srotate});
              
            }, 1000 );
          
        
            setInterval( function() {
                var hours = new Date().getHours();
                var mins = new Date().getMinutes();
                var hdegree = hours * 30 + (mins / 2);
                var hrotate = "rotate(" + hdegree + "deg)";
                
                $(".hour", el).css({"-moz-transform" : hrotate, "-webkit-transform" : hrotate});
              
            }, 1000 );
            
            
            setInterval( function() {
                var mins = new Date().getMinutes();
                var mdegree = mins * 6;
                var mrotate = "rotate(" + mdegree + "deg)";
                
                $(".min", el).css({"-moz-transform" : mrotate, "-webkit-transform" : mrotate});
              
            }, 1000 );
        }       
       
    }
    
    var tileClock = new Clock("clock"); 
	
    var weather = new Weather("weather");
  /*
    var twitter = new SingleTwitter("twitter", {updateInterval: 1000*10, priorityInterval: 1000*30, cycleDepth: 5, searchString: "@manifestdigital OR from:manifestdigital"});
    var wallMessage = new SingleTwitter("wall-message", {updateInterval: 1000*5,
                                                         priorityInterval: 1000*20,
                                                         cycleDepth: 5,
                                                         searchString: "@md_wall OR to:md_wall OR from:md_wall OR #MDWall",
                                                         filters:[{search:/(^@MD_Wall)/g, replace:""},
                                                                  {search:/(^@md_wall)/g, replace:""},
                                                                  {search:/(^@MD_WALL)/g, replace:""},
                                                                  {search:/(^@md_Wall)/g, replace:""}
                                                                  ]
                                                         });
                                                         // (^@([A-Za-z0-9_]+))
    */
    //var instagram = new Instagram("instagram", {searchString:"#campvibes"});
    
    $("#instagram").instagram({
        clientId: '494a2117c72a4541a85ab40d77ff3fc7',
        show: '6',
        updateInterval: 1000*60*2,
        search: {lat:'41.886688', lng:'-87.627811', dist: '500'},
        image_size: 'low_resolution'
    })
	
	
	
		$(".fb").facebookPhotoId({ 'facebookAlbumId' : '10151159153399514' });
		
		$(".fb").carousel({
				'carouselItem'  : '.item', 
				'duration' : 500
		});
	
   
   
})
