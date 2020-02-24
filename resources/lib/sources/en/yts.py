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
from resources.lib.modules import client
from resources.lib.modules import control
from resources.lib.modules import cleantitle
from resources.lib.modules import source_utils
from resources.lib.modules import log_utils


class source:
    def __init__(self):
        self.priority = 0
        self.language = ['en']
        self.domains = ['yts.am']
        self.base_link = 'https://yts.am'
        self.search_link = '/api/v2/list_movies.json?query_term=%s'

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


    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []

            if url == None: return sources

            if not control.setting('pmcached.providers') == 'true' and not control.setting('rdcached.providers') == 'true': return sources
            if self.pm_api_key == '' and self.rd_api_key == '': return sources

            data = urlparse.parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])

            title = data['title']

            hdlr = data['year']

            imdbid = data['imdb']

            url = self.search_link % imdbid
            url = urlparse.urljoin(self.base_link, url)

            r = client.request(url)
            result = json.loads(r)

            try:
                moviesdata = result['data']['movies']
            except:
                moviesdata = None

            if moviesdata == None: return sources

            out = []

            for i in moviesdata:
                try:
                    data = (i['imdb_code'], i['torrents'])
                    out.append(data)
                except:
                    pass

            if control.setting('rdcached.providers') == 'true' and not self.rd_api_key == '':
                checktorr_r = self.checkrdcache()
                checktorr_result = json.loads(checktorr_r)

            for ii in out:
                try:
                    _imdb = ii[0]
                    if not _imdb == imdbid: raise Exception()
                    torrdata = [(i['hash'], i['size_bytes'], i['quality']) for i in ii[1]]

                    if control.setting('pmcached.providers') == 'true' and not self.pm_api_key == '':
                        for iii in torrdata:
                            try:
                                _hash = iii[0]
                                checkurl = urlparse.urljoin(self.pm_base_link, self.pm_checkcache_link % (self.pm_api_key, _hash, self.pm_api_key))
                                r = client.request(checkurl)
                                if not 'finished' in r: raise Exception()

                                size = ''
                                try:
                                    size = iii[1]
                                    size = float(size)/1073741824
                                    size = '%.2f GB' % size
                                except:
                                    pass
                                info = []
                                info += [size]
                                if '3D' in iii[2]: info += ['3D']
                                info = filter(None, info)
                                info = ' | '.join(info)

                                if '1080p' in iii[2]: quality = '1080p'
                                elif '720p' in iii[2]: quality = '720p'
                                else: quality = 'SD'

                                url = 'magnet:?xt=urn:btih:%s' % _hash

                                sources.append({'source': 'PMCACHED', 'quality': quality, 'language': 'en', 'url': url, 'info': info, 'direct': False, 'debridonly': False, 'cached': True})
                            except:
                                pass

                    if control.setting('rdcached.providers') == 'true' and not self.rd_api_key == '':
                        for iii in torrdata:
                            try:
                                _hash = iii[0]
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

                                size = ''
                                try:
                                    size = iii[1]
                                    size = float(size)/1073741824
                                    size = '%.2f GB' % size
                                except:
                                    pass
                                info = []
                                info += [size]
                                if '3D' in iii[2]: info += ['3D']
                                info = filter(None, info)
                                info = ' | '.join(info)

                                if '1080p' in iii[2]: quality = '1080p'
                                elif '720p' in iii[2]: quality = '720p'
                                else: quality = 'SD'

                                sources.append({'source': 'RDCACHED', 'quality': quality, 'language': 'en', 'url': url, 'info': info, 'direct': False, 'debridonly': False, 'cached': True})
                            except:
                                pass

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
