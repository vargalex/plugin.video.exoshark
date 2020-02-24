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
from resources.lib.modules import directstream
from resources.lib.modules import log_utils


class source:
    def __init__(self):
        self.priority = 0
        self.language = ['en']
        self.domains = ['m4ufree.tv']
        self.base_link = 'http://m4ufree.tv'
        self.search_link = '/search/%s.html'

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

    def searchShow(self, title, season, aliases):
        try:
            query = cleantitle.getsearch(title)
            url = urlparse.urljoin(self.base_link, self.search_link % query.replace(' ', '-'))
            r = client.request(url)
            results = client.parseDOM(r, 'div', attrs={'class': 'item'})
            results = [(client.parseDOM(i, 'a', ret='href')[0], client.parseDOM(i, 'a', ret='title')[0], re.findall('\(\s*(\d{4})\s*\)', i)[0]) for i in results]
            results = [(i[0], i[1].rsplit('(', 1)[0].strip(), i[2]) for i in results]
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

    def searchMovie(self, title, year, aliases):
        try:
            query = cleantitle.getsearch(title)
            url = urlparse.urljoin(self.base_link, self.search_link % query.replace(' ', '-'))
            r = client.request(url)
            results = client.parseDOM(r, 'div', attrs={'class': 'item'})
            results = [(client.parseDOM(i, 'a', ret='href')[0], client.parseDOM(i, 'a', ret='title')[0], re.findall('\(\s*(\d{4})\s*\)', i)[0]) for i in results]
            results = [(i[0], i[1].rsplit('(', 1)[0].strip(), i[2]) for i in results]
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

            if 'tvshowtitle' in data:
                season = int(data['season'])
                episode = int(data['episode'])
                url = self.searchShow(data['tvshowtitle'], data['season'], aliases)
            else:
                url = self.searchMovie(data['title'], data['year'], aliases)

            if url is None: return sources

            r = client.request(url)

            if 'tvshowtitle' in data:
                episodes = re.findall('(<h2.+?title=".+?<\/h2>)', r)
                for ep in episodes:
                    try:
                        if client.parseDOM(ep, 'button')[0] == 'S%02d-E%02d' % (season, episode):
                            ep_id = client.parseDOM(ep, 'button', ret='idepisode')[0]
                            ajaxurl = urlparse.urljoin(self.base_link, '/ajax-tvshow.php')
                            post = urllib.urlencode({'idepisode': ep_id})
                            r = client.request(ajaxurl, post=post)
                    except:
                        raise Exception()

            items = client.parseDOM(r, 'div', attrs={'class': 'le-server'})

            for item in items:
                try:
                    data_id = client.parseDOM(item, 'span', ret='data')[0]
                    ajaxurl = urlparse.urljoin(self.base_link, '/ajax_new.php')
                    post = urllib.urlencode({'m4u': data_id})
                    r = client.request(ajaxurl, post=post)
                    url = client.parseDOM(r, 'div', attrs={'class': 'containervideo'})[0]
                    url = client.parseDOM(url, 'iframe', ret='src')[0]
                    if 'drive.google' in url:
                        gd_urls = directstream.google(url)
                        for i in gd_urls:
                            try:
                                sources.append({'source': 'GDRIVE', 'quality': i['quality'], 'language': 'en', 'url': i['url'], 'direct': True, 'debridonly': False})
                            except:
                                pass
                    else:
                        valid, host = source_utils.is_host_valid(url, hostDict)
                        if valid:
                            quality, info = source_utils.get_release_quality(url)
                            sources.append({'source': host, 'quality': quality, 'language': 'en', 'url': url, 'info': '', 'direct': False, 'debridonly': False})
                except:
                    pass

            return sources
        except:
            log_utils.log('>>>> %s TRACE <<<<\n%s' % (__file__.upper().split('\\')[-1].split('.')[0], traceback.format_exc()), log_utils.LOGDEBUG)
            return sources

    def resolve(self, url):
        return url
