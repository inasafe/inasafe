// VARIABLES
// =========

var rootDir;
var contentHack = {
	selectorName: 'content',
	hackMode: 'content-in'
};
var self = this; // Used to set context in $.ajax
var rootDir = "/"; // Don't change this unless you've tried in settings.less already.
var extrasPath;
var appList = [];
var appArray = [];
var universals = {
	isSet: false,
	path: undefined
};
var readyFired = false; // Prevents multiple ajax calls from calling the kickstrap.ready() fxs
var appCheck = false; // Prevents a false positive for kickstrap.ready()
var thisVersion = "1.0.0 Beta"; // Don't change this! Used to check for updates with updater app

// FUNCTIONS
// ---------

if (!window.console) console = {log: function() {}};

// Allow overrides of directories.
function setDir(newDir, dirType) {dirType == 'root' ? rootDir = newDir : universals.path = newDir;}

// For reading commented-out items
String.prototype.isIgnored = function () {return (this.substr(0, 2) == "//" || this == "");}

// For reading public items
String.prototype.isPublic = function () {return (this.substr(0, 5) == "http:" || this.substr(0, 6) == "https:");}

// Differentiate JS from CSS dependencies.
String.prototype.isJS = function () {return (this.substr(this.length-3, this.length) == ".js");}

// Clears localStorage only.
function clearCache(testVal) {
	// Let's see if the browser has localStorage so this doesn't blow up.
	var hasStorage = ("w" == (localStorage.setItem = "w"));

	if(hasStorage) {
		localStorage.clear();
		consoleLog('Cache has been cleared. Reloading...');
		location.reload(true);
	} // This is the part that actually clears the cache.
	else {
		consoleLog('This browser does not support localStorage.','error');
	}
}

function consoleLog(msg, msgType, objName) { 
  // The user can turn this off.
	if(typeof window.consoleLogger == 'function') {
		try {consoleLogger(msg, msgType, objName);}
		catch(err) {
		  // If for some reason it breaks, 
		  // we should at least show the msg the normal way.
			console.error('Kickstrap error. Could not call consoleLog() ' + err);
			console.log(msg);
		}
  }
}

