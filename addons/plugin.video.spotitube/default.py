#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import re
import sys
import json
import shutil
import random
import socket
import urllib
import urllib2
import datetime
import xbmcplugin
import xbmcgui
import xbmcaddon
import xbmcvfs
import time
from operator import itemgetter
from datetime import date

#addon = xbmcaddon.Addon()
#addonID = addon.getAddonInfo('id')
addonID = 'plugin.video.spotitube'
addon = xbmcaddon.Addon(id=addonID)
pluginhandle = int(sys.argv[1])
socket.setdefaulttimeout(30)
opener = urllib2.build_opener()
xbox = xbmc.getCondVisibility("System.Platform.xbox")
region = xbmc.getLanguage(xbmc.ISO_639_1, region=True).split("-")[1]
icon = xbmc.translatePath('special://home/addons/'+addonID+'/icon.png')
addonUserDataFolder = xbmc.translatePath("special://profile/addon_data/"+addonID)
cacheDir = xbmc.translatePath(addon.getSetting("cacheDir"))
blacklist = addon.getSetting("blacklist").split(',')
infoEnabled = addon.getSetting("showInfo") == "true"
infoType = addon.getSetting("infoType")
infoDelay = int(addon.getSetting("infoDelay"))
infoDuration = int(addon.getSetting("infoDuration"))
forceView = addon.getSetting("forceView") == "true"
viewIDVideos = str(addon.getSetting("viewIDVideos"))
viewIDPlaylists = str(addon.getSetting("viewIDPlaylists"))
viewIDGenres = str(addon.getSetting("viewIDGenres"))
itunesShowSubGenres = addon.getSetting("itunesShowSubGenres") == "true"
itunesForceCountry = addon.getSetting("itunesForceCountry") == "true"
itunesCountry = addon.getSetting("itunesCountry")
spotifyForceCountry = addon.getSetting("spotifyForceCountry") == "true"
spotifyCountry = addon.getSetting("spotifyCountry")
youtubeAddonUrl = addon.getSetting("youtubeAddon")
youtubeAddonUrl = ["plugin://plugin.video.youtube/?path=/root/video&action=play_video&videoid=", "plugin://plugin.video.bromix.youtube/play/?video_id="][int(youtubeAddonUrl)]
userAgent = "Mozilla/5.0 (Windows NT 6.1; rv:30.0) Gecko/20100101 Firefox/30.0"
opener.addheaders = [('User-Agent', userAgent)]
urlMainBB = "http://www.billboard.com"
urlMainOC = "http://www.officialcharts.com"
urlMainBP = "https://www.beatport.com"
urlMainHypem = "http://hypem.com"
api_key = "AIzaSyCIM4EzNqi1in22f4Z3Ru3iYvLaY8tc3bo"
if itunesForceCountry and itunesCountry:
    iTunesRegion = itunesCountry
else:
    iTunesRegion = region
if spotifyForceCountry and spotifyCountry:
    spotifyRegion = spotifyCountry
else:
    spotifyRegion = region

if not os.path.isdir(addonUserDataFolder):
    os.mkdir(addonUserDataFolder)
if not cacheDir.startswith(('smb://', 'nfs://', 'upnp://', 'ftp://')) and not os.path.isdir(cacheDir):
    os.mkdir(cacheDir)

def index():
    addDir("Beatport", "", "bpMain", "")
    addDir("Billboard", "", "billboardMain", "")
    addDir("Hype Machine", "", "hypemMain", "")
    addDir(translation(30043), "", "itunesMain", "")
    addDir("Official Charts Company (UK)", "", "ocMain", "")
    addDir(translation(30044), "", "spotifyMain", "")
    xbmcplugin.endOfDirectory(pluginhandle)


def spotifyMain():
    addDir(translation(30041), "http://api.tunigo.com/v3/space/toplists?region="+spotifyRegion+"&page=0&per_page=50&platform=web", "listSpotifyPlaylists", "")
    addDir(translation(30042), "http://api.tunigo.com/v3/space/featured-playlists?region="+spotifyRegion+"&page=0&per_page=50&dt="+datetime.datetime.now().strftime("%Y-%m-%dT%H:%M").replace(":","%3A")+"%3A00&platform=web", "listSpotifyPlaylists", "")
    addDir(translation(30006), "http://api.tunigo.com/v3/space/genres?region="+spotifyRegion+"&per_page=1000&platform=web", "listSpotifyGenres", "")
    xbmcplugin.endOfDirectory(pluginhandle)


def hypemMain():
    addAutoPlayDir("Popular: Now", urlMainHypem+"/popular?ax=1&sortby=shuffle", 'listHypem', "", "", "browse")
    addAutoPlayDir("Popular: Last Week", urlMainHypem+"/popular/lastweek?ax=1&sortby=shuffle", 'listHypem', "", "", "browse")
    addAutoPlayDir("Time Machine", "", 'listTimeMachine', "", "", "browse")
    xbmcplugin.endOfDirectory(pluginhandle)


