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
from resources.lib.modules import log_utils


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['vidics.to']
        self.base_link = 'https://www.vidics.to'
        self.search_link = '/Category-%s/Genre-Any/%s-%s/Letter-Any/ByPopularity/1/Search-%s.htm'


    def movie(self, imdb, title, localtitle, aliases, year):
        try:    
            query = urlparse.urljoin(self.base_link, self.search_link % ('Movies', year, year, urllib.quote_plus(title)))
            headers = {'Host': 'www.vidics.to', 'Referer': self.base_link}
            r = client.request(query, headers=headers)

            result = client.parseDOM(r, 'td', attrs={'id': 'searchResults'})[0]
            result = client.parseDOM(result, 'div', attrs={'class': 'searchResult'})
            result = [(client.parseDOM(i, 'span', attrs={'itemprop': 'name'})[0], client.parseDOM(i, 'span', attrs={'itemprop': 'copyrightYear'})[0], i) for i in result]
            result = [i[2] for i in result if cleantitle.get(title) == cleantitle.get(i[0].strip().encode('utf-8')) and year in i[1]]
            if not len(result) == 1: raise Exception()

            url = client.parseDOM(result, 'a', ret='href')[0]
            url = urlparse.urljoin(self.base_link, url)
            url = url.encode('utf-8')
            return url
        except:
            log_utils.log('>>>> %s TRACE <<<<\n%s' % (__file__.upper().split('\\')[-1].split('.')[0], traceback.format_exc()), log_utils.LOGDEBUG)
            return


    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            query = urlparse.urljoin(self.base_link, self.search_link % ('TvShows', year, year, urllib.quote_plus(tvshowtitle)))
            headers = {'Host': 'www.vidics.to', 'Referer': self.base_link}
            r = client.request(query, headers=headers)

            result = client.parseDOM(r, 'td', attrs={'id': 'searchResults'})[0]
            result = client.parseDOM(result, 'div', attrs={'class': 'searchResult'})
            result = [(client.parseDOM(i, 'span', attrs={'itemprop': 'name'})[0], client.parseDOM(i, 'span', attrs={'itemprop': 'copyrightYear'})[0], i) for i in result]
            result = [i[2] for i in result if cleantitle.get(tvshowtitle) == cleantitle.get(i[0].strip().encode('utf-8')) and year in i[1]]
            if not len(result) == 1: raise Exception()

            url = client.parseDOM(result, 'a', ret='href')[0]
            url = urlparse.urljoin(self.base_link, url)
            url = url.encode('utf-8')
            return url
        except:
            log_utils.log('>>>> %s TRACE <<<<\n%s' % (__file__.upper().split('\\')[-1].split('.')[0], traceback.format_exc()), log_utils.LOGDEBUG)
            return


    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if url == None: return

            headers = {'Host': 'www.vidics.to', 'Referer': self.base_link}
            r = client.request(url, headers=headers)

            se_result = client.parseDOM(r, 'div', attrs={'class': 'season season_\d*'})
            se_result = [(client.parseDOM(i, 'a')[0], i) for i in se_result]
            se_result = [i[1] for i in se_result if i[0].lower().strip() == 'season %s' % season]
            if not len(se_result) == 1: raise Exception()

            ep_result = client.parseDOM(se_result, 'a', ret='href')
            ep_result = [i for i in ep_result if '-episode-%s' % episode in i.lower()]
            if not len(ep_result) == 1: raise Exception()

            url = urlparse.urljoin(self.base_link, ep_result[0])
            url = url.encode('utf-8')

            return url
        except:
            log_utils.log('>>>> %s TRACE <<<<\n%s' % (__file__.upper().split('\\')[-1].split('.')[0], traceback.format_exc()), log_utils.LOGDEBUG)
            return


    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []
            if url == None: return sources

            headers = {'Host': 'www.vidics.to', 'Referer': self.base_link}
            r = client.request(url, headers=headers)

            result = client.parseDOM(r, 'div', attrs={'class': 'lang'})[0]
            items = re.findall('href="([^"]+)"[^<>]+>([^<>]+)<\/a>', result)

            locDict = [(i.rsplit('.', 1)[0], i) for i in hostDict]         

            for item in items:
                try: 
                    host = item[1]
                    host = host.lower().replace('www.', '').rsplit('.', 1)[0].strip()
                    host = [x[1] for x in locDict if host == x[0]][0]
                    if not host in hostDict: raise Exception()
                    host = client.replaceHTMLCodes(host)
                    host = host.encode('utf-8')
                    url = urlparse.urljoin(self.base_link, item[0])
                    url = client.replaceHTMLCodes(url)
                    url = url.encode('utf-8')
                    sources.append({'source': host, 'quality': 'SD', 'language': 'en', 'info': '', 'url': url, 'direct': False, 'debridonly': False})
                except:
                    pass
            return sources
        except:
            log_utils.log('>>>> %s TRACE <<<<\n%s' % (__file__.upper().split('\\')[-1].split('.')[0], traceback.format_exc()), log_utils.LOGDEBUG)
            return sources


    def resolve(self, url):
        try:
            headers = {'Host': 'www.vidics.to', 'Referer': self.base_link}
            r = client.request(url, headers=headers)
            r = client.parseDOM(r, 'div', attrs={'class': 'movie_link1'})[0]
            url = client.parseDOM(r, 'a', ret='href')[0]
            return url
        except:
            return