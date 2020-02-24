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
        self.domains = ['real-debrid.com']
        self.base_link = 'https://api.real-debrid.com'
        self.torrents_link = '/rest/1.0/torrents?limit=100&auth_token=%s'
        self.torrentsinfo_link = '/rest/1.0/torrents/info/%s?auth_token=%s'
        self.unrestrict_link = '/rest/1.0/unrestrict/link/?auth_token=%s'
        self.api_key = control.setting('rdcached.apikey')


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

            if not control.setting('rdcached.providers') == 'true': return sources
            if self.api_key == '': return sources

            data = urlparse.parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])

            title = data['tvshowtitle'] if 'tvshowtitle' in data else data['title']

            if 'tvshowtitle' in data:
                season = 'S%02d' % int(data['season'])
                episode = 'E%02d' % int(data['episode'])
            hdlr = 'S%02dE%02d' % (int(data['season']), int(data['episode'])) if 'tvshowtitle' in data else data['year']

            checktorr_r = self.checkrdcache()
            result = json.loads(checktorr_r)

            items = []

            for i in result:
                try:
                    if not i['status'] == 'downloaded': raise Exception()

                    name = i['filename']
                    t = re.sub('(\.|\(|\[|\s)(\d{4}|S\d*E\d*|S\d+|3D)(\.|\)|\]|\s|)(.+|)', '', name)
                    if not cleantitle.get(t) == cleantitle.get(title): raise Exception()
                    y = re.findall('[\.|\(|\[|\s](\d{4}|(?:S|s)\d*(?:E|e)\d*|(?:S|s)\d*)[\.|\)|\]|\s]', name)[-1].upper()

                    if not y == hdlr:
                        if 'tvshowtitle' in data:
                            if not y == season:
                                raise Exception()
                            else:
                                items += self.getSeasonItems(i, hdlr)
                    else:
                        info_url = urlparse.urljoin(self.base_link, self.torrentsinfo_link % (i['id'], self.api_key))

                        r = client.request(info_url)

                        torr_info = json.loads(r)
                        links = torr_info['links']
                        if len(links) == 0: raise Exception()
                        links = links[0]

                        u = [(name, links)]
                        items += u
                except:
                    pass

            for item in items:
                try:
                    name = item[0]
                    quality, info = source_utils.get_release_quality(name, None)
                    filetype = source_utils.getFileType(name)
                    info += [filetype.strip(), name]
                    info = filter(None, info)
                    info = ' | '.join(info)

                    sources.append({'source': 'RDCACHED', 'quality': quality, 'language': 'en', 'url': item[1], 'info': info, 'direct': False, 'debridonly': False, 'cached': True})
                except:
                    pass

            return sources
        except:
            log_utils.log('>>>> %s TRACE <<<<\n%s' % (__file__.upper().split('\\')[-1].split('.')[0], traceback.format_exc()), log_utils.LOGDEBUG)
            return sources


    def resolve(self, url):
        try:
            unrestrict_url = urlparse.urljoin(self.base_link, self.unrestrict_link % self.api_key)
            post = {'link': url}
            unres = client.request(unrestrict_url, post=post)
            u = json.loads(unres)
            url = u['download']
            return url
        except:
            return


    def getSeasonItems(self, item, hdlr):
        try:
            info_url = urlparse.urljoin(self.base_link, self.torrentsinfo_link % (item['id'], self.api_key))
            r = client.request(info_url)

            torr_info = json.loads(r)
            files = torr_info['files']
            filename = [i['path'].split('/')[-1] for i in files if i['selected'] == 1]
            links = torr_info['links']

            u = []
            items = [(x, y) for x, y in zip(filename, links)]

            for i in items:
                try:
                    y = re.findall('[\.|\(|\[|\s]((?:S|s)\d*(?:E|e)\d*)[\.|\)|\]|\s]', i[0])[-1].upper()
                    if not y == hdlr: raise Exception()
                    u += [(i[0], i[1])]
                except:
                    pass

            return u
        except:
            log_utils.log('>>>> %s TRACE <<<<\n%s' % (__file__.upper().split('\\')[-1].split('.')[0], traceback.format_exc()), log_utils.LOGDEBUG)
            return u


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
                    checktorr = urlparse.urljoin(self.base_link, self.torrents_link % self.api_key)
                    r = client.request(checktorr)
                    with open(rdfile, 'wb') as fh: fh.write(r)
                except:
                    pass

            return r

        except:
            log_utils.log('>>>> %s TRACE <<<<\n%s' % (__file__.upper().split('\\')[-1].split('.')[0], traceback.format_exc()), log_utils.LOGDEBUG)
            return