def ocMain():
    addAutoPlayDir("Official", urlMainOC+"/singles-chart/", "listOC", "", "", "browse")
    addAutoPlayDir("Sales", urlMainOC+"/singles-sales-chart/", "listOC", "", "", "browse")
    addAutoPlayDir("Downloads", urlMainOC+"/singles-download-chart/", "listOC", "", "", "browse")
    addAutoPlayDir("Streaming", urlMainOC+"/official-audio-streaming-chart/", "listOC", "", "", "browse")
    addAutoPlayDir("Classical", urlMainOC+"/official-classical-singles-chart/", "listOC", "", "", "browse")
    addAutoPlayDir("Rock & Metal", urlMainOC+"/rock-and-metal-singles-chart/", "listOC", "", "", "browse")
    addAutoPlayDir("Independent", urlMainOC+"/independent-singles-chart/", "listOC", "", "", "browse")
    #addAutoPlayDir("Catalogue", urlMainOC+"/catalogue-singles-chart/", "listOC", "", "", "browse")
    addAutoPlayDir("R&B", urlMainOC+"/r-and-b-singles-chart/", "listOC", "", "", "browse")
    addAutoPlayDir("Dance", urlMainOC+"/dance-singles-chart/", "listOC", "", "", "browse")
    addAutoPlayDir("Asian", urlMainOC+"/asian-chart/", "listOC", "", "", "browse")
    #addAutoPlayDir("Scottish", urlMainOC+"/scottish-singles-chart/", "listOC", "", "", "browse")
    xbmcplugin.endOfDirectory(pluginhandle)


def bpMain():
    addAutoPlayDir("All Genres", urlMainBP+"/top-100", "listBP", "", "", "browse")
    content = cache('https://pro.beatport.com', 30)
    match=re.findall('"genre-drop-list-item">.*?<a href="(.*?)">(.*?)</a>',content,re.S)
    for genreID, title in match:
		print genreID
		print title
		title = cleanTitle(title)
		url='https://pro.beatport.com%s/top-100' % genreID
		addAutoPlayDir(title,url, "listBP", "", "", "browse")
    xbmcplugin.endOfDirectory(pluginhandle)


def itunesMain():
    content = cache("https://itunes.apple.com/"+iTunesRegion+"/genre/music/id34", 30)
    content = content[content.find('id="genre-nav"'):]
    content = content[:content.find('</div>')]
    match=re.compile('<li><a href="https://itunes.apple.com/.+?/genre/.+?/id(.+?)"(.+?)title=".+?">(.+?)<', re.DOTALL).findall(content)
    title = "All Genres"
    if itunesShowSubGenres:
        title = '[B]'+title+'[/B]'
    addAutoPlayDir(title, "0", "listItunesVideos", "", "", "browse")
    for genreID, type, title in match:
        title = cleanTitle(title)
        if 'class="top-level-genre"' in type:
            if itunesShowSubGenres:
                title = '[B]'+title+'[/B]'
            addAutoPlayDir(title, genreID, "listItunesVideos", "", "", "browse")
        elif itunesShowSubGenres:
            title = '   '+title
            addAutoPlayDir(title, genreID, "listItunesVideos", "", "", "browse")
    xbmcplugin.endOfDirectory(pluginhandle)


def billboardMain():
    addAutoPlayDir(translation(30005), urlMainBB+"/rss/charts/hot-100", "listBillboardCharts", "", "", "browse")
    addAutoPlayDir("Trending 140", "Top 140 in Trending", "listBillboardChartsNew", "", "", "browse")
    addAutoPlayDir("Last 24 Hours", "Top 140 in Overall", "listBillboardChartsNew", "", "", "browse")
    #addDir("Archive", "", "listBillboardArchiveMain", "", "", "browse")
    addDir(translation(30006), "genre", "listBillboardChartsTypes", "", "", "browse")
    addDir(translation(30007), "country", "listBillboardChartsTypes", "", "", "browse")
    addDir(translation(30008), "other", "listBillboardChartsTypes", "", "", "browse")
    xbmcplugin.endOfDirectory(pluginhandle)


def listBillboardArchiveMain():
    for i in range(date.today().year,1957,-1):
        addAutoPlayDir(str(i), urlMainBB+"/archive/charts/"+str(i), "listBillboardArchive", "", "", "browse")
    xbmcplugin.endOfDirectory(pluginhandle)
    
    
def listBillboardArchive(url):
    content = cache(url, 30)
    match=re.compile('class="field-content">.+?href="(.+?)">(.+?)<', re.DOTALL).findall(content)
    for url, title in match:
        if not "billboard 200" in title.lower() and not "album" in title.lower():
            addAutoPlayDir(cleanTitle(title), urlMainBB+url, "listBillboardArchiveVideos", "", "", "browse")
    xbmcplugin.endOfDirectory(pluginhandle)
    
    
