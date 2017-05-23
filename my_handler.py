import hal
import gtk
import hal_glib
import linuxcnc
import os
import time
from gscreen import preferences
from gscreen import keybindings

keydown_panel=0xC0
keyup_panel = 0x80
rowshift_panel = 3
_X = 0;_Y = 1;_Z = 2;_A = 3;_B = 4;_C = 5;_U = 6;_V = 7;_W = 8
KEY_DOWN = 1 ; KEY_UP =0 

try:
    s = linuxcnc.stat() # create a connection to the status channel
    c = linuxcnc.command () #create a connection to the command
except linuxcnc.error, detail:
    print "error", detail
    sys.exit(1)

def get_handlers(halcomp,builder,useropts,gscreen):
     return [HandlerClass(halcomp,builder,useropts,gscreen)]


class HandlerClass:
    def __init__(self,halcomp,builder,useropts,gscreen):

        self.emc=gscreen.emc
        self.gscreen=gscreen
        self.data=gscreen.data
        self.widgets=gscreen.widgets
        self.halcomp = hal.component("my_gscreen")
        global keydown_panel
        global keyup_panel
        global rowshift_panel
        self.prefs = preferences.preferences()
        inifile = linuxcnc.ini(os.getenv("INI_FILE_NAME"))


        self.step_feed_override = self.prefs.getpref('STEP_FEED_OVERRIDE',0.2, float  ,"PANEL")
        self.max_feed_override = self.prefs.getpref('MAX_FEED_OVERRIDE',1.5, float  ,"PANEL")

        self.step_spindle_override = self.prefs.getpref('STEP_SPINDLE_OVERRIDE',0.2,float,"PANEL")
        self.max_spindle_override = self.prefs.getpref('MAX_SPINDLE_OVERRIDE',1.5,float,"PANEL")

        self.x1_mpg_scale = self.prefs.getpref('MPG_SCALE_X1',1, int ,"PANEL")
        self.x10_mpg_scale = self.prefs.getpref('MPG_SCALE_X10',2, int ,"PANEL")
        self.x100_mpg_scale = self.prefs.getpref('MPG_SCALE_X100',5, int ,"PANEL")
        self.x1_mpg_angular_scale = self.prefs.getpref('MPG_ANGULAR_SCALE_X1',1, int ,"PANEL")
        self.x10_mpg_angular_scale = self.prefs.getpref('MPG_ANGULAR_SCALE_X10',10, int ,"PANEL")
        self.x100_mpg_angular_scale = self.prefs.getpref('MPG_ANGULAR_SCALE_X100',100, int ,"PANEL")
        self.jog_mode = 0   # 0=no jog, 1= jog, 2=inc_jog, 3=mpg
        self.rapid_speed_select = 0
        self.rapid_speed_low = self.prefs.getpref('JOG_SPEED_LOW', '12', int ,"PANEL")
        self.rapid_speed_hi = self.prefs.getpref('JOG_SPEED_HI', '120', int ,"PANEL")
        self.rapid_angular_speed_low = self.prefs.getpref('JOG_ANGULAR_SPEED_LOW', '120', int ,"PANEL")
        self.rapid_angular_speed_hi = self.prefs.getpref('JOG_ANGULAR_SPEED_HI', '220', int ,"PANEL")

        
        self.set_jog_speed=0
        self.function_list = {
            '0': 'mpg','1': 'home_all','2':'inc_jog','3':'spindle_minus','4':'spindle_reset','5':'spindle_plus',
            '8': 'jog','9': 'mdi_mode', '10':'auto_mode','11':'spindle_cw','12':'spindle_stop','13':'spindle_ccw','15':'nic',
            '16':'x1', '17':'x10','18':'x100','19':'feed_minus','20':'feed_reset','21':'feed_plus',
            '24':'z_plus','25':'y_plus','26':'a_plus',
            '32':'x_minus','33':'rapid','34':'x_plus','35':'light','36':'toolchange',
            '40':'z_minus','41':'y_minus','42':'a_minus'
			
            }
        self.update_led_list = (
		    '0','1','2','3','4','5','8','9','10','11','12','13','16','17','18','19','20','21','24','25','26','32','33','34','35','40','41','42')

 
    def initialize_widgets(self):
        self.gscreen.initialize_widgets()
        self.gscreen.init_show_windows()
        print "my inicializace widgetu"
        self.gscreen.set_jog_rate(absolute = self.rapid_speed_low)
        self.gscreen.update_jog_rate_label()

 
 
 
			
    def light_func (self,key):
        if key:
            if self.halcomp['light'] :
                self.halcomp['light'] = False
            else:
                self.halcomp['light'] = True
				
    def toolchange_func (self,key):

        print "--------toolchange-----------"
        s.poll() # get current valuess.poll()		
        print "max_position_limit" , s.axis[0]['max_position_limit']
        print "max_position_limit" , s.axis[1]['max_position_limit']
        print "max_position_limit" , s.axis['x']['max_position_limit']
        print "limit" , s.limit
        c.set_max_limit(_Z, 150.0)
        s.poll() # get current valuess.poll()		
        print "max_position_limit" , s.axis[_Z]['max_position_limit']
		
		
		
		
		
    def light_update (self):
        return self.halcomp['light'] == True

    def periodic (self):
        self.gscreen.update_position()
        if self.set_jog_speed==1:
            self.setup_jog_speed ()
        s.poll() # get current valuess.poll()		
        for i in self.update_led_list :
            ret = eval("self."+self.function_list[i]+"_update()")
            time.sleep(0.003)
            self.send_led_key(i,ret)
        """print self.gscreen.data.jog_increments[self.gscreen.data.current_jogincr_index]"""
		
    def setup_jog_speed (self):
        print "--------rapid_speed_curre from jog speed ",self.rapid_speed_current
        print "self.halcomp['wheel'] , self.current_wheel",self.halcomp['wheel'] , self.current_wheel
        if self.rapid_speed_select == 0:
            if self.gscreen.data.angular_jog_adjustment_flag:
                self.rapid_angular_speed_low = self.rapid_speed_current + self.halcomp['wheel'] - self.current_wheel
                self.gscreen.set_jog_rate(absolute = self.rapid_angular_speed_low)
            else:
                self.rapid_speed_low = self.rapid_speed_current + self.halcomp['wheel'] - self.current_wheel
                self.gscreen.set_jog_rate(absolute = self.rapid_speed_low)
        else:
            if self.gscreen.data.angular_jog_adjustment_flag:
                self.rapid_angular_speed_hi = self.rapid_speed_current + self.halcomp['wheel'] - self.current_wheel
                self.gscreen.set_jog_rate(absolute = self.rapid_angular_speed_hi)
            else:
                self.rapid_speed_hi = self.rapid_speed_current + self.halcomp['wheel'] - self.current_wheel
                self.gscreen.set_jog_rate(absolute = self.rapid_speed_hi)
        


		
    def init_my_pins(self):
        """create HAL pins """
            
        self.data['key_panel'] = hal_glib.GPin(self.halcomp.newpin('key_panel', hal.HAL_U32, hal.HAL_IN))
        self.data['key_led'] = hal_glib.GPin(self.halcomp.newpin('key_led', hal.HAL_U32, hal.HAL_OUT))
        self.data['wheel'] = hal_glib.GPin(self.halcomp.newpin('wheel', hal.HAL_S32, hal.HAL_IN))
        self.data['light'] = hal_glib.GPin(self.halcomp.newpin('light', hal.HAL_BIT, hal.HAL_OUT))
        self.data['nokey'] = hal_glib.GPin(self.halcomp.newpin('nokey', hal.HAL_BIT, hal.HAL_IN))
        self.data['jog_scale'] = hal_glib.GPin(self.halcomp.newpin('jog_scale', hal.HAL_FLOAT, hal.HAL_OUT))
        self.data['jog_angular_scale'] = hal_glib.GPin(self.halcomp.newpin('jog_angular_scale', hal.HAL_FLOAT, hal.HAL_OUT))
        self.data['shutdown'] = hal_glib.GPin(self.halcomp.newpin('shutdown', hal.HAL_BIT, hal.HAL_IN))
        self.halcomp['jog_scale']=self.x1_mpg_scale
        self.halcomp['jog_angular_scale']=self.x1_mpg_angular_scale



    def connect_signals(self,handlers):
        self.gscreen.connect_signals(handlers)
        self.data['key_panel'].connect('value-changed', self.key_panel_func)
        self.data['shutdown'].connect('value-changed', self.shutdown)
        self.data['nokey'].connect('value-changed', self.nokey_func)
    
    def initialize_pins(self):
        self.gscreen.initialize_pins()
        self.init_my_pins()

    def shutdown (self,status):
        if self.halcomp['shutdown'] :
            os.system("./shutdown.sh")
            time.sleep(2)
            print "--------shutdown--------:", status
            gtk.main_quit()

		
    def home_all_func (self,key):
        if key :
            print "home all"
            if not self.data.all_homed:
                self.gscreen.home_all()
		
    def home_all_update (self):
        return self.data.all_homed
        
		

		
    def rapid_func (self,key):
        if key:
            count=0
            while  self.halcomp['key_panel'] == 33 | keydown_panel:
                count=count+1
                time.sleep(0.001)
                if count>500:
                    print "prechayim do nastaveni------------"
                    self.set_jog_speed=1
                    self.current_wheel = self.halcomp['wheel']
                    if self.rapid_speed_select == 0:
                        self.rapid_speed_current = self.rapid_speed_low
                    else:
                        self.rapid_speed_current = self.rapid_speed_hi
                    for i in self.data.axis_list:
                        self.widgets["axis_%s"%i].set_active(False)
                    print "----------current speed je ", self.rapid_speed_current
                    break
					
            print "----------adjust flag + rotacni osa ",self.gscreen.data.angular_jog_adjustment_flag , self.data.rotary_joints
            if self.rapid_speed_select and not self.set_jog_speed :
                print "----angular, linear", self.rapid_angular_speed_low,self.rapid_speed_low
                if self.data.rotary_joints:
                    self.gscreen.data.angular_jog_adjustment_flag = True
                    self.gscreen.set_jog_rate(absolute = self.rapid_angular_speed_low)
                    self.gscreen.update_jog_rate_label()
                    self.gscreen.data.angular_jog_adjustment_flag = False
                self.gscreen.set_jog_rate(absolute = self.rapid_speed_low)
                self.gscreen.update_jog_rate_label()
                self.rapid_speed_select = 0
                print "nastavuju pomalou"
            elif not self.rapid_speed_select and not self.set_jog_speed:
                if  self.data.rotary_joints:
                    self.gscreen.data.angular_jog_adjustment_flag = True
                    self.gscreen.set_jog_rate(absolute = self.rapid_angular_speed_hi)
                    self.gscreen.update_jog_rate_label()
                    self.gscreen.data.angular_jog_adjustment_flag = False
                self.gscreen.set_jog_rate(absolute = self.rapid_speed_hi)
                self.gscreen.update_jog_rate_label()
                self.rapid_speed_select = 1
                print "nastavuju rychlou"
        else:
            print "-----------------uvolneno-------"
            self.gscreen.update_jog_rate_label()
            self.prefs.putpref('JOG_SPEED_LOW', self.rapid_speed_low , int ,"PANEL")
            self.prefs.putpref('JOG_SPEED_HI', self.rapid_speed_low , int ,"PANEL")
            self.prefs.putpref('JOG_ANGULAR_SPEED_LOW', self.rapid_angular_speed_low , int ,"PANEL")
            self.prefs.putpref('JOG_ANGULAR_SPEED_HI', self.rapid_angular_speed_hi , int ,"PANEL")

            self.set_jog_speed=0
            self.gscreen.data.angular_jog_adjustment_flag = False
			
    def rapid_update (self):
        return self.rapid_speed_select == 1
		
    def x1_func (self,key):
        if key and self.jog_mode!=1:  #nelze nastavit pro jog - continuous
            self.gscreen.data.current_jogincr_index = 0
            self.gscreen.data.current_angular_jogincr_index = 0
            jogincr = self.gscreen.data.jog_increments[self.gscreen.data.current_jogincr_index]
            self.widgets.jog_increments.set_text(jogincr)
            if self.data.rotary_joints:
                jogincr = self.gscreen.data.angular_jog_increments[self.gscreen.data.current_angular_jogincr_index]
                self.widgets.angular_jog_increments.set_text(jogincr)
            self.halcomp['jog_scale']=self.x1_mpg_scale
            self.halcomp['jog_angular_scale']=self.x1_mpg_angular_scale

		
    def x10_func (self,key):
        if key and self.jog_mode!=1:
            print self.gscreen.data.jog_increments[self.gscreen.data.current_jogincr_index]
            self.gscreen.data.current_jogincr_index = 1
            self.gscreen.data.current_angular_jogincr_index = 1
            jogincr = self.gscreen.data.jog_increments[self.gscreen.data.current_jogincr_index]
            self.widgets.jog_increments.set_text(jogincr)
            if self.data.rotary_joints:
                jogincr = self.gscreen.data.angular_jog_increments[self.gscreen.data.current_angular_jogincr_index]
                self.widgets.angular_jog_increments.set_text(jogincr)
            self.halcomp['jog_scale']=self.x10_mpg_scale
            self.halcomp['jog_angular_scale']=self.x10_mpg_angular_scale

    def x100_func (self,key):
        if key and self.jog_mode!=1:
            print self.gscreen.data.jog_increments[self.gscreen.data.current_jogincr_index]
            self.gscreen.data.current_jogincr_index = 2
            self.gscreen.data.current_angular_jogincr_index = 2
            jogincr = self.gscreen.data.jog_increments[self.gscreen.data.current_jogincr_index]
            self.widgets.jog_increments.set_text(jogincr)
            if self.data.rotary_joints:
                jogincr = self.gscreen.data.angular_jog_increments[self.gscreen.data.current_angular_jogincr_index]
                self.widgets.angular_jog_increments.set_text(jogincr)
            self.halcomp['jog_scale']=self.x100_mpg_scale
            self.halcomp['jog_angular_scale']=self.x100_mpg_angular_scale
	
	
    def mpg_func (self,key):
        if key and self.data.all_homed:
            print "mpg mode"
            self.gscreen.data.mode_order = 0,1,2
            label = self.gscreen.data.mode_labels
            self.widgets.button_mode.set_label(label[self.data.mode_order[0]])
            self.gscreen.mode_changed(self.data.mode_order[0])
            for i in self.data.axis_list:
                self.widgets["axis_%s"%i].set_active(False)
            if not self.widgets.button_jog_mode.get_active() or self.jog_mode != 3:
                self.jog_mode = 3
                self.widgets.button_jog_mode.set_active(True)
                self.gscreen.jog_mode()
                self.gscreen.data.current_jogincr_index = 0
                if self.data.rotary_joints:
                    self.gscreen.data.current_angular_jogincr_index = 0
                    jogincr = self.gscreen.data.angular_jog_increments[self.gscreen.data.current_angular_jogincr_index]
                    self.widgets.angular_jog_increments.set_text(jogincr)
            else:
                self.widgets.button_jog_mode.set_active(False)
                self.jog_mode = 0
            jogincr = self.gscreen.data.jog_increments[self.gscreen.data.current_jogincr_index]
            self.widgets.jog_increments.set_text(jogincr)
			
			
    def jog_func (self,key):
        if key and self.data.all_homed:
            print "continues jog mode"
            self.gscreen.data.mode_order = 0,1,2
            label = self.gscreen.data.mode_labels
            self.widgets.button_mode.set_label(label[self.data.mode_order[0]])
            self.gscreen.mode_changed(self.data.mode_order[0])
            for i in self.data.axis_list:
                self.widgets["axis_%s"%i].set_active(False)
            if not self.widgets.button_jog_mode.get_active() or self.jog_mode !=1 :
                self.jog_mode = 1
                self.widgets.button_jog_mode.set_active(True)
                self.gscreen.jog_mode()
                self.gscreen.data.current_jogincr_index = -1
                if self.data.rotary_joints:
                    self.gscreen.data.current_angular_jogincr_index = -1
                    jogincr = self.gscreen.data.angular_jog_increments[self.gscreen.data.current_angular_jogincr_index]
                    self.widgets.angular_jog_increments.set_text(jogincr)
            else:
                self.widgets.button_jog_mode.set_active(False)
                self.jog_mode = 0
            jogincr = self.gscreen.data.jog_increments[self.gscreen.data.current_jogincr_index]
            self.widgets.jog_increments.set_text(jogincr)
            
			

        


    def inc_jog_func (self,key):
        if key and self.data.all_homed:
            print "incremental jog mode", self.jog_mode
            self.gscreen.data.mode_order = 0,1,2
            label = self.gscreen.data.mode_labels
            self.widgets.button_mode.set_label(label[self.data.mode_order[0]])
            self.gscreen.mode_changed(self.data.mode_order[0])
            for i in self.data.axis_list:
                self.widgets["axis_%s"%i].set_active(False)
            if not self.widgets.button_jog_mode.get_active() or self.jog_mode != 2:
                self.jog_mode = 2
                self.widgets.button_jog_mode.set_active(True)
                self.gscreen.jog_mode()
                self.gscreen.data.current_jogincr_index = 0
                if self.data.rotary_joints:
                    self.gscreen.data.current_angular_jogincr_index = 0
                    jogincr = self.gscreen.data.angular_jog_increments[self.gscreen.data.current_angular_jogincr_index]
                    self.widgets.angular_jog_increments.set_text(jogincr)
            else:
                self.widgets.button_jog_mode.set_active(False)
                self.jog_mode = 0
            jogincr = self.gscreen.data.jog_increments[self.gscreen.data.current_jogincr_index]
            self.widgets.jog_increments.set_text(jogincr)
		
    def x_plus_func (self,key):
        if key:
            if self.jog_mode == 3:
                self.widgets["axis_x"].set_active(True)
            else:
                self.gscreen.do_key_jog(_X,1,1)
        else :
            self.gscreen.do_key_jog(_X,1,0)
			
    def a_plus_func (self,key):
        if self.data.rotary_joints:
            if key:
                if self.set_jog_speed==1:
                    print "-------------nastavuju rotarz flag -----------------"
                    self.gscreen.data.angular_jog_adjustment_flag = True
                    self.current_wheel = self.halcomp['wheel']
                    if self.rapid_speed_select == 0:
                        self.rapid_speed_current = self.rapid_angular_speed_low
                    else:
                        self.rapid_speed_current = self.rapid_angular_speed_hi
                    print "------------rapid_speed_current", self.rapid_speed_current
                else:
                    if self.jog_mode == 3:
                        self.widgets["axis_a"].set_active(True)
                    else:
                        self.widgets["axis_a"].set_active(True)
                        self.gscreen.do_jog(1,1)
                        self.widgets["axis_a"].set_active(False)
            else:
                self.widgets["axis_a"].set_active(True)
                self.gscreen.do_jog(1,0)
                if not self.jog_mode == 3:
                    self.widgets["axis_a"].set_active(False)
					
    def a_minus_func (self,key):
        if self.data.rotary_joints:
            if key:
                if self.set_jog_speed==1:
                    print "-------------nastavuju rotarz flag -----------------"
                    self.gscreen.data.angular_jog_adjustment_flag = True
                    self.current_wheel = self.halcomp['wheel']
                    if self.rapid_speed_select == 0:
                        self.rapid_speed_current = self.rapid_angular_speed_low
                    else:
                        self.rapid_speed_current = self.rapid_angular_speed_hi
                    print "------------rapid_speed_current", self.rapid_speed_current
                else:
                    if self.jog_mode == 3:
                        self.widgets["axis_a"].set_active(True)
                    else:
                        self.widgets["axis_a"].set_active(True)
                        self.gscreen.do_jog(0,1)
                        self.widgets["axis_a"].set_active(False)
            else:
                print "----------------------error-----------------"
                self.widgets["axis_a"].set_active(True)
                self.gscreen.do_jog(1,0)
                if not self.jog_mode == 3:
                    self.widgets["axis_a"].set_active(False)
                
				
    def a_plus_update (self):
        if self.data.rotary_joints:
            return self.jog_mode==3 and self.widgets["axis_a"].get_active() and self.widgets.button_jog_mode.get_active()
        else:
            return False
			
    def a_minus_update (self):
        if self.data.rotary_joints:
            return self.jog_mode==3 and self.widgets["axis_a"].get_active() and self.widgets.button_jog_mode.get_active()
        else:
            return False
				
    def x_plus_update (self):
        return self.jog_mode==3 and self.widgets["axis_x"].get_active() and self.widgets.button_jog_mode.get_active()
			
    def x_minus_func (self,key):
        if key:
            if self.jog_mode == 3:
                self.widgets["axis_x"].set_active(True)
            else:
                self.gscreen.do_key_jog(_X,0,1)
        else :
            self.gscreen.do_key_jog(_X,0,0)
		
    def x_minus_update (self):
        return self.jog_mode==3 and self.widgets["axis_x"].get_active() and self.widgets.button_jog_mode.get_active()
		
    def y_plus_func (self,key):
        if key:
            if self.jog_mode == 3:
                self.widgets["axis_y"].set_active(True)
            else:
                self.gscreen.do_key_jog(_Y,1,1)
        else :
            self.gscreen.do_key_jog(_Y,1,0)
			
    def y_plus_update (self):
        return self.jog_mode==3 and self.widgets["axis_y"].get_active() and self.widgets.button_jog_mode.get_active()
			
    def y_minus_func (self,key):
        if key:
            if self.jog_mode == 3:
                self.widgets["axis_y"].set_active(True)
            else:
                self.gscreen.do_key_jog(_Y,0,1)
        else :
            self.gscreen.do_key_jog(_Y,0,0)
		
    def y_minus_update (self):
        return self.jog_mode==3 and self.widgets["axis_y"].get_active() and self.widgets.button_jog_mode.get_active()
		

    def z_plus_func (self,key):
        if key:
            if self.jog_mode == 3:
                self.widgets["axis_z"].set_active(True)
            else:
                self.gscreen.do_key_jog(_Z,1,1)
        else :
            self.gscreen.do_key_jog(_Z,1,0)
		
    def z_plus_update (self):
        return self.jog_mode==3 and self.widgets["axis_z"].get_active() and self.widgets.button_jog_mode.get_active()
		
    def z_minus_func (self,key):
        if key:
            if self.jog_mode == 3:
                self.widgets["axis_z"].set_active(True)
            else:
                self.gscreen.do_key_jog(_Z,0,1)
        else :
            self.gscreen.do_key_jog(_Z,0,0)
		
    def z_minus_update (self):
        return self.jog_mode==3 and self.widgets["axis_z"].get_active() and self.widgets.button_jog_mode.get_active()
			

		
    def x1_update (self):
        return self.gscreen.data.current_jogincr_index == 0
		
    def x10_update (self):
        return self.gscreen.data.current_jogincr_index == 1
		
    def x100_update (self):
        return self.gscreen.data.current_jogincr_index == 2

    def jog_update (self):
        return self.jog_mode == 1 and self.widgets.button_jog_mode.get_active()  # 0=no jog, 1= jog, 2=inc_jog, 3=mpg
        #self.gscreen.data.jog_increments[self.gscreen.data.current_jogincr_index]==("continuous") and self.widgets.button_jog_mode.get_active()
		
    def inc_jog_update (self):
        return self.jog_mode == 2  and self.widgets.button_jog_mode.get_active()# 0=no jog, 1= jog, 2=inc_jog, 3=mpg
        #not self.gscreen.data.jog_increments[self.gscreen.data.current_jogincr_index]==("continuous") and self.widgets.button_jog_mode.get_active()
		
    def mpg_update (self):
        return self.jog_mode == 3  and self.widgets.button_jog_mode.get_active() # 0=no jog, 1= jog, 2=inc_jog, 3=mpg

		
    
		
    def send_led_key (self,led_number,on_off):
        self.halcomp['key_led']=int(led_number) | int(on_off==True) << 8 
        



    def feed_minus_update (self):
        return float(s.feedrate) <0.99
        	
    def feed_plus_update (self):
        return float(s.feedrate) >1.01 
			
    def feed_reset_update (self):
        return float(s.feedrate) <1.01 and float(s.feedrate) >0.99 
		
    def spindle_minus_update (self):
        return float(s.spindlerate) <0.99
        	
    def spindle_plus_update (self):
        return float(s.spindlerate) >1.01 
			
    def spindle_reset_update (self):
        return float(s.spindlerate) <1.01 and float(s.spindlerate) >0.99 
		
    def nokey_func (self,widget):
        print "---------no key func -------"
        if (self.halcomp['nokey'] and self.data.all_homed and self.jog_mode==1) :
            print "---------no key-------"
            self.x_plus_func(0)
            self.y_plus_func(0)
            self.z_plus_func(0)
            self.a_plus_func(0)
    def key_panel_func (self,widget):
        keycode = self.halcomp['key_panel']  & ~(keydown_panel | keyup_panel)
        print "-----key code--------", self.halcomp['key_panel']
        key = 100
        if ((self.halcomp['key_panel'] & keydown_panel) == keydown_panel) :
            key=KEY_DOWN
            print "key down"
        elif ((self.halcomp['key_panel'] & keydown_panel) == keyup_panel) :
            key=KEY_UP
            print "key up"
        
            

        r = keycode >> rowshift_panel
        c = keycode & ~(0xFFFFFFFF << rowshift_panel)
        if  (r < 0 or  c < 0 or r >= 8  or c >= 8 ):
            return
        print "row" ,r , "colu" , c
        cudlik=r * 8 + c
        print "poradove cislo cudliku" ,cudlik
        try:
            print "volam funkci ", self.function_list[str(cudlik)] , "_func(", key,")"
            eval("self."+self.function_list[str(cudlik)]+"_func("+str(key)+")")
            """eval("self."+self.function_list[str(cudlik)]+"_func()")"""
        except:
            print "takovej cudlik jeste neni definovan"


    

    def mdi_mode_func(self,key):
        if key:
            if self.data.all_homed:
                self.jog_mode = 0
                if self.data.mode_order[0] == 1:
                    self.gscreen.data.mode_order = 0,1,2
                else:
                    self.gscreen.data.mode_order = 1,2,0
                label = self.gscreen.data.mode_labels
                self.widgets.button_mode.set_label(label[self.data.mode_order[0]])
                self.gscreen.mode_changed(self.data.mode_order[0])
                try:
                    self.widgets.hal_mdihistory.entry.grab_focus()
                except:
                    print "nemuzu focusovat"
            else:
                 print "neni nahoumovano"

			 
    def mdi_mode_update (self):
        return self.data.mode_order[0] == 1
		

				
    def auto_mode_func(self,key):
        if key:
            if self.data.all_homed:
                self.jog_mode = 0
                if self.data.mode_order[0] == 2:
                    self.gscreen.data.mode_order = 0,1,2
                else:
                    self.gscreen.data.mode_order = 2,0,1
                label = self.gscreen.data.mode_labels
                self.widgets.button_mode.set_label(label[self.data.mode_order[0]])
                self.gscreen.mode_changed(self.data.mode_order[0])
            else:
                print "neni nahoumovano"
			
    def auto_mode_update (self):
        return self.data.mode_order[0] == 2

    def manual_mode_func(self,key):
        if key:
            if self.data.all_homed:
                self.jog_mode = 0
                self.gscreen.data.mode_order = 0,1,2
                label = self.gscreen.data.mode_labels
                self.widgets.button_mode.set_label(label[self.data.mode_order[0]])
                self.gscreen.mode_changed(self.data.mode_order[0])


    def feed_reset_func (self,key):
        if key:
            c.feedrate(1.0)

    def feed_minus_func (self,key):
        if key:
            s.poll() # get current valuess.poll()
            feed=s.feedrate-float(self.step_feed_override)
            if float(feed) < 0:
                feed=0.0
            c.feedrate(feed)

    def feed_plus_func (self,key):
        if key:
            s.poll() # get current valuess.poll()
            feed=s.feedrate+float(self.step_feed_override)
            if float(feed) > float(self.max_feed_override):
                feed = float(self.max_feed_override)
            c.feedrate(feed)

    def spindle_reset_func (self,key):
        if key:
            c.spindleoverride(1.0)

    def spindle_minus_func (self,key):
        if key:
            s.poll() # get current valuess.poll()
            spindle=s.spindlerate-float(self.step_spindle_override)
            if float(spindle) < 0:
                spindle=0.0
            c.spindleoverride(spindle)
        
    def spindle_plus_func (self,key):
        if key:
            s.poll() # get current valuess.poll()
            spindle=s.spindlerate+float(self.step_spindle_override)
            if float(spindle) > float(self.max_spindle_override):
                spindle = float(self.max_spindle_override)
            c.spindleoverride(spindle)
		
    def spindle_stop_func (self,key):
        if key and self.data.all_homed:
            c.spindle(linuxcnc.SPINDLE_OFF)
		
    def spindle_cw_func (self,key):
        if key and self.data.all_homed :
            c.spindle(linuxcnc.SPINDLE_FORWARD)
		
    def spindle_ccw_func (self,key):
        if key and self.data.all_homed:
            c.spindle(linuxcnc.SPINDLE_REVERSE)
		
    def spindle_stop_update (self):
        return s.spindle_brake==1
        
		
    def spindle_cw_update (self):
        return s.spindle_direction==1
		
    def spindle_ccw_update (self):
        return s.spindle_direction==-1
        

