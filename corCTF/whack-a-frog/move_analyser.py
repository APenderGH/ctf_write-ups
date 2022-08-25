import pyshark

pcap = pyshark.FileCapture("C:\\Users\\ssamu\\Desktop\\WHACK-A-FROG\\moves.pcap")

class movement:
    def __init__(self, x, y, event):
        self.x = x;
        self.y = y;
        self.event = event;

movements = []
isDragging = False

for pkt in pcap:
    request = pkt[pkt.highest_layer].request_uri
    x = request[request.find('x') + 2 : request.find('&')]
    y = request[request.find('y') + 2 : request.find('&', request.find('&') + 1)]
    event = request[request.find('event') + len('event='):]
    
    movements.append(movement(x,y,event))

for move in movements:
    if (move.event == 'mousedown'):
        isDragging = True
    elif (move.event == 'mouseup'):
        isDragging = False
    
    if (isDragging):
        print(f"document.elementFromPoint({move.x}, {move.y}),")


#document.elementFromPoint(16, 13).childNodes[0] (selects a frog from point x and y)
#x.forEach((element) => { if (element.src) {element.src = null;} })

#this script prints the x, y coordinates of the other persons mouse into code that will select elements in the browser based on those coordinates. 
#The elementFromPoint method depends on the viewport though, so you have to move around a bit until the msg fits.

#1. load the webpage
#2. position your screen
#3. x = array printed by this script
#4. x.forEach((element) => { if (element.src) {element.src = null;} }) // set the img sources to null