def listBillboardArchiveVideos(type, url, limit):
    if type=="play":
        musicVideos = []
        playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
        playlist.clear()
    content = cache(url, 30)
    match=re.compile('views-field-field-chart-item-song.+?>(.+?)<.+?href="/artist/.+?">(.+?)<', re.DOTALL).findall(content)
    pos = 1
    for title, artist in match:
        title = title.strip()
        if title.lower()!="song":
            title = cleanTitle(artist+" - "+title)
            filtered = False
            for entry2 in blacklist:
                if entry2.strip().lower() and entry2.strip().lower() in title.lower():
                    filtered = True
            if filtered:
                continue
            if type=="browse":
                addLink(title, title.replace(" - ", " "), "playYTByTitle", "")
            else:
                if xbox:
                    url = "plugin://video/Youtube Music/?url="+urllib.quote_plus(title.replace(" - ", " "))+"&mode=playYTByTitle"
                else:
                    url = "plugin://"+addonID+"/?url="+urllib.quote_plus(title.replace(" - ", " "))+"&mode=playYTByTitle"
                    print 'ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff'+url
                musicVideos.append([title, url, ""])
                if limit and int(limit)==pos:
                    break
                pos+=1
    if type=="browse":
        xbmcplugin.endOfDirectory(pluginhandle)
    else:
        random.shuffle(musicVideos)
        for title, url, thumb in musicVideos:
            listitem = xbmcgui.ListItem(title, thumbnailImage=thumb)
            playlist.add(url, listitem)
        xbmc.Player().play(playlist)
    
    
def listBillboardChartsTypes(type):
    if type=="genre":
        addAutoPlayDir(translation(30009), urlMainBB+"/rss/charts/pop-songs", "listBillboardCharts", "", "", "browse")
        addAutoPlayDir(translation(30010), urlMainBB+"/rss/charts/rock-songs", "listBillboardCharts", "", "", "browse")
        addAutoPlayDir(translation(30011), urlMainBB+"/rss/charts/alternative-songs", "listBillboardCharts", "", "", "browse")
        addAutoPlayDir(translation(30012), urlMainBB+"/rss/charts/r-b-hip-hop-songs", "listBillboardCharts", "", "", "browse")
        addAutoPlayDir(translation(30013), urlMainBB+"/rss/charts/r-and-b-songs", "listBillboardCharts", "", "", "browse")
        addAutoPlayDir(translation(30014), urlMainBB+"/rss/charts/rap-songs", "listBillboardCharts", "", "", "browse")
        addAutoPlayDir(translation(30015), urlMainBB+"/rss/charts/country-songs", "listBillboardCharts", "", "", "browse")
        addAutoPlayDir(translation(30016), urlMainBB+"/rss/charts/latin-songs", "listBillboardCharts", "", "", "browse")
        addAutoPlayDir(translation(30017), urlMainBB+"/rss/charts/jazz-songs", "listBillboardCharts", "", "", "browse")
        addAutoPlayDir(translation(30018), urlMainBB+"/rss/charts/dance-club-play-songs", "listBillboardCharts", "", "", "browse")
        addAutoPlayDir(translation(30019), urlMainBB+"/rss/charts/dance-electronic-songs", "listBillboardCharts", "", "", "browse")
        addAutoPlayDir(translation(30020), urlMainBB+"/rss/charts/heatseekers-songs", "listBillboardCharts", "", "", "browse")
    elif type=="country":
        addAutoPlayDir(translation(30021), urlMainBB+"/rss/charts/canadian-hot-100", "listBillboardCharts", "", "", "browse")
        addAutoPlayDir(translation(30022), urlMainBB+"/rss/charts/k-pop-hot-100", "listBillboardCharts", "", "", "browse")
        addAutoPlayDir(translation(30023), urlMainBB+"/rss/charts/japan-hot-100", "listBillboardCharts", "", "", "browse")
        addAutoPlayDir(translation(30024), urlMainBB+"/rss/charts/germany-songs", "listBillboardCharts", "", "", "browse")
        addAutoPlayDir(translation(30025), urlMainBB+"/rss/charts/france-songs", "listBillboardCharts", "", "", "browse")
        addAutoPlayDir(translation(30026), urlMainBB+"/rss/charts/united-kingdom-songs", "listBillboardCharts", "", "", "browse")
    elif type=="other":
        addAutoPlayDir(translation(30028), urlMainBB+"/rss/charts/radio-songs", "listBillboardCharts", "", "", "browse")
        addAutoPlayDir(translation(30029), urlMainBB+"/rss/charts/digital-songs", "listBillboardCharts", "", "", "browse")
        addAutoPlayDir(translation(30030), urlMainBB+"/rss/charts/streaming-songs", "listBillboardCharts", "", "", "browse")
        addAutoPlayDir(translation(30031), urlMainBB+"/rss/charts/on-demand-songs", "listBillboardCharts", "", "", "browse")
    xbmcplugin.endOfDirectory(pluginhandle)


