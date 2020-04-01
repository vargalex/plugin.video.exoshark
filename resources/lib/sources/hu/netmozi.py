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


import re, urllib, urlparse, traceback, json
from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import log_utils
from resources.lib.modules import control
from resources.lib.modules import source_utils
from resources.lib.modules import cache

class source:
    def __init__(self):
        self.priority = 1
        self.language = ['hu']
        self.domains = ['netmozi.com']
        self.base_link = 'https://netmozi.com'
        self.search_link = '/?type=%s&search=%s'
        self.login_link = '/login/do'
        self.username = control.setting('netmozi.user')
        self.password = control.setting('netmozi.pass')

    def getURL(self, title, localtitle, year, searchType):
        for sTitle in [title, localtitle]:
            url_content = client.request('%s%s' % (self.base_link, self.search_link) % (searchType, urllib.quote_plus(sTitle)))
            movies = client.parseDOM(url_content, 'div', attrs={'class': 'col-sm-4 col_main'})
            for movie in movies:
                url = client.parseDOM(movie, 'a', attrs={'class': 'col_a'}, ret='href')[0]
                infoDiv = client.parseDOM(movie, 'div', attrs={'class': 'col-sm-6'})[1]
                infoRows = client.parseDOM(infoDiv, 'div', attrs={'class': 'row'})
                movieYear = re.sub('<.*>', '', client.replaceHTMLCodes(infoRows[0]).encode('utf-8')).strip()
                if int(year)-1<=int(movieYear)<=int(year)+1:# in years:
                    return url
        return


    def movie(self, imdb, title, localtitle, aliases, year):
        return self.getURL(title, localtitle, year, "1")

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        return self.getURL(tvshowtitle, localtvshowtitle, year, "2")

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if url == None: return
            url = "%s/s%s/e%s" % (url, season, episode)
            return url
        except:
            log_utils.log('>>>> %s TRACE <<<<\n%s' % (__file__.upper().split('\\')[-1].split('.')[0], traceback.format_exc()), log_utils.LOGDEBUG)
            return


    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []
            if url == None: return sources

            loginCookie = cache.get(self.getCookie, 24)
            if loginCookie == None:
                raise ValueError("Sikertelen bejelentkezés! Hibás felhasználó név/jelszó?")
            url_content = client.request('%s%s' %(self.base_link, url), cookie=loginCookie)
            table = client.parseDOM(url_content, 'table', attrs={'class': 'table table-responsive'})
            if table:
                hostDict = hostprDict + hostDict
                rows = client.parseDOM(table, 'tr')
                for row in rows:
                    row=row.replace("\r", "").replace("\n", "").replace("</td>", "</td>\n").replace("\t", "")
                    #cols = client.parseDOM(row, 'td')
                    cols=re.findall(r'<td>(.*)</td>', row)
                    valid, host = source_utils.is_host_valid(cols[5].encode('utf-8'), hostDict)
                    if not valid: 
                        continue
                    host = client.replaceHTMLCodes(host)
                    host = host.encode('utf-8')
                    if 'hungary.gif' in cols[0]:
                        info = 'szinkron'
                    elif 'usa.gif' in cols[0]:
                        info='külföldi'
                    elif 'uk-hu.png' in cols[0]:
                        info = 'felirat'
                    elif 'red_mark.png' in cols[1]:
                        info = 'érvénytelen'
                    else:
                        info = ''
                    if 'Mozis hang' in cols[4]:
                        info = 'szinkron (mozis hang)'
                    if 'DVD' in cols[4] or 'TV' in cols[4]:
                        quality = 'SD' 
                    if 'CAM' in cols[4] or 'TS' in cols[4] or 'TC' in cols[4]:
                        quality = 'CAM'
                    if 'HD' in cols[4]:
                        quality = 'HD'
                    src=client.parseDOM(cols[3], 'a', attrs={'class': 'btn btn-outline-primary btn-sm'}, ret='href')[0].encode('utf-8')
                    sources.append({'source': host, 'quality': quality, 'language': 'hu', 'info': info, 'url': src, 'direct': False, 'debridonly': False, 'sourcecap': True})
            return sources
        except:
            log_utils.log('>>>> %s TRACE <<<<\n%s' % (__file__.upper().split('\\')[-1].split('.')[0], traceback.format_exc()), log_utils.LOGDEBUG)
            return sources


    def resolve(self, url):
        try:
            loginCookie = cache.get(self.getCookie, 24)
            url_content = client.request('%s%s' % (self.base_link, url), cookie=loginCookie)
            matches = re.search(r'^(.*)var link(.*)= "(.*)";(.*)$', url_content, re.MULTILINE)
            if matches:
                url = matches.group(3).decode('base64')
                return url
            return
        except: 
            return

    def getCookie(self):
        if (self.username and self.password) != '':
            login_cookies = client.request("%s%s" % (self.base_link, self.login_link), post="username=%s&password=%s" % (urllib.quote_plus(self.username), urllib.quote_plus(self.password)), output='cookie')
            if 'ca=' in login_cookies:
                return login_cookies
            raise Exception()
        return