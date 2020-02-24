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
from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import log_utils


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['hu']
        self.domains = ['online-filmek.tv']
        self.base_link = 'http://online-filmek.tv'
        self.search_link = '/quick.php?q=%s'


    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            url = None
            years = [str(int(year)-1), str(int(year)+1)] 

            t = localtitle.replace(' ', '+')

            query = urlparse.urljoin(self.base_link, self.search_link % t)
            r = client.request(query)
            if not r: raise exception()
            result = json.loads(r)

            result = [i for i in result if cleantitle.get(i['nev'].encode('utf-8')) == cleantitle.get(localtitle)]
            result = [i for i in result if i['ev'] == year]
            if not len(result) == 1: raise Exception()

            url = urlparse.urljoin(self.base_link, '/film/%s-%s'  % (result[0]['id'].encode('utf-8'), result[0]['value'].encode('utf-8')))
            return url
        except:
            log_utils.log('>>>> %s TRACE <<<<\n%s' % (__file__.upper().split('\\')[-1].split('.')[0], traceback.format_exc()), log_utils.LOGDEBUG)
            return


    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            url = {'imdb': imdb, 'tvdb': tvdb, 'tvshowtitle': tvshowtitle, 'localtvshowtitle': localtvshowtitle, 'year': year}
            url = urllib.urlencode(url)
            return url
        except:
            return


    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if url == None: return
            data = urlparse.parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])
            title = data['tvshowtitle'] if 'tvshowtitle' in data else data['title']
            localtvshowtitle = data['localtvshowtitle'] if 'localtvshowtitle' in data else title

            t = localtvshowtitle.replace(' ', '+')

            query = urlparse.urljoin(self.base_link, self.search_link % t)
            r = client.request(query)
            if not r: raise exception()
            result = json.loads(r)
            result = [i for i in result if cleantitle.get(re.sub('(?:\s\d\.\s*\xe9vad)\s*', '', i['nev']).encode('utf-8')) == cleantitle.get(localtvshowtitle)]
            result = [i for i in result if '-%s-evad' % season in i['value']]
            if not len(result) == 1: raise Exception()

            url = urlparse.urljoin(self.base_link, '/sorozat/%s-%s_%s-resz'  % (result[0]['id'].encode('utf-8'), result[0]['value'].encode('utf-8'), episode))
            return url
        except:
            log_utils.log('>>>> %s TRACE <<<<\n%s' % (__file__.upper().split('\\')[-1].split('.')[0], traceback.format_exc()), log_utils.LOGDEBUG)
            return


    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []
            if url == None: return sources

            r = client.request(url)
            try: r = r.decode('iso-8859-1').encode('utf-8')
            except: pass
            result = client.parseDOM(r, 'div', attrs={'class': 'buttons'})
            result = [i for i in result if 'megoszto_link' in i]
            url = client.parseDOM(result[0], 'a', ret='href')[0]
            r = client.request(url)
            try: r = r.decode('iso-8859-1').encode('utf-8')
            except: pass
            r = r.replace('\n', '')

            result = re.findall('<tr>.+?class="(.+?)".+?div>(.+?)<.+?<b>(.+?)<.+?href="(.+?)"', r)

            locDict = [(i.rsplit('.', 1)[0], i) for i in hostDict]

            for i in result:
                try:
                    host = i[2].split()[0].rsplit('.', 1)[0].strip().lower()
                    host = [x[1] for x in locDict if host == x[0]][0]
                    if not host in hostDict: raise Exception()
                    host = client.replaceHTMLCodes(host)
                    host = host.encode('utf-8')
                    if  i[1] == 'Kiv\xc3\xa1l\xc3\xb3' or i[1] == 'J\xc3\xb3': quality = 'SD'
                    elif i[1] == 'Kamer\xc3\xa1s': quality = 'CAM'
                    else: quality = 'SD'
                    info = 'szinkron' if i[0] == 'kep-magyar_szinkron' else ''
                    url = client.replaceHTMLCodes(i[3])
                    url = url.encode('utf-8')  
                    sources.append({'source': host, 'quality': quality, 'language': 'hu', 'info': info, 'url': url, 'direct': False, 'debridonly': False})
                except:
                    pass

            return sources
        except:
            log_utils.log('>>>> %s TRACE <<<<\n%s' % (__file__.upper().split('\\')[-1].split('.')[0], traceback.format_exc()), log_utils.LOGDEBUG)
            return sources


    def resolve(self, url):
        try:
            result = client.request(url)
            urlr = client.parseDOM(result, 'a', ret='href')[-1]
            urlr = urlr.replace('/check.php?r=', '')
            try: urlr = urllib.unquote(urlr)
            except: pass
            urlr = client.replaceHTMLCodes(urlr)
            r = client.request(urlr)
            try: url = client.parseDOM(r, 'iframe', ret='src')[0]
            except: url = client.parseDOM(r, 'IFRAME', ret='SRC')[0]
            url = client.replaceHTMLCodes(url)
            url = url.encode('utf-8')
            return url
        except:
            return
