# -*- coding: utf-8 -*-

import os
import shutil
import sys
import urllib
import xbmc
import xbmcaddon
import xbmcgui,xbmcplugin
import xbmcvfs
import uuid
import urllib2, socket, cookielib, re, os, shutil, base64
import socket, cookielib, re, json

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

if xbmcvfs.exists(temp):
  shutil.rmtree(temp)
xbmcvfs.mkdirs(temp)

sys.path.append (resource)

from OSUtilities import OSDBServer, log, hashFile, normalizeString


def getSettings():
  global user
  user=addon.getSetting("user")
  global pw
  pw=addon.getSetting("pw")
  global backNav
  backNav=addon.getSetting("backNav")
  global pause
  pause=addon.getSetting("pause")
  global saveSub
  saveSub=addon.getSetting("saveSub")
  global language
  language=addon.getSetting("language")
  global debuging
  debuging=addon.getSetting("debug")
  global useThumbAsFanart
  useThumbAsFanart=addon.getSetting("useThumbAsFanart") == "true"
  
  
getSettings()
try:
  currentFile = xbmc.Player().getPlayingFile()
except:
    dialog = xbmcgui.Dialog()
    nr=dialog.select("TV4User.de", [translation(30109)])
    xbmc.log("TV4User: Es Leuft kein Video")  
    quit()

cj = cookielib.CookieJar()
mainUrl = "http://board.TV4User.de"
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
userAgent = "Mozilla/5.0 (Windows NT 6.2; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0"
opener.addheaders = [('User-Agent', userAgent)]
xy=opener.open(mainUrl+"/index.php?form=UserLogin", data="loginUsername="+urllib.quote_plus(user)+"&loginPassword="+urllib.quote_plus(pw)).read()

  
while (user=="" or pw==""):
  addon.openSettings()
  getSettings()

currentEpisode=""
currentSeason=""
currentEpisode=xbmc.getInfoLabel('VideoPlayer.Episode')
currentSeason=xbmc.getInfoLabel('VideoPlayer.Season')

dirName = ""
try:
  cf=currentFile.replace("\\","/")
  all=cf.split("/")
  #dirName=(currentFile.split(os.sep)[-2]).lower()
  dirName=all[-2].lower()
  fileName=all[-1].lower()
except:
  pass

if currentEpisode=="":
  matchDir=re.compile('\\.s(.+?)e(.+?)\\.', re.DOTALL).findall(dirName)
  matchFile=re.compile('\\.s(.+?)e(.+?)\\.', re.DOTALL).findall(fileName)
  if len(matchDir)>0:
    currentSeason=matchDir[0][0]
    currentEpisode=matchDir[0][1]
  elif len(matchFile)>0:
    currentSeason=matchFile[0][0]
    currentEpisode=matchFile[0][1]

if currentEpisode=="":
  match=re.compile('(.+?)- s(.+?)e(.+?) ', re.DOTALL).findall(xbmc.getInfoLabel('VideoPlayer.Title').lower())
  if len(match)>0:
    currentSeason=match[0][1]
    currentEpisode=match[0][2]

if len(currentEpisode)==1:
  currentEpisode="0"+currentEpisode
if len(currentSeason)==1:
  currentSeason="0"+currentSeason

currentRelease=""
if "-" in fileName:
  currentRelease=(fileName.split("-")[-1]).lower()
  if "." in currentRelease:
    currentRelease=currentRelease[:currentRelease.find(".")]
elif "-" in dirName:
  currentRelease=(dirName.split("-")[-1]).lower()

