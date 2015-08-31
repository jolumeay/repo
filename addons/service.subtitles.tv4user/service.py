# -*- coding: utf-8 -*-

import os
import shutil
import sys
import urllib
import xbmc
import xbmcaddon
import xbmcgui,xbmcplugin
import xbmcvfs
import urllib2, socket, cookielib, re, os, shutil
import cookielib, json


# Globals
addon = xbmcaddon.Addon()
base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
addonID = addon.getAddonInfo('id')
translation = addon.getLocalizedString
profile    = xbmc.translatePath( addon.getAddonInfo('profile') ).decode("utf-8")
temp       = xbmc.translatePath( os.path.join( profile, 'temp', '') ).decode("utf-8")
cwd        = xbmc.translatePath( addon.getAddonInfo('path') ).decode("utf-8")
resource   = xbmc.translatePath( os.path.join( cwd, 'resources', 'lib' ) ).decode("utf-8")
icon = xbmc.translatePath('special://home/addons/'+addonID+'/icon.png')
defaultBackground = "http://www.ard.de/pool/img/ard/background/base_xl.jpg"
defaultThumb = "http://www.ard.de/pool/img/ard/background/base_xl.jpg"
addonUserDataFolder=xbmc.translatePath("special://profile/addon_data/"+addonID)
subdir=xbmc.translatePath( os.path.join( temp, 'subs', '') ).decode("utf-8")
subdownload=xbmc.translatePath( os.path.join( temp, 'download', '') ).decode("utf-8")
subtitlefile="tv4user"




if xbmcvfs.exists(subdir):
  shutil.rmtree(subdir)
xbmcvfs.mkdirs(subdir)

if xbmcvfs.exists(subdownload):
  shutil.rmtree(subdownload)
xbmcvfs.mkdirs(subdownload)


if xbmcvfs.exists(temp):
  shutil.rmtree(temp)

xbmcvfs.mkdirs(temp)
xbmcvfs.mkdirs(subdir)
xbmcvfs.mkdirs(subdownload)

def debug(content):
    log(content, xbmc.LOGDEBUG)
    
def notice(content):
    log(content, xbmc.LOGNOTICE)

def log(msg, level=xbmc.LOGNOTICE):
    addon = xbmcaddon.Addon()
    addonID = addon.getAddonInfo('id')
    xbmc.log('%s: %s' % (addonID, msg), level) 

def getSettings():
  global user
  user=addon.getSetting("user")
  global pw
  pw=addon.getSetting("pw")
  global backNav
  
def get_params(string=""):
  param=[]
  if string == "":
    paramstring=sys.argv[2]
  else:
    paramstring=string
  if len(paramstring)>=2:
    params=paramstring
    cleanedparams=params.replace('?','')
    if (params[len(params)-1]=='/'):
      params=params[0:len(params)-2]
    pairsofparams=cleanedparams.split('&')
    param={}
    for i in range(len(pairsofparams)):
      splitparams={}
      splitparams=pairsofparams[i].split('=')
      if (len(splitparams))==2:
        param[splitparams[0]]=splitparams[1]

  return param  
  
def login():
  cj = cookielib.CookieJar()
  global mainUrl
  mainUrl = "http://board.TV4User.de"
  global opener
  opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
  userAgent = "Mozilla/5.0 (Windows NT 6.2; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0"
  opener.addheaders = [('User-Agent', userAgent)]
  xy=opener.open(mainUrl+"/index.php?form=UserLogin", data="loginUsername="+urllib.quote_plus(user)+"&loginPassword="+urllib.quote_plus(pw)).read()
  
  
def getUrl(url):
        
        debug("TV4User: Get Url")
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:23.0) Gecko/20100101 Firefox/23.0')
        response = urllib2.urlopen(req)
        content=response.read()
        response.close()
        return content

def clean_serie(title):
        title=title.lower().replace('the ','') 
        title=title.replace('.','')
        title=title.replace("'","")
        return title
        
def lies_serien():
        debug("TV4User: Starte ShowAllSeries")
        content = opener.open(mainUrl+"/index.php").read()
        content = content[content.find('Alphabetische Serien-&Uuml;bersicht')+1:]
        content = content[:content.find('</form>')]
        match=re.compile('<option value="([0-9]+?)">([^<>]+?)</option>', re.DOTALL).findall(content)
        threadIDs = []
        threadNames = []
        threadNamesclean = []
        for id, title in match:
          threadIDs.append(id)
          threadNamesclean.append(clean_serie(title))   
          threadNames.append(title) 
        threadIDs, threadNames,threadNamesclean = (list(x) for x in zip(*sorted(zip(threadNames, threadIDs,threadNamesclean))))
        return threadIDs, threadNames,threadNamesclean


        
