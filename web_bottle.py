from __future__ import print_function
import os.path
import bottle
import time
from threading import Thread
from wsgiref.simple_server import make_server
from ws4py.websocket import WebSocket
from ws4py.server.wsgirefserver import WSGIServer, WebSocketWSGIRequestHandler
from ws4py.server.wsgiutils import WebSocketWSGIApplication
from neopixel import *
import RPi.GPIO as GPIO

DEBUG = 1

GPIO.setmode(GPIO.BOARD)
GPIO.setup(16, GPIO.IN)
GPIO.setup(3, GPIO.OUT)
GPIO.output(3, GPIO.LOW)
GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

#-------------------------------------------------------------------

# LED strip configuration:
LED_COUNT      = 16      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (must support PWM!).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 5       # DMA channel to use for generating signal (try 5)
LED_BRIGHTNESS = 205     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)

strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS)
strip.begin()

# Define functions which animate LEDs in various ways.
def colorWipe(strip, color, wait_ms=50):
	"""Wipe color across display a pixel at a time."""
	for i in range(strip.numPixels()):
		strip.setPixelColor(i, color)
		strip.show()
		time.sleep(wait_ms/1000.0)

def theaterChase(strip, color, wait_ms=50, iterations=10):
	"""Movie theater light style chaser animation."""
	for j in range(iterations):
		for q in range(3):
			for i in range(0, strip.numPixels(), 3):
				strip.setPixelColor(i+q, color)
			strip.show()
			time.sleep(wait_ms/1000.0)
			for i in range(0, strip.numPixels(), 3):
				strip.setPixelColor(i+q, 0)

def wheel(pos):
	"""Generate rainbow colors across 0-255 positions."""
	if pos < 85:
		return Color(pos * 3, 255 - pos * 3, 0)
	elif pos < 170:
		pos -= 85
		return Color(255 - pos * 3, 0, pos * 3)
	else:
		pos -= 170
		return Color(0, pos * 3, 255 - pos * 3)

def rainbow(strip, wait_ms=20, iterations=1):
	"""Draw rainbow that fades across all pixels at once."""
	for j in range(256*iterations):
		for i in range(strip.numPixels()):
			strip.setPixelColor(i, wheel((i+j) & 255))
		strip.show()
		time.sleep(wait_ms/1000.0)

def rainbowCycle(strip, wait_ms=20, iterations=5):
	"""Draw rainbow that uniformly distributes itself across all pixels."""
	for j in range(256*iterations):
		for i in range(strip.numPixels()):
			strip.setPixelColor(i, wheel((int(i * 256 / strip.numPixels()) + j) & 255))
		strip.show()
		time.sleep(wait_ms/1000.0)

def theaterChaseRainbow(strip, wait_ms=50):
	"""Rainbow movie theater light style chaser animation."""
	for j in range(256):
		for q in range(3):
			for i in range(0, strip.numPixels(), 3):
				strip.setPixelColor(i+q, wheel((i+j) % 255))
			strip.show()
			time.sleep(wait_ms/1000.0)
			for i in range(0, strip.numPixels(), 3):
				strip.setPixelColor(i+q, 0)


def printD(message):
	if DEBUG:
		print(message)

#-------------------------------------------------------------------

### Parse request from webif
#required format-> command:value
def WebRequestHandler(requestlist):
	returnlist = ""
	for request in requestlist:
		request =  request.strip()
		requestsplit = request.split(':')
		requestsplit.append("dummy")
		command = requestsplit[0]
		value = requestsplit[1]
		if value == "dummy":
			value = "0"
		if command == "haupt":
			if value =="an":
				colorWipe(strip, Color(255, 255, 255))
				GPIO.output(3, GPIO.HIGH)
				returnlist += "\n Beleuchtung:an"
			elif value == "aus":
				colorWipe(strip, Color(0, 0, 0))
				GPIO.output(3, GPIO.LOW)
				returnlist += "\n Beleuchtung:aus"
		elif command == "effekt":
			if value == "kino":
				theaterChase(strip, Color(127, 127, 127))
				returnlist += "\n Effekt:Theaterchase"
			elif value == "regenbogen":
				rainbow(strip)
				returnlist += "\n Effekt:Rainbow"
			elif value == "regenbogenroto":
				rainbowCycle(strip)
				returnlist += "\n Effekt:RainbowCycle"
			elif value == "kinoregenbogen":
				theaterChaseRainbow(strip)
				returnlist += "\n Effekt:TheaterchaseRainbow"
		elif command == "farbe":
			rwert = int(requestsplit[1])
			gwert = int(requestsplit[2])
			bwert = int(requestsplit[3])
			colorWipe(strip, Color(rwert, gwert, bwert))
			returnlist += "\n Farbe:"+str(rwert)+', '+str(gwert)+', '+str(bwert)
	return returnlist

class myWebSocketHandler(WebSocket):
	connections = []
	def opened(self):
		printD("New WebSocket client connected")
		self.send("You are connected")
		self.connections.append(self)
	def received_message(self, message):
		msg = message.data.decode()
		printD("Message from WebIf: >>>"+msg+"<<<")
		requestlist = msg.splitlines() 
		self.send(WebRequestHandler(requestlist))
	def closed(self, code, reason):
		printD("WebSocket closed %s %s" % (code, reason))
		self.connections.remove(self)
		
#-------------------------------------------------------------------

@bottle.route('/')
def MainHandler():
	values = {
				'debug': 1,
			}
	return bottle.template('index.html', values)

@bottle.route('/static/<filename>')
def StaticHandler(filename):
	if filename.endswith(".css"):
		bottle.response.content_type = 'text/css'
	elif filename.endswith(".js"):
		bottle.response.content_type = 'text/javascript'
	elif filename.endswith(".png"):
		bottle.response.content_type = 'image/png'
	elif filename.endswith(".jpg"):
		bottle.response.content_type = 'image/jpeg'		
	return bottle.static_file(filename, root=os.path.join(os.path.dirname(__file__), 'static'))


try:
	websocket_server = make_server(
		'', 7070,
		server_class=WSGIServer,
		handler_class=WebSocketWSGIRequestHandler,
		app=WebSocketWSGIApplication(handler_cls=myWebSocketHandler)
	)
	websocket_server.initialize_websockets_manager()
	# Start Child Thread for WebSocket
	print('Starting Child Thread for WebSocket_Server')
	ws = Thread(target=websocket_server.serve_forever)
	ws.setDaemon(True)
	ws.start()

	bottle.debug(True) #sollte spaeter ausgeschaltet werden!
	bottle.TEMPLATE_PATH.insert(0, os.path.join(os.path.dirname(__file__), 'templates'))
	bottle.run(host='0.0.0.0', port='8080', debug=True, quiet=False)
		
except KeyboardInterrupt:
	pass
finally:
	print('Shutting down Servers')
	ws.join(1)
	try:
		ws.shutdown()
	except:
		pass