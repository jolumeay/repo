#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib
import urllib2
import socket
import sys
import re
import os
import random
import xbmcplugin
import xbmcgui
import xbmcaddon

#addon = xbmcaddon.Addon()
#addonID = addon.getAddonInfo('id')
addonID = 'plugin.video.kika_de'
addon = xbmcaddon.Addon(id=addonID)
socket.setdefaulttimeout(30)
pluginhandle = int(sys.argv[1])
ab3Only = addon.getSetting("ab3Only") == "true"
playSound = addon.getSetting("playSound") == "true"
forceViewMode = addon.getSetting("forceViewMode") == "true"
useThumbAsFanart = addon.getSetting("useThumbAsFanart") == "true"
viewMode = str(addon.getSetting("viewMode"))
translation = addon.getLocalizedString
icon = xbmc.translatePath('special://home/addons/'+addonID+'/icon.png')
urlMain = "http://kika.de"
opener = urllib2.build_opener()
opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:25.0) Gecko/20100101 Firefox/25.0')]


def index():
    if ab3Only:
        kikaninchen()
    else:
        addDir(translation(30001), "", 'kikaninchen', icon)
        addDir(translation(30004), "", 'listShowsAZ', icon)
        addLink(translation(30005), "", 'playLive', icon)
        xbmcplugin.endOfDirectory(pluginhandle)


def kikaninchen():
    content = opener.open("http://www.kikaninchen.de/kikaninchen/filme/filme100-flashXml.xml").read()
    content = content[content.find('<links id="program">'):]
    spl = content.split('<multiMediaLink id="">')
    for i in range(1, len(spl), 1):
        entry = spl[i]
        match = re.compile('<description><!\\[CDATA\\[(.+?)\\]\\]></description>', re.DOTALL).findall(entry)
        desc = match[0]
        desc = cleanTitle(desc)
        match = re.compile('<path type="intern" target="flashapp">(.+?)</path>', re.DOTALL).findall(entry)
        url = match[0]
        match = re.compile('/kikaninchen/filme/(.+?)/', re.DOTALL).findall(url)
        showID = match[0]
        showTitles = {'kikabaumhaus':'Baumhaus', 'zigbydaszebra':'Zigby das Zebra', 'einfallfuerfreunde':'Ein Fall für die drei Freunde', 'raketenfliegertimmi':'Raketenflieger Timmi', 'bummi':'Bummi', 'diesendungmitdemelefanten':'Die Sendung mit dem Elefanten', 'wdewlidh':'Weißt Du eigentlich, wie lieb ich dich hab?', 'mitmachmuehle':'Mit-Mach-Mühle', 'tauchtimmytauch':'tauch Timmy tauch', 'tillyundihrefreunde':'Tilly und Ihre Freunde', 'sesamstrassepraesentierteinemoehrefuerzwei':'Eine Möhre für Zwei', 'zoeszauberschrank':'Zoes Zauberschrank', 'unsersandmaennchen':'Unser Sandmännchen', 'enemenebuunddranbistdu':'ENE MENE BU - und dran bist du', 'ichkenneeintier':'Ich kenne ein Tier', 'meinbruderundich':'Mein Bruder und ich', 'sesamstrasse':'Die Sesamstraße', 'singasmusikbox':'Singas Musik Box', 'kallisgutenachtgeschichten':'Kallis GuteNachtGeschichten', 'tomunddaserdbeermarmeladebrot':'TOM und das Erdbeermarmeladebrot mit Honig', 'elefantastisch':'Elefantastisch!'}
        title = showTitles.get(showID, showID.title())
        match = re.compile('<image>(.+?)</image>', re.DOTALL).findall(entry)
        thumb = match[0]
        match = re.compile('<audio>(.+?)</audio>', re.DOTALL).findall(entry)
        audioUrl = ""
        if match:
            audioUrl = match[0]
        #GetImageHash - unable to stat url
        #thumb = thumb[:thumb.find('_h')]+"_v-galleryImage_-fc0f89b63e73c7b2a5ecbe26bac10a07631d8c2f.jpg"
        if not "auswahlkikaninchenfilme" in url and not "kikaninchentrailer" in url:
            addDir(title, url, 'listShowsKN', thumb, desc, audioUrl)
    xbmcplugin.endOfDirectory(pluginhandle)
    if forceViewMode:
        xbmc.executebuiltin('Container.SetViewMode('+viewMode+')')


