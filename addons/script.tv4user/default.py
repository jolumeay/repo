#!/usr/bin/python
# -*- coding: utf-8 -*-
import xbmc, xbmcgui, xbmcaddon, urllib, urllib2, socket, cookielib, re, os, shutil, base64, xbmcvfs,json

addon = xbmcaddon.Addon()
socket.setdefaulttimeout(60)
addonID = addon.getAddonInfo('id')
translation = addon.getLocalizedString
addonUserDataFolder=xbmc.translatePath("special://profile/addon_data/"+addonID)
subTempDir=xbmc.translatePath("special://profile/addon_data/"+addonID+"/srtTemp/")
icon = xbmc.translatePath('special://home/addons/'+addonID+'/icon.png')
rarFile=xbmc.translatePath(addonUserDataFolder+"/sub.")
subFile=xbmc.translatePath(addonUserDataFolder+"/sub.srt")
favFile=xbmc.translatePath(addonUserDataFolder+"/favourites")
apiKeyFile=xbmc.translatePath(addonUserDataFolder+"/api.key")



if not os.path.isdir(addonUserDataFolder):
  os.makedirs(addonUserDataFolder)
if not os.path.isdir(subTempDir):
  os.makedirs(subTempDir)

if os.path.exists(apiKeyFile):
  fh = open(apiKeyFile, 'r')
  ownKey = fh.read()
  fh.close()
else:
  ownKey=""

user=""
pw=""
backNav=""
pause=""
saveSub=""
language=""

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

getSettings()
if debuging=="true":
  xbmc.log("TV4User: pruefe ob Pause gesetzt werden soll")
if pause=="true" and xbmc.Player().isPlayingVideo():
  if debuging=="true":
    xbmc.log("TV4User: Video wird angehalten")
  xbmc.Player().pause()
if debuging=="true":
 xbmc.log("TV4User: Lese Playliste ein")
playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
if debuging=="true":
  xbmc.log("TV4User: Momentan spielt Video Nr: "+ str(playlist.getposition()) +" ab")
  xbmc.log("TV4User: Lese Titel des Videos ein")
if playlist.getposition()>=0:
  if debuging=="true":
    xbmc.log("TV4User: Lese Titel des Videos ein")
  currentTitle = playlist[playlist.getposition()].getdescription()

if debuging=="true":
  xbmc.log("TV4User: Lese Aktuelles VideoFile ein")
try:
  currentFile = xbmc.Player().getPlayingFile()
except:
    dialog = xbmcgui.Dialog()
    nr=dialog.select("TV4User.de", [translation(30109)])
    xbmc.log("TV4User: Es Leuft kein Video")  
    quit()
if debuging=="true":
  xbmc.log("TV4User: Logge ein")
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

def main():
        global mainType
        mainType = ""
        if debuging=="true":
          xbmc.log("TV4User: Starte Main")
          xbmc.log("TV4User: Zeige Auswahl an")
        dialog = xbmcgui.Dialog()
        nr=dialog.select("TV4User.de", [translation(30013),translation(30001),translation(30002),translation(30011)])
        if nr==0:
          search()
        elif nr==1:
          mainType="fav"
          showFavourites()
        elif nr==2:
          mainType="all"
          showAllSeries()
        elif nr==3:
          addon.openSettings()
          getSettings()
          main()
        else:
          if pause=="true" and xbmc.Player().isPlayingVideo():
            xbmc.Player().pause()

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
          general="AIzaSyB_OW0_DjRXdYB8tJgnvHL3_hr4DOmwXxU"
          global ownKey
          if ownKey=="":
            ownKey=general
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
                if contentEN!="":
                  tempEN=appendSubInfo(tvShowTitle,season,episode,release,contentEN,"EN")
                  attachments += tempEN[0]
                  titles += tempEN[1]
              elif language=="1":
                tempDE=appendSubInfo(tvShowTitle,season,episode,release,contentDE,"DE")
                attachments += tempDE[0]
                titles += tempDE[1]
              elif language=="2" and contentEN!="":
                tempEN=appendSubInfo(tvShowTitle,season,episode,release,contentEN,"EN")
                attachments += tempEN[0]
                titles += tempEN[1]            
              if len(titles)>0:
                titles, attachments = (list(x) for x in zip(*sorted(zip(titles, attachments))))
                dialog = xbmcgui.Dialog()
                nr=dialog.select(os.path.basename(currentFile), titles)
                if nr>=0:
                  subUrl=attachments[nr]
                  setSubtitle(subUrl)
                elif backNav=="true":
                   main()
            else:
              xbmc.executebuiltin('XBMC.Notification(TV4User.de:,'+translation(30015)+'!,3000,'+icon+')')
              main()
          else:
              xbmc.executebuiltin('XBMC.Notification(TV4User.de:,'+translation(30015)+'!,3000,'+icon+')')
              main()
          