def listHypem(type, url, limit):
    musicVideos = []
    if type=="play":
        playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
        playlist.clear()
    parentUrl = url
    if url==urlMainHypem+"/popular?ax=1&sortby=shuffle":
        content = cache(url, 0)
    else:
        content = cache(url, 1)
    match = re.compile('class="rank">(.+?)<.+?href="/artist/.+?">(.+?)<.+?class="base-title">(.+?)<', re.DOTALL).findall(content)
    spl=content.split('class="rank"')
    for i in range(1,len(spl),1):
        entry=spl[i]
        match=re.compile('>(.+?)<', re.DOTALL).findall(entry)
        rank=match[0]
        artist=re.findall('href=".*?">(.*?)</a>',entry,re.S)[0]
        match=re.compile('class="base-title">(.+?)<', re.DOTALL).findall(entry)
        title=match[0]
        match=re.compile('class="remix-link">(.+?)<', re.DOTALL).findall(entry)
        if match:
            title+=" - "+match[0]
        match=re.compile('class="thumb".+?background:url\\((.+?)\\)', re.DOTALL).findall(entry)
        thumb = ""
        if match:
            thumb=match[0]
        title = cleanTitle(artist.strip()+" - "+title.strip())
        oTitle = title
        '''match=re.compile('class="toggle-reposts">(.+?)<', re.DOTALL).findall(entry)
        if match:
            reposts = match[0]
            reposts = reposts.replace("Posted by","").replace("blogs","").strip()
            title+=" ["+reposts+"+]"'''
        filtered = False
        for entry2 in blacklist:
            if entry2.strip().lower() and entry2.strip().lower() in title.lower():
                filtered = True
        if filtered:
            continue
        if type=="play":
            if xbox:
                url = "plugin://video/Youtube Music/?url="+urllib.quote_plus(oTitle.replace(" - ", " "))+"&mode=playYTByTitle"
            else:
                url = "plugin://"+addonID+"/?url="+urllib.quote_plus(oTitle.replace(" - ", " "))+"&mode=playYTByTitle"
        else:
            url = oTitle
        musicVideos.append([int(rank), title, url, thumb])
    musicVideos = sorted(musicVideos, key=itemgetter(0))
    if type=="browse":
        for rank, title, url, thumb in musicVideos:
            addLink(title, url.replace(" - ", " "), "playYTByTitle", "")
        xbmcplugin.endOfDirectory(pluginhandle)
    else:
        if limit:
            musicVideos = musicVideos[:int(limit)]
        random.shuffle(musicVideos)
        for rank, title, url, thumb in musicVideos:
            listitem = xbmcgui.ListItem(title, thumbnailImage=thumb)
            playlist.add(url, listitem)
        xbmc.Player().play(playlist)


def listTimeMachine():
    for i in range(1, 210, 1):
        dt = datetime.date.today()
        while dt.weekday()!=0:
            dt -= datetime.timedelta(days=1)
        dt -= datetime.timedelta(weeks=i)
        months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
        month = months[int(dt.strftime("%m"))-1]
        addAutoPlayDir(dt.strftime("%b %d, %Y"), urlMainHypem+"/popular/week:"+month+"-"+dt.strftime("%d-%Y")+"?ax=1&sortby=shuffle", 'listHypem', "", "", "browse")
    xbmcplugin.endOfDirectory(pluginhandle)


def listSpotifyGenres(url):
    content = cache(url, 30)
    content = json.loads(content)
    for item in content['items']:
        genreID = item['genre']['templateName']
        try:
            thumb = item['genre']['iconImageUrl']
        except:
            thumb = ""
        title = item['genre']['name'].encode('utf-8')
        if title.strip().lower()!="top lists":
            addDir(title, "http://api.tunigo.com/v3/space/"+genreID+"?region="+spotifyRegion+"&page=0&per_page=50&platform=web", "listSpotifyPlaylists", thumb)
    xbmcplugin.endOfDirectory(pluginhandle)
    if forceView:
        xbmc.executebuiltin('Container.SetViewMode('+viewIDGenres+')')