def listShowsKN(url, audioUrl):
    if playSound and audioUrl and not xbmc.Player().isPlaying():
        xbmc.Player().play(audioUrl)
    if url.endswith("index.html"):
        content = opener.open(url).read()
        match = re.compile('flashvars.page = "(.+?)"', re.DOTALL).findall(content)
        url = match[0]
    content = opener.open(url).read()
    spl = content.split('<movie>')
    for i in range(1, len(spl), 1):
        entry = spl[i]
        match = re.compile('<title>(.+?)</title>', re.DOTALL).findall(entry)
        title = match[0]
        title = cleanTitle(title)
        match = re.compile('<mediaType>.+?</mediaType>.+?<flashMediaServerURL>(.+?)<', re.DOTALL).findall(entry)
        url = match[0].split(":") #url was mp4:mp4dyn/1/FCMS-[HASH].mp4
        if len(url) > 1:
            url = url[1]
        else:
            url = url[0]
        match = re.compile('<flashMediaServerApplicationURL>(.+?)<', re.DOTALL).findall(entry)
        url = match[0] + url

        match = re.compile('<image>(.+?)</image>', re.DOTALL).findall(entry)
        thumb = match[0]
        #GetImageHash - unable to stat url
        #thumb = thumb[:thumb.find('_h')]+"_v-galleryImage_-fc0f89b63e73c7b2a5ecbe26bac10a07631d8c2f.jpg"
        addLink(title, url, 'playVideo', thumb)
    xbmcplugin.endOfDirectory(pluginhandle)
    if forceViewMode:
        xbmc.executebuiltin('Container.SetViewMode('+viewMode+')')


#list all shows available at kika.de
#the link of the show leads to an overview page, so we
#need to parse another file to get the "all episodes"-page
def listShows(url):
    xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)
    content = opener.open(url).read()
	#each entry starts with the following code snipped
    spl = content.split('class="teaser teaserStandard')
    for i in range(1, len(spl), 1):
        entry = spl[i]
        match = re.compile('<noscript>.+?<img.*?src="(.*?)".+?>', re.DOTALL).findall(entry)
        thumb = urlMain + match[0]
        match = re.compile('<h4 class="headline">.+?<a href="(.+?)"', re.DOTALL).findall(entry)
        url = urlMain + match[0]
        match = re.compile('<a href="(.+?)" class="linkAll" title="(.+?)"></a>', re.DOTALL).findall(entry)
        title = cleanTitle(match[0][1])
        addDir(title, url, 'listEpisodes', thumb)
    xbmcplugin.endOfDirectory(pluginhandle)
    if forceViewMode:
        xbmc.executebuiltin('Container.SetViewMode('+viewMode+')')



#lists all episodes of a single show (plus pagination)
def listEpisodes(url):
    content = opener.open(url).read()
	#each entry starts with the following code snipped
    spl = content.split('class="teaser teaserStandard')
    for i in range(1, len(spl), 1):
        entry = spl[i]
        match = re.compile('<noscript>.+?<img.*?src="(.*?)".+?>', re.DOTALL).findall(entry)
        thumb = urlMain + match[0]

        match = re.compile('<h4 class="headline">.+?<a href="(.+?)"', re.DOTALL).findall(entry)
        #now the url links to the "alle folgen" are
        url = match[0].replace("sendereihe", "buendelgruppe")
        url = urlMain + url

        match = re.compile('<a href="(.+?)" class="linkAll" title="(.+?)"></a>', re.DOTALL).findall(entry)
        title = cleanTitle(match[0][1])

        addDir(title, url, 'listEpisodeFormats', thumb)
    xbmcplugin.endOfDirectory(pluginhandle)
    if forceViewMode:
        xbmc.executebuiltin('Container.SetViewMode('+viewMode+')')




#lists a single episode and available options (-> "play")
def listEpisodeFormats(url):
    #xbmc.log("listing episode formats: "+url)

    #load html site to get xml-data-url
    content = opener.open(url).read()

    match = re.compile('dataURL:\'([^\']*)\'', re.DOTALL).findall(content)
    xmlUrl = ""
    if match:
        xmlUrl = urlMain + match[0]

    if not xmlUrl == "":
        xbmc.log("listing episode formats from xml: "+xmlUrl)
        #load final xml content (containing video urls)
        content = opener.open(xmlUrl).read()

        #contains a thumbnail-template, but "hash"-key is missing
        #match = re.compile('<url>(.+?)</url>', re.DOTALL).findall(entry)
        #thumb = match[0]
        #thumb = thumb.replace("_v-", "-resimage_v-")
        #thumb = thumb.replace("**aspectRatio**", "tlarge169")
        #thumb = thumb.replace("**width**", "600")
        thumb = ""


        spl = content.split('<asset>')
        for i in range(1, len(spl), 1):
            url = ""
            entry = spl[i]
            match = re.compile('<profileName>(.+?)</profileName>', re.DOTALL).findall(entry)
            title = cleanTitle(match[0])
            xbmc.log("title: "+title)

            matches = re.compile('<flashMediaServerURL>(.+?)</flash', re.DOTALL).findall(entry)
            for match in matches:
                url = match.split(":") #url was mp4:mp4dyn/1/FCMS-[HASH].mp4
                if len(url) > 1:
                    url = url[1]
                else:
                    url = url[0]
                appMatch = re.compile('<flashMediaServerApplicationURL>(.+?)<', re.DOTALL).findall(entry)
                url = appMatch[0] + "/" + url

            if url == "":
                match = re.compile('<progressiveDownloadUrl>(.+?)<', re.DOTALL).findall(entry)
                url = match[0]

            xbmc.log("url: "+url)
            addLink(title, url, 'playVideo', thumb)
    else:
        addLink("Kein abspielbares Video gefunden", "", 'playVideo', "")
    xbmcplugin.endOfDirectory(pluginhandle)
    if forceViewMode:
        xbmc.executebuiltin('Container.SetViewMode('+viewMode+')')



