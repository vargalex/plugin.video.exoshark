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


import re, urllib, urlparse, traceback, json, xbmcgui
from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import log_utils
from resources.lib.modules import control
from resources.lib.modules import source_utils
from resources.lib.modules import cache
from requests import Session

class source:
    def __init__(self):
        self.priority = 1
        self.language = ['hu']
        self.domains = ['wofvideo.club']
        self.base_link = 'https://wofvideo.club/'
        self.search_link = 'aj/search'

    def getURL(self, imdb, title, localtitle, year):
        result = client.request(self.base_link, output='extended')
        hash = client.parseDOM(result[0], 'input', attrs={'class': 'main_session'}, ret='value')[0]
        for sTitle in [localtitle.replace(':', ' -'), localtitle.replace(' - ', ': '), localtitle, title]:
            url_content = client.request('%s%s' % (self.base_link, self.search_link), post="hash=%s&search_value=%s" % (hash, urllib.quote_plus(sTitle)), headers={'Referer': self.base_link}, cookie=result[4])
            jsonResult = json.loads(url_content)
            if jsonResult["status"] == 200:
                movies = client.parseDOM("<html>%s</html>" % jsonResult["html"], 'div', attrs={'class': 'search-result'})
                for movie in movies:
                    movieTitle = client.parseDOM(movie, 'a')[0].replace(' online','').encode("utf-8")
                    if cleantitle.get(movieTitle) == cleantitle.get(sTitle):
                        url = client.parseDOM(movie, 'a', ret='href')[0]
                        return url
        return


    def movie(self, imdb, title, localtitle, aliases, year):
        return self.getURL(imdb, title, localtitle, year)

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        return urllib.urlencode({"title": tvshowtitle, "localtitle": localtvshowtitle, "year": year})

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        params=dict(urlparse.parse_qsl(url))
        return self.getURL(imdb, "%s %s.évad %s.rész" % (params["title"], season, episode), "%s %s.évad %s.rész" % (params["localtitle"], season, episode), params["year"])

    def sources(self, url, hostDict, hostprDict):
        sources = []
        if url == None: return sources
        sources.append({'source': 'wofvideo', 'quality': "SD", 'language': 'hu', 'info': 'ismeretlen', 'url': url, 'direct': False, 'debridonly': False, 'sourcecap': True})
        return sources

    def resolve(self, url):
        session = Session()
        url_content = session.get(url).text
        url = re.match(r'(.*)<source src="([^"]*)"(.*)', url_content, re.S)
        if url != None:
            url = url.group(2)
            return url
        return