# -*- coding: utf-8 -*-
import urllib
import urllib2
import os.path
import re
import xbmcplugin
import xbmcaddon
import xbmcgui

img_resolution = '640x360'
path = os.path.dirname(os.path.realpath(__file__))
icon = os.path.join(path, "icon.png")
addonID = 'plugin.video.dfb_tv'
addon = xbmcaddon.Addon(id=addonID)
is_xbox = xbmc.getCondVisibility("System.Platform.xbox")
if is_xbox: hd = False
else: hd = addon.getSetting("maxVideoQuality") == "1"

def index():
    add_category(title = 'Neue Videos', mode = 'list-videos')
    add_category(title = 'Fußball (Männer)', mode = 'category-men',)
    add_category(title = 'Fußball (Frauen)', mode = 'category-women')
    add_category(title = 'Internationale Wettbewerbe', mode = 'list-videos', categories = 'Wettbewerbe+International')
    add_category(title = 'Amateurfußball', mode = 'list-videos', categories = 'Amateurfußball')
    add_category(title = 'Fan Club', mode = 'list-videos', categories = 'Fan+Club')
    add_category(title = 'Englische Videos', mode = 'list-videos', categories = 'English+Videos')
    add_category(title = 'Livestreams', mode = 'list-livestreams')
    add_category(title = 'Suche', mode = 'search')
    xbmcplugin.endOfDirectory(int(sys.argv[1]))

def get_last_page(total_results):
    if not total_results: return 0
    if total_results % 10 == 0: return total_results // 10
    return total_results // 10 + 1

def clean_text(text):
    return text.replace('\n', '').replace('\t', '').replace('&amp;', '&').replace('   ', '').replace('  ', ' ').replace('\\"', '"').replace('\\u0026', '&').replace('\\t', '')
    
def is_livestreamdata_available():
    css_url = 'http://tv.dfb.de/style/main.css'
    try:
        css_data = urllib2.urlopen(css_url).read()
        regex_livestream_color = '.livestream_link.*?{(.+?)}'
        livestream_color = re.findall(regex_livestream_color, css_data, re.DOTALL)[0]
    except: return False
    return 'red' in livestream_color
    
def list_livestreams(live_url = 'http://tv.dfb.de/static/livestreams/'):
    try:
        html = urllib2.urlopen(live_url).read()
        regex_videos = '<div class="video-teaser.*?<img src="/images/(.+?)_.*?subline">(.+?)</.*?-headline">(.+?)</'
        videos = re.findall(regex_videos, html, re.DOTALL)
    except: return False
    item_added = False
    for video in videos:
        try:
            video_id = video[0]
            subline = clean_text(video[1])
            title = clean_text(video[2])
            thumb = 'http://tv.dfb.de/images/' + video_id + '_' + img_resolution + '.jpg'
            date = subline[:subline.find('//')]
            add_video(date + title, video_id, thumb, 'play-livestream', title + '\n' + subline)
            item_added = True
        except: continue
    xbmcplugin.endOfDirectory(int(sys.argv[1]))
    return item_added

#def is_livestream_online(video_id):
#    xml_url = 'http://tv.dfb.de/server/hd_video.php?play=' + video_id
#    try: xml_data = urllib2.urlopen(xml_url).read()
#    except: return False
#    return not ('Video not found' in xml_data)
    
def get_search_string():
    keyboard = xbmc.Keyboard('', 'Suche')
    keyboard.doModal()
    if keyboard.isConfirmed() and keyboard.getText():
        return keyboard.getText().replace(" ", "+")
    return False