def getEpisodes(entry):
        if debuging=="true":
          xbmc.log("TV4User: Starte GetEpisodes")
        ep=ep2=""
        match=re.compile('>E(.+?) -', re.DOTALL).findall(entry,0,10)
        match2=re.compile('>(.+?)x(.+?) -', re.DOTALL).findall(entry,0,10)
        match3=re.compile('>(.+?)\\. ', re.DOTALL).findall(entry,0,10)
        match4=re.compile('>(.+?) -', re.DOTALL).findall(entry,0,10)
        match5=re.compile('>(.+?)<', re.DOTALL).findall(entry,0,10)
        if "- komplett<" in entry.lower():
          ep=ep2=" - Komplett"
        else:
          if len(match)>0:
            ep=match[0]
          elif len(match2):
            ep=match2[0][1]
          elif len(match3):
            ep=match3[0]
          elif len(match4):
            ep=match4[0]
          elif len(match5):
            ep=match5[0]
          else:
            ep="00"
          ep2="E"+ep
        return [ep,ep2]

def appendSubInfo(tvShowTitle,season,episode,release,content,lang):
        if debuging=="true":
          xbmc.log("TV4User: AppendSubinfo:"+ episode)
        attachments1 = []
        titles1 = []    
        attachmentsold = []
        titlesolds= [] 
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
                   attach = []
                   title = []
                   attach.append(url)
                   ep2="E"+episode
                   title.append(lang+" - "+tvShowTitle+" - S"+season+ep2+" - "+ep)					 
                   attachments1=attachmentsold+attach
                   titles1=titlesolds+title
                   attachments1=attachmentsold+attach
               return [attachments1,titles1]			

        return ["",""]

def showFavourites():
        if debuging=="true":
          xbmc.log("TV4User: Starte ShowFavourites")
        ids = []
        titles = []
        counter = 0
        if os.path.exists(favFile):
          fh = open(favFile, 'r')
          for line in fh:
            id = line[:line.find("#")]
            title = line[line.find("#")+1:]
            title = title[:title.find("#END")]
            ids.append(id)
            titles.append(title)
            counter=counter+1
          fh.close()
        if (counter > 0):
         titles, ids = (list(x) for x in zip(*sorted(zip(titles, ids))))
         dialog = xbmcgui.Dialog()
         nr=dialog.select(translation(30001), titles)
         if nr>=0:
           id=ids[nr]
           title=titles[nr]
           showSeries(id)
         elif backNav=="true":
           main()
        else:
		  dialog2 = xbmcgui.Dialog()
		  nr=dialog2.select(translation(30108), [translation(30108)])
		  main()

def showAllSeries():
        if debuging=="true":
          xbmc.log("TV4User: Starte ShowAllSeries")
        content = opener.open(mainUrl+"/index.php").read()
        content = content[content.find('Alphabetische Serien-&Uuml;bersicht')+1:]
        content = content[:content.find('</form>')]
        match=re.compile('<option value="([0-9]+?)">([^<>]+?)</option>', re.DOTALL).findall(content)
        threadIDs = []
        threadNames = []
        for id, title in match:
          threadIDs.append(id)
          threadNames.append(title)
        dialog = xbmcgui.Dialog()
        nr=dialog.select(translation(30002), threadNames)
        if nr>=0:
          id=threadIDs[nr]
          title=threadNames[nr]
          showSeries(id)
        elif backNav=="true":
          main()

def showSeries(seriesID):
        if debuging=="true":
          xbmc.log("TV4User: Start showSeries")
        content = opener.open(mainUrl+"/serien/board"+seriesID+"-D.html").read()
        match=re.compile('<title>(.+?) -', re.DOTALL).findall(content)
        SeriesTitle=match[0]
        if debuging=="true":
             xbmc.log("TV4User: SeriesTitle:" + match[0])
        content = content[content.find('<div class="border borderMarginRemove" id="topThreadsStatus">'):]
        content = content[:content.find('<div class="contentFooter">')]
        spl=content.split('<div class="smallPages">')
        threadIDs = []
        threadNames = []
        season=currentSeason
        if season[0:1]=="0":
          season=season[1:]
        if debuging=="true":
           xbmc.log("TV4User: Start showSeries len(spl):"+ str(len(spl)))
        for i in range(1,len(spl)-1,1):
          entry=spl[i]