def listSpotifyPlaylists(url):
    content = cache(url, 1)
    content = json.loads(content)
    for item in content['items']:
        uri = item['playlist']['uri'].encode('utf-8')
        try:
            thumb = "http://d3rt1990lpmkn.cloudfront.net/300/"+item['playlist']['image']
        except:
            thumb = ""
        title = item['playlist']['title'].encode('utf-8')
        description = item['playlist']['description'].encode('utf-8')
        addAutoPlayDir(title, uri, "listSpotifyVideos", thumb, description, "browse")
    match=re.compile('page=(.+?)&per_page=(.+?)&', re.DOTALL).findall(url)
    currentPage = int(match[0][0])
    perPage = int(match[0][1])
    nextPage = currentPage+1
    if nextPage*perPage<content['totalItems']:
        addDir(translation(30001), url.replace("page="+str(currentPage),"page="+str(nextPage)), "listSpotifyPlaylists", "")
    xbmcplugin.endOfDirectory(pluginhandle)
    if forceView:
        xbmc.executebuiltin('Container.SetViewMode('+viewIDPlaylists+')')


def listSpotifyVideos(type, url, limit):
    if type=="play":
        musicVideos = []
        playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
        playlist.clear()
    content = cache("https://embed.spotify.com/?uri="+url, 1)
    spl=content.split('music-paused item')
    pos = 1
    for i in range(1,len(spl),1):
        entry=spl[i]
        match=re.compile('class="artist.+?>(.+?)<', re.DOTALL).findall(entry)
        artist=match[0]
        match=re.compile('class="track-title.+?>(.+?)<', re.DOTALL).findall(entry)
        videoTitle=match[0]
        videoTitle=videoTitle[videoTitle.find(".")+1:].strip()
        if " - " in videoTitle:
            videoTitle=videoTitle[:videoTitle.rfind(" - ")]
        if " [" in videoTitle:
            videoTitle=videoTitle[:videoTitle.rfind(" [")]
        if "," in artist:
            artist = artist.split(",")[0]
        title=cleanTitle(artist+" - "+videoTitle)
        match=re.compile('data-ca="(.+?)"', re.DOTALL).findall(entry)
        thumb=match[0]
        filtered = False
        for entry2 in blacklist:
            if entry2.strip().lower() and entry2.strip().lower() in title.lower():
                filtered = True
        if filtered:
            continue
        if type=="browse":
            addLink(title, title.replace(" - ", " "), "playYTByTitle", thumb)
        else:
            if xbox:
                url = "plugin://video/Youtube Music/?url="+urllib.quote_plus(title.replace(" - ", " "))+"&mode=playYTByTitle"
            else:
                url = "plugin://"+addonID+"/?url="+urllib.quote_plus(title.replace(" - ", " "))+"&mode=playYTByTitle"
            musicVideos.append([title, url, thumb])
            if limit and int(limit)==pos:
                break
            pos+=1
    if type=="browse":
        xbmcplugin.endOfDirectory(pluginhandle)
        if forceView:
            xbmc.executebuiltin('Container.SetViewMode('+viewIDVideos+')')
    else:
        random.shuffle(musicVideos)
        for title, url, thumb in musicVideos:
            listitem = xbmcgui.ListItem(title, thumbnailImage=thumb)
            playlist.add(url, listitem)
        xbmc.Player().play(playlist)


def listOC(type, url, limit):
    if type=="play":
        musicVideos = []
        playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
        playlist.clear()
    content = cache(url, 1)
    spl=content.split('class="track')
    pos = 1
    for i in range(1,len(spl),1):
        entry=spl[i]
        artist=re.findall('<a href=".*?">(.*?)</a>',entry,re.S)[1]
        videoTitle=re.findall('<a href=".*?">(.*?)</a>',entry,re.S)[0]
        if " FT " in artist:
            artist=artist[:artist.find(" FT ")].strip()
        if "/" in artist:
            artist=artist[:artist.find("/")].strip()
        if "&amp;" in artist:
            artist=artist[:artist.find("&amp;")].strip()
        title=cleanTitle(artist+" - "+videoTitle)
        match=re.compile('src="(.+?)"', re.DOTALL).findall(entry)
        thumb=match[0].replace("_50.jpg","_500.jpg")
        filtered = False
        for entry2 in blacklist:
            if entry2.strip().lower() and entry2.strip().lower() in title.lower():
                filtered = True
        if filtered:
            continue
        if type=="browse":
            addLink(title, title.replace(" - ", " "), "playYTByTitle", thumb)
        else:
            if xbox:
                url = "plugin://video/Youtube Music/?url="+urllib.quote_plus(title.replace(" - ", " "))+"&mode=playYTByTitle"
            else:
                url = "plugin://"+addonID+"/?url="+urllib.quote_plus(title.replace(" - ", " "))+"&mode=playYTByTitle"
                print 'ffffffffffffffffffffffffffffffffffffffff'+url
            musicVideos.append([title, url, thumb])
            if limit and int(limit)==pos:
                break
            pos+=1
    if type=="browse":
        xbmcplugin.endOfDirectory(pluginhandle)
        if forceView:
            xbmc.executebuiltin('Container.SetViewMode('+viewIDVideos+')')
    else:
        random.shuffle(musicVideos)
        for title, url, thumb in musicVideos:
            listitem = xbmcgui.ListItem(title, thumbnailImage=thumb)
            playlist.add(url, listitem)
        xbmc.Player().play(playlist)