def list_all_videos(search_string = '', categories = '', current_page = 1, last_page = 0, meta = ''):
    json_url = 'http://search.dfb.de/search/videos.json?'
    if search_string: json_url += 'q=' + search_string + '&'
    if categories: json_url += 'categories=' + categories + '&'
    if meta: json_url += 'meta_attribute_ids' + meta + '&'
    json_url += 'page=' + str(current_page)
    try:
        json = urllib2.urlopen(json_url).read()
        if hd: regex_video_info = '"guid":.*?"video-(.+?)","title":"(.+?)",.*?"medium_hires":"(.+?)",.*?"pub_date":"(.+?)"'
        else: regex_video_info = '"guid":.*?"video-(.+?)","title":"(.+?)",.*?"image_url":"(.+?)",.*?"pub_date":"(.+?)"'
        videos = re.findall(regex_video_info, json, re.DOTALL)
    except: return False
    item_added = False
    for video in videos:
        try:
            video_id = video[0]
            title = clean_text(video[1])
            thumb = video[2]
            date = video[3]
            add_video(date + ' - ' + title, video_id, thumb, 'play-video')
            item_added = True
        except: continue
    if not item_added: return warning('Keine Videos gefunden.')
    if not last_page: 
        regex_total = '"total":(.+?),'
        try: last_page = get_last_page(int(re.findall(regex_total, json)[0]))
        except: last_page = current_page
    if current_page < last_page:
        add_category('Nächste Seite (%d)' % (current_page + 1), 'list-videos', '', current_page + 1, last_page, search_string, categories, meta)
    xbmcplugin.endOfDirectory(int(sys.argv[1]))
    return True

def add_video(title, video_id, thumb, mode, desc = ''):
    link = sys.argv[0] + "?id=" + video_id + "&title=" + urllib.quote_plus(title) + "&thumb=" + urllib.quote_plus(thumb) + "&mode=" + mode
    liz = xbmcgui.ListItem(title, iconImage=icon, thumbnailImage=thumb)
    liz.setInfo(type="Video", infoLabels={"Title": title, "Plot": desc})
    return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=link, listitem=liz, isFolder=True)
    
def add_category(title, mode, thumb = '', current_page = 1, last_page = 0, search_string = '', categories = '', meta = ''):
    link = sys.argv[0] + "?current_page=" + str(current_page) + "&last_page=" + str(last_page) + "&thumb=" + urllib.quote_plus(thumb) + "&mode=" + mode
    if search_string: link += '&search_string=' + urllib.quote_plus(search_string)
    if categories: link += '&categories=' + urllib.quote_plus(categories)
    if meta: link += '&meta=' + urllib.quote_plus(meta)
    liz = xbmcgui.ListItem(title, iconImage=icon, thumbnailImage=thumb)
    liz.setInfo(type="Video", infoLabels={"Title": title})
    return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=link, listitem=liz, isFolder=True)
    
def play_video(title, stream, thumb):
    liz = xbmcgui.ListItem(title, iconImage=icon, thumbnailImage=thumb)
    liz.setInfo(type="Video", infoLabels={"Title": title})
    xbmc.Player().play(stream, liz)
    return True

def get_stream_url(video_id):
    xml_url = 'http://tv.dfb.de/server/hd_video.php?play=' + video_id
    try:
        xml_data = urllib2.urlopen(xml_url).read()
        if '<live>true</live>' in xml_data:
            if not ('<islive>true</islive>' in xml_data): return False
        regex_url = '<url>(.+?)</url>'
        xml_url_video = clean_text(re.findall(regex_url, xml_data, re.DOTALL)[0]).split('?')[0] + '?format=iphone'
        xml_url_video = 'http:' + xml_url_video.replace(' //', '//')
        xml_data_video = urllib2.urlopen(xml_url_video).read()
        regex_url_video = 'url="(.+?)"'
        video_url = re.findall(regex_url_video, xml_data_video, re.DOTALL)[0]
    except: return False
    if '/dfb_live' in video_url and video_url.endswith('.m3u8'): return video_url
    base_url = video_url[:video_url.find('_,')+2]
    if not ',1200,' in video_url:
        if not ',800,' in video_url:
            if not ',500,' in video_url:
                if not ',300,' in video_url: return False
                return base_url + '300,.mp4.csmil/index_0_av.m3u8'
            return base_url + '500,.mp4.csmil/index_0_av.m3u8'
        return base_url + '800,.mp4.csmil/index_0_av.m3u8'
    if hd: return base_url + '1200,.mp4.csmil/index_0_av.m3u8'
    return base_url + '800,.mp4.csmil/index_0_av.m3u8'

