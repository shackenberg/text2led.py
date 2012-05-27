#! /usr/bin/env python
# -*- coding: UTF-8 -*-

""" 
text2led.py
This is a python script to control led display boards or
 'led ticker' via serial or usb connection.

The script works at least with following displays.
- Skytronic MSB-67 / 153.141
- Velleman MML16CN 
- AM004-03127 
Please inform me, if it also works with other models.

The core class is taken from:
http://gathering.tweakers.net/forum/list_message/30160421#30160421
-----------------------

The script offers three modi operandi:

Manual: The script waits for input via the cmd line.

ITunes: The script uses AppleScript to poll ITunes 
        every second for current song's name and artist.
        Only on OSX

VirtualDJ: The script checks every second the history of
           the DJ program VirtualDJ for new entries and
           outputs the last entrie's song name and artist.
           Tested on Windows7 and OSX. Please look at the 
           function for further details.

Each one of the three modi is activate by commenting out 
the other two. 
    

-----------------------

Preparations:

- find out the right serialport
  for Windows it is "\\.\COM3" in my experince
  for Mac OSX it is "/dev/cu.SLAB_USBtoUART"
  For OSX you first have to install the USB2Serial driver. I used:
  http://www.silabs.com/products/mcu/Pages/USBtoUARTBridgeVCPDrivers.aspx
- edit the serial port, see __main__


------------------------

How to change display options:

The display options can be changed via the settings variable.
All the different supported options can be found in the 
documentation of the led display boards. Copies can be found here:
- http://www.produktinfo.conrad.com/datenblaetter/575000-599999/590998-da-01-en-LED_LAUFSCHRIFT_ROT.pdf
- http://www.domotiga.nl/attachments/39/RGB_ledbar_conrad.pdf
"""

import re
import os
import subprocess
import time

class LedDisplay:
    # from http://gathering.tweakers.net/forum/list_message/30160421#30160421
    import serial, operator, re
    def __init__(self, device, device_id = 1, timeout = 0.1, noisy = False):
        self._device    = device
        self._device_id = device_id
        self._timeout   = timeout
        self._noisy     = noisy
        self._port      = self.serial.Serial(self._device, 9600, self.serial.EIGHTBITS, self.serial.PARITY_NONE, self.serial.STOPBITS_ONE, self._timeout, False, False)

    def __del__(self):
        self._port.close()

    def send(self, data_packet):
        clean_string = self.clean_string(data_packet)
        checksum = reduce(self.operator.__xor__, map(ord, clean_string), 0)
        command = "<ID%02X>%s%02X<E>" % (self._device_id, clean_string, checksum)
        if self._noisy:
            print "sending to device %s: \"%s\"" % (self._device, command)
        self._port.write(command)
        response = self._port.read(100)
        if self._noisy:
            if len(response) == 0:
                print "received no response from device \"%s\"." % self._device
            else:
                print "received %d-byte response from device \"%s\": \"%s\"." % (len(response), self._device, response)

    def clean_string(self,input_string): 
        data = [['€','<U0>'], ['  ','<U1>'],
            ['‚','<U2>'], ['ƒ','<U3>'], ['„','<U4>'], ['…','<U5>'], ['†','<U6>'],
            ['‡','<U7>'], ['ˆ','<U8>'], ['‰','<U9>'], ['Š','<UA>'], ['‹','<UB>'],
            ['Œ','<UC>'], ['  ','<UD>'], ['Ž','<UE>'], ['  ','<UF>'], ['  ','<U10>'],
            ['‘','<U11>'], ['’','<U12>'], ['“','<U13>'], ['”','<U14>'], ['•','<U15>'],
            ['–','<U16>'], ['—','<U17>'], ['˜','<U18>'], ['™','<U19>'], ['š','<U1A>'],
            ['›','<U1B>'], ['œ','<U1C>'], ['©','<U1D>'], ['ž','<U1E>'], ['Ÿ','<U1F>'],
            [' ','<U20>'], ['¡','<U21>'], ['¢','<U22>'], ['£','<U23>'], ['¤','<U24>'],
            ['¥','<U25>'], ['¦','<U26>'], ['§','<U27>'], ['¨','<U28>'], ['©','<U29>'],
            ['ª','<U2A>'], ['«','<U2B>'], ['¬','<U2C>'], ['-0','<U2D>'], ['®','<U2E>'],
            ['¯','<U2F>'], ['°','<U30>'], ['±','<U31>'], ['²','<U32>'], ['³','<U33>'],
            ['´','<U34>'], ['µ','<U35>'], ['¶','<U36>'], ['·','<U37>'], ['¸','<U38>'],
            ['¹','<U39>'], ['º','<U3A>'], ['»','<U3B>'], ['¼','<U3C>'], ['½','<U3D>'],
            ['¾','<U3E>'], ['¿','<U3F>'], ['À','<U40>'], ['Á','<U41>'], ['Â','<U42>'],
            ['Ã','<U43>'], ['Ä','<U44>'], ['Å','<U45>'], ['Æ','<U46>'], ['Ç','<U47>'],
            ['È','<U48>'], ['É','<U49>'], ['Ê','<U4A>'], ['Ë','<U4B>'], ['Ì','<U4C>'],
            ['Í','<U4D>'], ['Î','<U4E>'], ['Ï','<U4F>'], ['Ð','<U50>'], ['Ñ','<U51>'],
            ['Ò','<U52>'], ['Ó','<U53>'], ['Ô','<U54>'], ['Õ','<U55>'], ['Ö','<U56>'],
            ['×','<U57>'], ['Ø','<U58>'], ['Ù','<U59>'], ['Ú','<U5A>'], ['Û','<U5B>'],
            ['Ü','<U5C>'], ['Ý','<U5D>'], ['Þ','<U5E>'], ['ß','<U5F>'], ['à','<U60>'],
            ['á','<U61>'], ['â','<U62>'], ['ã','<U63>'], ['ä','<U64>'], ['å','<U65>'],
            ['æ','<U66>'], ['ç','<U67>'], ['è','<U68>'], ['é','<U69>'], ['ê','<U6A>'],
            ['ë','<U6B>'], ['ì','<U6C>'], ['í','<U6D>'], ['î','<U6E>'], ['ï','<U6F>'],
            ['ð','<U70>'], ['ñ','<U71>'], ['ò','<U72>'], ['ó','<U73>'], ['ô','<U74>'],
            ['õ','<U75>'], ['ö','<U76>'], ['÷','<U77>'], ['ø','<U78>'], ['ù','<U79>'],
            ['ú','<U7A>'], ['û','<U7B>'], ['ü','<U7C>'], ['ý','<U7D>'], ['þ','<U7E>'],
            ['ÿ','<U7F>'] ] # http://www.danshort.com/ASCIImap/indexhex.htm
        for unsafe, safe in data: 
            input_string =  re.sub(unsafe,safe,input_string) 
        return input_string

