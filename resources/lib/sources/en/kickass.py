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
from resources.lib.modules import cfscrape
from resources.lib.modules import client
from resources.lib.modules import control
from resources.lib.modules import cleantitle
from resources.lib.modules import source_utils
from resources.lib.modules import log_utils


class source:
    def __init__(self):
        self.priority = 0
        self.language = ['en']
        self.domains = ['kat.sx']
        self.base_link = 'https://kat.sx'
        self.search_link = '/usearch/%s/?field=size&sorder=desc'
        self.scraper = cfscrape.create_scraper()

        self.pm_base_link = 'https://www.premiumize.me'
        self.pm_checkcache_link = '/api/torrent/checkhashes?apikey=%s&hashes[]=%s&apikey=%s'
        self.pm_dl_link = '/api/transfer/directdl?apikey=%s&src=%s'
        self.pm_api_key = control.setting('pmcached.apikey')

        self.rd_base_link = 'https://api.real-debrid.com'
        self.rd_checklib_link = '/rest/1.0/torrents?limit=100&auth_token=%s'
        self.rd_checkcache_link = '/rest/1.0/torrents/instantAvailability/%s?auth_token=%s'
        self.rd_addmagnet_link = '/rest/1.0/torrents/addMagnet?auth_token=%s'
        self.rd_torrentsinfo_link = '/rest/1.0/torrents/info/%s?auth_token=%s'
        self.rd_selectfiles_link = '/rest/1.0/torrents/selectFiles/%s?auth_token=%s'
        self.rd_unrestrict_link = '/rest/1.0/unrestrict/link/?auth_token=%s'
        self.rd_api_key = control.setting('rdcached.apikey')


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

            if not control.setting('pmcached.providers') == 'true' and not control.setting('rdcached.providers') == 'true': return sources
            if self.pm_api_key == '' and self.rd_api_key == '': return sources

            data = urlparse.parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])

            title = data['tvshowtitle'] if 'tvshowtitle' in data else data['title']

            hdlr = 'S%02dE%02d' % (int(data['season']), int(data['episode'])) if 'tvshowtitle' in data else data['year']

            query = '%s S%02dE%02d' % (data['tvshowtitle'], int(data['season']), int(data['episode'])) if 'tvshowtitle' in data else '%s %s' % (data['title'], data['year'])
            query = re.sub('(\\\|/| -|:|;|\*|\?|"|\'|<|>|\|)', ' ', query)

            url = self.search_link % urllib.quote_plus(query)
            url = urlparse.urljoin(self.base_link, url)

            r = self.scraper.get(url).content

            result = client.parseDOM(r, 'table', attrs={'class': 'data'})[0]
            result = client.parseDOM(result, 'tr')
            result = [i for i in result if 'torType Video' in i]
            result = [(re.findall('href="(magnet[^"]+)"', i)[0],
                       client.parseDOM(i, 'a', attrs={'class': 'cellMainLink'})[0],
                       client.parseDOM(i, 'td', attrs={'class': 'nobr center'})[0]) for i in result[1:]]

            items = []

            for item in result:
                try:
                    name = item[1]
                    magnetlink = item[0]

                    size = ''
                    try:
                        size = item[2].replace('&nbsp;', ' ')
                        size = re.findall('((?:\d+\.\d+|\d+\,\d+|\d+) (?:GB|GiB|MB|MiB))', size)[0]
                        div = 1 if size.endswith(('GB', 'GiB')) else 1024
                        size = float(re.sub('[^0-9|/.|/,]', '', size))/div
                        size = '%.2f GB' % size
                    except:
                        pass

                    t = re.sub('(\.|\(|\[|\s)(\d{4}|S\d*E\d*|S\d+|3D)(\.|\)|\]|\s|)(.+|)', '', name)
                    t = re.sub('<.+?>', '', t)
                    if not cleantitle.get(t) == cleantitle.get(title): raise Exception()
                    y = re.findall('[\.|\(|\[|\s](\d{4}|(?:S|s)\d*(?:E|e)\d*|(?:S|s)\d*)[\.|\)|\]|\s]', name)[-1].upper()
                    if not y == hdlr: raise Exception()

                    u = [(name, magnetlink, size)]
                    items += u
                except:
                    pass

            if control.setting('pmcached.providers') == 'true' and not self.pm_api_key == '':
                for item in items:
                    try:
                        _hash = re.findall('btih:(.*?)\W', item[1])[0]
                        checkurl = urlparse.urljoin(self.pm_base_link, self.pm_checkcache_link % (self.pm_api_key, _hash, self.pm_api_key))
                        r = client.request(checkurl)
                        if not 'finished' in r: raise Exception()

                        name = client.replaceHTMLCodes(item[0])
                        quality, info = source_utils.get_release_quality(name, None)
                        filetype = source_utils.getFileType(name)
                        info += [filetype.strip(), name]
                        info = filter(None, info)
                        info = ' | '.join(info)
                        if not item[2] == '':
                            info = '%s | %s' % (item[2], info)
                        url = 'magnet:?xt=urn:btih:%s' % _hash

                        sources.append({'source': 'PMCACHED', 'quality': quality, 'language': 'en', 'url': url, 'info': info, 'direct': False, 'debridonly': False, 'cached': True})
                    except:
                        pass

            if control.setting('rdcached.providers') == 'true' and not self.rd_api_key == '':
                checktorr_r = self.checkrdcache()
                checktorr_result = json.loads(checktorr_r)

                for item in items:
                    try:
                        _hash = re.findall('btih:(.*?)\W', item[1])[0]
                        _hash = _hash.lower()

                        url = ''
                        for i in checktorr_result:
                            try:
                                if _hash == i['hash'] and i['status'] == 'downloaded':
                                    url = i['links'][0]
                                    break
                            except:
                                pass

                        if url == '':
                            checkurl = urlparse.urljoin(self.rd_base_link, self.rd_checkcache_link % (_hash, self.rd_api_key))
                            r = client.request(checkurl)
                            checkinstant = json.loads(r)
                            checkinstant = checkinstant[_hash]

                            checkinstant_num = 0
                            try:
                                checkinstant_num = len(checkinstant['rd'])
                            except:
                                pass

                            if checkinstant_num == 0: raise Exception()
                            url = 'rdmagnet:?xt=urn:btih:%s' % _hash

                        if url == '': raise Exception()

                        name = client.replaceHTMLCodes(item[0])
                        quality, info = source_utils.get_release_quality(name, None)
                        filetype = source_utils.getFileType(name)
                        info += [filetype.strip(), name]
                        info = filter(None, info)
                        info = ' | '.join(info)
                        if not item[2] == '':
                            info = '%s | %s' % (item[2], info)

                        sources.append({'source': 'RDCACHED', 'quality': quality, 'language': 'en', 'url': url, 'info': info, 'direct': False, 'debridonly': False, 'cached': True})
                    except:
                        pass

            return sources
        except:
            log_utils.log('>>>> %s TRACE <<<<\n%s' % (__file__.upper().split('\\')[-1].split('.')[0], traceback.format_exc()), log_utils.LOGDEBUG)
            return sources


    def resolve(self, url):
        try:
            if url.startswith('magnet'):
                url = urlparse.urljoin(self.pm_base_link, self.pm_dl_link % (self.pm_api_key, url))
                r = client.request(url)
                items = json.loads(r)
                if not items['status'] == 'success': raise Exception()
                items = items['content']
                items = [i for i in items if not i['stream_link'] == False]
                items = [(i['link'], i['size']) for i in items]
                items = sorted(items, key=lambda x: int(x[1]), reverse = True)
                url = items[0][0]
            elif url.startswith('rdmagnet'):
                addmagnet_url = urlparse.urljoin(self.rd_base_link, self.rd_addmagnet_link % self.rd_api_key)
                url = url.replace('rdmagnet', 'magnet')
                post = {'magnet': url}
                r = client.request(addmagnet_url, post=post)
                result = json.loads(r)
                torrent_id = result['id']
                torrentsinfo_url = urlparse.urljoin(self.rd_base_link, self.rd_torrentsinfo_link % (torrent_id, self.rd_api_key))
                r = client.request(torrentsinfo_url)
                u = json.loads(r)
                file_id = [(i['id'], i['path'], i['bytes']) for i in u['files']]
                file_id = sorted(file_id, key=lambda x: x[2], reverse = True)
                file_id = file_id[0][0]
                selectfiles_url = urlparse.urljoin(self.rd_base_link, self.rd_selectfiles_link % (torrent_id, self.rd_api_key))
                post = {'files': file_id}
                select = client.request(selectfiles_url, post=post)
                r1 = client.request(torrentsinfo_url)
                u1 = json.loads(r1)
                res_link = u1['links'][0]
                unrestrict_url = urlparse.urljoin(self.rd_base_link, self.rd_unrestrict_link % self.rd_api_key)
                post = {'link': res_link}
                unres = client.request(unrestrict_url, post=post)
                u2 = json.loads(unres)
                url = u2['download']
            elif 'real-debrid.com/d/' in url:
                unrestrict_url = urlparse.urljoin(self.rd_base_link, self.rd_unrestrict_link % self.rd_api_key)
                post = {'link': url}
                unres = client.request(unrestrict_url, post=post)
                u = json.loads(unres)
                url = u['download']
            return url
        except:
            return


    def checkrdcache(self):
        try:
            import os
            rdfile = os.path.join(control.dataPath, 'rdcache.v')

            r = ''
            try:
                with open(rdfile, 'rb') as fh: r = fh.read()
            except:
                pass

            if r == '':
                try:
                    checktorr = urlparse.urljoin(self.rd_base_link, self.rd_checklib_link % self.rd_api_key)
                    r = client.request(checktorr)
                    with open(rdfile, 'wb') as fh: fh.write(r)
                except:
                    pass

            return r

        except:
            log_utils.log('>>>> %s TRACE <<<<\n%s' % (__file__.upper().split('\\')[-1].split('.')[0], traceback.format_exc()), log_utils.LOGDEBUG)
            return
