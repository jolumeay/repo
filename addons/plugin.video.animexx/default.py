#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import urllib
import urlparse
import xbmcgui
import xbmcplugin
import xbmcaddon
import urllib, urllib2, socket, cookielib, re, os, shutil,json
from StringIO import StringIO

# Setting Variablen Des Plugins
base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = urlparse.parse_qs(sys.argv[2][1:])
addon = xbmcaddon.Addon()
# Lade Sprach Variablen
translation = addon.getLocalizedString
# Welche Seite Laden
mainUrl = "http://animexx.onlinewelten.com"
global debuging
debuging=""
# Cookies und Url Parser Laden
cj = cookielib.CookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
# Es geht um Videos
xbmcplugin.setContent(addon_handle, 'movies')

# Urls fuer Funtionen erzeugen
# Mode=funtkion
# Pfad= die Url die die Funtkion Nutzen soll
def build_url(modus,pfad):
    if id == 0:
      return base_url + '?' + urllib.urlencode({'mode': modus})
    else:
      return base_url + '?' + urllib.urlencode({'mode': modus,'pfad': pfad})
    
# Laed die Url mit den Richtigen Parametern  gei Category und Schlagwoerter 
def getUrl():
  if debuging=="true":
    xbmc.log("Hole URL")
  userAgent = "Mozilla/5.0 (Windows NT 6.2; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0"
  opener.addheaders = [('User-Agent', userAgent)]
  global content
  content=opener.open(mainUrl+"/videos/").read()
# Laed die Settings
def getSettings():
  global debuging
  debuging=addon.getSetting("debug")
getSettings()
# LAed die Kategorieren  
def Kategorieholen():
  if debuging=="true":
    xbmc.log("Kategorie Starten")
  # Kuerzen der Seite auf das Notwendigste
  Kategorie = content[content.find("<h2>Kategorien</h2>")+1:]
  Kategorie = Kategorie[:Kategorie.find("</div>")]
  # Alle Links raussuchen 
  match=re.compile('<a href=\'(.+?)\'>(.+?)</a>', re.DOTALL).findall(Kategorie)
  # Ueber Allle Links Loopen
  for pfad, name in match:
    if debuging=="true":
      xbmc.log("Kategorieholen PFAD:"+ pfad)
      xbmc.log("Kategorieholen NAME:"+ name)
    # Url fuer Seite Laden einer Kategorie (pfad) auisgeben  
    url = build_url("Seite_start",pfad)
    li = xbmcgui.ListItem(name)
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,listitem=li, isFolder=True)
  # Seite Anzeigen
  xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)

