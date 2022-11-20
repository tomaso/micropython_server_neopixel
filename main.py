import machine, network, socket, utime, neopixel

print("Setting network to client mode")
sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)

print("Connecting to rentom_IoT")
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
print('the leds are 0-22')

np = neopixel.NeoPixel(machine.Pin(28), 23)

while True:
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
