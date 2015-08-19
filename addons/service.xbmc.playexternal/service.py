from __future__ import unicode_literals
import asyncore, socket
import xbmc
import xbmcaddon
import time
import base64

import SocketServer
import SimpleHTTPServer
import subprocess
import sys
import threading
import urllib
import os



addon = xbmcaddon.Addon()
ipaddress=addon.getSetting("ipaddress")
port=int(addon.getSetting("port"))
global rtmpdump
rtmpdump=addon.getSetting("rtmpdump")

global popenobj

def debug(content):
    log(content, xbmc.LOGDEBUG)
    
def notice(content):
    log(content, xbmc.LOGNOTICE)

def log(msg, level=xbmc.LOGNOTICE):
    addon = xbmcaddon.Addon()
    addonID = addon.getAddonInfo('id')
    xbmc.log('%s: %s' % (addonID, msg), level) 
class CustomHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):

 def move(self,url):
   self.ende=0
   url=url[1:]
   url=urllib.unquote(url)  
   debug("start move")
 #mp4:7/V_813873_MCHY_13-13000178135_124474_h264-mq_bb4ea742eed38bce10f163b047725cbb.f4v
 #' '-r "rtmpe://fms.rtl.de" -a "rtlnow" -W "http://cdn.static-fra.de/now/vodplayer.swf" -p "http://rtlnow.rtl.de" -y "mp4:7/V_813873_MCHY_13-13000178135_124474_h264-mq_bb4ea742eed38bce10f163b047725cbb.f4v"
   debug("move IP: " + ipaddress)
   if ipaddress == '127.0.0.1':
     popenobj = subprocess.Popen(url, stdout=subprocess.PIPE, shell=True)
   else:
      debug ("SET:"+ rtmpdump+" "+url)
      #popenobj = subprocess.Popen(rtmpdump+" "+url, stdout=subprocess.PIPE, shell=True)
      args = shlex.split("exec " + rtmpdump)
      popenobj = subprocess.Popen(args, stdout=subprocess.PIPE)
   t = threading.Thread(target=self.stdoutprocess, args=(popenobj,))
   t.start()
   debug ("Starte move schleife")
#   popenobj.wait()
   while (not xbmc.abortRequested):
     debug ("Move Schleife")
     time.sleep(1)   
     #t.join()
     if self.ende==1:
       debug("KILLL1")
       popenobj.kill()
       debug("KILLL2")
       t.exit()
       debug("KILLL3")
       break


 def stdoutprocess(self,o):
   debug("start stdoutprocess")
   time.sleep(2)
   while True:
      debug("stdoutprocess schleife")
      stdoutdata = o.stdout.readline()
      try:
        if stdoutdata:
           self.wfile.write(stdoutdata)
        else:
           break
      except:
           debug("stdoutprocess break")
           self.ende=1
           break     
   debug("end stdoutprocess")
   self.ende=1
   return -1
         
 def do_GET(self):  
            debug("GET")
            self.send_response(200)
            self.send_header('Content-type','application/octet-stream')
            self.end_headers()
            debug("Rufe Get Auf")
            self.move(self.path) #call sample function here
            return
        



if __name__ == '__main__':
    monitor = xbmc.Monitor()
    httpd = SocketServer.ThreadingTCPServer((ipaddress, port),CustomHandler)
    httpd.socket.settimeout(1)
    httpd.ende=0
    while not monitor.abortRequested():    
        httpd.handle_request()
        time.sleep(0.1)   
    debug("exit main")