def appendSubInfo(tvShowTitle,season,episode,release,content,lang):
        if debuging=="true":
          xbmc.log("TV4User: AppendSubinfo:"+ episode)
        attachments1 = []
        titles1 = []    
        attachmentsold = []
        titlesolds= [] 
        sprache=[]
        spracheold =[]
        match=re.compile('<td class="nr">(.+?) -</td><td class="episode">', re.DOTALL).findall(content)		
        for sepisode in match:
           if sepisode == episode: 
               if debuging=="true":
                 xbmc.log("TV4User: addSubInfo: Episode:" + episode)
               contentFOLGE = content[content.find('<td class="nr">'+ episode +' -</td><td class="episode">')+1:]
               contentFOLGE = contentFOLGE[:contentFOLGE.find('</tr>')]		   
               match2=re.compile('<a href="(.+?)">(.+?)</a>', re.DOTALL).findall(contentFOLGE)
               for url, ep in match2:
                   if debuging=="true":
                     xbmc.log("TV4User: AppendSubinfo: URL"+ url)
                     xbmc.log("TV4User: AppendSubinfo: EP"+ ep)  
                   attachmentsold=attachments1
                   titlesolds=titles1
                   spracheold=sprache
                   attach = []
                   title = []
                   sprache = []
                   attach.append(url)
                   ep2="E"+episode
                   title.append(tvShowTitle+" - S"+season+ep2+" - "+ep)	
                   sprache.append(lang)
                   attachments1=attachmentsold+attach
                   titles1=titlesolds+title
                   attachments1=attachmentsold+attach
                   sprache=spracheold+sprache
               return [attachments1,titles1,sprache]			

        return ["",""]
        
def getUrl(url):
        if debuging=="true":
          xbmc.log("TV4User: Get Url")
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:23.0) Gecko/20100101 Firefox/23.0')
        response = urllib2.urlopen(req)
        content=response.read()
        response.close()
        return content
        
def search():
        title=xbmc.getInfoLabel('VideoPlayer.TVShowTitle')
        season=currentSeason
        episode=currentEpisode
        release=currentRelease
        if debuging=="true":
          xbmc.log("TV4User: Starte Suche")
        
        if title=="" or season=="":
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
        
        if title=="" or season=="" or episode=="":
          xbmc.executebuiltin('XBMC.Notification(TV4User.de:,'+translation(30014)+'!,3000,'+icon+')')
          main()
        else:
          if season[0:1]=="0":
            season=season[1:]

          #general=base64.b64decode("QUl6YVN5RGJtNzRTNlZia1VjWmNQeC1HTTFtU1B5N2ZYU0R2Vy1J")
          ownKey="AIzaSyB_OW0_DjRXdYB8tJgnvHL3_hr4DOmwXxU"
          searchString1='intitle:"[Untertitel] '+title+' - staffel '+season+'|0'+season+'"'
          searchString2='intitle:"[Untertitel] The '+title+' - staffel '+season+'|0'+season+'"'
          searchString3=" 'Offizielle Homepage'"
          fullUrl='https://www.googleapis.com/customsearch/v1?key='+ownKey+'&cx=006543634684860557840:mixnofny-ac&q='+urllib.quote_plus(searchString1)+'|'+urllib.quote_plus(searchString2)+urllib.quote_plus(searchString3)+'&alt=json'
          xbmc.log("SCDE Addon Log - Search: "+title+"#"+season)
          xbmc.log("SCDE Addon Log - Fullurl: "+fullUrl)
          if debuging=="true":
             xbmc.log("TV4User: Sting ist"+ searchString1 + "Oder"+ searchString2 )
          content = getUrl(fullUrl)
          struktur = json.loads(content)
          finalUrl=""
          if debuging=="true":
                 xbmc.log("TV4User: Wieviel: "+struktur['searchInformation']['totalResults'])
          if struktur['searchInformation']['totalResults']!="0":
            anz=len(struktur['items'])
            for i in range(1,anz):
              url=struktur['items'][i]['link']
              title=struktur['items'][i]['title']
              post=re.search('.*?/p[0-9]+?[^/]+?.html$',url)
              url = re.sub('index[0-9]+.html$','index1.html', url)
              if debuging=="true":
                 xbmc.log("TV4User: Search URL"+url)
              if "staffel" in title.lower() and "untertitel" in title.lower() and not post:
                  finalUrl=url
                  break
	      else:
   	         if debuging=="true":
                    xbmc.log("TV4User: URL WEG="+  url)
            if len(season)==1:
              season="0"+season
            if debuging=="true":
               xbmc.log("TV4User: URL="+  finalUrl)
            if finalUrl!="":
              content = opener.open(finalUrl).read()
              attachments = []
              titles = []            
              sprache = []            
              match=re.compile('<title>(.+?)-', re.DOTALL).findall(content)
              tvShowTitle=match[0].replace("[Untertitel]","").strip()              
              contentDE = content[content.find("<!-- Deutsche Untertitel -->")+1:]
              contentDE = contentDE[:contentDE.find("<!-- Englische Untertitel -->")]
              contentEN = content[content.find("<!-- Englische Untertitel -->")+1:]
              contentEN = contentEN[:contentEN.find("<!-- Copyright oder Subberinteresse -->")]
              if language=="0":
                tempDE=appendSubInfo(tvShowTitle,season,episode,release,contentDE,"DE")
                attachments += tempDE[0]
                titles += tempDE[1]
                sprache += tempDE[2]
                if contentEN!="":
                  tempEN=appendSubInfo(tvShowTitle,season,episode,release,contentEN,"EN")
                  attachments += tempEN[0]
                  titles += tempEN[1]
                  sprache += tempEN[2]
              elif language=="1":
                tempDE=appendSubInfo(tvShowTitle,season,episode,release,contentDE,"DE")
                attachments += tempDE[0]
                titles += tempDE[1]
                sprache += tempDE[2]
              elif language=="2" and contentEN!="":
                tempEN=appendSubInfo(tvShowTitle,season,episode,release,contentEN,"EN")
                attachments += tempEN[0]
                titles += tempEN[1]            
                sprache += tempEN[2]
              xbmc.log("XXX attachments: "+str(len(attachments)))
              xbmc.log("XXX sprache: "+str(len(sprache)))
              xbmc.log("XXX titles: "+str(len(titles)))
              if len(titles)>0:
                titles, attachments,sprache = (list(x) for x in zip(*sorted(zip(titles, attachments,sprache))))
                #titles, attachments = (list(x) for x in zip(*sorted(zip(titles, attachments))))
                xbmc.log("XXX titles: "+ str(len(attachments)))
                for i in range(0,len(titles),1):
                   addLink(titles[i], attachments[i], "getsub", "", "",lang=sprache[i])
                #iif nr>=0:
                #  subUrl=attachments[nr]
                #  setSubtitle(subUrl)
                #elif backNav=="true":
                #   main()
            else:
              xbmc.executebuiltin('XBMC.Notification(TV4User.de:,'+translation(30015)+'!,3000,'+icon+')')
              main()
          else:
              xbmc.executebuiltin('XBMC.Notification(TV4User.de:,'+translation(30015)+'!,3000,'+icon+')')
              main()
              
