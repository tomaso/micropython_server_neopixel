import machine, network, socket, utime, neopixel
import json, sys, urandom

# Load config and set global variables
config = json.load(open('config.json'))
SSID = config['ssid']
WIFI_PASSWORD = config['pass']
LED_COUNT = config['led_count']
DATA_PIN = config['data_pin']

# Sanity checks
if LED_COUNT<2:
    print("led_count must be more than 1")
    sys.exit()

print("Setting network to client mode")
sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)

print(f"Connecting to {SSID}")
sta_if.connect(SSID, WIFI_PASSWORD)
while not sta_if.isconnected():
    print("We are not connected yet")
    utime.sleep(1)
print(sta_if.ifconfig())

addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]

s = socket.socket()
s.bind(addr)
s.listen(1)

print('listening on', addr)
print('GET /<r>/<g>/<b>/1/2/... => switch leds with addresses 1,2,... to RGB values')
print(f'there are {LED_COUNT} leds')

np = neopixel.NeoPixel(machine.Pin(DATA_PIN), LED_COUNT)

for v in range(0,255,25):
    for i in range(LED_COUNT):
        np[i] = (v,v,v)
    np.write()
    utime.sleep(0.1)

print("Intro is over")

while True:
    try:
        cl, addr = s.accept()
        print('client connected from', addr)
        cl_file = cl.makefile('rwb', 0)
        leds = []
        r = g = b = 0
        while True:
            line = cl_file.readline()
            if not line or line == b'\r\n':
                break
            else:
                if line.split()[0]==b'GET':
                    _,r,g,b,res = line.split()[1].split(b'/', 4)
                    r = int(r)
                    g = int(g)
                    b = int(b)
                    print(r,g,b)
                    print(res)
                    for i in res.split(b'/'):
                        np[int(i)] = (r,g,b)
                    np.write()
        cl.send('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
        cl.send('\n')
        cl.close()
    except Exception as exc:
        print(f"Exception caught: {exc}")
