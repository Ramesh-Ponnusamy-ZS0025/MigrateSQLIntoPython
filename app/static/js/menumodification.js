$(document).ready(function() {
document.title = "Transformer";
var link = document.querySelector("link[rel*='icon']") || document.createElement('link');
    link.type = 'image/x-icon';
    link.rel = 'shortcut icon';
    var clink= window.location.origin;
    //clink = clink.substring(0,clink.indexOf('/'));
    var faveicon = clink+"/static/images/appicon.png";
    var menuicon  =  clink+"/static/images/appicon.png";
    link.href = faveicon;
    document.getElementsByTagName('head')[0].appendChild(link);

//headtag.innerHTML('<link rel="shortcut icon" href="https://cdn.sstatic.net/Sites/stackoverflow/img/favicon.ico?v=4f32ecc8f43d">');
var versand = document.getElementsByClassName('navbar-brand')[0];
versand.getElementsByTagName('a')[0].textContent = ''
versand.getElementsByTagName('a')[0].innerHTML="<img id = 'menuimg' src=\" "+menuicon+ "\" style=\" width: 40px; height: 40px; margin-top: -11px; \">";

});


