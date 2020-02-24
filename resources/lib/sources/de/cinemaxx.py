# -*- coding: utf-8 -*-

import urllib
import urlparse
import re

from resources.lib.modules import client
from resources.lib.modules import dom_parser
from resources.lib.modules import source_utils
from resources.lib.modules import cleantitle
# from resources.lib.modules import hdgo


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['de']
        self.domains = ['cinemaxx.cc']
        self.base_link = 'http://cinemaxx.cc/'

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            url = self.__search([localtitle] + source_utils.aliases_to_array(aliases))
            if not url and title != localtitle: url = self.__search([title] + source_utils.aliases_to_array(aliases))
            return url
        except:
            return

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            url = self.__search([localtvshowtitle] + source_utils.aliases_to_array(aliases))
            if not url and tvshowtitle != localtvshowtitle:
                url = self.__search([tvshowtitle] + source_utils.aliases_to_array(aliases))

            return url
        except:
            return

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if not url:
                return
            return [episode, url]
        except:
            return

    def sources(self, url, hostDict, hostprDict):
        sources = []
        try:
            if not url:
                return sources
            episode = None
            if isinstance(url, list):
                episode, url = url
            url = urlparse.urljoin(self.base_link, url)

            content = client.request(url)
            link = dom_parser.parse_dom(content, 'div', attrs={'id': 'full-video'})
            link = dom_parser.parse_dom(link, 'iframe')

            if len(link) > 0:
                if episode:
                    links = self.getPlaylistLinks(link[0].attrs['src'])
                    link = links[int(episode)-1]
                    sources = self.getStreams(link, sources)
                else:
                    sources = self.getStreams(link[0].attrs['src'], sources)

            return sources
        except:
            return sources


    def resolve(self, url):
        try:
            return url
        except:
            return url

    def __search(self, titles):
        try:
            t = [cleantitle.get(i) for i in set(titles) if i]

            for title in titles:
                params = {
                    'do': 'search',
                    'subaction': 'search',
                    'story': title
                }

                result = client.request(self.base_link, post=params, headers={'Content-Type': 'application/x-www-form-urlencoded'}, error=True)

                links = dom_parser.parse_dom(result, 'div', attrs={'class': 'shortstory-in'})
                links = [dom_parser.parse_dom(i, 'a')[0] for i in links]
                links = [(i.attrs['href'], i.attrs['title']) for i in links]
                links = [i[0] for i in links if cleantitle.get(i[1]) in t]

                if len(links) > 0:
                    return source_utils.strip_domain(links[0])
            return
        except:
            return

    def getPlaylistLinks(self, url):
        try:
            hdgoContent = client.request(url)
            playlistLink = dom_parser.parse_dom(hdgoContent, 'iframe')
            if len(playlistLink) > 0:
                playlistLink = playlistLink[0].attrs['src']
                playListContent = client.request('http:' + playlistLink)
                links = re.findall('\[(".*?)\]', playListContent, re.DOTALL)
                links = links[0].split(',')
                links = [i.replace('"', '').replace('\r\n','').replace('/?ref=hdgo.cc', '') for i in links]
                return [urlparse.urljoin('http://hdgo.cc', i) for i in links]
        except:
            return


    def getStreams(self, url, sources):
        try:
            hdgostreams = self.getHDGOStreams(url)
            if hdgostreams is not None:
                if len(hdgostreams) > 1:
                    hdgostreams.pop(0)
                quality = ["SD", "HD", "1080p", "2K", "4K"]
                for i, stream in enumerate(hdgostreams):
                    sources.append({'source': 'hdgo.cc', 'quality': quality[i], 'language': 'de',
                                    'url': stream + '|Referer=' + url, 'direct': True,
                                    'debridonly': False})
            return sources
        except:
            return sources


    def getHDGOStreams(self, url):
        try:
            request = client.request(url, referer=url)
            request = dom_parser.parse_dom(request, 'iframe')[0].attrs['src']
            request = client.request(urlparse.urljoin('http://', request), referer=url)
            pattern = "url:[^>]'([^']+)"
            request = re.findall(pattern, request, re.DOTALL)
            return request
        except:
            return None
