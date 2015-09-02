# -*- coding: utf-8 -*-
import xbmcaddon
import xbmcgui
import xbmcplugin
import urllib, urllib2
import re
import json
import os.path

addon_handle = int(sys.argv[1])
xbmcplugin.setContent(addon_handle, "movies")
path = os.path.dirname(os.path.realpath(__file__))
icon = os.path.join(path, "icon.png")
bundesliga_thumb = os.path.join(path, "resources", "bundesliga_thumb.jpg")
kkl_thumb = os.path.join(path, "resources", "kkl_thumb.jpg")
base_url = 'http://www.bild.de'
is_xbox = xbmc.getCondVisibility("System.Platform.xbox")
addonID = os.path.basename(path)
addon = xbmcaddon.Addon(id=addonID)
zeige_ergebnis = addon.getSetting("showMatchResult") == "true"
good_quality = addon.getSetting("maxVideoQuality") == "1"

if is_xbox or not good_quality: delivery = 'delivery=pmd.mp4'   #360p
else: delivery = 'delivery=hls2.m3u8'   #720p

def hole_bundesliga_spieltag(liga = 1):
    var = '' 
    if liga == 2: var = '2'
    url = 'http://sportdaten.bild.de/sportdaten/widgets/rpc_competition-info/' + var + 'bl/'
    try: html_json_info = urllib2.urlopen(url)
    except: return False
    info_json_data = json.load(html_json_info)
    # {"season_id": XXXXX, "round_id": XXXXX, "matchday": XX, "group_matchday": X, "current_mode": "XYXYXY"}
    season_id = info_json_data["season_id"]
    round_id = info_json_data["round_id"]
    matchday = info_json_data["matchday"]
    return (matchday, season_id, round_id)

def hole_mannschaften_ergebnis_link(matchday, season_id, round_id):
    global zeige_ergebnis
    url = 'http://sportdaten.bild.de/sportdaten/widgets/rpc_dmm_widget-gameplan-bibuli/sp1/se' + season_id + '/ro' + round_id + '/md' + matchday + '/'
    try: html = urllib2.urlopen(url).read()
    except: return False
    if html.count('.html') < 52: return False
    count = 0
    liste_spiele = re.findall('title="(.+?)"(.+?)title="(.+?)"(.+?)match_result_ats(.+?)href="(.+?)"><span class="finished">(.+?)</span>', html)
    for spiel in liste_spiele:
        link = spiel[-2]
        if not 'html' in link: continue
        home = spiel[0]
        away = spiel[2]
        ergebnis = ' '
        if zeige_ergebnis: ergebnis += spiel[-1]
        addDir(home + ' - ' + away + ergebnis, '', bundesliga_thumb, 'buli_link_' + link + '_')
        count += 1
    return count

def addDir(title, stream, thumb, mode):
    link = sys.argv[0]+"?url="+urllib.quote_plus(stream)+"&mode="+str(mode)
    liz = xbmcgui.ListItem(title, iconImage=icon, thumbnailImage=thumb)
    liz.setInfo(type="Video", infoLabels={"Title": title})
    return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=link, listitem=liz, isFolder=True)

def add_knop_videos(page = 1):
    page -= 1
    url = 'http://www.bild.de/video/clip/tb-matze-knop-37721724,page=' + str(page) + ',view=ajax.bild.html'
    try: html = urllib2.urlopen(url).read()
    except: return False
    video_list = re.findall('<div class="hentry(.+?)<meta itemprop="thumbnailUrl".*?</div>', html, re.DOTALL)
    count = 0
    for video in video_list:
        title = re.findall('<meta itemprop="name" content="(.+?)"/>', video_list[count])[0].replace("&#039;", "'").replace("&#034;", '"').replace("&amp;", "&")
        desc = re.findall('<meta itemprop="description" content="(.+?)"/>', video_list[count])[0].replace("&#039;", "'").replace("&#034;", '"').replace("&amp;", "&")
        video_page_url = re.findall('<meta itemprop="url" content ="(.+?)"/>', video_list[count])[0]
        if len(video_page_url) == 0:
            video_page_url = re.findall('<meta itemprop="url" content="(.+?)"/>', video_list[count])[0]
            if len(video_page_url) == 0:
                count += 1
                continue
        thumb = re.findall('<img class="photo" src="(.+?)"', video_list[count])[0]
        count += 1
        if not '.jpg' in thumb: continue
        if not video_page_url.endswith('.html'): continue
        try:
            id_part = video_page_url.split('-')[-1]
            id = id_part.split('.')[0]
            id_part_1 = id[0:2]
            id_part_2 = id[2:4]
            id_part_3 = id[4:6]
            id_part_4 = id[6:8]
        except: continue
        stream = 'http://videos-world.ak.token.bild.de/BILD/' + id_part_1 + '/' + id_part_2 + '/' + id_part_3 + '/' + id_part_4 + '/' + id + ',property=Video.mp4'
        thumb = thumb.split(',')[0] + ',w=400.bild.jpg'
        #print(title, desc, stream, thumb)
        liz = xbmcgui.ListItem(title, iconImage=icon, thumbnailImage=thumb)
        liz.setInfo(type="Video", infoLabels={"Title": title, "plot": desc})
        #liz.setProperty('VideoResolution', '480')
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=stream, listitem=liz)
    xbmcplugin.endOfDirectory(addon_handle)
    return True

