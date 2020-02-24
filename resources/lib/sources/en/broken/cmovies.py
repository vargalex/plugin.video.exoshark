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


import re, urllib, urlparse, json, traceback
from resources.lib.modules import cfscrape
from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import source_utils
from resources.lib.modules import log_utils


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['cmovieshd.net']
        self.base_link = 'http://cmovieshd.net'
        self.search_link = '/search/?q=%s'
        self.scraper = cfscrape.create_scraper()


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
            t = cleantitle.getsearch(title)
            query = urlparse.urljoin(self.base_link, self.search_link % t.replace(' ', '+'))
            r = client.request(query)
            results = client.parseDOM(r, 'div', attrs={'class': 'ml-item'})
            results = [(client.parseDOM(i, 'a', ret='href')[0], client.parseDOM(i, 'a', ret='title')[0], re.findall('\-\s*Season\s*(\d+)', i)[0]) for i in results]
            try:
                url = [i[0] for i in results if self.matchAlias(i[1].rsplit(' - Season')[0], aliases) and (season == i[2])][0]
            except:
                url = None
                pass

            return url
        except:
            log_utils.log('>>>> %s TRACE <<<<\n%s' % (__file__.upper().split('\\')[-1].split('.')[0], traceback.format_exc()), log_utils.LOGDEBUG)
            return


    def searchMovie(self, title, year, aliases, headers):
        try:
            t = cleantitle.getsearch(title)
            query = urlparse.urljoin(self.base_link, self.search_link % t.replace(' ', '+'))
            r = self.scraper.get(query).content
            results = client.parseDOM(r, 'div', attrs={'class': 'ml-item'})
            results = [(client.parseDOM(i, 'a', ret='href')[0], client.parseDOM(i, 'a', ret='title')[0], client.parseDOM(i, 'a', ret='rel')[0]) for i in results]
            items = []
            for i in results:
                try:
                    if not self.matchAlias(i[1].rsplit('(')[0], aliases): continue
                    r = self.scraper.get(i[2]).content
                    yr = re.findall('>\s*(\d{4})\s*<', r)[0]
                    if yr == year: items += [(i[0], i[1])]
                except:
                    pass

            try:
                url = [i[0] for i in items][0]
            except:
                url = None

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
                url = self.searchShow(data['tvshowtitle'], data['season'], aliases, headers)
                if url is None: return sources
                url = url + 'watch'
            else:
                url = self.searchMovie(data['title'], data['year'], aliases, headers)
                if url is None: return sources
                url = url + 'watch'

            if url is None: return sources

            items = []

            r = self.scraper.get(url).content

            if 'tvshowtitle' in data:
                ep_list = client.parseDOM(r, 'div', attrs={'id': 'list-eps'})[-1]
                ep_list = client.parseDOM(ep_list, 'div', attrs={'class': 'le-server'})
                ep_list = [re.findall('href="([^"]+)".+?>([^<>]+)</a>', i) for i in ep_list]
                for i in ep_list:
                    for ii in i:
                        try:
                            quality = ii[1]
                            if not 'Episode %02d' % int(data['episode']) in quality: raise Exception()
                            r = client.request(ii[0])
                            episode_id = client.parseDOM(r, 'input', attrs={'name': 'episodeID'}, ret='value')[0]
                            api_url = 'https://api.streamdor.co/episode/embed/%s' % episode_id
                            result = client.request(api_url)
                            result = json.loads(result)
                            items += [(result['embed'], quality)]
                        except:
                            pass
            else:
                ep_list = client.parseDOM(r, 'div', attrs={'id': 'list-eps'})[0]
                ep_list = client.parseDOM(ep_list, 'div', attrs={'class': 'le-server'})
                ep_list = [(client.parseDOM(i, 'a', ret='href')[0], client.parseDOM(i, 'a')[0]) for i in ep_list]
                for i in ep_list:
                    try:
                        quality = i[1]
                        r = client.request(i[0])
                        episode_id = client.parseDOM(r, 'input', attrs={'name': 'episodeID'}, ret='value')[0]
                        api_url = 'https://api.streamdor.co/episode/embed/%s' % episode_id
                        result = client.request(api_url)
                        result = json.loads(result)
                        items += [(result['embed'], quality)]
                    except:
                        pass

            for item in items:
                try:
                    url = item[0]
                    if '720p' in item[1].lower(): quality = '720p'
                    elif 'cam' in item[1].lower(): quality = 'CAM'
                    else: quality = 'SD'
                    valid, hoster = source_utils.is_host_valid(url, hostDict)
                    urls, host, direct = source_utils.check_directstreams(url, hoster)
                    if valid:
                        for x in urls: sources.append({'source': host, 'quality': quality, 'language': 'en', 'url': x['url'], 'direct': direct, 'debridonly': False})
                except:
                    pass
                    
            return sources
        except:
            log_utils.log('>>>> %s TRACE <<<<\n%s' % (__file__.upper().split('\\')[-1].split('.')[0], traceback.format_exc()), log_utils.LOGDEBUG)
            return sources


    def resolve(self, url):
        return url
