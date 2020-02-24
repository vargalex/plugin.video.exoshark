# -*- coding: utf-8 -*-

'''
    ExoShark Add-on

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''


import re, urllib, urlparse, traceback

from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import source_utils
from resources.lib.modules import log_utils


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['solarmovie.cam', 'solarmovie.watch', 'solarmovie.plus', 'solarmovie.solar']
        self.base_link = 'https://solarmovie.cam'


    def matchAlias(self, title, aliases):
        try:
            for alias in aliases:
                if cleantitle.get(title) == cleantitle.get(alias['title']):
                    return True
        except:
            return False


    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            aliases.append({'country': 'us', 'title': title})
            url = {'imdb': imdb, 'title': title, 'year': year, 'aliases': aliases}
            url = urllib.urlencode(url)
            return url
        except:
            return


    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            aliases.append({'country': 'us', 'title': tvshowtitle})
            url = {'imdb': imdb, 'tvdb': tvdb, 'tvshowtitle': tvshowtitle, 'year': year, 'aliases': aliases}
            url = urllib.urlencode(url)
            return url
        except:
            return


    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if url == None: return
            url = urlparse.parse_qs(url)
            url = dict([(i, url[i][0]) if url[i] else (i, '') for i in url])
            url['title'], url['premiered'], url['season'], url['episode'] = title, premiered, season, episode
            url = urllib.urlencode(url)
            return url
        except:
            return


    def searchShow(self, title, season, aliases, headers):
        try:
            query = '%s Season %s' % (title, season)
            post = urllib.urlencode({'do': 'search', 'subaction': 'search', 'story': query})
            r = client.request(self.base_link, post=post, headers=headers, timeout='15')
            results = client.parseDOM(r, 'div', attrs={'class': 'ml-item'})
            results = [(client.parseDOM(i, 'a', ret='href')[0], client.parseDOM(i, 'a', ret='title')[0], re.findall('- Season\s*(\d+)', i)[0]) for i in results]
            try:
                url = [i[0] for i in results if self.matchAlias(i[1].rsplit(' - Season')[0], aliases) and (season == i[2])][0]
            except:
                url = None
                pass

            if (url == None):
                url = [i[0] for i in results if self.matchAlias(i[1].rsplit(' - Season')[0], aliases)][0]
            return url
        except:
            log_utils.log('>>>> %s TRACE <<<<\n%s' % (__file__.upper().split('\\')[-1].split('.')[0], traceback.format_exc()), log_utils.LOGDEBUG)
            return


    def searchMovie(self, title, year, aliases, headers):
        try:
            post = urllib.urlencode({'do': 'search', 'subaction': 'search', 'story': title})
            r = client.request(self.base_link, post=post, headers=headers, timeout='15')
            results = client.parseDOM(r, 'div', attrs={'class': 'ml-item'})
            results = [(client.parseDOM(i, 'a', ret='href')[0], client.parseDOM(i, 'a', ret='title')[0], re.findall('\:\s*(\d{4})\s*<', i)[0]) for i in results]
            try:
                url = [i[0] for i in results if self.matchAlias(i[1], aliases) and (year == i[2])][0]
            except:
                url = None
                pass

            if (url == None):
                url = [i[0] for i in results if self.matchAlias(i[1], aliases)][0]
            return url
        except:
            log_utils.log('>>>> %s TRACE <<<<\n%s' % (__file__.upper().split('\\')[-1].split('.')[0], traceback.format_exc()), log_utils.LOGDEBUG)
            return


    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []

            if url is None: return sources

            data = urlparse.parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])
            aliases = eval(data['aliases'])
            headers = {}

            if 'tvshowtitle' in data:
                episode = int(data['episode'])
                url = self.searchShow(data['tvshowtitle'], data['season'], aliases, headers)
            else:
                episode = 0
                url = self.searchMovie(data['title'], data['year'], aliases, headers)

            try:
                url = url.rsplit('.', 1)[0] + '/watching.html'
                r = client.request(url)

                qual = client.parseDOM(r, 'span', attrs = {'class': 'quality'})[0]
                if any(x in qual.lower() for x in ['ts', 'cam']): quality = 'CAM'
                elif any(x in qual.lower() for x in ['hd', '720p']): quality = '720p'
                else: quality = 'SD'
                if 'hdtv' in qual.lower(): quality = 'SD'

                if 'tvshowtitle' in data:
                    r = client.parseDOM(r, 'div', attrs = {'class': 'series-list'})[0]
                else:
                    r = client.parseDOM(r, 'div', attrs = {'class': 'pas-list'})[0]

                items = client.parseDOM(r, 'li')

                if 'tvshowtitle' in data:
                    items = [(client.parseDOM(i, 'span', attrs = {'class': 'epinum'})[0], i) for i in items]
                    items = [(re.sub('<[^<>]+>', '', i[0]), i[1]) for i in items]
                    items = [i[1] for i in items if episode == int(i[0].split(' #')[-1])]
                    if not len(items) == 1: raise Exception()
                    items = items[0].split('\n')

                for item in items:
                    try:
                        link = client.parseDOM(item, 'a', ret='data-link')[0]
                        if not link.startswith('http'): link = 'http:' + link
                        if 'megadrive.co' in link:
                            sources.append({'source': 'CDN', 'quality': quality, 'language': 'en', 'url': link, 'direct': True, 'debridonly': False})
                        else:
                            valid, hoster = source_utils.is_host_valid(link, hostDict)
                            urls, host, direct = source_utils.check_directstreams(link, hoster)
                            if valid:
                                for x in urls: sources.append({'source': host, 'quality': quality, 'language': 'en', 'url': x['url'], 'direct': direct, 'debridonly': False})
                    except:
                        pass
            except:
                pass

            return sources
        except:
            log_utils.log('>>>> %s TRACE <<<<\n%s' % (__file__.upper().split('\\')[-1].split('.')[0], traceback.format_exc()), log_utils.LOGDEBUG)
            return sources


    def resolve(self, url):
        if 'megadrive' in url:
            urlr = re.findall('\/e\/([^\/]+)\/', url)[0]
            urlt = 'http://%s/embed/%s' % (urlparse.urlparse(url.strip()).netloc, urlr)
            r = client.request(urlt)
            url = re.findall('(?s)videos:.+?mp4:"([^"]+)"', r)[0]
        return url