def get_uberschriften_new(content):
  match=re.compile('<td>([^<]+)</td>', re.DOTALL).findall(content)
  return match
 
              
def newthread (url)  :
    content=getUrl(url)
    debug("star newthread")
    gefunden=0
    if "<!-- Deutsche Untertitel -->" in content:
      contentDE = content[content.find("<!-- Deutsche Untertitel -->")+1:]
      contentDE = contentDE[:contentDE.find("<!-- Englische Untertitel -->")]    
      folge,untertitel_qualitaet,untertitel_release,untertitel_link,lang_array=get_content(contentDE,"DE")
      if video['episode']:
        for folge_zeile in range(0, len(folge), 1):
          if int(folge[folge_zeile]) == int(video['episode']):
            addLink("Staffel "+ video['season'] + " Folge "+video['episode']+" "+ untertitel_release[folge_zeile]+" ( "+ untertitel_qualitaet[folge_zeile] + " ) ", untertitel_link[folge_zeile], "download", "", duration="", desc="", genre='',lang=lang_array[folge_zeile])
            gefunden=1           
    
      if gefunden==0 :
         for folgenr in range(0, len(folge), 1):
            addLink("Folge "+folge[folgenr]+" "+ untertitel_release[folgenr]+" ( "+ untertitel_qualitaet[folgenr] + " ) ", untertitel_link[folgenr], "download", "", duration="", desc="", genre='',lang=lang_array[folgenr])                      
    if "<!-- Englische Untertitel -->" in content:
      contentEN = content[content.find("<!-- Englische Untertitel -->")+1:]
      contentEN = contentEN[:contentEN.find("<!-- Copyright oder Subberinteresse -->")]  
      folge,untertitel_qualitaet,untertitel_release,untertitel_link,lang_array=get_content(contentEN,"EN")
      if video['episode']:
        for folge_zeile in range(0, len(folge), 1):
          if int(folge[folge_zeile]) == int(video['episode']):
              addLink("Staffel "+ video['season'] + " Folge "+video['episode']+" "+ untertitel_release[folge_zeile]+" ( "+ untertitel_qualitaet[folge_zeile] + " ) ", untertitel_link[folge_zeile], "download", "", duration="", desc="", genre='',lang=lang_array[folge_zeile])          
              gefunden=1
      if gefunden==0 :
        for folgenr in range(0, len(folge), 1):
          addLink("Folge "+folge[folgenr]+" "+ untertitel_release[folgenr]+" ( "+ untertitel_qualitaet[folgenr] + " ) ", untertitel_link[folgenr], "download", "", duration="", desc="", genre='',lang=lang_array[folgenr])                  
    xbmcplugin.endOfDirectory(addon_handle)
    
def get_content(content,lang ):
    debug ("Get Content")
    debug ("Get Content content:"+ content)
    untertitel_link_array=[]
    untertitel_release_array=[]
    untertitel_qualitaet=[]
    untertitel_lang=[]
    folge_array=[]    
    zeile = content.split('</tr')
    ueberschrift=get_uberschriften_new(zeile[0])    
    
    for zeilenr in range(1, len(zeile), 1):
      entry = zeile[zeilenr]
      match=re.compile('<td class="nr">([0-9]+) -', re.DOTALL).findall(entry)
      if not match:
        break
      folge=match[0]
      spalte = entry.split('<td>')
      for spaltennr in range(1, len(spalte), 1):
          entry = spalte[spaltennr]
          if 'href="' in entry:
            untertitel=re.compile('href="([^"]+)">([^<]+)</a>', re.DOTALL).findall(entry)
            for untertitelnr in range(0, len(untertitel), 1):
               debug("Untertitel: Folgenr: "+ folge)
               debug("Untertitel: Folge: " + untertitel[untertitelnr][0])
               debug("Untertitel: Release: " + untertitel[untertitelnr][1])
               debug("Untertitel: Qualität: " + ueberschrift[spaltennr-1])
               debug("Untertitel: Sprache: " + lang)
               debug("------------------")               
               untertitel_link_array.append(untertitel[untertitelnr][0])
               untertitel_release_array.append(untertitel[untertitelnr][1])
               untertitel_qualitaet.append(ueberschrift[spaltennr-1])
               untertitel_lang.append(lang)
               if untertitel[untertitelnr][0] and untertitel[untertitelnr][1] and ueberschrift[spaltennr-1] and lang :
                  folge_array.append(folge)
    if folge_array and untertitel_qualitaet and untertitel_release_array and untertitel_link_array and untertitel_lang:
       folge_array,untertitel_qualitaet,untertitel_release_array,untertitel_link_array,untertitel_lang = (list(x) for x in zip(*sorted(zip(folge_array,untertitel_qualitaet,untertitel_release_array,untertitel_link_array,untertitel_lang))))
    return folge_array,untertitel_qualitaet,untertitel_release_array,untertitel_link_array,untertitel_lang
    
    