# Seite Anzeigen  
def GetSeite(webpage,zurueck):
  if debuging=="true":
    xbmc.log("GetSeite: Video SeiteLaden")   
    xbmc.log("GetSeite: Video url:"+ webpage)  
  # Wird gebraucht da die links bei serien mit ./ beginnen    
  webpage=webpage.replace("/./","/")  
  # Url Laden
  page=opener.open(mainUrl+webpage).read()  
  if debuging=="true": 
    xbmc.log("GetSeite: Page:"+mainUrl+webpage) 
  #Anfuerungszeichen richtig setzen
  page=page.replace('&quot;','"')
  # Seite kuerzen auf Videos
  Webseiten = page[page.find("<div class='seiten_blaettern_leiste align_center width700'>")+1:]
  Webseiten = Webseiten[:Webseiten.find('<table class="width700 blau padding0 align_center">')]
  # Alle Links Durchgehen
  match=re.compile('<a +href=\'(.+?)\' rel=.+?>(.+?)</a>', re.DOTALL).findall(Webseiten)
  # Fuer Alle Links
  for Kpfad, name in match:
  #Wenn Link Weiter ist Dann den Weiter Link Erzeugen
   if 'Weiter' in name:
    url = build_url("Seite",Kpfad)
    li = xbmcgui.ListItem("Weiter")
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,listitem=li, isFolder=True)
   # Wenn Link Zurueck gibt dann Zurueck Link Erzeugen 
   if 'Zurück' in name:
    url = build_url("Seite",Kpfad)
    li = xbmcgui.ListItem("Zurueck")
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,listitem=li, isFolder=True)
   if debuging=="true":
       xbmc.log("GetKategoriVideo: VideoURL WEITER"+ url)   
  # Strings die Vorkommen in der Seite Aber beim Suchen in Regexp stoeren weglassen       
  web2=page.replace("style='font-weight: bold; cursor: pointer;'><span class='pics_pfeil_rechts'></span> <span itemprop='name'>","")
  web2=web2.replace("class='video_caller'\n","")  
  web2=web2.replace("\n"," ")  
  web2=web2.replace("\r"," ")
  # Suche Jedes Video, dabei brauchen wir name,url und id
  match=re.compile("<a[^']+?href='([^']+?)'[^>]+?><span class='pics_pfeil_rechts'></span>.+?<a +href=\"([^\"]+?)\"([^<]+?)</span></a>", re.DOTALL).findall(web2)
  for Youtube,Kpfad, name in match:
    #Wenn es ein Youtubne Video Ist
    if "youtube" in Youtube:
       # Video Url Setzene
       Youtube=Youtube.replace("http://www.youtube.com/watch?v=","")
       # Vorschau Bild Setzen
       Preview="http://i.ytimg.com/vi/"+Youtube+"/1.jpg"
       # Hintegrund Bild
       Fanart="http://i.ytimg.com/vi/"+Youtube+"/hqdefault.jpg"
       # Meta Daten Holen
       req = urllib2.Request('https://www.googleapis.com/youtube/v3/videos?part=snippet&id='+ Youtube +'&key=AIzaSyBTOhQM6vxriNmdkdbEgRCV3PcUm7KQXHQ')
       req.add_header('Referer', 'http://repo.l0re.com')
       r = urllib2.urlopen(req).read()
       # Metadaten in Json Laden
       struktur = json.loads(r)
       # Meta Daten Setzen
       plot = struktur['items'][0]['snippet']['description'].encode("utf-8")
       erschienen = struktur['items'][0]['snippet']['publishedAt'].encode("utf-8")
       title = struktur['items'][0]['snippet']['title'].encode("utf-8")
    else:
        #Wenn es ein Vimeo Video Ist
        # Pfad des Url Relativ machen
        Youtube=Youtube.replace("http://vimeo.com/","")
        # Meta Daten laden
        pagen = urllib2.Request("http://vimeo.com/api/v2/video/"+Youtube+".json")
        r = urllib2.urlopen(pagen).read()
        # Meta Daten in Json wandeln
        struktur = json.loads(r)
        # Meta Daten einlesen
        plot = struktur[0]['description'].encode("utf-8").replace("<br />","")
        erschienen = struktur[0]['upload_date']
        title = struktur[0]['title'].encode("utf-8")
        Preview=struktur[0]['thumbnail_large']
        Fanart=struktur[0]['thumbnail_large']
    #Die Eingelesene Daten Setzen fuer das eine Video (Pfad ist das Video Bei animexx
    url = build_url("Video",Kpfad)
    li = xbmcgui.ListItem(name.strip())  
    li.setInfo('video', { 'plot': plot})
    li.setInfo('video', { 'premiered': erschienen})
    li.setInfo('video', { 'title': title})
    li.setThumbnailImage (Preview)
    li.setIconImage(Preview)
    li.setProperty('fanart_image',Fanart) 
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,listitem=li, isFolder=False)
    if debuging=="true":
      xbmc.log("GetKategoriVideo Kategorie Starten URL"+ url)
      xbmc.log("GetKategoriVideo Kategorie Starten NAME"+ name.strip())
  # Wenn es Zureuck gibt, nicht als neue Seite betrachten damit der ".." Knopf geht
  if ( zurueck == 1):
    xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)
  else:
    xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=True,cacheToDisc=False)

# Schlagwoerter einlesen
def Schlagwoerterholen():
  if debuging=="true":
    xbmc.log("Schlagworte Starten")
  # Inhalt Verkuerzen damit es keine Fehltreffer gibt
  Schlagwoerter = content[content.find("<h2>Schlagworte</h2>")+1:]
  Schlagwoerter = Schlagwoerter[:Schlagwoerter.find("</div>")]
  # Alle Links Holen
  match=re.compile('<a href=\'(.+?)\'>(.+?)</a>', re.DOTALL).findall(Schlagwoerter)
  # Fuer Jeden Link
  for pfad, name in match:
    if debuging=="true":
      xbmc.log("Schlagwoerterholen PFAD:"+ pfad)
      xbmc.log("Schlagwoerterholen NAME:"+ name)
    # Sonderzeichen Richtig umwandeln
    name=name.replace('&quot;','"')
    #Link Erzeugen
    url = build_url("Seite_start",pfad)
    li = xbmcgui.ListItem(name)
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,listitem=li, isFolder=True)
  # Menu Anzeigen
  xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)

  
