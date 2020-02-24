# -*- coding: utf-8 -*-

import urllib
import urlparse
import re

from resources.lib.modules import client
from resources.lib.modules import cfscrape
from resources.lib.modules import dom_parser
from resources.lib.modules import source_utils
from resources.lib.modules import cleantitle

class source:
    def __init__(self):
        self.priority = 1
        self.language = ['de']
        self.domains = ['kinoger.com']
        self.base_link = 'http://kinoger.com/'
        self.search=self.base_link + 'index.php?do=search&subaction=search&search_start=1&full_search=0&result_from=1&story=%s'
        self.scraper=cfscrape.create_scraper()

        self.hdgo_quality = ["SD", "HD", "1080p", "2K", "4K"]

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            url = self.__search(localtitle,aliases ,year)

            if not url and title != localtitle:
                url = self.__search(title, aliases, year)
            return urllib.urlencode({'url': url, 'imdb': re.sub('[^0-9]', '', imdb)}) if url else None
            
        except:
            return

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            url = self.__search(tvshowtitle, aliases, year)
            if not url and tvshowtitle != localtvshowtitle:
                url = self.__search(localtvshowtitle, aliases, year)
            return urllib.urlencode({'url': url, 'imdb': re.sub('[^0-9]', '', imdb)}) if url else None
        except:
            return

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if not url:
                return
            
            data = urlparse.parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])
            if not data["url"]:
                return
            data.update({'season': season, 'episode': episode})
            return urllib.urlencode(data)
        except:
            return

    def sources(self, url, hostDict, hostprDict):
        sources = []
        try:
            if not url:
                return sources


            data = urlparse.parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])
            url = urlparse.urljoin(self.base_link, data.get('url', ''))
            season = data.get('season')
            episode = data.get('episode')

            sHtmlContent=self.scraper.get(url).content

            quality = "SD"

            # do we have multiple hoster?
            # i.e. http://kinoger.com/stream/1911-bloodrayne-2-deliverance-2007.html
            link_containers = dom_parser.parse_dom(sHtmlContent,"section")
            if len(link_containers) == 0: #only one, i.e. http://kinoger.com/stream/890-lucy-2014.html
                #only one
                link_containers = dom_parser.parse_dom(sHtmlContent,"div",attrs={"id":"container-video"})

            for container in link_containers:
                #3 different types found till now: hdgo.show, namba.show and direct (mail.ru etc.)
                # i.e. http://kinoger.com/stream/1911-bloodrayne-2-deliverance-2007.html

                if ".show" in container.content:
                    pattern = ',\[\[(.*?)\]\]'
                    links = re.compile(pattern, re.DOTALL).findall(container.content)
                    if len(links) == 0: continue;
                    #split them up to get season and episode
                    season_array = links[0].split("],[")

                    source_link = None
                    if season and episode:
                        if len(season_array) < int(season):
                            continue
                        episode_array = season_array[int(season)-1].split(",")
                        if len(episode_array) < int(episode):
                            continue
                        source_link = episode_array[int(episode)-1]
                    elif len(season_array) == 1:
                        source_link = season_array[0]

                    if source_link:
                        source_link = source_link.strip("'")
                        if "hdgo" in container.content:
                            hdgostreams = self.getHDGOStreams(source_link)
                            if hdgostreams is not None:
                                if len(hdgostreams) > 1:
                                    hdgostreams.pop(0)
                                for i, stream in enumerate(hdgostreams):
                                    sources.append({'source': 'hdgo.cc', 'quality': self.hdgo_quality[i], 'language': 'de',
                                                    'url': stream + '|Referer=' + source_link, 'direct': True,
                                                    'debridonly': False})
                                    quality = self.hdgo_quality[i]
                            else:
                                continue
                        elif "namba" in container.content:
                            sources.append({'source': 'kinoger.com', 'quality': quality, 'language': 'de', 'url': "http://v1.kinoger.pw/vod/"+source_link, 'direct': False,
                                    'debridonly': False, 'checkquality': True})

                elif "iframe" in container.content:
                    frame = dom_parser.parse_dom(container.content, "iframe")
                    if len(frame) == 0:
                        continue
                    if 'hdgo' in frame[0].attrs["src"]:
                        hdgostreams = self.getHDGOStreams(frame[0].attrs["src"])
                        if hdgostreams is not None:
                            if len(hdgostreams) > 1:
                                hdgostreams.pop(0)
                            for i, stream in enumerate(hdgostreams):
                                sources.append({'source': 'hdgo.cc', 'quality': self.hdgo_quality[i], 'language': 'de',
                                                'url': stream + '|Referer=' + frame[0].attrs["src"], 'direct': True,
                                                'debridonly': False})
                                quality = self.hdgo_quality[i]
                        else:
                            continue
                    else:
                        valid, host = source_utils.is_host_valid(frame[0].attrs["src"], hostDict)
                        if not valid: continue

                        sources.append({'source': host, 'quality': quality, 'language': 'de', 'url': frame[0].attrs["src"], 'direct': False,
                                        'debridonly': False, 'checkquality': True})

                else:
                    #warning?
                    continue
                    
            return sources
        except:
            return sources


    def resolve(self, url):
        try:
            if 'kinoger' in url:
                request = self.scraper.get(url).content
                pattern = 'src:  "(.*?)"'
                request = re.compile(pattern, re.DOTALL).findall(request)
                return request[0]+ '|Referer=' + url
            return url
        except:
            return url

    def __search(self, localtitle, aliases ,year):
        try:

            aliases = [b["title"] for b in aliases]
            aliases = [localtitle] + aliases
            #KinoGer Suche
            url=self.search % str(localtitle)

            sHtmlContent=self.scraper.get(url).content
            search_results = dom_parser.parse_dom(sHtmlContent,'div', attrs={'id':'dle-content'})
            if len(search_results) == 0:
                raise Exception()

            #split content by seperator
            contentGroup = search_results[0].content.split("separator2")
            for c in contentGroup:

                #Fiter out English streams. I.e.: Downsizing
                category_content = dom_parser.parse_dom(c,'li', attrs={'class':'category'})
                if len(category_content) > 0 and "Englisch" in category_content[0].content:
                    continue

                r = dom_parser.parse_dom(c,'div', attrs={'class':'titlecontrol'})
                if len(r) == 0:
                    raise Exception()
                titlecontainer = r[0]
                k = dom_parser.parse_dom(titlecontainer,'a')
                for link in k:
                    linkTitle = cleantitle.get(link.content)
                    #clean it from
                    staffIndex = linkTitle.find('staffel')
                    if staffIndex > -1 :
                        linkTitle = linkTitle[:staffIndex]
                    linkTitle = linkTitle.replace("film","")
                    for alias in aliases:
                        if linkTitle in cleantitle.get(alias):
                            return link.attrs["href"]
                
            return
        except:
            return

    def getHDGOStreams(self,url):
        try:
            request = client.request(url, referer=url)
            pattern = '<iframe[^>]src="//([^"]+)'
            request = re.compile(pattern, re.DOTALL).findall(request)
            request = client.request('http://' + request[0], referer=url)
            pattern = "url:[^>]'([^']+)"
            request = re.compile(pattern, re.DOTALL).findall(request)
            return request
        except:
            return None
