#config settings must be made before anything else is imported
from kivy.config import Config
#Config.set('input', 'mouse', 'mactouch') #as opposed to "mouse"
Config.set('graphics', 'fullscreen', 'auto') 
#Config.set('graphics','show_cursor','0') 
#Config.write() #This will save the changes

from kivy.app import App
from kivy.base import EventLoop
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.graphics import Color, Rectangle #Ellipse, Line,Rectangle
from kivy.support import install_twisted_reactor
from kivy.uix.image import Image
from kivy.uix.textinput import TextInput
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock
from kivy.properties import ObjectProperty
from kivy.properties import StringProperty
install_twisted_reactor()
import ujson, os, random, pickle, time, datetime
from kivy.uix.popup import Popup
from kivy.uix.slider import Slider



from twisted.internet import reactor, protocol
from twisted.protocols import basic

#def send_message(msg):
#    msg += Glbls.end_marker
#    if msg and Glbls.connection:
#        Glbls.connection.sendLine(msg)

class Glbls():
    try:                                        #Checks to see if the last ip address was stored
        ip_address = pickle.load(open('temp_ip'))          
    except(IOError):
        ip_address = ""
    participant_name = ""
    participant_gender = ""
    participant_age = ""
    participant_handedness = ""
    connection = None
    playing = False
    own_canvas_color = [0,1]
    partner_canvas_color = [0,1]
    timestamp_format = "%b-%d-%y; %H:%M:%S.%f"



    instructions = ("Welcome! You're going to be playing a very simple game.\n\n"
                    "It works like this: By clicking on the mouse or trackpad you change the color of your partner's screen. "
                    "If your partner's screen is black, it will become white. If your partner's screen is white, it will become black. "
                    "On the bottom right of your screen you can see the color of your partner's screen. "
                    "By clicking their own trackpad your partner can change the color of your screen in the same way. "
                    "You can both click as frequently or as infrequently as you want, in any pattern. "
                    "But you cannot make any noise or do anything else to signal to your partner. "
                    "There is no turn taking.\n\n"
                    "The question is this: Is your partner human?\n\n"
                    "There is another participant in the lab, but is that who you're exchanging signals with? "
                    "50% of pairs are not sending signals to each other at all, but are simply receiving signals from a computer. "
                    "At the end of the experiment you will be asked which you think was the case.")
    
    
    

class SignalingClientProtocol(basic.LineReceiver):
    def connectionMade(self):
        print("connected succesfully!")
        Glbls.connection = self
        demographics = {"name":Glbls.participant_name,"age":Glbls.participant_age,"gender":Glbls.participant_gender,"handedness":Glbls.participant_handedness}
        msg = ujson.dumps(("demographics",demographics))
        self.sendLine(msg)
        
    def lineReceived(self,line):
        #print line
        loadedmsg = ujson.loads(line)

        if loadedmsg[0] == "parameters":
            sm.current = 'expscreen'
            Glbls.playing = True
            
        if loadedmsg[0] == "switch":
            if Glbls.playing == True:
                Glbls.vse.canvas_wid.switch_color()

        if loadedmsg[0] == "finished":
            Glbls.vse.ask_question()
            
        if loadedmsg[0] == "answer":
            print "/n/n/nANSWER MESSAGE!!!/n/n"
            print loadedmsg
            Glbls.vse.reveal_answer(loadedmsg[1])
        