// There are a couple ways we might do this.
function formatString(str, extensive) {
  str = String(str);

  if (extensive) {
	  str = String(str);
		str=str.replace(/\\'/g,'\'');
		str=str.replace(/\\"/g,'"');
		str=str.replace(/\\0/g,'\0');
		str=str.replace(/\\\\/g,'\\');
		str=str.substring(1,str.length-1);
  }
  else {
		str = str.replace(/['"]/g,'');
	}
  str = str.replace(/br-/ig,';'); // Semicolons in the content attr act like the content's semicolon.
	return str;
}

// Thanks http://ejohn.org/blog/javascript-array-remove/
Array.prototype.remove = function(from, to) {
  var rest = this.slice((to || from) + 1 || this.length);
  this.length = from < 0 ? this.length + from : from;
  return this.push.apply(this, rest);
} 

//Modified version of CSV splitter thanks to 
//http://www.greywyvern.com/?post=258
String.prototype.splitCSV = function(sep) {
  for (var foo = this.split(sep = sep || ","), x = foo.length - 1, tl; x >= 0; x--) {
  	foo[x] = foo[x].replace(/ /g,''); // Modified to remove spaces from string too.
	    if (foo[x].replace(/"\s+$/, '"').charAt(foo[x].length - 1) == '"') {
	      if ((tl = foo[x].replace(/^\s+"/, '"')).length > 1 && tl.charAt(0) == '"') {
	        foo[x] = foo[x].replace(/^\s*"|"\s*$/g, '').replace(/""/g, '"');
	      } else if (x) {
	        foo.splice(x - 1, 2, [foo[x - 1], foo[x]].join(sep));
	      } else foo = foo.shift().split(sep).concat(foo);
	    } else foo[x].replace(/""/g, '"');
  } return foo;
};

// Support for .every in IE
if (!('every' in Array.prototype)) {
  Array.prototype.every= function(tester, that /*opt*/) {
    for (var i= 0, n= this.length; i<n; i++)
      if (i in this && !tester.call(that, this[i], i, this))
        return false;
    return true;
  };
}

// Manual app execution 
function loadApp(appName) {
	appArray = [];
	appList = [appName];
	window[appName] = new app(appName);
}

var kickstrap = {
	hello: 'Kickstrap: Hi! (' + thisVersion + ')',
	edit: function() {
		document.body.contentEditable='true'; document.designMode='on'; void 0;
		if(typeof window.$.pnotify == 'function') {
			$.pnotify({
				title: 'Prototyping Mode',
				text: 'You can now edit anything in this page. (But it won\'t be saved!)',
				type: 'success',
				styling: 'bootstrap'
			});
		}
	},
	readyFxs: [],
	ready: function(customFn) {this.readyFxs.push(customFn)},
	testParams: {
		readyCount: 0
	}
}

function themeFunction(urlPath) {$.ajax({type: "GET", url: rootDir + 'Kickstrap/themes/' + urlPath + '/functions.js', dataType: "script", context: self});}

// BEGIN
// =====

// Look for script#app and get app list
setupKickstrap();

function setupKickstrap() {
  // Those with IE shall be marked.
	var ver = getInternetExplorerVersion();
	if (ver > -1)
	{
	  if ( ver < 9.0) {
	    contentHack.selectorName = 'ie8';
		  contentHack.hackMode = 'ie8';
	  }
	  else if (ver >= 9.0) {
	    //alert('IE9 detected');
	  }
	  else {
	    contentHack.selectorName = 'content';
	  }
	}	
	function getInternetExplorerVersion() {
	  var rv = -1; // Return value assumes failure.
	  if (navigator.appName == 'Microsoft Internet Explorer')
	  {
	    var ua = navigator.userAgent;
	    var re  = new RegExp("MSIE ([0-9]{1,}[\.0-9]{0,})");
	    if (re.exec(ua) != null)
	      rv = parseFloat( RegExp.$1 );
	  }
	  return rv;
	}
	if($('#appList').css('content') == 'normal' ||
	  $('#appList').css('content') == undefined) {
		contentHack.selectorName == 'ie8';
		if ($('#appList').css('ie8') == undefined ||
		$('#appList').css('ie8') == '') {
		  var writeScripts = '';
		  contentHack.hackMode = 'loop'; // last resort
			for(i = 0; i < document.styleSheets.length; i++) {
			  for (j = 0; j < document.styleSheets[i].rules.length; j++) {
				var selector = document.styleSheets[i].rules[j].selectorText;
				if (selector == "#appList") {
				  appList = formatString(document.styleSheets[i].rules[j].style.content, true).splitCSV();
				}
				else if (selector == "script#rootDir" || selector == "script#console" || selector == "script#caching") {
				  writeScripts += formatString(document.styleSheets[i].rules[j].style.content, true);
				  //if(selector == "script#caching") initKickstrap();
				}
			  }
			}
			document.write(writeScripts);
		}
	};
	
	//if (contentHack.hackMode != 'loop') {
		// Create our "boring stuff" appendMagics
		
		document.write('<script id="rootDir" type="text/javascript">appendMagic(\'#rootDir\');</script><script id="themeFunctions">appendMagic(\'#themeFunctions\');</script><script id="console" type="text/javascript">appendMagic(\'#console\');</script><script id="caching" type="text/javascript">appendMagic(\'#caching\');initKickstrap();</script>');

	//}
	
}

// The appendMagics we just created will need this.
function appendMagic(newAppendee) {
  if (contentHack.hackMode != 'loop') {
		var scriptString = formatString($(newAppendee).css(contentHack.selectorName), true);
		if (scriptString == 'ndefine') {scriptString = '<script></script>'}; 
		// (above) Prevents "[u]ndefine[d]" from being printed when the appended script is removed.
		document.write(scriptString);
	}
}

// The last appendMagic will call this function and get things started.
function initKickstrap() {
	// Allow the user to skip universals loading
  if (!universals.isSet && universals.path == "none") universals.isSet = true;
  if (universals.isSet) {
    if (contentHack.hackMode != 'loop') { // In which case we already have the app list.
	    appList = (formatString($('#appList').css(contentHack.selectorName))).splitCSV(); // Get list
	  }
	  // TODO: If there are no apps, fire kickstrap.ready()
		for(i = 0;i<appList.length;i++) 
		{
		  theapp = appList[i];
			if (theapp.isIgnored()) {
			  // Remove commented items from list.
			  if (theapp != "") {
			  	//consoleLog('Deactivated ' + theapp.substr(2,theapp.length), 'warn');
			  }
				appList.remove(i);
				i--;
			}
			else {
			  // Make each app an app object
			  //consoleLog('Activating ' + theapp + '...');
				window[appList[i]] = new app(theapp);
			}
		}
	}
	else {universal = new app("universal");}
}

function cssIfy(filePath) { // Global so ks-window pages can use this.
	var linkElement = document.createElement("link");
  linkElement.setAttribute("rel", "stylesheet");
  linkElement.setAttribute("type", "text/css");
  linkElement.setAttribute("href", filePath);
  document.getElementsByTagName('body')[0].appendChild(linkElement);
}

/*
You ask me why I dwell in green mountains
I smile and make no reply 
for my heart is free of care.

As the peach blossom flows downstream
and is gone into the unknown

I have a world apart that is not among men.
*/

function app(x) {

  // Set up the app object's parts
  this.resourcesRequired = [];
  this.resourcesDependent = [];
  this.countRequired=[999,0]; // Starting w/ 999 insures a false "complete" positive does not occur (0 == 0)
  this.countDependent=[999,0];
  this.name = x;
  this.loaded = false;
  extrasPath = rootDir + "Kickstrap/apps/";
  this.configPath = extrasPath + x + '/config.ks';
  // Override if user wants CDN-hosted config.ks files.
  if (x.substring(0, 5) == "http:" || x.substring(0,6) == "https:") {
    this.configPath = x;
  }
  if(!universals.isSet && universals.path != "local" && universals.path != undefined) {this.configPath = universals.path + '/universal/config.ks'}
  // Now open config and fill out the app object structure.
	$.ajax({type: "GET", url: this.configPath, dataType: "html", context: self,
		success: function(data) {
		  // config file successfully found, now we'll parse.
			this.resources = data.split(/\r\n|\n/);
			parseConfig(this.resources); // Must be an external function to use variables.
		},
	  error:function (xhr, ajaxOptions, thrownError){
	    // Common error, the user just spelled the name wrong.
	    consoleLog('"' + x + '"? Are you sure you spelled that correctly? [' + xhr.status + ' (' + thrownError + ')]', 'error');
	  }  
	});
	function parseConfig(resources) {
	  // Get the required dependencies and create array.
		var resourcesRequired = resources[0].splitCSV();
		for (i=0;i<resourcesRequired.length;i++) {
		  if(resourcesRequired[i].isIgnored()) { //Splice commented items from array.
		    resourcesRequired.splice(resourcesRequired.indexOf(resourcesRequired[i]), 1);
			}
		}	// Commented items removed, finalize the required items in the app object.
		window[x].resourcesRequired = resourcesRequired;
		// Now look for dependent items.
		if (resources[1]) {
			var resourcesDependent = resources[1].splitCSV();
			for (i=0;i<resourcesDependent.length;i++) {
			  if(resourcesDependent[i].isIgnored()) { //Splice commented items from array.
			    resourcesDependent.splice(resourcesDependent.indexOf(resourcesDependent[i]), 1);
				}
			}
			window[x].resourcesDependent = resourcesDependent;
		}
		appArray.push(window[x]);
		if(!universals.isSet) {loadResources()}
    // Test to see if the resources we loaded are equal to the resources we've found.
		if(appArray.length == appList.length) {loadResources();}
	}
	
  function finishUniversals() {
	  universals.isSet = true;
    appArray = [];
    initKickstrap();
    universal.loaded = true;
  }
  
	function loadResources() {
		if (universals.isSet && appList.length > 0) {appCheck = true;}
		for (i = 0;i<appArray.length || function() {if(!universals.isSet && appArray[0].countRequired[1] == 0){finishUniversals();}}();i++) {
			appArray[i].countRequired[0] = 0;
			if(contentHack.hackMode != 'ie8') {
				consoleLog('Kickstrap: ' +  appArray[i].name, null, appArray[i])}; // Tell the user what we're loading.
		  for (j = 0;j<appArray[i].resourcesRequired.length;j++) {
		  
		    var requiredResource = appArray[i].resourcesRequired[j];
		    var filePath = extrasPath + appArray[i].name + '/' + requiredResource;
		    // Override filePath if public.
		    if(requiredResource.isPublic()) {filePath = requiredResource;}
		    if(!requiredResource.isIgnored()) {
			    if(requiredResource.isJS()) {
			      // Load JS
						$.ajax({type: "GET", url: (filePath), dataType: "script", context: this, 
						  beforeSend: function(jqXHR, settings) {
						    jqXHR.thisIs = appArray[i];
						    jqXHR.thisIs.countRequired[1]++;
						  },
						  success: function(data, textStatus, jqXHR) {
						    var currentObj = jqXHR.thisIs;
						    currentObj.countRequired[0]++; // Like teenagers, XMLHttpRequests have a way of not calling if they come home late.

						    if(currentObj.countRequired[0] == currentObj.countRequired[1]) {
						      if(!universals.isSet) {
							      universals.isSet = true;
							      appArray = [];
							      initKickstrap();
							      universal.loaded = true;
							      universal.countDependent = [0, 0];
						      }
						      currentObj.countDependent[0] = 0;
						      kickstrapReady(currentObj.name);
							    for (k = 0;k<currentObj.resourcesDependent.length;k++) {
							      var filePath = extrasPath + currentObj.name + '/' + currentObj.resourcesDependent[k];
							      if (currentObj.resourcesDependent[k].isPublic()) {filePath = currentObj.resourcesDependent[k];}
							      if(filePath.isJS()) {
								      $.ajax({type: "GET", url: (filePath), dataType: "script", context: this,
										  beforeSend: function(jqXHR, settings) {
										    jqXHR.thisIs = currentObj;
										    jqXHR.thisIs.countDependent[1]++;
										  },
										  success: function(data, textStatus, jqXHR) {
										    var currentObj = jqXHR.thisIs;
										    currentObj.countDependent[0]++;
										    kickstrapReady(currentObj.name);
										  }
										  });
							      }
							      else {
							       currentObj.countDependent[0]++;
							       currentObj.countDependent[1]++;
							       cssIfy(filePath);
							      };
							    }
						    }
						  }
						});
					}
					else {
					  // Make CSS Link
					  appArray[i].countRequired[0]++;
					  appArray[i].countRequired[1]++;
					  cssIfy(filePath);
					}
				}
			}
		}
	}
}

function kickstrapReady(myNameIs) {

	// Fire fire() only if all the resource counts match
	if (appCheck) {
		this.loadedLoop = []; // Store loaded = false/true vals in array to validate.
		for(i = 0;i<appArray.length || function(){if(this.loadedLoop.every(Boolean))fire()}();i++) {
			var appR = appArray[i].countRequired;
			var appD = appArray[i].countDependent;
			
			if (appR[0] == appR[1] && appD[0] == appD[1]) { 
				appArray[i].loaded = true;
			}
			else {appArray[i].loaded = false;}
			this.loadedLoop.push(appArray[i].loaded);
			//console.log(this.loadedLoop + ' ' + myNameIs + ' ' + appR + ' ' + appD); // For debugging
		}
	}

	function fire() {
		if (!readyFired) {
			readyFired = true;
	  	kickstrap.testParams.readyCount++;
	  	consoleLog('Executing kickstrap.ready() functions');
			for (i = 0;i<kickstrap.readyFxs.length;i++) { // This allows the user to use this function all over the place.
				(kickstrap.readyFxs[i])(); // Go to the next function in array and fire.
			}
		}
	}
}

/*
When people see some things as beautiful,
other things become ugly.
When people see some things as good,
other things become bad.

Being and non-being create each other.
Difficult and easy support each other.
Long and short define each other.
High and low depend on each other.
Before and after follow each other.

Therefore the Master
acts without doing anything
and teaches without saying anything.
Things arise and she lets them come;
things disappear and she lets them go.
She has but doesn't possess,
acts but doesn't expect.
When her work is done, she forgets it.
That is why it lasts forever.
*/