def listBP(type, url, limit):
    if type=="play":
        musicVideos = []
        playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
        playlist.clear()
    content = cache(url, 1)
    spl=content.split('"bucket-item track"')
    pos = 1
    for i in range(1,len(spl),1):
        entry=spl[i]
        artist=re.findall('data-artist=".*?">(.*?)</a>',entry,re.S)[0]
        videoTitle=re.findall('title="(.*?)"',entry,re.S)[0]
        if "(Original Mix)" in videoTitle:
            videoTitle=videoTitle[:videoTitle.find("(Original Mix)")].strip()
        if "feat" in videoTitle:
            videoTitle=videoTitle[:videoTitle.find("feat")].strip()
        title=cleanTitle(artist+" - "+videoTitle)
        thumb=re.findall('data-src="(.*?)"',entry,re.S)[0].replace("/95x95/","/500x500/")
        filtered = False
        for entry2 in blacklist:
            if entry2.strip().lower() and entry2.strip().lower() in title.lower():
                filtered = True
        if filtered:
            continue
        if type=="browse":
            addLink(title, title.replace(" - ", " "), "playYTByTitle", thumb)
        else:
            if xbox:
                url = "plugin://video/Youtube Music/?url="+urllib.quote_plus(title.replace(" - ", " "))+"&mode=playYTByTitle"
            else:
                url = "plugin://"+addonID+"/?url="+urllib.quote_plus(title.replace(" - ", " "))+"&mode=playYTByTitle"
            musicVideos.append([title, url, thumb])
            if limit and int(limit)==pos:
                break
            pos+=1
    if type=="browse":
        xbmcplugin.endOfDirectory(pluginhandle)
        if forceView:
            xbmc.executebuiltin('Container.SetViewMode('+viewIDVideos+')')
    else:
        random.shuffle(musicVideos)
        for title, url, thumb in musicVideos:
            listitem = xbmcgui.ListItem(title, thumbnailImage=thumb)
            playlist.add(url, listitem)
        xbmc.Player().play(playlist)


def listItunesVideos(type, genreID, limit):
    if type=="play":
        musicVideos = []
        playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
        playlist.clear()
    url = "https://itunes.apple.com/"+iTunesRegion+"/rss/topsongs/limit=100"
    if genreID!="0":
        url += "/genre="+genreID
    url += "/explicit=true/json"
    content = cache(url, 1)
    content = json.loads(content)
    pos = 1
    for item in content['feed']['entry']:
        artist=item['im:artist']['label'].encode('utf-8')
        videoTitle=item['im:name']['label'].encode('utf-8')
        if " (" in videoTitle:
            videoTitle=videoTitle[:videoTitle.rfind(" (")]
        title=cleanTitle(artist+" - "+videoTitle)
        try:
            thumb=item['im:image'][2]['label'].replace("170x170-75.jpg","400x400-75.jpg")
        except:
            thumb=""
        filtered = False
        for entry2 in blacklist:
            if entry2.strip().lower() and entry2.strip().lower() in title.lower():
                filtered = True
        if filtered:
            continue
        if type=="browse":
            addLink(title, title.replace(" - ", " "), "playYTByTitle", thumb)
        else:
            if xbox:
                url = "plugin://video/Youtube Music/?url="+urllib.quote_plus(title.replace(" - ", " "))+"&mode=playYTByTitle"
            else:
                url = "plugin://"+addonID+"/?url="+urllib.quote_plus(title.replace(" - ", " "))+"&mode=playYTByTitle"
            musicVideos.append([title, url, thumb])
            if limit and int(limit)==pos:
                break
            pos+=1
    if type=="browse":
        xbmcplugin.endOfDirectory(pluginhandle)
        if forceView:
            xbmc.executebuiltin('Container.SetViewMode('+viewIDVideos+')')
    else:
        random.shuffle(musicVideos)
        for title, url, thumb in musicVideos:
            listitem = xbmcgui.ListItem(title, thumbnailImage=thumb)
            playlist.add(url, listitem)
        xbmc.Player().play(playlist)

        
def listBillboardCharts(type, url, limit):
    if type=="play":
        musicVideos = []
        playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
        playlist.clear()
    content = cache(url, 1)
    match = re.compile('<item>.+?<artist>(.+?)</artist>.+?<chart_item_title>(.+?)</chart_item_title>', re.DOTALL).findall(content)
    pos = 1
    for artist, title in match:
        title = cleanTitle(artist+" - "+title[title.find(":")+1:]).replace("Featuring", "Feat.")
        if type=="browse":
            addLink(title, title.replace(" - ", " "), "playYTByTitle", "")
        else:
            if xbox:
                url = "plugin://video/Youtube Music/?url="+urllib.quote_plus(title.replace(" - ", " "))+"&mode=playYTByTitle"
            else:
                url = "plugin://"+addonID+"/?url="+urllib.quote_plus(title.replace(" - ", " "))+"&mode=playYTByTitle"
            musicVideos.append([title, url, ""])
            if limit and int(limit)==pos:
                break
            pos+=1
    if type=="browse":
        xbmcplugin.endOfDirectory(pluginhandle)
    else:
        random.shuffle(musicVideos)
        for title, url, thumb in musicVideos:
            listitem = xbmcgui.ListItem(title, thumbnailImage=thumb)
            playlist.add(url, listitem)
        xbmc.Player().play(playlist)


