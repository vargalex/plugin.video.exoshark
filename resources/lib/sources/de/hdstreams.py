# -*- coding: utf-8 -*-

"""
    Covenant Add-on

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
"""

import json
import re
import base64

from resources.lib.modules import cfscrape
from resources.lib.modules import source_utils
from resources.lib.modules import cleantitle



class source:
    def __init__(self):
        self.priority = 1
        self.language = ['de']
        self.domains = ['hd-streams.org']
        self.base_link = 'https://hd-streams.org/'
        self.movie_link = self.base_link + 'movies?perPage=54'
        self.movie_link = self.base_link + 'seasons?perPage=54'
        self.search = self.base_link + 'search?q=%s&movies=true&seasons=true&actors=false&didyoumean=false'
        self.scraper = cfscrape.create_scraper()

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            objects = self.__search(imdb, True)

            t = [cleantitle.get(i) for i in set(source_utils.aliases_to_array(aliases)) if i]
            t.append(cleantitle.get(title))
            t.append(cleantitle.get(localtitle))

            for i in range(1, len(objects)):
                if cleantitle.get(objects[i]['title']) in t:
                    url = objects[i]['url']
                    break

            return url
            
        except:
            return

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            objects = self.__search(imdb, False)

            t = [cleantitle.get(i) for i in set(source_utils.aliases_to_array(aliases)) if i]
            t.append(cleantitle.get(tvshowtitle))
            t.append(cleantitle.get(localtvshowtitle))

            for i in range(1, len(objects)):
                if cleantitle.get(objects[i]['title']) in t:
                    return objects[i]['seasons']
        except:
            return

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if not url:
                return

            url = [i['url'] for i in url if 'season/' + season in i['url']]

            return url[0]
        except:
            return

    def sources(self, url, hostDict, hostprDict):
        sources = []
        try:
            if not url:
                return sources

            sHtmlContent=self.scraper.get(url).content
            
            pPattern = "recaptcha[^>]'([^']+)', '([^']+)', '([^']+).*?"
            pPattern += '>.*?>([^"]+)</v-btn>'
            aResult = re.compile(pPattern, re.DOTALL).findall(sHtmlContent)
            
            pattern = '<meta name="csrf-token" content="([^"]+)">'
            string = str(sHtmlContent)
            token = re.compile(pattern, flags=re.I | re.M).findall(string)
            
            # 1080p finden
            if '1080p' in string:
                q = '1080p'
      
            for e, h, sLang, sName in aResult:
                link=self.__getlinks(e,h,sLang,sName,token,url)
                
                # hardcoded, da Qualität auf der Webseite inkorrekt beschrieben ist unnd sName.strip() problem liefert aufgrund webseite. nxload kanndamit unterdrückt werden
                
                if q == '1080p' and e == '1':
                    if 'openload' in link:
                        sources.append({'source': 'openload.com', 'quality': '1080p', 'language': 'de', 'url': link, 'direct': False, 'debridonly': False})
                    elif 'streamango' in link:
                        sources.append({'source': 'streamango.com', 'quality': 'HD', 'language': 'de', 'url': link, 'direct': False, 'debridonly': False})
                    elif 'nxload' in link:
                        sources.append({'source': 'nxload.com', 'quality': '1080p', 'language': 'de', 'url': link, 'direct': False, 'debridonly': False})
                    elif 'streamcloud' in link:
                        sources.append({'source': 'streamcloud.com', 'quality': 'SD', 'language': 'de', 'url': link, 'direct': False, 'debridonly': False})
                else:
                    if 'openload' in link:
                        sources.append({'source': 'openload.com', 'quality': 'HD', 'language': 'de', 'url': link, 'direct': False, 'debridonly': False})
                    elif 'streamango' in link:
                        sources.append({'source': 'streamango.com', 'quality': 'HD', 'language': 'de', 'url': link, 'direct': False, 'debridonly': False})
                    elif 'nxload' in link:
                        sources.append({'source': 'nxload.com', 'quality': 'HD', 'language': 'de', 'url': link, 'direct': False, 'debridonly': False})
                    elif 'streamcloud' in link:
                        sources.append({'source': 'streamcloud.com', 'quality': 'SD', 'language': 'de', 'url': link, 'direct': False, 'debridonly': False})

            return sources
        except:
            return sources

    def __getlinks(self,e, h, sLang, sName,token,url):
            url = url + '/stream'
            # hardcoded german language
            params={'e':e,'h':h,'lang':'de', 'q':'','grecaptcha':''}
            sHtmlContent=self.scraper.post(url,headers={'X-CSRF-TOKEN':token[0],'X-Requested-With':'XMLHttpRequest'},data=params).content
                        
            pattern = 'ct[^>]":[^>]"([^"]+).*?iv[^>]":[^>]"([^"]+).*?s[^>]":[^>]"([^"]+).*?e"[^>]([^}]+)'
            
            aResult = re.compile(pattern, re.DOTALL).findall(sHtmlContent)
            
            token=base64.b64encode(token[0])
           
            for ct, iv, s, e in aResult:                
                ct = re.sub(r"\\", "", ct[::-1])
                s = re.sub(r"\\", "", s)

            from resources.lib.modules import source_utils

            sUrl2 = source_utils.evp_decode(ct, token, s.decode('hex'))
            fUrl=sUrl2.replace('\/', '/').replace('"', '')       
                
            return fUrl

    def resolve(self, url):
        return url

    def __search(self, imdb, isMovieSearch):
        try:
            sHtmlContent = self.scraper.get(self.base_link).content

            pattern = '<meta name="csrf-token" content="([^"]+)">'
            string = str(sHtmlContent)
            token = re.compile(pattern, flags=re.I | re.M).findall(string)

            if len(token) == 0:
                return #No Entry found?
            # first iteration of session object to be parsed for search

            sHtmlContent = self.scraper.get(self.search % imdb, headers={'X-CSRF-TOKEN':token[0],'X-Requested-With':'XMLHttpRequest'}).text

            content = json.loads(sHtmlContent)

            if isMovieSearch:
                returnObjects = content["movies"]
            else:
                returnObjects = content["series"]

            return returnObjects
        except:
            return
