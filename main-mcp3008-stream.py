from gpiozero import MCP3008,MotionSensor
from time import sleep
import threading
from flask import *

pir = MotionSensor(26)
pot = MCP3008(0) # Pot is connected to CH0
ldr = MCP3008(1) # LDR is connected to CH1

thresh = 0.5 # set threshold level to differentiate between light and dark

# Thread for handling MCP3008 data stream
class readMCP3008(threading.Thread):
 
    def __init__(self):
        super(readMCP3008, self).__init__()
        self.terminated = False
        self.start()
 
    def run(self):
        global read_pot
        global read_ldr
        print '\nMCP3008 started! Reading input channels....'
        while not self.terminated:
            # Build LED sequence
	    read_pot = pot.value
	    read_ldr = ldr.value
	    sleep(0.5)
	
            if self.terminated:
	        break
        print 'MCP3008 stopped'

# Thread for handling PIR data stream
class readPIR(threading.Thread):
 
    def __init__(self):
        super(readPIR, self).__init__()
        self.terminated = False
        self.start()
 
    def run(self):
        global pir_state
        print '\nPIR started!'
        while not self.terminated:
            pir_state = pir.motion_detected
            sleep(0.5)
            
            if self.terminated:
	        break
        print 'PIR stopped'

# Startup sequence
print 'Initialize MCP3008'
readMCP3008 = readMCP3008()
print 'Initialize PIR'
readPIR = readPIR()

app = Flask(__name__)

@app.route('/')
def index():
    global read_pot
    global read_ldr
    global pir_state
    return render_template('index-json.html', p = read_pot , l = read_ldr ,pir = pir_state)

# the following route will send JSON data streams to client browser
# variables are GLOBAL as we are grabbing those values from other external function/class in background thread
@app.route('/stream')
def stream():
    global read_pot
    global read_ldr
    global pir_state
    def read_sensor():
        while True:
            stream_state = {    'pot_json' : read_pot,
                                'ldr_json' : read_ldr,
                                'pir_json' : pir_state,
                           }

            yield 'data:{0}\n\n'.format(json.dumps(stream_state))
            sleep(0.5)

    return Response(read_sensor(), mimetype='text/event-stream')
    
if __name__ == "__main__":
    try:
	print 'Press CTRL+C to quit\n'
	print 'Starting Flask web server...'
	app.run(host='0.0.0.0',debug = True)
	
    except KeyboardInterrupt:
            print '\nShutting down...'
    readMCP3008.terminated = True
    readMCP3008.join()
    readPIR.terminated = True
    readPIR.join()

    print


