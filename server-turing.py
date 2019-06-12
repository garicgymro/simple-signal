#config settings must be made before anything else is imported
#from kivy.config import Config
#Config.set('input', 'mouse', 'mactouch') #as opposed to "mouse"
#Config.write() This will save the changes

from kivy.support import install_twisted_reactor
install_twisted_reactor()


from twisted.internet import reactor, protocol #endpoints
from twisted.protocols import basic
import ujson, random, os, time, socket, datetime

from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse, Line, Rectangle
from kivy.clock import Clock
from kivy.properties import ObjectProperty
from kivy.lang import Builder
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.popup import Popup
from kivy.uix.button import Button


class Glbls():
    results_folder = "results"
    clients = []
    max_clients = 2
    timestamp_format = "%b-%d-%y; %H:%M:%S.%f: "
    results = ["Condition: Human free signalling ('computer')"]
    results_file = None
    ready = False
    results_interval = 2 #how often to write to results
    game_length = 10*60
    guesses = []
    answer = "human"
    started = False


class VSpaceServerProtocol(basic.LineReceiver):
    def connectionMade(self):
        Glbls.clients.append(self)
        if len(Glbls.clients) == Glbls.max_clients:
            Glbls.ready = True
    
    def lineReceived(self,line):
        tm = datetime.datetime.now().strftime(Glbls.timestamp_format)
        loadedmsg = ujson.loads(line)
        
        if loadedmsg[0] == "certainty_guess":
            Glbls.guesses.append(self)
            if len(Glbls.guesses) >= Glbls.max_clients:
                msg = ujson.dumps(("answer",Glbls.answer))
                for client in Glbls.clients:
                    client.sendLine(msg)
        
        if loadedmsg[0] == "sent switch":
            if Glbls.max_clients == 2 and Glbls.clients.index(self) == 0:
                receiver = Glbls.clients[1]
            elif Glbls.max_clients == 2 and Glbls.clients.index(self) == 1:
                receiver = Glbls.clients[0]
            msg = ujson.dumps(["switch"])
            receiver.sendLine(msg)        
        
        rf_item = tm + "Client " + str(Glbls.clients.index(self)) + ": " + str(loadedmsg)  
        Glbls.results.append(rf_item)
        
        

class VSpaceServerFactory(protocol.Factory):
    protocol = VSpaceServerProtocol

    def __init__(self, app):
        self.app = app



class ServerWidget(RelativeLayout):
    ip_address=socket.gethostbyname(socket.gethostname())
    ip_label = ObjectProperty()




Builder.load_string("""

                    
<ServerWidget>:
    ip_label: ipl
    RelativeLayout:
        size_hint: (0.5, 0.5)
        pos_hint: {'center_x': 0.5,'center_y': 0.5}
        Label:
            font_size: '20sp'
            color: 1, 1, 1, 1
            text: "ip address: "+root.ip_address
            id: ipl
    RelativeLayout:
        size_hint: (0.2, 0.2)
        pos_hint: {'center_x': 0.5,'center_y': 0.3}
        Button:
            text: 'Start experiment'
            on_press: app.start_button_pressed()

            
""")




class TuringServerApp(App):

    
    def start_button_pressed(self):
        if Glbls.ready == True and Glbls.started == False:
            content = GridLayout(cols=1)
            popup_cancel = Button(text="No. Cancel!")
            popup_accept = Button(text="Yes. Start!")
            popup_label = Label(text="Are you sure you want to start?")
            content.add_widget(popup_label)
            content.add_widget(popup_accept)
            content.add_widget(popup_cancel)
            
            Glbls.start_popup = Popup(title="", content = content,
                            size_hint=(.4,.4), auto_dismiss=False)
            popup_cancel.bind(on_release=Glbls.start_popup.dismiss)
            popup_accept.bind(on_release=self.start_game)
            Glbls.start_popup.open()
        else:
            pass
        
    def startResultsClock(self):
        self.results_clock = Clock.schedule_interval(self.write_results,Glbls.results_interval)

    def startGameClock(self):
        self.game_clock = Clock.schedule_once(self.end_game,Glbls.game_length)    
        
    
    def start_game(self,btn):
        Glbls.started = True
        Glbls.start_popup.dismiss()
        parameters_msg = ujson.dumps(("parameters","human"))
        #parameters_msg += Glbls.end_marker
        for client in Glbls.clients:
            client.sendLine(parameters_msg)
        self.startResultsClock()
        self.startGameClock()
        print "start!"
        
    def end_game(self,dt):
        print "finished"
        tm = datetime.datetime.now().strftime(Glbls.timestamp_format)
        rf_item = tm + "Game ended"
        Glbls.results.append(rf_item)
        for client in Glbls.clients:
            msg = ujson.dumps(["finished"])
            client.sendLine(msg)
        self.write_results(9999)
        
        
        
    def write_results(self,dt):
        towrite = Glbls.results
        Glbls.results = []
        rf = open(Glbls.results_file,"a")
        for item in towrite:
            rf.write(item)
            rf.write("\n")
        rf.close()            
                
    
    def build(self):
        if not os.path.exists(Glbls.results_folder):
            os.makedirs(Glbls.results_folder)
        results_filename = 'results'+time.strftime("%b-%d-%y_%H-%M-%S")+'.txt'
        Glbls.results_file = os.path.join(Glbls.results_folder,results_filename)
        print Glbls.results_file
        
        reactor.listenTCP(8000, VSpaceServerFactory(self))
        self.label = Label(text="server started\n")
        srvw = ServerWidget()
        Glbls.srvw = srvw
        return srvw
    


if __name__ == '__main__':
    TuringServerApp().run()