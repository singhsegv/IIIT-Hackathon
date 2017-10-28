function getCurrentTabUrl(callback) {
  // Query filter to be passed to chrome.tabs.query - see
  // https://developer.chrome.com/extensions/tabs#method-query
  var queryInfo = {
    active: true,
    currentWindow: true
  };

  chrome.tabs.query(queryInfo, (tabs) => {
  
    var tab = tabs[0];
    var url = tab.url;

    console.assert(typeof url == 'string', 'tab.url should be a string');
    callback(url);
  });
}

function hasGetUserMedia() {
  return !!(navigator.getUserMedia || navigator.webkitGetUserMedia ||
            navigator.mozGetUserMedia || navigator.msGetUserMedia);
}

document.addEventListener('DOMContentLoaded', function() {
    var btn = document.getElementById('record');
    
    btn.addEventListener('click', function() {
        if (hasGetUserMedia()) {
            var errorCallback = function(e) {
            console.log('Reeeejected!', e);
            };

            navigator.getUserMedia({audio: true}, function(localMediaStream) {
              
              // Ready to go. Do some stuff.
          }, errorCallback); 
        } else {
            alert('getUserMedia() is not supported in your browser');
       }
    });
});