def get_content_old(content,lang):
      debug("get_content_old")
      untertitel_link_array=[]
      untertitel_release_array=[]
      untertitel_qualitaet=[]
      untertitel_lang=[]
      folge_array=[]    
      qual_content = content.split('<span class="normalfont">&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;')
      debug("Anz :" + str(len(qual_content)))
      for qualnr in range(1, len(qual_content), 1):
         entry = qual_content[qualnr]
         debug("Start Qulitaet")
         qual=re.compile('<b>([^<]+)</b>', re.DOTALL).findall(entry)
         qualitaet=qual[0]
         untertitels=re.compile('<a href="([^"]+)">([^<]+)</a>', re.DOTALL).findall(entry)
         for untertitelnr in range(0, len(untertitels), 1):
             link=untertitels[untertitelnr][0]
             filename=untertitels[untertitelnr][1]
             debug ("Filename: "+ filename)
             if "Attachment" in link :
                untertitel_link_array.append(link)
                episode_staffel=re.compile('.*S([0-9]+)E([0-9]+).+', re.DOTALL).findall(filename)
                untertitel_qualitaet.append(qualitaet)
                untertitel_lang.append(lang)
                untertitel_release_array.append(filename)
                if episode_staffel:
                   folge_array.append(episode_staffel[0][1])
      if folge_array and untertitel_qualitaet and untertitel_release_array and untertitel_link_array and untertitel_lang:
         folge_array,untertitel_qualitaet,untertitel_release_array,untertitel_link_array,untertitel_lang = (list(x) for x in zip(*sorted(zip(folge_array,untertitel_qualitaet,untertitel_release_array,untertitel_link_array,untertitel_lang))))
      return folge_array,untertitel_qualitaet,untertitel_release_array,untertitel_link_array,untertitel_lang
    
def oldthread(url):
    content=getUrl(url)
    debug("OldThread")
      
    gefunden=0
    if '<span style="font-size: 14pt"><strong><span style="text-decoration: underline">Deutsche Untertitel:</span></strong>' in content:
      contentDE = content[content.find('<span style="font-size: 14pt"><strong><span style="text-decoration: underline">Deutsche Untertitel:</span></strong>')+1:]
      contentDE = contentDE[:contentDE.find('<span style="font-size: 14pt"><strong><span style="text-decoration: underline">Englische Untertitel:</span></strong>')] 
      folge,untertitel_qualitaet,untertitel_release,untertitel_link,lang_array=get_content_old(contentDE,"DE")
      if video['episode']:
        for folge_zeile in range(0, len(folge), 1):
          if int(folge[folge_zeile]) == int(video['episode']):
            addLink("Staffel "+ video['season'] + " Folge "+video['episode']+" "+ untertitel_release[folge_zeile]+" ( "+ untertitel_qualitaet[folge_zeile] + " ) ", untertitel_link[folge_zeile], "download", "", duration="", desc="", genre='',lang=lang_array[folge_zeile])
            gefunden=1               
      if gefunden==0 :
         for folgenr in range(0, len(folge), 1):
            addLink("Folge "+folge[folgenr]+" "+ untertitel_release[folgenr]+" ( "+ untertitel_qualitaet[folgenr] + " ) ", untertitel_link[folgenr], "download", "", duration="", desc="", genre='',lang=lang_array[folgenr])                      
    if '<span style="font-size: 14pt"><strong><span style="text-decoration: underline">Englische Untertitel:</span></strong>' in content:
      contentEN = content[content.find('<span style="font-size: 14pt"><strong><span style="text-decoration: underline">Englische Untertitel:</span></strong>')+1:]
      contentEN = contentEN[:contentEN.find('<div class="containerIcon"><i class="taggingM css-sprite"></i></div>')]
      folge,untertitel_qualitaet,untertitel_release,untertitel_link,lang_array=get_content_old(contentEN,"EN")
      if video['episode']:
        for folge_zeile in range(0, len(folge), 1):
          if int(folge[folge_zeile]) == int(video['episode']):
              addLink("Staffel "+ video['season'] + " Folge "+video['episode']+" "+ untertitel_release[folge_zeile]+" ( "+ untertitel_qualitaet[folge_zeile] + " ) ", untertitel_link[folge_zeile], "download", "", duration="", desc="", genre='',lang=lang_array[folge_zeile])          
              gefunden=1
      if gefunden==0 :
        for folgenr in range(0, len(folge), 1):
          addLink( untertitel_release[folgenr]+" ( "+ untertitel_qualitaet[folgenr] + " ) ", untertitel_link[folgenr], "download", "", duration="", desc="", genre='',lang=lang_array[folgenr])                  
    xbmcplugin.endOfDirectory(addon_handle)
    

    