#class SignalingClientProtocol(protocol.Protocol):
    #def connectionMade(self):
    ##    self.factory.app.on_connection(self.transport)
    #
    #def dataReceived(self, data):
    #        #print "data received"
    #        End = Glbls.end_marker
    #        total_data = Glbls.databuffer
    #        messages = []
    #        if End in data:
    #            total_data.append(data[:data.find(End)])
    #            messages.append(total_data)
    #            total_data = []
    #            Glbls.databuffer = []
    #            message_length = len(End) + len(data[:data.find(End)])
    #            if message_length < len(data):
    #                leftover = data[message_length:]
    #                while True:
    #                    if End in leftover:
    #                        total_data.append(leftover[:leftover.find(End)])
    #                        messages.append(total_data)
    #                        total_data = []
    #                        message_length = len(End) + len(leftover[:leftover.find(End)])
    #                        if len(leftover) == message_length:
    #                            break
    #                        else:
    #                            leftover = leftover[message_length:]
    #                    else:
    #                        self.buffer.append(leftover)
    #                        break
    #        total_data.append(data)
    #        if len(total_data)>1:
    #            #check if end_of_data was split
    #            last_pair=total_data[-2]+total_data[-1]
    #            if End in last_pair:
    #                total_data[-2]=last_pair[:last_pair.find(End)]
    #                total_data.pop()
    #                
    #        messages2return = []
    #        for msg in messages:
    #            messages2return.append(''.join(msg))
    #        
    #        response = Glbls.vse.handle_message(messages2return)
        
        
class SignalingClientFactory(protocol.ClientFactory):
    protocol = SignalingClientProtocol

    def __init__(self, app):
        self.app = app

    def clientConnectionLost(self, conn, reason):
        print("connection lost")

    def clientConnectionFailed(self, conn, reason):
        sm.current = "settings"
        print("connection failed")
        
    
class InstructionWidget(RelativeLayout):
    instruction_label_wid = ObjectProperty()
    


            

class FeedbackWidget(RelativeLayout):
    
    def switch_color(self,touch):
        if Glbls.playing == True:
            tm = datetime.datetime.now().strftime(Glbls.timestamp_format)
            Glbls.partner_canvas_color.reverse()
            col = Glbls.partner_canvas_color[0]
            self.canvas.clear()
            with self.canvas:
                Color(col,col,col)
                Rectangle(pos=self.pos,size=self.size)
            msg = ujson.dumps(("sent switch",col,tm))
            if Glbls.connection:
                Glbls.connection.sendLine(msg)


class CanvasWidget(RelativeLayout):
    
    def switch_color(self):
        if Glbls.playing == True:
            tm = datetime.datetime.now().strftime(Glbls.timestamp_format)
            Glbls.own_canvas_color.reverse()
            col = Glbls.own_canvas_color[0]
            self.canvas.clear()
            with self.canvas:
                Color(col,col,col)
                Rectangle(pos=self.pos,size=self.size)
            msg = ujson.dumps(("received switch",col,tm))
            if Glbls.connection:
                Glbls.connection.sendLine(msg)

   