def Download(id,url,format,stack=False):
  subtitle_list = []
  return subtitle_list

def get_params(string=""):
    param=[]
    if string == "": paramstring=sys.argv[2]
    else:
        paramstring=string 
    if len(paramstring)>=2:
        params=paramstring
        cleanedparams=params.replace('?','')
        if (params[len(params)-1]=='/'): params=params[0:len(params)-2]
        pairsofparams=cleanedparams.split('&')
        param={}
        for i in range(len(pairsofparams)):
            splitparams={}
            splitparams=pairsofparams[i].split('=')
            if (len(splitparams))==2: param[splitparams[0]]=splitparams[1]
    return param
def addLink(name, url, mode, iconimage, duration="", desc="", genre='',lang=""):
	u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
	ok = True
	liz = xbmcgui.ListItem(label=lang,label2=name, iconImage=defaultThumb, thumbnailImage=iconimage)
	#liz.setInfo(type="Video", infoLabels={"Title": name, "Duration": duration, "Plot": desc, "Genre": genre})
	liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": desc, "Genre": genre})
	liz.setProperty('IsPlayable', 'true')
	liz.addStreamInfo('video', { 'duration' : duration })
	if useThumbAsFanart:
		if not iconimage or iconimage==icon or iconimage==defaultThumb:
			iconimage = defaultBackground
		liz.setProperty("fanart_image", iconimage)
	else:
		liz.setProperty("fanart_image", defaultBackground)
	#liz.addContextMenuItems([(translation(30012), 'RunPlugin(plugin://'+addonID+'/?mode=queueVideo&url='+urllib.quote_plus(u)+'&name='+urllib.quote_plus(name)+')',)])
	xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
	ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz)
	return ok
  
  
def addDir(name, url, mode, iconimage, desc=""):
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
  
def main():
      addDir("Suche","","search","","")
      xbmcplugin.endOfDirectory(addon_handle)
      
params=get_params()
if params['action'] == 'search' :
  search()
    



#xbmc.executebuiltin('runaddon(script.tv4user)')
