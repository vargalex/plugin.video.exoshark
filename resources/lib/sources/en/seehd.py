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
from resources.lib.modules import cfscrape
from resources.lib.modules import source_utils
from resources.lib.modules import log_utils


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['en']
        self.domains = ['seehd.pl']
        self.base_link = 'http://www.seehd.pl'
        self.search_link = '/search/%s/feed/rss2/'
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

            hdlr = 'S%02dE%02d' % (int(data['season']), int(data['episode'])) if 'tvshowtitle' in data else data['year']

            # query = '%s S%02dE%02d' % (data['tvshowtitle'], int(data['season']), int(data['episode'])) if 'tvshowtitle' in data else '%s %s' % (data['title'], data['year'])
            # query = re.sub('(\\\|/| -|:|;|\*|\?|"|\'|<|>|\|)', ' ', query)

            url = self.search_link % urllib.quote_plus(title)
            url = urlparse.urljoin(self.base_link, url)

            r = self.scraper.get(url).content
            r = client.parseDOM(r, 'item')
            r = [(client.parseDOM(i, 'title')[0], re.findall('(\d{4})\s*</strong>', i)[0], i) for i in r]

            items = []

            for item in r:
                try:
                    t = item[0]
                    t = re.sub('(\[.*?\])|(<.+?>)', '', t)
                    t1 = re.sub('(\.|\(|\[|\s)(\d{4}|S\d*E\d*|S\d+|3D|(?:w|W)atch (?:o|O)nline)(\.|\)|\]|\s|)(.+|)', '', t)

                    if not cleantitle.get(t1) == cleantitle.get(title): raise Exception()

                    if not item[1] == hdlr: raise Exception()

                    try:
                        items += client.parseDOM(item[2], 'a', ret='href')
                    except:
                        pass
                    try:
                        items += client.parseDOM(item[2], 'iframe', ret='src')
                    except:
                        pass

                except:
                    pass

            for item in items:
                try:
                    if 'pasted.co' in item:
                        r = client.request(item)
                        urlr = client.parseDOM(r, 'iframe', ret='src')[0]
                        r1 = client.request(urlr)
                        r1 = client.parseDOM(r1, 'pre')[0]
                        urls = r1.split('\n')
                        for i in urls:
                            valid, host = source_utils.is_host_valid(i.strip(), hostDict)
                            if valid:
                                sources.append({'source': host, 'quality': 'SD', 'language': 'en', 'url': i.strip(), 'info': '', 'direct': False, 'debridonly': False})
                    valid, host = source_utils.is_host_valid(item, hostDict)
                    if valid:
                        sources.append({'source': host, 'quality': 'SD', 'language': 'en', 'url': item, 'info': '', 'direct': False, 'debridonly': False})
                except:
                    pass

            return sources
        except:
            log_utils.log('>>>> %s TRACE <<<<\n%s' % (__file__.upper().split('\\')[-1].split('.')[0], traceback.format_exc()), log_utils.LOGDEBUG)
            return sources


    def resolve(self, url):
        return url