def play_buli_stream(url):
    global zeige_ergebnis
    try: match_html = urllib2.urlopen(url).read()
    except: return False
    video_link_pattern = 'data-video="(.+?)"'
    try: video_link = re.search(video_link_pattern, match_html, re.DOTALL).group(1)
    except AttributeError: video_link = ''
    if not video_link or 'bild-plus' in video_link: return False
    final_link = base_url + video_link.split(",")[0] + ',view=json,width=400.bild.html'
    try: html_json_match = urllib2.urlopen(final_link)
    except: return False
    matchdata_json = json.load(html_json_match)
    id = matchdata_json['id']
    title = matchdata_json['headline']
    if not zeige_ergebnis: title = title[:title.rfind(" ")]
    thumb = matchdata_json['poster']
    stream = 'http://hds.ak.token.bild.de/' + id + ',' + delivery
    liz = xbmcgui.ListItem(title, iconImage=icon, thumbnailImage=thumb)
    liz.setInfo(type="Video", infoLabels={"Title": title})
    xbmc.Player().play(stream, liz)
    return True

def index():
    addDir('1. Bundesliga', '', bundesliga_thumb, 'erste_liga')
    addDir('2. Bundesliga', '', bundesliga_thumb, 'zweite_liga')
    addDir('Knops Kult Liga', '', kkl_thumb, 'matze_knop')
    xbmcplugin.endOfDirectory(addon_handle)

def create_knop_pages():
    for i in range(1,10):
        addDir('Seite ' + str(i), '', kkl_thumb, 'knop_' + str(i))
    xbmcplugin.endOfDirectory(addon_handle)
        
def create_matches(matchdays_until_today, liga, season_id, round_id):
    matchdays_until_today = int(matchdays_until_today)
    if matchdays_until_today > 34 or matchdays_until_today < 1: return False
    liga_string = 'erste'
    if liga != 1: liga_string = 'zweite'
    for i in range(matchdays_until_today, 0, -1):
        addDir(str(i) + '. Spieltag', '', bundesliga_thumb, liga_string + '_liga_spieltag_' + str(i) + '_season_' + str(season_id) + '_round_' +str(round_id) + '_')
    xbmcplugin.endOfDirectory(addon_handle)
    return True
    
def parameters_string_to_dict(parameters):
	paramDict = {}
	if parameters:
		paramPairs = parameters[1:].split("&")
		for paramsPair in paramPairs:
			paramSplits = paramsPair.split('=')
			if (len(paramSplits)) == 2:
				paramDict[paramSplits[0]] = paramSplits[1]
	return paramDict
    
params = parameters_string_to_dict(sys.argv[2])
mode = urllib.unquote_plus(params.get('mode', ''))
    
if mode == 'erste_liga':
    bundesliga_infos = hole_bundesliga_spieltag(1)
    try:
        create_matches(bundesliga_infos[0], 1, bundesliga_infos[1], bundesliga_infos[2])
    except:
        title = "Bundesliga bei Bild"
        text = "Keine Netzwerkverbindung?"
        time = 4500  # ms
        xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%(title, text, time, icon))
elif mode == 'zweite_liga':
    bundesliga_infos = hole_bundesliga_spieltag(2)
    try:
        if not create_matches(bundesliga_infos[0], 2, bundesliga_infos[1], bundesliga_infos[2]):
            title = "Bundesliga bei Bild"
            text = "Es gibt noch keine Infos für die neue Saison!"
            time = 4500  # ms
            xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%(title, text, time, icon))
    except:
        title = "Bundesliga bei Bild"
        text = "Keine Netzwerkverbindung?"
        time = 4500  # ms
        xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%(title, text, time, icon))
elif 'erste_liga' in mode or 'zweite_liga' in mode:
    matchday = re.findall('_spieltag_(.+?)_', mode)[0]
    season_id = re.findall('_season_(.+?)_', mode)[0]
    round_id = re.findall('_round_(.+?)_', mode)[0]
    result = hole_mannschaften_ergebnis_link(matchday, season_id, round_id)
    if not result:
        title = "Bundesliga bei Bild"
        text = "Videos noch nicht veröffentlicht!"
        time = 4500  # ms
        xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%(title, text, time, icon))
    else: xbmcplugin.endOfDirectory(addon_handle)
elif mode == 'matze_knop':
    create_knop_pages()
elif 'knop_' in mode:
    page = int(mode[-1])
    if not add_knop_videos(page):
        title = "Bundesliga bei Bild"
        text = "Keine Netzwerkverbindung?"
        time = 4500  # ms
        xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%(title, text, time, icon))
elif 'buli_link' in mode:
    url = re.findall('buli_link_(.+?)_', mode)[0]
    if not play_buli_stream(url):
        title = "Bundesliga bei Bild"
        text = "Video noch nicht veröffentlicht!"
        time = 4500  # ms
        xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%(title, text, time, icon))
else:
    index()