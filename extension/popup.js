// Copyright (c) 2012 The Chromium Authors. All rights reserved.
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

'use strict';

function click(e) {
  chrome.tabs.executeScript(null,
      {code:"document.body.style.backgroundColor='" + e.target.id + "'"});

  window.close();

}

chrome.tabs.query({'active': true, 'windowId': chrome.windows.WINDOW_ID_CURRENT},
   function(tabs){
      var url = (tabs[0].url);
      var bias_desc = "Unknown";

      function reqListener() {

        var data = JSON.parse(this.responseText);
        bias_desc = data["bias"];
        var articles = data["similar_articles"]["articles"];
        for(var i = 0; i < Math.min(3, articles.length); i++){

          var j = i + 1;
          var new_url = articles[i]["url"];
          var title = articles[i]["title"];
          var img_url = articles[i]["urlToImage"];
          document.getElementById("title"+j).innerHTML = "<a href=\""+new_url+"\" target=\"_blank\"> " + title +" </a>";
          document.getElementById("img"+j).setAttribute("src", img_url);

        }
        document.getElementById("bias").innerHTML = bias_desc;

      }

      function reqError(err) {
        console.log('Fetch Error :-S', err);
      }

      var oReq = new XMLHttpRequest();
      oReq.onload = reqListener;
      oReq.onerror = reqError;
      oReq.open('get', 'http://127.0.0.1:5000/api/bias?url='   + url, true);
      oReq.send();
      //alert("http://127.0.0.1:5000/api/bias?url=" + url);


   }
);

document.addEventListener('DOMContentLoaded', function () {

});