def Serienholen():
  if debuging=="true":
    xbmc.log("Serienholen: Hole URL")
  userAgent = "Mozilla/5.0 (Windows NT 6.2; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0"
  opener.addheaders = [('User-Agent', userAgent)]
  global content
  content=opener.open(mainUrl+"/videos/thema/").read()
  xbmc.log("content:" + content)
  # Laed die Settings
  if debuging=="true":
    xbmc.log("Serienholen Starten")
  # Inhalt Verkuerzen damit es keine Fehltreffer gibt
  Serien = content[content.find('<caption>Videos nach Serie</caption>')+1:]
  Serien = Serien[:Serien.find('</td></tr></table></div>')]
  # Alle Links Holen
  match=re.compile('<a href=\'(.+?)\'>(.+?)</a>', re.DOTALL).findall(Serien)
  # Fuer Jeden Link
  for pfad, name in match:
    if debuging=="true":
      xbmc.log("Serienholen PFAD:"+ pfad)
      xbmc.log("Serienholen NAME:"+ name)
    # Sonderzeichen Richtig umwandeln
    name=name.replace('&quot;','"')
    #Link Erzeugen
    url = build_url("Seite_start",'/videos/thema/'+pfad)
    li = xbmcgui.ListItem(name)
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,listitem=li, isFolder=True)
  # Menu Anzeigen
  xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)  
  
  
# Video ueber Plugin Laden  
def PlayVideo(webpage):
  if debuging=="true":
    xbmc.log("Play Video video:"+ webpage)  
  # Animexx Video Seite laden
  page=opener.open(webpage).read()                       
  match=re.compile('<tr class=\"video_row\" data-type=\"([^"]+?)\" data-id=\"([^"]+?)\"', re.DOTALL).findall(page)  
  # Typ und ID Einlesen
  for type, id in match:
      if debuging=="true":
         xbmc.log("PlayVideo typ"+ type)
         xbmc.log("PlayVideo id"+ id)        
      if type == "youtube" :     
         plugin='plugin://plugin.video.youtube/?action=play_video&videoid='+ id 
      if type == "vimeo" :     
         plugin="plugin://plugin.video.vimeo/play/?video_id="+ id
  # Video auf Youtube oder Vimeo abspielen
  xbmc.executebuiltin("xbmc.PlayMedia("+plugin+")")
    
# Einlesen der Uebergebenen Parameter
mode = args.get('mode', None)
pfad = args.get('pfad', None)


# Haupt Menu Anzeigen      
if mode is None:
    url = build_url("Category",0)
    li = xbmcgui.ListItem(translation(40001))
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,listitem=li, isFolder=True)

    url = build_url("Tags",0)
    li = xbmcgui.ListItem(translation(40002))
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,listitem=li, isFolder=True)
    
    url = build_url("Serien",0)
    li = xbmcgui.ListItem(translation(40005))
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,listitem=li, isFolder=True)
    
    url = build_url("Settings",0)
    li = xbmcgui.ListItem(translation(40003))
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url,listitem=li, isFolder=True)
    

    xbmcplugin.endOfDirectory(addon_handle,succeeded=True,updateListing=False,cacheToDisc=True)
else:
  # Wenn Settings ausgewählt wurde
  if mode[0] == 'Settings':
          addon.openSettings()
          getSettings()
  # Wenn Kategory ausgewählt wurde
  if mode[0] == 'Category':
          getUrl()
          Kategorieholen()
  # Wenn Serien ausgewählt wurde
  if mode[0] == 'Serien':
          Serienholen()
  # Wenn Tags ausgewaelt wurden
  if mode[0] == 'Tags':
          getUrl()
          Schlagwoerterholen()
  # Wenn ein Seite gewählt wurde
  if mode[0] == 'Seite':
          GetSeite(pfad[0],0)   
  # Erste Seite gewählt
  if mode[0] == 'Seite_start':
          GetSeite(pfad[0],1)            
  # Video Aspielen ausgewählt          
  if mode[0] == 'Video':
          PlayVideo(pfad[0])