def listBillboardChartsNew(type, url, limit):
    if type=="play":
        musicVideos = []
        playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
        playlist.clear()
    content = opener.open("http://realtime.billboard.com/").read()
    content = content[content.find("<h1>"+url+"</h1>"):]
    content = content[:content.find("</table>")]
    match = re.compile('<tr>.*?<td>(.+?)</td>.*?<td><a href=".*?">(.+?)</a></td>.*?<td>(.+?)</td>.*?<td>(.+?)</td>.*?</tr>', re.DOTALL).findall(content)
    pos = 1
    for nr, artist, title, rating in match:
        if "(" in title:
            title = title[:title.find("(")].strip()
        title = cleanTitle(artist+" - "+title).replace("Featuring", "Feat.")
        if type=="browse":
            addLink(title, title.replace(" - ", " "), "playYTByTitle", "")
        else:
            if xbox:
                url = "plugin://video/Youtube Music/?url="+urllib.quote_plus(title.replace(" - ", " "))+"&mode=playYTByTitle"
            else:
                url = "plugin://"+addonID+"/?url="+urllib.quote_plus(title.replace(" - ", " "))+"&mode=playYTByTitle"
            musicVideos.append([title, url, ""])
            if limit and int(limit)==pos:
                break
            pos+=1
    if type=="browse":
        xbmcplugin.endOfDirectory(pluginhandle)
    else:
        random.shuffle(musicVideos)
        for title, url, thumb in musicVideos:
            listitem = xbmcgui.ListItem(title, thumbnailImage=thumb)
            playlist.add(url, listitem)
        xbmc.Player().play(playlist)


def playYTByTitle(title):
    try:
        youtubeID = getYoutubeId(title)
        if xbox:
            url = "plugin://video/YouTube/?path=/root/video&action=play_video&videoid=" + youtubeID
        else:
            url = youtubeAddonUrl + youtubeID
        listitem = xbmcgui.ListItem(path=url)
        xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)
        if infoEnabled:
            showInfo()
    except:
        pass


def getYoutubeId(title):
	title=urllib.quote_plus(title.lower())
	content = cache("https://www.googleapis.com/youtube/v3/search?part=snippet&max-results=1&order=relevance&q=%s&key=%s"% (title,api_key), 1)
	video_id=re.findall('"videoId": "(.*?)"',content,re.S)[0]
	return video_id


def queueVideo(url, name):
    playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
    listitem = xbmcgui.ListItem(name)
    playlist.add(url, listitem)        


def cache(url, duration):
    cacheFile = os.path.join(cacheDir, (''.join(c for c in unicode(url, 'utf-8') if c not in '/\\:?"*|<>')).strip())
    if os.path.exists(cacheFile) and duration!=0 and (time.time()-os.path.getmtime(cacheFile) < 60*60*24*duration):
        fh = open(cacheFile, 'r')
        content = fh.read()
        fh.close()
    else:
        content = opener.open(url).read()
        fh = open(cacheFile, 'w')
        fh.write(content)
        fh.close()
    return content


def showInfo():
    count = 0
    while not xbmc.Player().isPlaying():
        xbmc.sleep(200)
        if count==50:
            break
        count+=1
    xbmc.sleep(infoDelay*1000)
    if infoType == "0":
        xbmc.executebuiltin('XBMC.ActivateWindow(12901)')
        xbmc.sleep(infoDuration*1000)
        xbmc.executebuiltin('XBMC.ActivateWindow(12005)')
    elif infoType == "1":
        title = 'Now playing:'
        videoTitle = xbmc.getInfoLabel('VideoPlayer.Title').replace(","," ")
        thumb = xbmc.getInfoImage('VideoPlayer.Cover')
        xbmc.executebuiltin('XBMC.Notification(%s, %s, %s, %s)' % (title, videoTitle, infoDuration*1000, thumb))


def translation(id):
    return addon.getLocalizedString(id).encode('utf-8')


def cleanTitle(title):
    title = title.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&").replace("&#39;", "'").replace("&#039;", "'").replace("&quot;", "\"").replace("&szlig;", "ß").replace("&ndash;", "-")
    title = title.replace("&Auml;", "Ä").replace("&Uuml;", "Ü").replace("&Ouml;", "Ö").replace("&auml;", "ä").replace("&uuml;", "ü").replace("&ouml;", "ö")
    title = title.strip()
    return title


