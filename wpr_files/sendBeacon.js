var endpoint = 'https://';
if (location.protocol != 'https:')
    {
     endpoint = 'http://';
    }
endpoint = endpoint + 'www.bperf.xyz/app/public/beacon/catcher.php';
var user_agent = navigator.userAgent;
console.log('Fragment_before: ' + fragment)
var fragment = window.location.hash;
if (fragment === undefined || fragment.length < 5){
    var urlString=window.location.href;
    var fragment = '#' + urlString.split("/#")[1];
  }
BOOMR.init({
  //beacon_url: "https://www.bperf.xyz/index.php"
  beacon_url: endpoint
});
BOOMR.addVar("jn_agent", user_agent);
BOOMR.addVar("jn_browser", fragment);
console.log('Fragment_after: ' + fragment);
