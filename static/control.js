if (typeof(String.prototype.strip) === "undefined") {
    String.prototype.strip = function() {
        return String(this).replace(/^\s+|\s+$/g, '');
    };
}

function isset(strVariableName) { 
    try { 
        eval( strVariableName );
    } catch( err ) { 
        if ( err instanceof ReferenceError ) 
            return false;
    }
    return true;
}

function sleep(millis, callback) {
    setTimeout(function() { callback(); } , millis);
}

//source of: http://www.html5tutorial.info/html5-range.php
function printValue(sliderID, textbox) {
    var x = document.getElementById(textbox);
    var y = document.getElementById(sliderID);
    x.value = y.value;
}


function mylog(message) {
    if (isset(DEBUG) && DEBUG == 0) {
        console.log(message);
        if (document.getElementById("Log") !== null) {
            var logthingy;
            logthingy = document.getElementById("Log");
            if( logthingy.innerHTML.length > 5000 )
                logthingy.innerHTML = logthingy.innerHTML.slice(logthingy.innerHTML.length-5000);
            logthingy.innerHTML = logthingy.innerHTML+"<br/>"+message;
            logthingy.scrollTop = logthingy.scrollHeight*2;
        }
    }
}

//----------------------------------------------------------------


function parseResponse(requestlist) {
    //mylog("Parsing: "+requestlist)
    for (var i=0; i<requestlist.length; i++) {
        var requestsplit = requestlist[i].strip().split(':')
        requestsplit[requestsplit.length] = "dummy";
        command = requestsplit[0];
        val = requestsplit[1];
        val2 = requestsplit[2];

        if (command == "Beleuchtung") {
			if (val == "an") {
				document.getElementById("lstat").innerHTML = "Aktueller Status: Beleuchtung ein";
				document.getElementById("lstat").style.color = "#000";
				document.getElementById("lstat").style.backgroundColor = "#efefef";
				}
			else if (val == "aus") {
				document.getElementById("lstat").innerHTML = "Aktueller Status: Beleuchtung aus";
				document.getElementById("lstat").style.color = "#fff";
				document.getElementById("lstat").style.backgroundColor = "#000";
				}
			}
		else if (command == "Effekt") {
			if (val == "Rainbow") {
				document.getElementById("lstat").innerHTML = "Aktueller Status: Regenbogeneffekt";
				document.getElementById("lstat").style.color = "#000";
				document.getElementById("lstat").style.backgroundColor = "#efefef";
				}
			else if (val == "Theaterchase") {
				document.getElementById("lstat").innerHTML = "Aktueller Status: Theaterchaseeffekt";
				document.getElementById("lstat").style.color = "#000";
				document.getElementById("lstat").style.backgroundColor = "#efefef";
				}
			else if (val == "RainbowCycle") {
				document.getElementById("lstat").innerHTML = "Aktueller Status: Regenbogenzyklus";
				document.getElementById("lstat").style.color = "#000";
				document.getElementById("lstat").style.backgroundColor = "#efefef";
				}
			else if (val == "TheaterchaseRainbow") {
				document.getElementById("lstat").innerHTML = "Aktueller Status: Kinoregenbogeneffekt";
				document.getElementById("lstat").style.color = "#000";
				document.getElementById("lstat").style.backgroundColor = "#efefef";
				}
			}
		else if (command =="Farbe") {
			document.getElementById("lstat").innerHTML = "Aktueller Status: Beleuchtung " + val;
			document.getElementById("lstat").style.color = "#000";
			document.getElementById("lstat").style.backgroundColor = "#efefef";
			}
		}
}