class SignalingExperiment(Screen): #class SignalingExperiment(RelativeLayout):
    
    canvas_wid = ObjectProperty()
    feedback_wid = ObjectProperty()


                

            
    def ask_question(self):
        content = GridLayout(cols=1)
        human_button = Button(text="Human")
        computer_button = Button(text="Computer")
        gameover_label = Label(text="That's the end!")
        question_label = Label(text="Were you paired with a human or receiving signals from a computer?")
        content.add_widget(gameover_label)
        content.add_widget(question_label)
        x = random.randint(0,1)
        if x == 0:
            content.add_widget(human_button)
            content.add_widget(computer_button)
        else:
            content.add_widget(computer_button)
            content.add_widget(human_button)
        human_button.bind(on_release=self.ask_question2)
        computer_button.bind(on_release=self.ask_question2)
        Glbls.question_popup = Popup(title="", content = content,size_hint=(.5,.5),auto_dismiss=False)
        Glbls.question_popup.open()
        
        
    def ask_question2(self,btn):
        tm = datetime.datetime.now().strftime(Glbls.timestamp_format)
        Glbls.question_popup.dismiss()
        msg = ujson.dumps(("guess",btn.text,tm))
        Glbls.connection.sendLine(msg)
        content = GridLayout(cols=1)
        recap_text = 'You guessed "' + btn.text + '"'
        recap_label = Label(text=recap_text)
        question_label = Label(text="How sure are you of your guess?")
        Glbls.certainty_slider = Slider(min=0, max=100, value=50)
        submit_button = Button(text="submit")
        content.add_widget(recap_label)
        content.add_widget(question_label)
        slider_content = GridLayout(rows=1)
        
        left_slider_label = Label(text="Not at all")
        right_slider_label = Label(text="Completely")
        slider_content.add_widget(left_slider_label)
        slider_content.add_widget(Glbls.certainty_slider)
        slider_content.add_widget(right_slider_label)
    
        content.add_widget(slider_content)
        content.add_widget(submit_button)
        submit_button.bind(on_release=self.answered)
        Glbls.question_popup2 = Popup(title="", content = content,size_hint=(.5,.5),auto_dismiss=False)
        Glbls.question_popup2.open()        
        
        
        
    def answered(self,btn):
        Glbls.accept_input = False
        tm = datetime.datetime.now().strftime(Glbls.timestamp_format)
        certainty = Glbls.certainty_slider.value_normalized
        print certainty
        Glbls.question_popup2.dismiss()
        msg = ujson.dumps(("certainty_guess",certainty,tm))
        Glbls.connection.sendLine(msg)
        content = GridLayout(cols=1)
        gameover_label = Label(text="Thank you for your time.")
        gameover_label2 = Label(text="When the other participant has guessed,\n the answer will be revealed.")
        content.add_widget(gameover_label)
        content.add_widget(gameover_label2)
        Glbls.waiting_popup = Popup(title="", content = content,size_hint=(.5,.5),auto_dismiss=False)
        Glbls.waiting_popup.open()
        
        
    def reveal_answer(self,answer):
        content = GridLayout(cols=1)
        ans = "You were in fact paired with a " + answer
        gameover_label = Label(text=ans)
        gameover_label2 = Label(text="The experiment is now over. Thank you.")
        content.add_widget(gameover_label)
        content.add_widget(gameover_label2)
        try:
            Glbls.waiting_popup.dismiss()
        except:
            pass
        Glbls.gameover_popup = Popup(title="", content = content,size_hint=(.5,.5),auto_dismiss=False)
        Glbls.gameover_popup.open()
        
        