def parameters_string_to_dict(parameters):
    paramDict = {}
    if parameters:
        paramPairs = parameters[1:].split("&")
        for paramsPair in paramPairs:
            paramSplits = paramsPair.split('=')
            if (len(paramSplits)) == 2:
                paramDict[paramSplits[0]] = paramSplits[1]
    return paramDict
    
def warning(text, title = 'DFB TV', time = 4500):
    xbmc.executebuiltin('Notification(%s, %s, %d, %s)' % (title, text, time, icon))

params = parameters_string_to_dict(sys.argv[2])
mode = urllib.unquote_plus(params.get('mode', ''))
id = urllib.unquote_plus(params.get('id', ''))
title = urllib.unquote_plus(params.get('title', ''))
thumb = urllib.unquote_plus(params.get('thumb', ''))
c_page = urllib.unquote_plus(params.get('current_page', ''))
l_page = urllib.unquote_plus(params.get('last_page', ''))
search_st = urllib.unquote_plus(params.get('search_string', ''))
cat = urllib.unquote_plus(params.get('categories', ''))
meta_ids = urllib.unquote_plus(params.get('meta', ''))

if mode == 'list-livestreams':
    if is_livestreamdata_available(): list_livestreams()
    else: warning('Es gibt in nächster Zeit keine Livestreams.')
elif mode == 'play-livestream':
    stream_url = get_stream_url(id)
    if stream_url: play_video(title, stream_url, thumb)
    else: warning('Dieser Stream ist aktuell nicht online!')
elif mode == 'play-video':
    stream_url = get_stream_url(id)
    if stream_url: play_video(title, stream_url, thumb)
    else: warning('Das Video konnte nicht abgespielt werden.')
elif mode == 'search':
    search_s = get_search_string()
    if search_s: list_all_videos(search_string = search_s)
elif mode == 'category-men':
    add_category(title = 'Alle Videos', mode = 'list-videos', categories = 'Männer')
    add_category(title = 'Nationalmannschaft', mode = 'list-videos', categories = 'Die+Mannschaft')
    add_category(title = 'Bundesliga', mode = 'list-videos', categories = 'Bundesliga')
    add_category(title = 'DFB-Pokal', mode = 'list-videos', categories = 'DFB-Pokal')
    add_category(title = 'U21', mode = 'list-videos', categories = 'U+21-Männer')
    add_category(title = 'U20', mode = 'list-videos', categories = 'U20-Männer')
    add_category(title = 'Junioren', mode = 'list-videos', search_string = 'junioren')
    xbmcplugin.endOfDirectory(int(sys.argv[1]))
elif mode == 'category-women':
    add_category(title = 'Alle Videos', mode = 'list-videos', categories = 'Frauen')
    add_category(title = 'Frauen Nationalmannschaft', mode = 'list-videos', categories = 'Frauen+Nationalmannschaft')
    add_category(title = 'Allianz Frauen-Bundesliga', mode = 'list-videos', categories = 'Allianz+Frauen-Bundesliga')
    add_category(title = 'DFB-Pokal der Frauen', mode = 'list-videos', categories = 'DFB-Pokal+der+Frauen')
    add_category(title = 'Juniorinnen', mode = 'list-videos', search_string = 'juniorinnen')
    xbmcplugin.endOfDirectory(int(sys.argv[1]))
elif mode == 'list-videos':
    if not list_all_videos(search_st, cat, int(c_page), int(l_page), meta_ids): warning('Es konnten keine Videos hinzugefügt werden.')
else:
    index()