def manual(ledz,settings="<L1><PA><FE><MQ><WC><FA>"):
    
    while True:
        input_line = raw_input()
        ledz.send(settings+input_line)    
    del ledz

def virtualDJ(ledz,settings="<L1><PA><FE><MQ><WC><FA>"):
    """ 
    To make this function work, you have to give to the variable
    filename the path to the history. The file is called 'tracklist.txt.'
    and instructions on how to find the tracklist can be found here:
    http://www.virtualdj.com/wiki/INSTALL.html
    
    VirtualDJ writes songs only after 20s of playtime into the tracklist.
    To change this you have adjust the 'HistoryTimer' field. How to change 
    this setting depends on you OS. See following URL for further
    details. http://de.virtualdj.com/wiki/RegistryValues.html
    Note: VirtualDJ has to be closed before you change the setting, as 
    it writes it settings to disk, when it is closed.
    """    
    
    # Mac
    filename = '/Users/ludwig/Library/VirtualDJ/Tracklisting/tracklist.txt'

    # Win
    #filename = 'C:\\Users\\{USERNAME}\\Documents\\VirtualDJ\\Tracklisting\\tracklist.txt'

    old_time = os.stat(filename).st_mtime
    while True:
        new_time =  os.stat(filename).st_mtime
        if new_time != old_time:
            with open(filename) as tracklist:
                input_line =  (list(tracklist)[-1])
                pivot = input_line.find(' : ')
                ledz.send(settings+input_line[pivot+3:])  
            old_time = new_time  
    del ledz
 
def itunes(ledz,settings="<L1><PA><FE><MQ><WC><FA>"):  
    # needs apple script => OSX needed 
    cmdTrackName = ["""osascript -e 'tell application "iTunes" to set trackName to name of current track'"""]
    cmdArtistName = ["""osascript -e 'tell application "iTunes" to set artistName to artist of current track'"""]
    old_line4led =''
    while True:
        p = subprocess.Popen(cmdTrackName, shell=True, stdout=subprocess.PIPE)
        trackname = p.stdout.read()[:-1] # cutting of the newline
        p = subprocess.Popen(cmdArtistName, shell=True, stdout=subprocess.PIPE)
        artist = p.stdout.read()[:-1] # cutting of the newline
        line4led = artist+' - '+trackname# cutting of the newline
        if line4led != old_line4led:
            ledz.send(settings+line4led)
            old_line4led = line4led
        time.sleep(1)


    
if __name__ == "__main__":
    settings = "<L1><PA><FE><MQ><WC><FA>"

    ## Mac
    ledz = LedDisplay("/dev/cu.SLAB_USBtoUART", noisy = True) 

    ## Windows
    #ledz = LedDisplay("\\.\COM3", noisy = True)

    ## Modi
    #manual(ledz,settings) # waits for input from the cmd
    #itunes(ledz,settings) needs apple script => OSX needed
    virtualDJ(ledz,settings)