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
from resources.lib.modules import dom_parser
from resources.lib.modules import source_utils
from resources.lib.modules import log_utils


class source:
    def __init__(self):
        self.priority = 0
        self.language = ['en']
        self.domains = ['watch-series.io', 'watch-series.co','watch-series.ru']
        self.base_link = 'https://watch-series.ru'
        self.search_link = '/search.html?keyword=%s'


    def matchAlias(self, title, aliases):
        try:
            for alias in aliases:
                if cleantitle.get(title) == cleantitle.get(alias['title']):
                    return True
        except:
            return False


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


    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []

            if url == None: return sources

            data = urlparse.parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])

            title = data['tvshowtitle']
            aliases = eval(data['aliases'])
            season, episode = int(data['season']), int(data['episode'])

            t = cleantitle.getsearch(title)
            query = urlparse.urljoin(self.base_link, self.search_link % urllib.quote_plus(t))
            r = client.request(query)
            
            result = client.parseDOM(r, 'li', attrs={'class': 'video-block'})
            result = [(client.parseDOM(i, 'a', ret='href')[0], client.parseDOM(i, 'a', ret='title')[0], re.findall('\-\s*(?:S|s)eason\s*(?:0|)(\d+)', i)[0]) for i in result]

            try:
                url = [i[0] for i in result if self.matchAlias(i[1].rsplit(' - Season')[0], aliases) and (str(season) == i[2])][0]
                url = urlparse.urljoin(self.base_link, url)
                url = url + '/season'
            except:
                return sources

            r = client.request(url)

            result = client.parseDOM(r, 'div', attrs={'class': 'video_container'})
            result = [(client.parseDOM(i, 'a', ret='href')[0], client.parseDOM(i, 'a', ret='title')[0]) for i in result]
            url = [i[0] for i in result if re.findall('\s*(?:E|e)pisode\s*(?:0|)(\d+)\s*', i[1])[0] == str(episode)][0]
            url = urlparse.urljoin(self.base_link, url)

            hostDict += ['akamaized.net', 'google.com', 'picasa.com', 'blogspot.com']

            r = client.request(url)
            
            dom = dom_parser.parse_dom(r, 'a', req='data-video')
            urls = [i.attrs['data-video'] if i.attrs['data-video'].startswith('http') else 'http:' + i.attrs['data-video'] for i in dom]

            for url in urls:
                try:
                    dom = []
                    if 'vidnode.net/streaming' in url:
                        result = client.request(url, timeout='10')

                        src = re.findall('''['"]?file['"]?\s*:\s*['"]([^'"]+)['"][^}]*['"]?label['"]?\s*:\s*['"]([\d]+)''', result, re.DOTALL)
                        src = [i for i in src if 'play?fileName' in i[0]]

                        links = [(i[0], '1080p') for i in src if int(i[1]) >= 1080]
                        links += [(i[0], 'HD') for i in src if 720 <= int(i[1]) < 1080]
                        links += [(i[0], 'SD') for i in src if int(i[1]) < 720]
                        for i in links: sources.append({'source': 'gvideo', 'quality': i[1], 'language': 'en', 'url': i[0], 'direct': True, 'debridonly': False})
                    elif 'vidcloud.icu' in url:
                        result = client.request(url, timeout='10')

                        src = re.findall('''['"]?file['"]?\s*:\s*['"]([^'"]+)['"][^}]*['"]?label['"]?\s*:\s*['"]([^'"]+)''', result, re.DOTALL)
                        src = [i for i in src if i[0].startswith('http')]
                        for i in src:
                            sources.append({'source': 'CDN', 'quality': 'SD', 'language': 'en', 'url': i[0], 'direct': True, 'debridonly': False}) 
                    elif 'ocloud.stream' in url:
                        result = client.request(url, timeout=10)
                        base = re.findall('<base href="([^"]+)">', result)[0]
                        hostDict += [base]
                        dom = dom_parser.parse_dom(result, 'a', req=['href','id'])
                        dom = [(i.attrs['href'].replace('./embed',base+'embed'), i.attrs['id']) for i in dom if i]
                        dom = [(re.findall("var\s*ifleID\s*=\s*'([^']+)", client.request(i[0]))[0], i[1]) for i in dom if i]                        
                    if dom:                
                        try:
                            for r in dom:
                                valid, hoster = source_utils.is_host_valid(r[0], hostDict)
    
                                if not valid: continue
                                quality = source_utils.label_to_quality(r[1])
                                urls, host, direct = source_utils.check_directstreams(r[0], hoster)
                                for x in urls:
                                    if direct: size = source_utils.get_size(x['url'])
                                    if size: sources.append({'source': host, 'quality': quality, 'language': 'en', 'url': x['url'], 'direct': direct, 'debridonly': False, 'info': size})         
                                    else: sources.append({'source': host, 'quality': quality, 'language': 'en', 'url': x['url'], 'direct': direct, 'debridonly': False})         
                        except:
                            pass
                    else:
                        valid, hoster = source_utils.is_host_valid(url, hostDict)
                        if not valid: continue
                        try:
                            url.decode('utf-8')
                            sources.append({'source': hoster, 'quality': 'SD', 'language': 'en', 'url': url, 'direct': False, 'debridonly': False})
                        except:
                            pass
                except:
                    pass
            return sources
        except:
            log_utils.log('>>>> %s TRACE <<<<\n%s' % (__file__.upper().split('\\')[-1].split('.')[0], traceback.format_exc()), log_utils.LOGDEBUG)
            return sources


    def resolve(self, url):
        if 'vidcdn.pro' in url: url = url.replace('https', 'http')
        if 'play?fileName' in url:
            r = client.request(url, output='extended', redirect=False)
            location = r[2]['Location']
            url = urlparse.urljoin(url, location)
        return url