def addLink(name, url, mode, iconimage="", duration="", desc="", genre='',lang=""):
	u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
	ok = True
	liz = xbmcgui.ListItem(label=lang,label2=name)
	#liz.setInfo(type="Video", infoLabels={"Title": name, "Duration": duration, "Plot": desc, "Genre": genre})
	liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": desc, "Genre": genre})
	liz.setProperty('IsPlayable', 'true')
	liz.addStreamInfo('video', { 'duration' : duration })
	liz.setProperty("fanart_image", defaultBackground)
	#liz.addContextMenuItems([(translation(30012), 'RunPlugin(plugin://'+addonID+'/?mode=queueVideo&url='+urllib.quote_plus(u)+'&name='+urllib.quote_plus(name)+')',)])
	xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
	ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz)
	return ok
  
  
def addDir(name, url, mode, iconimage="", desc=""):
	u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
	ok = True
	liz = xbmcgui.ListItem(name, iconImage=icon, thumbnailImage=iconimage)
	liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": desc})
	if useThumbAsFanart:
		if not iconimage or iconimage==icon or iconimage==defaultThumb:
			iconimage = defaultBackground
		liz.setProperty("fanart_image", iconimage)
	else:
		liz.setProperty("fanart_image", defaultBackground)
	ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
	return ok



def list_folgen(url):
  debug("list_folgen: "+ url)
  content=getUrl(url)
  if "<!-- Englische Untertitel -->" in content:
    newthread(url)
  else :
     oldthread(url)
    
  
def get_staffeln(id):
    serienpage=mainUrl+"/serien/board"+id+"-1.html"
    content=getUrl(serienpage)
    content = content[content.find('<div class="smallPages">')+1:]
    content = content[:content.find('<div class="contentFooter">')]
    linklist= []
    staffellist=[]
    gefunden=0
    spl = content.split('<div class="smallPages">')
    for i in range(1, len(spl), 1):
        entry = spl[i]
        if "[Untertitel]" in entry :
           match = re.compile('<a href="([^"]+)">([^-]+)[\ ]+-[\ ]+Staffel ([0-9]+)[^<]+</a>', re.DOTALL).findall(entry)
           for link,dummy,staffel in match:
             debug("suche staffel:"+ video['season']+"X")
             if video['season']:
                if int(staffel.strip()) == int( video['season'].strip()):
                    gefunden=1
                    list_folgen(link) 
                else :
                    staffellist.append("Staffel "+ staffel)
                    linklist.append(link)
             else :
                 staffellist.append("Staffel "+ staffel)
                 linklist.append(link)
    if gefunden==0 :
      staffellist,linklist = (list(x) for x in zip(*sorted(zip(staffellist, linklist))))
      dialog = xbmcgui.Dialog()
      nr=dialog.select("TV4User.de", staffellist)
      seite=linklist[nr]
      list_folgen(seite)
                

def search():
  debug("Start search")
  error=0
  serien_complete,ids,serien=lies_serien()
  show=clean_serie(video['tvshow'])
  if not show == '':
    try:
      index=serien.index(show)
      id=ids[index]
    except:
       error=1
  else :
        error=1
  if error==1:
    dialog = xbmcgui.Dialog()
    nr=dialog.select("TV4User.de", serien_complete)
    id=ids[nr]
  get_staffeln(id) 
  

