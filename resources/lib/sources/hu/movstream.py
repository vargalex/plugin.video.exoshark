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
        self.language = ['hu']
        self.domains = ['movstream.do.am']
        self.base_link = 'http://movstream.do.am'


    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            url = {'imdb': imdb, 'title': title, 'localtitle': localtitle, 'year': year}
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
            localtitle = data['localtvshowtitle'] if 'localtvshowtitle' in data else data['localtitle']
            year = data['year']

            query = urlparse.urljoin(self.base_link, '/load/')
            post = urllib.urlencode({'query': localtitle, 'a': '2'})
            r = client.request(query, post=post)
            result = client.parseDOM(r, 'div', attrs={'class': 'poster_box'})

            result = [i for i in result if not '/load/sorozatok/' in i]
            result = [(client.parseDOM(i, 'div', ret='title')[0], i) for i in result]
            result = [i[1] for i in result if cleantitle.get(localtitle) == cleantitle.get(i[0].encode('utf-8'))]
            if len(result) == 0: raise Exception()

            result = [(re.search('block-subtitle">\s*(\d{4})\s*<', i).group(1), i) for i in result]
            result = [i[1] for i in result if year == i[0]]
            urlr = client.parseDOM(result, 'a', ret='href')[0]
            url = urlparse.urljoin(self.base_link, urlr)

            r = client.request(url)

            tag = client.parseDOM(r, 'div', attrs={'class': 'vep-details'})[0]
            tag = tag.lower()

            q = re.search('vep-author[->]+\s*(.+?)\s*<\/span', tag).group(1)
            if 'cam' in q or 'mozis' in q: quality = 'CAM'
            else: quality = 'SD'
            l = re.search('vep-channel[->]+\s*(.+?)\s*<\/span', tag).group(1)
            info = []
            if not 'felirat' in l and not 'angol' in l: info.append('szinkron')

            result = client.parseDOM(r, 'div', attrs={'class': 'vep-year'})[0]
            items = re.findall('href="([^"]+)"[^>]+>([^<>]+)<\/a', result)

            locDict = [(i.rsplit('.', 1)[0], i) for i in hostDict]         

            for item in items:
                try: 
                    host = item[1]
                    host = host.strip().lower()
                    host = [x[1] for x in locDict if host == x[0]][0]
                    if not host in hostDict: raise Exception()
                    host = client.replaceHTMLCodes(host)
                    host = host.encode('utf-8')
                    url = item[0]
                    url = client.replaceHTMLCodes(url)
                    url = url.encode('utf-8')
                    sources.append({'source': host, 'quality': quality, 'language': 'hu', 'info': ' | '.join(info), 'url': url, 'direct': False, 'debridonly': False})
                except:
                    pass

            return sources
        except:
            log_utils.log('>>>> %s TRACE <<<<\n%s' % (__file__.upper().split('\\')[-1].split('.')[0], traceback.format_exc()), log_utils.LOGDEBUG)
            return sources


    def resolve(self, url):
        return url