Builder.load_string("""
                    

            
<CanvasWidget>:
    canvas:
        Color:
            rgb: 0, 0, 0
        Rectangle:
            pos: self.pos
            size: self.size
    
            
<FeedbackWidget>:
    canvas:
        Color:
            rgb: 0, 0, 0
        Rectangle:
            pos: self.pos
            size: self.size
            

        
<IPWidget>:
    iptextinput_wid: ipti
    TextInput:
        text: root.ip_address
        multiline: False
        on_text: app.get_setup_text("ip",args[1])
        write_tab: False
        id: ipti

        unfocus_on_touch: False

<NameWidget>:
    TextInput:
        text: ''
        multiline: False
        on_text: app.get_setup_text("name",args[1])
        write_tab: False
        # on_text_validate: app.start_button_pressed()

<AgeWidget>:
    TextInput:
        text: ''
        multiline: False
        on_text: app.get_setup_text("age",args[1])
        write_tab: False
        # on_text_validate: app.start_button_pressed()

# <GenderWidget>:
#     TextInput:
#         text: ''
#         multiline: False
#         on_text: app.get_setup_text("gender",args[1])
#         write_tab: False
#         # on_text_validate: app.start_button_pressed()

<LeftHandBtn>:
    ToggleButton:
        text: 'Left-handed'
        group: 'handedness'
        on_press: app.get_setup_text("handedness","left-handed")

<RightHandBtn>:
    ToggleButton:
        text: 'Right-handed'
        group: 'handedness'
        on_press: app.get_setup_text("handedness","right-handed")

<AmbiHandBtn>:
    ToggleButton:
        text: 'Ambidextrous'
        group: 'handedness'
        on_press: app.get_setup_text("handedness","ambidextrous")

<MaleGenderBtn>:
    ToggleButton:
        text: 'Male'
        group: 'gender'
        on_press: app.get_setup_text("gender","male")

<FemaleGenderBtn>:
    ToggleButton:
        text: 'Female'
        group: 'gender'
        on_press: app.get_setup_text("gender","female")

<NeitherGenderBtn>:
    ToggleButton:
        text: 'Neither'
        group: 'gender'
        on_press: app.get_setup_text("gender","neither")



<InstructionWidget>:
    instruction_label_wid: instruction_label
    canvas:
        Color:
            rgb: 1, 1, 1
        Rectangle:
            pos: self.pos
            size: self.size
    Label:
        font_size: '17sp'
        #size: self.texture_size
        padding_x: 10
        valign: 'top'
        color: 0, 0, 0, 1
        text_size: self.size
        text: ""
        id: instruction_label

        


<InstructionScreen>:
    instruction_wid: iw

    
    RelativeLayout:
        size_hint: (.5,1)
        pos_hint: {'x': 0.25, 'y': 0}
        InstructionWidget:
            id: iw
  
<SignalingExperiment>:
    canvas_wid: cw
    feedback_wid: fw


    on_touch_down: 
        fw.switch_color(args[1])

    RelativeLayout:
        size_hint: (1,1)
        pos_hint: {'x': 0, 'y': 0}
        CanvasWidget:
            id: cw
            
    RelativeLayout:
        size_hint: (.5, .2)
        pos_hint: {'x': 0.5, 'y': 0}
        FeedbackWidget:
            id: fw

            
            
<SettingsScreen>:
    name_wid: nw
    ip_wid: ipw
    age_wid: aw
    lh_button: lhb
    rh_button: rhb
    ambih_button: ahb
    mg_button: mgb
    fg_button: fgb
    ng_button: ngb
    
    #on_touch_down:
     #   ipw.get_focus()
        


    RelativeLayout:
        size_hint: (0.5, 0.05)
        pos_hint: {'center_x': 0.5,'y': 0.9}
        Label:
            font_size: '20sp'
            color: 1, 1, 1, 1
            text: 'Server IP Address:'

    RelativeLayout:
        size_hint: (0.5, 0.05)
        pos_hint: {'center_x': 0.5,'y': 0.85}
        IPWidget:
            id: ipw
            
    RelativeLayout:
        size_hint: (0.5, 0.05)
        pos_hint: {'center_x': 0.5,'y': 0.7}
        Label:
            font_size: '20sp'
            color: 1, 1, 1, 1
            text: 'Participant name:'
            
    RelativeLayout:
        size_hint: (0.5, 0.05)
        pos_hint: {'center_x': 0.5,'y': 0.65}
        NameWidget:
            id: nw

    RelativeLayout:
        size_hint: (0.5, 0.05)
        pos_hint: {'center_x': 0.5,'y': 0.6}
        Label:
            font_size: '20sp'
            color: 1, 1, 1, 1
            text: 'Participant age:'
            
    RelativeLayout:
        size_hint: (0.5, 0.05)
        pos_hint: {'center_x': 0.5,'y': 0.55}
        AgeWidget:
            id: aw

    RelativeLayout:
        size_hint: (0.5, 0.05)
        pos_hint: {'center_x': 0.5,'y': 0.45}
        Label:
            font_size: '20sp'
            color: 1, 1, 1, 1
            text: 'Participant gender:'

    RelativeLayout:
        size_hint: (0.2, 0.1)
        pos_hint: {'center_x': 0.2,'y': 0.35}
        MaleGenderBtn:
            id: mgb
    RelativeLayout:
        size_hint: (0.2, 0.1)
        pos_hint: {'center_x': 0.5,'y': 0.35}
        FemaleGenderBtn:
            id: fgb
    RelativeLayout:
        size_hint: (0.2, 0.1)
        pos_hint: {'center_x': 0.8,'y': 0.35}
        NeitherGenderBtn:
            id: ngb

            
    # RelativeLayout:
    #     size_hint: (0.5, 0.05)
    #     pos_hint: {'center_x': 0.5,'y': 0.45}
    #     GenderWidget:
    #         id: gw

    RelativeLayout:
        size_hint: (0.5, 0.05)
        pos_hint: {'center_x': 0.5,'y': 0.25}
        Label:
            font_size: '20sp'
            color: 1, 1, 1, 1
            text: 'Participant handedness:'
            
    RelativeLayout:
        size_hint: (0.2, 0.1)
        pos_hint: {'center_x': 0.2,'y': 0.15}
        LeftHandBtn:
            id: lhb
    RelativeLayout:
        size_hint: (0.2, 0.1)
        pos_hint: {'center_x': 0.5,'y': 0.15}
        RightHandBtn:
            id: rhb
    RelativeLayout:
        size_hint: (0.2, 0.1)
        pos_hint: {'center_x': 0.8,'y': 0.15}
        AmbiHandBtn:
            id: ahb


ScreenManager:
    Screen
            
""")


