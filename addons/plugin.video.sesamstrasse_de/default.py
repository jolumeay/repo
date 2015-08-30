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
addonID = 'plugin.video.sesamstrasse_de'
addon = xbmcaddon.Addon(id=addonID)
socket.setdefaulttimeout(30)
pluginhandle = int(sys.argv[1])
forceViewMode = addon.getSetting("forceViewMode") == "true"
useThumbAsFanart = addon.getSetting("useThumbAsFanart") == "true"
viewMode = str(addon.getSetting("viewMode"))
max_quality = addon.getSetting("maxVideoQuality")
if max_quality == '0':
    quality = 'lo'
elif max_quality == '1':
    quality = 'hi'
elif max_quality == '2':
    quality = 'hq'
else:
    quality = 'hd'

translation = addon.getLocalizedString
icon = xbmc.translatePath('special://home/addons/'+addonID+'/icon.png')
opener = urllib2.build_opener()
opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:25.0) Gecko/20100101 Firefox/25.0')]
urlMain = "http://www.sesamstrasse.de"

def index():
    content = opener.open(urlMain+"/home/homepage1077.html").read()
    spl = content.split('<div class="thumb">')
    for i in range(1, len(spl), 1):
        entry = spl[i]
        match = re.compile('title="(.+?)"', re.DOTALL).findall(entry)
        title = cleanTitle(match[0])
        match = re.compile('href="(.+?)"', re.DOTALL).findall(entry)
        url = urlMain+match[0]
        match = re.compile('src="(.+?)"', re.DOTALL).findall(entry)
        thumb = urlMain+match[0]
        thumb = thumb[:thumb.find("_")]+"_v-original.jpg"
        match = re.compile('<div class="subline">(.+?)&nbsp;\\|&nbsp;(.+?):', re.DOTALL).findall(entry)
        date = ""
        duration = ""
        if match:
            date = match[0][0]
            date = date[:date.rfind('.')].strip()
            duration = match[0][1]
            title = date+" - "+title
        addLink(title, url, 'playVideo', thumb, "", duration)
    xbmcplugin.endOfDirectory(pluginhandle)
    if forceViewMode:
        xbmc.executebuiltin('Container.SetViewMode('+viewMode+')')


def playVideo(url):
    global quality
    try:
        if ',sesamstrasse' in url:
            regex_suffix_id = ',sesamstrasse(.+?).html'
            try: suffix_id = re.findall(regex_suffix_id, url)[0]
            except: suffix_id = '3000'
        else: suffix_id = '3000'
        content = opener.open(url).read()
        json_uuid = re.findall('player_image-(.+?)_', content)[0]
        json_url = 'http://www.sesamstrasse.de/sendungsinfos/sesamstrasse%s-ppjson_image-%s.json' % (suffix_id, json_uuid)
        json = opener.open(json_url).read()
        regex_qualities = '\.,(.+?),\.'
        qualities = re.findall(regex_qualities, json)[-1].split(',')
        if not (quality in qualities): quality = qualities[-1]
        regex_url = '"src": "http://(.+?)"'
        urls = re.findall(regex_url, json)
        stream_url = ''
        for url in urls:
            if url.endswith('.mp4'):
                stream_url = 'http://' + url[:-6] + quality + '.mp4'
                break
        if not stream_url: return
    except: return
    listitem = xbmcgui.ListItem(path=stream_url)
    xbmcplugin.setResolvedUrl(pluginhandle, True, listitem)


def queueVideo(url, name, thumb):
    playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
    listitem = xbmcgui.ListItem(name, thumbnailImage=thumb)
    playlist.add(url, listitem)


def cleanTitle(title):
    title = title.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&").replace("&#039;", "\\").replace("&quot;", "\"").replace("&szlig;", "ß").replace("&ndash;", "-")
    title = title.replace("&Auml;", "Ä").replace("&Uuml;", "Ü").replace("&Ouml;", "Ö").replace("&auml;", "ä").replace("&uuml;", "ü").replace("&ouml;", "ö").replace("&#034;", '"')
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
    liz.addContextMenuItems([(translation(30001), 'RunPlugin(plugin://'+addonID+'/?mode=queueVideo&url='+urllib.quote_plus(u)+'&name='+str(name)+'&thumb='+urllib.quote_plus(iconimage)+')',)])
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz)
    return ok


params = parameters_string_to_dict(sys.argv[2])
mode = urllib.unquote_plus(params.get('mode', ''))
url = urllib.unquote_plus(params.get('url', ''))
name = urllib.unquote_plus(params.get('name', ''))
thumb = urllib.unquote_plus(params.get('thumb', ''))

if mode == 'playVideo':
    playVideo(url)
elif mode == 'queueVideo':
    queueVideo(url, name, thumb)
else:
    index()
