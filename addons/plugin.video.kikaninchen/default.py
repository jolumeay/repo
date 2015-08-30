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

addonID = 'plugin.video.kikaninchen'
addon = xbmcaddon.Addon(id=addonID)
socket.setdefaulttimeout(30)
pluginhandle = int(sys.argv[1])
playSound = addon.getSetting("playSound") == "true"
forceViewMode = addon.getSetting("forceViewMode") == "true"
useThumbAsFanart = addon.getSetting("useThumbAsFanart") == "true"
viewMode = str(addon.getSetting("viewMode"))
translation = addon.getLocalizedString
icon = xbmc.translatePath('special://home/addons/'+addonID+'/ico.png')
urlMain = "http://kikaninchen.de"
opener = urllib2.build_opener()
opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:25.0) Gecko/20100101 Firefox/25.0')]


def index():
    content = opener.open("http://www.kikaninchen.de/kikaninchen/filme/filme100-flashXml.xml").read()
    content = content[content.find('<links id="program">'):]
    spl = content.split('<multiMediaLink id="">')
    for i in range(1, len(spl), 1):
        entry = spl[i]
        match = re.compile('<description><!.CDATA.(.+?).></description>', re.DOTALL).findall(entry)
        desc = match[0].replace("]","")
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
            addDir(title, url, 'listVideosKN', thumb, desc, audioUrl)
    xbmcplugin.endOfDirectory(pluginhandle)
    if forceViewMode:
        xbmc.executebuiltin('Container.SetViewMode('+viewMode+')')


def listVideosKN(url, audioUrl):
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
        match2 = re.compile('<number>(.+?)</number>', re.DOTALL).findall(entry)
        if match2:
            title = match[0] + ' ' + match2[0]
        else:
            title = match[0]
        title = cleanTitle(title)
        match = re.compile('<mediaType>WEBL</mediaType>.+?<flashMediaServerURL>(.+?)<', re.DOTALL).findall(entry)
        urltmp = match[0]
        url = urltmp.replace("mp4:mp4dyn/","")
        match = re.compile('<image>(.+?)</image>', re.DOTALL).findall(entry)
        thumb = match[0]
        #GetImageHash - unable to stat url
        #thumb = thumb[:thumb.find('_h')]+"_v-galleryImage_-fc0f89b63e73c7b2a5ecbe26bac10a07631d8c2f.jpg"
        addLink(title, url, 'playVideo', thumb)
    xbmcplugin.endOfDirectory(pluginhandle)
    if forceViewMode:
        xbmc.executebuiltin('Container.SetViewMode('+viewMode+')')


def playVideo(url):
    if url.startswith("http://"):
        content = opener.open(url).read()
        match1 = re.compile('"fullscreenPfad", "(.+?)"', re.DOTALL).findall(content)
        match2 = re.compile('"pfad", "(.+?)"', re.DOTALL).findall(content)
        if match1:
            url = match1[0]
        elif match2:
            url = match2[0]
    else:
        url = "http://pmdonline.kika.de/mp4dyn/"+url
    listitem = xbmcgui.ListItem(path=url)
    xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)


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
    index()
elif mode == 'listVideosKN':
    listVideosKN(url, audioUrl)
elif mode == 'listVideos':
    listVideos(url)
elif mode == 'playVideo':
    playVideo(url)
elif mode == 'queueVideo':
    queueVideo(url, name, thumb)
else:
    index()