def resivefile():
  currentFile = xbmc.Player().getPlayingFile()
  try:
     cf=currentFile.replace("\\","/")
     all=cf.split("/")  
     dirName=all[-2].lower()
     fileName=all[-1].lower()
     debug("Dirname: "+dirname)
     debug ("Filename: "+filename)
  except:
     pass
  if video['episode']=="":
    matchDir=re.compile('\\.s(.+?)e(.+?)\\.', re.DOTALL).findall(dirName)
    matchFile=re.compile('\\.s(.+?)e(.+?)\\.', re.DOTALL).findall(fileName)
    if len(matchDir)>0:
      video['season'] =matchDir[0][0]
      video['episode']=matchDir[0][1]
    elif len(matchFile)>0:
      video['season'] =matchFile[0][0]
      video['episode']=matchFile[0][1]
  if video['episode']=="":
      match=re.compile('(.+?)- s(.+?)e(.+?) ', re.DOTALL).findall(xbmc.getInfoLabel('VideoPlayer.Title').lower())
      if len(match)>0:
         video['season']=match[0][1]
         video['episode']=match[0][2]

  video['release']=""
  if "-" in fileName:
     video['release']=(fileName.split("-")[-1]).lower()
  if "." in video['release']:
    video['release']=video['release'][:video['release'].find(".")]
  elif "-" in dirName:
    video['release']=(dirName.split("-")[-1]).lower()
  title=video['tvshow']
  if title=="" or video['season']=="":
          matchDir=re.compile('(.+?)\\.s(.+?)e(.+?)\\.', re.DOTALL).findall(dirName)
          matchFile=re.compile('(.+?)\\.s(.+?)e(.+?)\\.', re.DOTALL).findall(fileName)
          matchTitle=re.compile('(.+?)- s(.+?)e(.+?) ', re.DOTALL).findall(xbmc.getInfoLabel('VideoPlayer.Title').lower())
          if len(matchDir)>0:
           title=matchDir[0][0]
          elif len(matchFile)>0:
            title=matchFile[0][0]
          elif len(matchTitle)>0:
            title=matchTitle[0][0].strip()
          title=title.replace("."," ")
          if "(" in title:
             title=title[:title.find("(")].strip()
  video['tvshow']=title
  debug("YYY TITLE: " +title)
  
params = get_params()
getSettings() 

def clearSubTempDir(pfad):

        files = os.listdir(pfad)
        for file in files:
          try:
            os.remove(xbmc.translatePath(pfad+"/"+file))
          except:
            pass
def setSubtitle(subUrl):  
        subtitle_list = []    
        debug("SUB: " + subUrl)  
        downloadfile=xbmc.translatePath(subdownload+subtitlefile)
        clearSubTempDir(subdownload)
        clearSubTempDir(subdir)
        rarContent = opener.open(subUrl).read()
        if rarContent.startswith("Rar"):
          ext="rar"
        else:
          ext="zip"        
        Paket=downloadfile+"."+ext
        debug ("Hole File:" +Paket)
        fh = open(Paket, 'wb')
        fh.write(rarContent)
        fh.close()
        debug("Versuche file zu entpacken in "+ subdir)
        xbmc.executebuiltin("XBMC.Extract("+Paket+", "+subdir+")",True)
        for file in xbmcvfs.listdir(subdir)[1]:
           file = os.path.join(subdir, file)
           subtitle_list.append(file)
        for sub in subtitle_list:
             debug("XXYX: "+ sub)
             listitem = xbmcgui.ListItem(label=sub)
             xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=sub,listitem=listitem,isFolder=False)
        xbmcplugin.endOfDirectory(addon_handle)





while (user=="" or pw==""):
  addon.openSettings()
  getSettings()

login()
global video
video ={}
video['year']               = xbmc.getInfoLabel("VideoPlayer.Year")                         # Year
video['season']             = str(xbmc.getInfoLabel("VideoPlayer.Season"))                  # Season
video['episode']            = str(xbmc.getInfoLabel("VideoPlayer.Episode"))                 # Episode
video['tvshow']             = xbmc.getInfoLabel("VideoPlayer.TVshowtitle")  # Show
video['title']              = xbmc.getInfoLabel("VideoPlayer.OriginalTitle") # try to get original title
video['file_original_path'] = xbmc.Player().getPlayingFile().decode('utf-8')                 # Full path of a playing file
video['3let_language']      = [] #['scc','eng']
video['release']            = ""
PreferredSub		      = params.get('preferredlanguage')

if video['title'] == "":
    debug(  "tvshow.OriginalTitle not found")
    video['title']  = xbmc.getInfoLabel("VideoPlayer.Title")    # no original title, get just Title
resivefile()

url = urllib.unquote_plus(params.get('url', ''))  

  

if params['action'] == 'search' :
  search()
    
if params['action'] == 'download' :
  setSubtitle(url)


#xbmc.executebuiltin('runaddon(script.tv4user)')