def parameters_string_to_dict(parameters):
    paramDict = {}
    if parameters:
        paramPairs = parameters[1:].split("&")
        for paramsPair in paramPairs:
            paramSplits = paramsPair.split('=')
            if (len(paramSplits)) == 2:
                paramDict[paramSplits[0]] = paramSplits[1]
    return paramDict


def addLink(name, url, mode, iconimage):
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultAudio.png", thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name})
    liz.setProperty('IsPlayable', 'true')
    entries = []
    entries.append((translation(30004), 'RunPlugin(plugin://'+addonID+'/?mode=queueVideo&url='+urllib.quote_plus(u)+'&name='+urllib.quote_plus(name)+')',))
    liz.addContextMenuItems(entries)
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz)
    return ok

def addDir(name, url, mode, iconimage="", description="", type="", limit=""):
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&type="+str(type)+"&limit="+str(limit)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultMusicVideos.png", thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": description})
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok

def addAutoPlayDir(name, url, mode, iconimage="", description="", type="", limit=""):
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&type="+str(type)+"&limit="+str(limit)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultMusicVideos.png", thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": description})
    entries = []
    entries.append(("Autoplay All", 'RunPlugin(plugin://'+addonID+'/?mode='+str(mode)+'&url='+urllib.quote_plus(url)+'&type=play&limit=)',))
    entries.append(("Autoplay Top10", 'RunPlugin(plugin://'+addonID+'/?mode='+str(mode)+'&url='+urllib.quote_plus(url)+'&type=play&limit=10)',))
    entries.append(("Autoplay Top20", 'RunPlugin(plugin://'+addonID+'/?mode='+str(mode)+'&url='+urllib.quote_plus(url)+'&type=play&limit=20)',))
    entries.append(("Autoplay Top30", 'RunPlugin(plugin://'+addonID+'/?mode='+str(mode)+'&url='+urllib.quote_plus(url)+'&type=play&limit=30)',))
    entries.append(("Autoplay Top40", 'RunPlugin(plugin://'+addonID+'/?mode='+str(mode)+'&url='+urllib.quote_plus(url)+'&type=play&limit=40)',))
    entries.append(("Autoplay Top50", 'RunPlugin(plugin://'+addonID+'/?mode='+str(mode)+'&url='+urllib.quote_plus(url)+'&type=play&limit=50)',))
    liz.addContextMenuItems(entries)
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok

params = parameters_string_to_dict(sys.argv[2])
mode = urllib.unquote_plus(params.get('mode', ''))
url = urllib.unquote_plus(params.get('url', ''))
name = urllib.unquote_plus(params.get('name', ''))
type = urllib.unquote_plus(params.get('type', ''))
limit = urllib.unquote_plus(params.get('limit', ''))
chartTitle = urllib.unquote_plus(params.get('chartTitle', ''))

if mode == 'playYTByTitle':
    playYTByTitle(url)
elif mode == 'playYTByTitle':
    playYTByTitle(url)
elif mode == 'spotifyMain':
    spotifyMain()
elif mode == 'itunesMain':
    itunesMain()
elif mode == 'billboardMain':
    billboardMain()
elif mode == 'listBillboardArchiveMain':
    listBillboardArchiveMain()
elif mode == 'ocMain':
    ocMain()
elif mode == 'bpMain':
    bpMain()
elif mode == 'hypemMain':
    hypemMain()
elif mode == 'listOC':
    listOC(type, url, limit)
elif mode == 'listBP':
    listBP(type, url, limit)
elif mode == 'listHypem':
    listHypem(type, url, limit)
elif mode == 'listTimeMachine':
    listTimeMachine()
elif mode == 'listSpotifyGenres':
    listSpotifyGenres(url)
elif mode == 'listSpotifyPlaylists':
    listSpotifyPlaylists(url)
elif mode == 'listSpotifyVideos':
    listSpotifyVideos(type, url, limit)
elif mode == 'playSpotifyVideos':
    playSpotifyVideos(url)
elif mode == 'listItunesVideos':
    listItunesVideos(type, url, limit)
elif mode == 'playItunesVideos':
    playItunesVideos(url)
elif mode == 'listBillboardCharts':
    listBillboardCharts(type, url, limit)
elif mode == 'listBillboardArchive':
    listBillboardArchive(url)
elif mode == 'listBillboardArchiveVideos':
    listBillboardArchiveVideos(type, url, limit)
elif mode == 'listBillboardChartsNew':
    listBillboardChartsNew(type, url, limit)
elif mode == 'listBillboardChartsTypes':
    listBillboardChartsTypes(url)
elif mode == 'queueVideo':
    queueVideo(url, name)
else:
    index()
