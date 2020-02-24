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
from resources.lib.modules import cfscrape
from resources.lib.modules import client
from resources.lib.modules import cleantitle
from resources.lib.modules import source_utils
from resources.lib.modules import log_utils


class source:
    def __init__(self):
        self.priority = 0
        self.language = ['en']
        self.domain = ['beetv.to', 'myputlocker.me']
        self.base_link = 'http://myputlocker.me'
        self.search_link = '/wp/wp-admin/admin-ajax.php?action=autocompleteCallback&term=%s'
        self.scraper = cfscrape.create_scraper()


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
            url['title'], url['premiered'], url['season'], url['episode'], url['imdb'] = title, premiered, season, episode, imdb
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
            season, episode = int(data['season']), int(data['episode'])
            imdb = data['imdb']

            url = self.search_link % urllib.quote_plus(title)
            url = urlparse.urljoin(self.base_link, url)

            r = self.scraper.get(url).content

            result = re.findall('(<a.+?<\/a>)', r)
            result = [(client.parseDOM(i, 'a', ret='href')[0], client.parseDOM(i, 'span', attrs={'class': 'searchheading'})[0], re.findall('(\d+)\s*<\/span>', i)[0]) for i in result]

            try:
                url = [i[0] for i in result if cleantitle.get(i[1]) == cleantitle.get(title) and (imdb.strip('tt') == i[2])][0]
            except:
                url = None

            if url == None: return sources

            url = urlparse.urljoin(self.base_link, url)

            r = self.scraper.get(url).content

            result = client.parseDOM(r, 'div', attrs={'class': 'episodes-list-wrapper'})[0]
            result = client.parseDOM(result, 'li')
            result = [client.parseDOM(i, 'a', ret='href')[0] for i in result]
            result = [i for i in result if i.endswith('s%s-e%s' % (season, episode))]

            url = urlparse.urljoin(self.base_link, result[0])

            r = self.scraper.get(url).content

            items = client.parseDOM(r, 'iframe', ret='src')

            for item in items:
                try:
                    valid, host = source_utils.is_host_valid(item, hostDict)
                    if valid: sources.append({'source': host, 'quality': 'SD', 'language': 'en', 'url': item, 'info': '', 'direct': False, 'debridonly': False})
                except:
                    pass

            return sources
        except:
            log_utils.log('>>>> %s TRACE <<<<\n%s' % (__file__.upper().split('\\')[-1].split('.')[0], traceback.format_exc()), log_utils.LOGDEBUG)
            return sources


    def resolve(self, url):
        return url
