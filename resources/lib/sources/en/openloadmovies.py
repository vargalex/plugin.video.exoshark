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
from resources.lib.modules import directstream
from resources.lib.modules import source_utils
from resources.lib.modules import cfscrape
from resources.lib.modules import log_utils


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['openloadmovies.net', 'openloadmovies.tv', 'pubfilmonline.net']
        self.base_link = 'https://openloadmovies.net'
        self.post_link = '/wp-admin/admin-ajax.php'
        self.search_link = '/?s=%s'
        self.scraper = cfscrape.create_scraper()


    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            url = {'imdb': imdb, 'title': title, 'year': year}
            url = urllib.urlencode(url)
            return url
        except:
            return


    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            url = {'imdb': imdb, 'tvdb': tvdb, 'tvshowtitle': tvshowtitle, 'year': year}
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


    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []

            if url == None: return sources

            data = urlparse.parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])

            title = data['tvshowtitle'] if 'tvshowtitle' in data else data['title']
            year = data['year']

            url = self.search_link % urllib.quote_plus(title)
            url = urlparse.urljoin(self.base_link, url)

            r = self.scraper.get(url).content

            result = client.parseDOM(r, 'div', attrs={'class': 'search-page'})[0]
            result = client.parseDOM(result, 'div', attrs={'class': 'result-item'})

            result = [client.parseDOM(i, 'div', attrs={'class': 'details'})[0] for i in result]
            result = [(client.parseDOM(i, 'a', ret='href')[0], client.parseDOM(i, 'a')[0], client.parseDOM(i, 'span', attrs={'class': 'year'})[0]) for i in result]
            result = [(i[0], re.sub('(\s*\.|\s*\(|\s*\[|\s)(\d{4}|3D)(\.|\)|\]|\s|)(.+|)', '', i[1]), i[2]) for i in result]

            try:
                url = [i[0] for i in result if cleantitle.get(i[1]) == cleantitle.get(title) and (year == i[2])][0]
            except:
                url = None

            if url == None: return sources

            if 'tvshowtitle' in data:
                url = '%s/episodes/%s-%01dx%01d/' % (self.base_link, url.rsplit('tvseries/', 1)[-1].strip('/'), int(data['season']), int(data['episode']))

            r = self.scraper.get(url).content

            try:
                items = re.findall('''(?s)['"]file['"]\s*:\s*['"]([^'"]+)['"].+?['"]label['"]\s*:\s*['"]([^'"]+)''', r)
                if items == []: raise Exception()
            except:
                jwplayer = re.findall('(?s)var Player\s*=\s*([^<>]+)<', r)[0]
                jwplayer_params = re.findall('"([^"]+)"', jwplayer)
                jwurl, player_id, player_data = jwplayer_params[0], jwplayer_params[1], jwplayer_params[2]
                payload = {'id': player_id, 'data': player_data}
                r = self.scraper.post(jwurl, data=payload).content
                try:
                    items = re.findall('''(?s)['"]file['"]\s*:\s*['"]([^'"]+)['"].+?['"]label['"]\s*:\s*['"]([^'"]+)''', r)
                    if items == []: raise Exception()
                except:
                    urlr = client.parseDOM(r, 'iframe', ret='src')[0]
                    if 'vproxy.online' in urlr:
                        urlr = 'https://vinh.vproxy.online/api/v1/caches/get?id=%s' % urlr.rsplit('?id=', 1)[-1]
                        result = self.scraper.get(urlr).content
                        items = re.findall('''(?s)['"]file['"]\s*:\s*['"]([^'"]+)['"].+?['"]label['"]\s*:\s*['"]([^'"]+)''', result)
                    else:
                        raise Exception()

            for i in items:
                url = i[0].replace('\/', '/')
                try: url = url.decode('unicode-escape')
                except: pass
                sources.append({'source': 'CDN', 'quality': source_utils.label_to_quality(i[1]), 'language': 'en', 'url': url, 'direct': True, 'debridonly': False})

            return sources
        except:
            log_utils.log('>>>> %s TRACE <<<<\n%s' % (__file__.upper().split('\\')[-1].split('.')[0], traceback.format_exc()), log_utils.LOGDEBUG)
            return sources

    def resolve(self, url):
        if 'google' in url:
            return directstream.googlepass(url)
        else:
            return url