def listShowsAZ():
    xbmcplugin.addSortMethod(pluginhandle, xbmcplugin.SORT_METHOD_LABEL)
    content = opener.open(urlMain+"/videos/allevideos/allevideos-buendelgruppen100.html").read()
	#begin
    content = content[content.find('class="bundleNaviWrapper"'):]
    #end
    content = content[:content.find('class="modCon"')]
    match = re.compile('<a href="(.+?)" class="pageItem".*?>(.+?)</a>', re.DOTALL).findall(content)
    for url, title in match:
        if "/kikaninchen/" in url:
            addDir(title, url, 'listShowsKN', icon)
        else:
            addDir(title, urlMain+url, 'listShows', icon)
    xbmcplugin.endOfDirectory(pluginhandle)
    if forceViewMode:
        xbmc.executebuiltin('Container.SetViewMode('+viewMode+')')


def playVideo(url):
    xbmc.log("URL: "+url)
    if url.startswith("http://"):
        content = opener.open(url).read()
        match1 = re.compile('"fullscreenPfad", "(.+?)"', re.DOTALL).findall(content)
        match2 = re.compile('"pfad", "(.+?)"', re.DOTALL).findall(content)
        if match1:
            url = match1[0]
        elif match2:
            url = match2[0]
    elif not url.startswith("rtmp://"):
        content = opener.open(urlMain+"/clients/kika/common/public/config/server.xml").read()
        servers = []
        spl = content.split('<server>')
        for i in range(1, len(spl), 1):
            entry = spl[i]
            match = re.compile('<ip>(.+?)</ip>', re.DOTALL).findall(entry)
            if "<activated>1</activated>" in entry and "<rtmp>1</rtmp>" in entry:
                servers.append(match[0])
        random.shuffle(servers)
        url = "rtmp://"+servers[0]+"/vod"+url
    listitem = xbmcgui.ListItem(path=url)
    xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)


def playLive():
    content = opener.open(urlMain+"/resources/player/xml/kika/livestream.xml").read()
    #skip to the "de"-content
    content = content[content.find('<geoZone>DE</geoZone>'):]

    matchDynamic = re.compile('<dynamicHttpStreamingRedirectorUrl>(.+?)</', re.DOTALL).findall(content)
    matchAdaptive = re.compile('<adaptiveHttpStreamingRedirectorUrl>(.+?)</', re.DOTALL).findall(content)
    if matchAdaptive:
        listitem = xbmcgui.ListItem(path=matchAdaptive[0].strip())
        xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)
    #is this even playable (f4m) ?
#   elif matchDynamic:
#       listitem = xbmcgui.ListItem( matchDynamic[0].Strip() )
#       xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)
    else:
        xbmc.executebuiltin("XBMC.Notification(%s, %s, 3500, %s)" % ("Sorry Kids", "Keinen Live-Stream gefunden", addon.getAddonInfo('icon')))

def queueVideo(url, name, thumb):
    playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
    listitem = xbmcgui.ListItem(name, thumbnailImage=thumb)
    playlist.add(url, listitem)


def cleanTitle(title):
    title = title.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&").replace("&#039;", "\\").replace("&quot;", "\"").replace("&szlig;", "ß").replace("&ndash;", "-")
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


def addLink(name, url, mode, iconimage, desc="", duration=""):
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": desc, "Duration": duration})
    liz.setProperty('IsPlayable', 'true')
    if useThumbAsFanart and iconimage!=icon:
        liz.setProperty("fanart_image", iconimage)
    liz.addContextMenuItems([(translation(30006), 'RunPlugin(plugin://'+addonID+'/?mode=queueVideo&url='+urllib.quote_plus(u)+'&name='+str(name)+'&thumb='+urllib.quote_plus(iconimage)+')',)])
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz)
    return ok


def addDir(name, url, mode, iconimage, desc="", audioUrl=""):
    u = sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&audioUrl="+urllib.quote_plus(audioUrl)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": desc})
    if useThumbAsFanart and iconimage!=icon:
        liz.setProperty("fanart_image", iconimage)
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok

params = parameters_string_to_dict(sys.argv[2])
mode = urllib.unquote_plus(params.get('mode', ''))
url = urllib.unquote_plus(params.get('url', ''))
name = urllib.unquote_plus(params.get('name', ''))
thumb = urllib.unquote_plus(params.get('thumb', ''))
audioUrl = urllib.unquote_plus(params.get('audioUrl', ''))

if mode == 'kikaninchen':
    kikaninchen()
elif mode == 'listShowsAZ':
    listShowsAZ()
elif mode == 'listShowsKN':
    listShowsKN(url, audioUrl)
elif mode == 'listShows':
    listShows(url)
elif mode == 'listEpisodes':
    listEpisodes(url)
elif mode == 'listEpisodeFormats':
    listEpisodeFormats(url)
elif mode == 'playVideo':
    playVideo(url)
elif mode == 'queueVideo':
    queueVideo(url, name, thumb)
elif mode == 'playLive':
    playLive()
else:
    index()