#          if debuging=="true":
#             xbmc.log("TV4User: entry "+ str(i) +" :" + entry)
          if 'http://board.tv4user.de/serien' in entry:
            match=re.compile('<a href="http://board.tv4user.de/serien([^\"]+?)">([^\<]+?)<\/a>', re.DOTALL).findall(entry)
            if debuging=="true":
              xbmc.log("TV4User: Start showSeries Thread:"+ match[0][0])
              xbmc.log("TV4User: Start showSeries Name:"+match[0][1])
            if ("staffel "+season in match[0][1].lower() or "staffel 0"+season in match[0][1].lower()) and "subs" in match[0][1].lower():
               threadIDs.append(match[0][0])
               threadNames.append(cleanTitle(match[0][1]))
               if debuging=="true":
                    xbmc.log("TV4User:  showSeries Added")
          if len(threadIDs)==0:
            for i in range(1,len(spl),1):
              entry=spl[i]
              if 'http://board.tv4user.de/serien' in entry:
               match=re.compile('<a href="http://board.tv4user.de/serien([^\"]+?)">([^\<]+?)<\/a>', re.DOTALL).findall(entry)
               if "subs" in match[0][1].lower():
                  threadIDs.append(match[0][0])
                  threadNames.append(cleanTitle(match[0][1]))			
        threadNames, threadIDs = (list(x) for x in zip(*sorted(zip(threadNames, threadIDs))))
        content=""
        if os.path.exists(favFile):
          fh = open(favFile, 'r')
          content=fh.read()
          fh.close()
        if seriesID+"#" not in content:
          threadNames.append(translation(30003))
        else:
          threadNames.append(translation(30004))
        dialog = xbmcgui.Dialog()
        nr=dialog.select(os.path.basename(currentFile), threadNames)
        if nr>=0:
          if nr==len(threadNames)-1:
            if threadNames[nr]==translation(30003):
              addToFavourites(seriesID,SeriesTitle)
            elif threadNames[nr]==translation(30004):
              removeFromFavourites(seriesID,SeriesTitle)
            showSeries(seriesID)
          else:
            id=threadIDs[nr]
            showSubtitles(seriesID,id)
        elif backNav=="true":
          if mainType=="all":
            showAllSeries()
          elif mainType=="fav":
            showFavourites()

