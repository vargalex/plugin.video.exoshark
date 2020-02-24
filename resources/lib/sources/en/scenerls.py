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



import re, urllib, urlparse, json

from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import cfscrape
from resources.lib.modules import debrid
from resources.lib.modules import source_utils
from resources.lib.modules import dom_parser2


class source:
    def __init__(self):
        self.priority = 0
        self.language = ['en']
        self.domains = ['scene-rls.net']
        self.base_link = 'http://scene-rls.net'
        self.search_link = '/?s=%s&submit=Find'
        self.search_link2 = '/releases/index.php?s=%s'
        self.scraper = cfscrape.create_scraper()
        self.useragent = 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.96 Safari/537.36'


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

            if not debrid.status(): raise Exception()

            data = urlparse.parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])

            title = data['tvshowtitle'] if 'tvshowtitle' in data else data['title']

            hdlr = 'S%02dE%02d' % (int(data['season']), int(data['episode'])) if 'tvshowtitle' in data else data['year']

            query = '%s S%02dE%02d' % (data['tvshowtitle'], int(data['season']), int(data['episode'])) if 'tvshowtitle' in data else '%s %s' % (data['title'], data['year'])
            query = re.sub('(\\\|/| -|:|;|\*|\?|"|\'|<|>|\|)', ' ', query)

            url = self.search_link2 % urllib.quote_plus(query)
            url = urlparse.urljoin(self.base_link, url)

            r = self.scraper.get(url).content
            r = client.parseDOM(r, 'div', attrs={'class': 'post'})
            r = [re.findall('''href="([^"]+)[^<>]+>([^<>]+)<\/a>[^<>]+<\/h2>''', i, re.DOTALL) for i in r]

            hostDict = hostprDict + hostDict

            items = []

            for item in r:
                try:
                    t = item[0][1]
                    t = re.sub('(\[.*?\])|(<.+?>)', '', t)
                    t1 = re.sub('(\.|\(|\[|\s)(\d{4}|S\d*E\d*|S\d+|3D)(\.|\)|\]|\s|)(.+|)', '', t)

                    if not cleantitle.get(t1) == cleantitle.get(title): raise Exception()

                    y = re.findall('[\.|\(|\[|\s](\d{4}|S\d*E\d*|S\d*)[\.|\)|\]|\s]', t)[-1].upper()

                    if not y == hdlr: raise Exception()

                    data = self.scraper.get(item[0][0]).content

                    if '>* * * * *<' in data:
                        itemr = data.split('>* * * * *<')
                        for ii in itemr:
                            t = re.findall('p\s*style.+?>([^<>]+)<', ii)[0]
                            t = re.sub('(\[.*?\])|(<.+?>)', '', t)
                            t1 = re.sub('(\.|\(|\[|\s)(\d{4}|S\d*E\d*|S\d+|3D)(\.|\)|\]|\s|)(.+|)', '', t)

                            if not cleantitle.get(t1) == cleantitle.get(title): raise Exception()

                            y = re.findall('[\.|\(|\[|\s](\d{4}|S\d*E\d*|S\d*)[\.|\)|\]|\s]', t)[-1].upper()

                            if not y == hdlr: raise Exception()

                            try:
                                size = re.findall('((?:\d+\.\d+|\d+\,\d+|\d+) (?:GB|GiB|MB|MiB))', ii)[0]
                                div = 1 if size.endswith(('GB', 'GiB')) else 1024
                                size = float(re.sub('[^0-9|/.|/,]', '', size))/div
                                size = '%.2f GB' % size
                            except:
                                pass

                            data = ii
                            data = dom_parser2.parse_dom(data, 'a', req='href')

                            if size:
                                u = [(t, i.attrs['href'], size) for i in data]
                            else:
                                u = [(t, i.attrs['href']) for i in data]
                            items += u
                    else:
                        try:
                            size = re.findall('((?:\d+\.\d+|\d+\,\d+|\d+) (?:GB|GiB|MB|MiB))', data)[0]
                            div = 1 if size.endswith(('GB', 'GiB')) else 1024
                            size = float(re.sub('[^0-9|/.|/,]', '', size))/div
                            size = '%.2f GB' % size
                        except:
                            pass

                        data = dom_parser2.parse_dom(data, 'a', req='href')

                        if size:
                            u = [(t, i.attrs['href'], size) for i in data]
                        else:
                            u = [(t, i.attrs['href']) for i in data]  
                        items += u

                except:
                    pass

            for item in items:
                try:
                    name = item[0]
                    name = client.replaceHTMLCodes(name)

                    quality, info = source_utils.get_release_quality(name, item[1])

                    url = item[1]

                    if item[2]:
                        if not info: info = []
                        info.append(item[2])

                    if 'go4up.com' in url:
                        try:
                            headers = {'User-Agent': self.useragent}
                            r = client.request(url, headers=headers)
                            rf = re.findall('url\:\s*"([^"]+)"', r)[0]
                            urlr = 'https://go4up.com/%s' % rf
                            r1 = client.request(urlr, headers=headers)
                            # try:
                                # if not info: info = []
                                # size = re.findall('center>\s*<h3>.+?((?:\d+\.\d+|\d+\,\d+|\d+) (?:GB|GiB|MB|MiB)).+?<\/h3', r)[0]
                                # div = 1 if size.endswith(('GB', 'GiB')) else 1024
                                # size = float(re.sub('[^0-9|/.|/,]', '', size))/div
                                # size = '%.2f GB' % size
                                # info.append(size)
                            # except:
                                # pass
                            info = ' | '.join(info)
                            items1 = json.loads(r1)
                            for i in items1:
                                link = i['link']
                                link = re.findall('">([^<>]+)<\/a', link)[0]
                                url = link.strip()
                                hostnum = url.rsplit('/', 1)[-1]

                                if hostnum == '2': hoster = 'uptobox'
                                elif hostnum == '4': hoster = 'filerio'
                                elif hostnum == '5': hoster = 'depositfiles'
                                elif hostnum == '6': hoster = '2shared'
                                elif hostnum == '12': hoster = 'filefactory'
                                elif hostnum == '13': hoster = 'uploaded.net'
                                elif hostnum == '17': hoster = 'turbobit'
                                elif hostnum == '18': hoster = 'free'
                                elif hostnum == '33': hoster = 'rapidgator'
                                elif hostnum == '34': hoster = 'share-online'
                                elif hostnum == '35': hoster = '4shared'
                                elif hostnum == '36': hoster = 'sendspace'
                                elif hostnum == '41': hoster = 'hitfile'
                                elif hostnum == '42': hoster = 'zippyshare'
                                elif hostnum == '43': hoster = '1fichier'
                                elif hostnum == '50': hoster = 'mega'
                                elif hostnum == '55': hoster = 'uppit'
                                elif hostnum == '57': hoster = 'tusfiles'
                                elif hostnum == '61': hoster = 'solidfiles'
                                elif hostnum == '64': hoster = 'filepup'
                                elif hostnum == '65': hoster = 'oboom'
                                elif hostnum == '68': hoster = 'bigfile'
                                elif hostnum == '76': hoster = 'userscloud'
                                elif hostnum == '78': hoster = 'filecloud'
                                elif hostnum == '80': hoster = 'openload'
                                elif hostnum == '82': hoster = 'speedvideo'
                                elif hostnum == '83': hoster = 'nitroflare'
                                elif hostnum == '85': hoster = 'clicknupload'
                                elif hostnum == '87': hoster = 'uploadboy'
                                elif hostnum == '90': hoster = 'rockfile'
                                elif hostnum == '91': hoster = 'faststore'
                                elif hostnum == '92': hoster = 'salefiles'
                                elif hostnum == '94': hoster = 'downace'
                                elif hostnum == '95': hoster = 'datafile'
                                elif hostnum == '97': hoster = 'katfile'
                                elif hostnum == '98': hoster = 'uploadgig'
                                elif hostnum == '99': hoster = 'owndrives'
                                elif hostnum == '100': hoster = 'cloudyfiles'

                                valid, host = source_utils.is_host_valid(hoster, hostDict)
                                if valid:
                                    sources.append({'source': host, 'quality': quality, 'language': 'en', 'url': url, 'info': info, 'direct': False, 'debridonly': True})
                        except:
                            pass

                    if not url.startswith('http'): continue
                    if any(x in url for x in ['.rar', '.zip', '.iso']): raise Exception()
                    url = client.replaceHTMLCodes(url)
                    url = url.encode('utf-8')

                    valid, host = source_utils.is_host_valid(url, hostDict)
                    if not valid: continue
                    host = client.replaceHTMLCodes(host)
                    host = host.encode('utf-8')

                    sources.append({'source': host, 'quality': quality, 'language': 'en', 'url': url, 'info': ' | '.join(info), 'direct': False, 'debridonly': True})
                except:
                    pass

            return sources
        except:
            log_utils.log('>>>> %s TRACE <<<<\n%s' % (__file__.upper().split('\\')[-1].split('.')[0], traceback.format_exc()), log_utils.LOGDEBUG)
            return sources


    def resolve(self, url):
        if 'go4up.com' in url:
            try:
                url = re.sub('https', 'http', url)
                url = re.sub('//go4up', '//dl.go4up', url)
                headers = {'User-Agent': self.useragent}
                r = client.request(url, headers=headers)
                r = client.parseDOM(r, 'div', attrs={'id': 'linklist'})[0]
                url = client.parseDOM(r, 'a', ret='href')[0]
            except:
                return
        return url