class IPWidget(RelativeLayout):
    iptextinput_wid = ObjectProperty()
    ip_address = Glbls.ip_address
    #ip_text = StringProperty()

    def get_focus(self):
        self.iptextinput_wid.focus = True


    

class NameWidget(RelativeLayout):
    pass

class AgeWidget(RelativeLayout):
    pass

# class GenderWidget(RelativeLayout):
#     pass

class LeftHandBtn(RelativeLayout):
    pass

class RightHandBtn(RelativeLayout):
    pass

class AmbiHandBtn(RelativeLayout):
    pass


class MaleGenderBtn(RelativeLayout):
    pass

class FemaleGenderBtn(RelativeLayout):
    pass

class NeitherGenderBtn(RelativeLayout):
    pass


        


        

class SettingsScreen(Screen):
    name_wid = ObjectProperty()
    ip_wid = ObjectProperty()

class InstructionScreen(Screen):
    instruction_wid = ObjectProperty()


    
    

    

sm = ScreenManager()
Glbls.settings_screen = SettingsScreen(name='settings')
Glbls.instruction_screen = InstructionScreen(name='instructions')
Glbls.vse = SignalingExperiment(name='expscreen')
sm.add_widget(Glbls.settings_screen)
sm.add_widget(Glbls.instruction_screen)
sm.add_widget(Glbls.vse)



class SignalingExperimentApp(App):
        
    connection = None

    def connect_to_server(self):
        reactor.connectTCP(Glbls.ip_address, 8000, SignalingClientFactory(self))
    
    #def on_connection(self, connection):
    #    print("connected succesfully!")
    #    Glbls.connection = connection
    #    msg = ujson.dumps(("name",Glbls.participant_name))
    #    send_message(msg)

    def build(self):
        #self.connect_to_server()
        #Glbls.vse = SignalingExperiment()
        Glbls.app = self
        return sm
        #return Glbls.vse
    
    def get_setup_text(self,text_type,val):
        if text_type == "ip":
            Glbls.ip_address = val
        if text_type == "name":
            Glbls.participant_name = val
        if text_type == "age":
            Glbls.participant_age = val
        if text_type == "gender":
            Glbls.participant_gender = val
        if text_type == "handedness":
            Glbls.participant_handedness = val


        if (Glbls.ip_address != "" and Glbls.participant_name != "" 
            and Glbls.participant_age != "" and Glbls.participant_gender != ""
            and Glbls.participant_handedness != ""):
            self.start_button_pressed()
            
    def start_button_pressed(self):
        if Glbls.participant_name.replace(" ", "") != "" and Glbls.ip_address.replace(" ", "") != "":
            Glbls.ip_address = Glbls.ip_address.replace(" ","")
            pickle.dump(Glbls.ip_address,open('temp_ip','w'))
            Glbls.app.connect_to_server() 
            sm.current = 'instructions'
            Glbls.instruction_screen.instruction_wid.instruction_label_wid.text = Glbls.instructions
        else:
            pass
        
        
        
        #return CanvasWidget()


if __name__ == '__main__':
    SignalingExperimentApp().run()
    