def showSubtitles(seriesID,id):
    if debuging=="true":
       xbmc.log("TV4User: ShowSubtitles")
    attachments1 = []
    titles1 = []    
    attachmentsold = []
    titlesolds= [] 
    season=""
    if debuging=="true":
       xbmc.log("TV4User: ShowSubtitles URL: http://board.tv4user.de/serien"+id)
    content = opener.open("http://board.tv4user.de/serien"+id).read()
    if '<h2>Englische Untertitel</h2>' in content :
        old=0
    else:
        old=1	
    if debuging=="true":
       xbmc.log("TV4User: Alter Serie: "+str(old))		
    if old==0 :
      contentDE = content[content.find("<!-- Deutsche Untertitel -->")+1:]
      contentDE = contentDE[:contentDE.find("<h2>Englische Untertitel</h2>")]
      contentEN = content[content.find("<h2>Englische Untertitel</h2>")+1:]
      contentEN = contentEN[:contentEN.find("<!-- Footer -->")]
    if old==1 :
      contentDE = content[content.find('<span style="font-size: 14pt"><strong><span style="text-decoration: underline">Deutsche Untertitel:</span></strong>')+1:]
      contentDE = contentDE[:contentDE.find('<span style="font-size: 14pt"><strong><span style="text-decoration: underline">Englische Untertitel:</span></strong>')]
      contentEN = content[content.find('<span style="font-size: 14pt"><strong><span style="text-decoration: underline">Englische Untertitel:</span></strong>')+1:]
      contentEN = contentEN[:contentEN.find('<div class="containerIcon"><i class="taggingM css-sprite"></i></div>')]
    match=re.compile('<title>(.+?)-', re.DOTALL).findall(content)
    tvShowTitle1=match[0].replace("[Subs]","").strip()
    tvShowTitle=tvShowTitle1.replace("[Untertitel]","").strip()
    match=re.compile('Staffel (.+?) ', re.DOTALL).findall(content)
    if match:	   
          season=match[0]
          weg=0
    else: 
          weg=1
    if "webisode" in content.lower() :
       season="Webisodes"
       weg=0
    if debuging=="true":
       xbmc.log("TV4User: ShowSubtitles Season: "+season)
       xbmc.log("TV4User: ShowSubtitles WEG: "+str(weg))
    if old==0 :		                
      match=re.compile('<td class="nr">([^-]+?)-.+?<td class="episode">', re.DOTALL).findall(contentDE)		
    if old==1 :
       match=["Dummy"]
    for sepisode in match:
        if debuging=="true":
          xbmc.log("TV4User: ShowSubtitles Episode DE:"+ sepisode)
        if old==0 :
          contentFOLGE = contentDE[contentDE.find('<td class="nr">')+1:]
          contentFOLGE = contentFOLGE[:contentFOLGE.find('</tr>')]		   
          match2=re.compile('<a href="(.+?)">(.+?)</a>', re.DOTALL).findall(contentFOLGE)
        if old==1 :		                                                                                 
          match2=re.compile('<td width="[0-9]+?%" align="left">•&nbsp;<a href="([^\"]+?)">([^\<]+?)</a></td>', re.DOTALL).findall(contentDE)
        for url, ep in match2:
          if debuging=="true":
            xbmc.log("TV4User: showSubtitles: URL: "+ url)
            xbmc.log("TV4User: ShowSubtitles: EP: "+ ep)  
          if old==1 :          
              match3=re.compile('.+?\.S[0-9]+?E([0-9]+?)\..+?', re.DOTALL).findall(ep)
              if match3:
                 sepisode=match3[0]
                 if debuging=="true":
                    xbmc.log("TV4User: showSubtitles: Folge: "+ match3[0])		  
          if weg==0:
            attachmentsold=attachments1
            titlesolds=titles1
            attach = []
            title = []
            attach.append(url)
            ep2="E"+sepisode
            title.append("DE - "+tvShowTitle+" - S"+season+ep2+" - "+ep)					 
            attachments1=attachmentsold+attach
            titles1=titlesolds+title
            attachments1=attachmentsold+attach	
			
			
    if old==0 :		                
      match=re.compile('<td class="nr">([^-]+?)-.+?<td class="episode">', re.DOTALL).findall(contentEN)		
    if old==1 :
       match=["Dummy"]
    for sepisode in match:
        if debuging=="true":
          xbmc.log("TV4User: ShowSubtitles Episode EN:"+ sepisode)
        if old==0 :
          contentFOLGE = contentEN[contentEN.find('<td class="nr">')+1:]
          contentFOLGE = contentFOLGE[:contentFOLGE.find('</tr>')]		   
          match2=re.compile('<a href="(.+?)">(.+?)</a>', re.DOTALL).findall(contentFOLGE)
        if old==1 :		                                                                                 
          match2=re.compile('<td width="[0-9]+?%" align="left">•&nbsp;<a href="([^\"]+?)">([^\<]+?)</a></td>', re.DOTALL).findall(contentEN)
        for url, ep in match2:
          if debuging=="true":
            xbmc.log("TV4User: showSubtitles: URL: "+ url)
            xbmc.log("TV4User: ShowSubtitles: EP: "+ ep)  
          if old==1 :          
              match3=re.compile('.+?\.S[0-9]+?E([0-9]+?)\..+?', re.DOTALL).findall(ep)
              if match3:
                 sepisode=match3[0]
                 if debuging=="true":
                    xbmc.log("TV4User: showSubtitles: Folge: "+ match3[0])		  
          if weg==0:
            attachmentsold=attachments1
            titlesolds=titles1
            attach = []
            title = []
            attach.append(url)
            ep2="E"+sepisode
            title.append("EN - "+tvShowTitle+" - S"+season+ep2+" - "+ep)					 
            attachments1=attachmentsold+attach
            titles1=titlesolds+title
            attachments1=attachmentsold+attach	   
		  
    if len(titles1)>0:
        titles1, attachments1 = (list(x) for x in zip(*sorted(zip(titles1, attachments1))))
        dialog = xbmcgui.Dialog()
        nr=dialog.select(os.path.basename(currentFile), titles1)
        if nr>=0:
          subUrl=attachments1[nr]
          setSubtitle(subUrl)
        elif backNav=="true":
          showSeries(seriesID)

		
		
		
		
            
def setSubtitle(subUrl):
        if debuging=="true":
          xbmc.log("TV4User: Starte setSubtitle")
          xbmc.log("TV4User: setSubtitle: subUrl:" + subUrl)
        global subFile
        clearSubTempDir()
        rarContent = opener.open(subUrl).read()
        if rarContent.startswith("Rar"):
          ext="rar"
        else:
          ext="zip"
        if debuging=="true":
           xbmc.log("TV4User: SetSubtitle" + ext)
        global rarFile
        rarFile=rarFile+ext
        fh = open(rarFile, 'wb')
        fh.write(rarContent)
        fh.close()
        xbmc.executebuiltin("XBMC.Extract("+rarFile+", "+subTempDir+")",True)
        files = os.listdir(subTempDir)
        tempFile=""
        if len(files)>1:
          dialog = xbmcgui.Dialog()
          nr=dialog.select(currentTitle, files)
          if nr>=0:
            tempFile = xbmc.translatePath(subTempDir+"/"+files[nr])
          else:
            clearSubTempDir()
            if backNav=="true":
              main()
        elif len(files)!=0:
          tempFile = xbmc.translatePath(subTempDir+"/"+files[0])
        else:
          xbmc.executebuiltin('XBMC.Notification(TV4User.de:,'+translation(30017)+'!,3000,'+icon+')')
          if pause=="true" and xbmc.Player().isPlayingVideo():
            xbmc.Player().pause()
        if tempFile!="":
          shutil.copyfile(tempFile, subFile)
          if saveSub=="true" and "http://" not in currentFile and "plugin://" not in currentFile:
            try:
              extLength = len(currentFile.split(".")[-1])
              archiveFile = currentFile[:-extLength]+"srt"
              xbmcvfs.copy(tempFile, archiveFile)
              subFile = archiveFile
            except:
              pass
          clearSubTempDir()
          xbmc.Player().setSubtitles(subFile)
          xbmc.executebuiltin('XBMC.Notification(TV4User.de:,'+translation(30012)+'!,2000,'+icon+')')
          if pause=="true" and xbmc.Player().isPlayingVideo():
            xbmc.Player().pause()
          xbmc.executebuiltin("Back")
		

def clearSubTempDir():
        if debuging=="true":
          xbmc.log("TV4User: Starte clearSubTempdir")
        files = os.listdir(subTempDir)
        for file in files:
          try:
            os.remove(xbmc.translatePath(subTempDir+"/"+file))
          except:
            pass

def addToFavourites(seriesID,title):
        if debuging=="true":
          xbmc.log("TV4User: Starte addToFavourites")
        entry=seriesID+"#"+title+"#END"
        if os.path.exists(favFile):
          fh = open(favFile, 'r')
          content=fh.read()
          fh.close()
          if entry not in content:
            fh=open(favFile, 'a')
            fh.write(entry+"\n")
            fh.close()
            xbmc.executebuiltin('XBMC.Notification(TV4User.de:,'+title+': '+translation(30008)+',3000,'+icon+')')
        else:
          fh=open(favFile, 'a')
          fh.write(entry+"\n")
          fh.close()

def removeFromFavourites(seriesID,title):
        if debuging=="true":
          xbmc.log("TV4User: removeFromFavourites")
        newContent=""
        fh = open(favFile, 'r')
        for line in fh:
          if seriesID+"#" not in line:
             newContent+=line
        fh.close()
        fh=open(favFile, 'w')
        fh.write(newContent)
        fh.close()
        xbmc.executebuiltin('XBMC.Notification(TV4User.de:,'+title+': '+translation(30009)+',3000,'+icon+')')

def getUrl(url):
        if debuging=="true":
          xbmc.log("TV4User: Get Url")
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:23.0) Gecko/20100101 Firefox/23.0')
        response = urllib2.urlopen(req)
        content=response.read()
        response.close()
        return content

def cleanTitle(title):
        if debuging=="true":
          xbmc.log("TV4User: cleanTitle")
        title=title.replace("&lt;","<").replace("&gt;",">").replace("&amp;","&").replace("&#039;","'").replace("&quot;","\"").replace("&szlig;","ß").replace("&ndash;","-")
        title=title.replace("&Auml;","Ä").replace("&Uuml;","Ü").replace("&Ouml;","Ö").replace("&auml;","ä").replace("&uuml;","ü").replace("&ouml;","ö")
        title=title.strip()
        return title

main()
