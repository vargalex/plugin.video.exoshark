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
        self.domains = ['premiumize.me']
        self.base_link = 'https://www.premiumize.me'
        self.transferlist_link = '/api/transfer/list?apikey=%s'
        self.folderlist_link = '/api/folder/list?apikey=%s'
        self.api_key = control.setting('pmcached.apikey')


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

            if not control.setting('pmcached.providers') == 'true': return sources
            if self.api_key == '': return sources

            data = urlparse.parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])

            title = data['tvshowtitle'] if 'tvshowtitle' in data else data['title']

            hdlr = 'S%02dE%02d' % (int(data['season']), int(data['episode'])) if 'tvshowtitle' in data else data['year']

            query = '%s S%02dE%02d' % (data['tvshowtitle'], int(data['season']), int(data['episode'])) if 'tvshowtitle' in data else '%s %s' % (data['title'], data['year'])
            query = re.sub('(\\\|/| -|:|;|\*|\?|"|\'|<|>|\|)', ' ', query)

            url = self.folderlist_link % self.api_key
            url = urlparse.urljoin(self.base_link, url)
            r = client.request(url)

            result = json.loads(r)

            if not result['status'] == 'success': raise Exception()
            pmitems = result['content']

            items = []

            for item in pmitems:
                try:
                    name, id, type = item['name'], item['id'], item['type']
                    t = re.sub('(\.|\(|\[|\s)(\d{4}|S\d*E\d*|S\d+|3D)(\.|\)|\]|\s|)(.+|)', '', name)
                    if not cleantitle.get(t) == cleantitle.get(title): raise Exception()
                    y = re.findall('[\.|\(|\[|\s](\d{4}|(?:S|s)\d*(?:E|e)\d*|(?:S|s)\d*)[\.|\)|\]|\s]', name)[-1].upper()
                    if not y == hdlr: raise Exception()
                    if type == 'folder':
                        params = {'id': id, 'includebreadcrumbs': 'false'}
                        params = '&' + urllib.urlencode(params)
                        url = self.folderlist_link % self.api_key
                        url = urlparse.urljoin(self.base_link, url + params)
                    elif type == 'file':
                        if item['stream_link'] == False: raise Exception()
                        url = item['link']
                    u = [(name, url)]
                    items += u
                except:
                    pass

            for item in items:
                try:
                    name = client.replaceHTMLCodes(item[0])
                    quality, info = source_utils.get_release_quality(name, None)
                    filetype = source_utils.getFileType(name)
                    info += [filetype.strip(), name]
                    info = filter(None, info)
                    info = ' | '.join(info)

                    sources.append({'source': 'PMCACHED', 'quality': quality, 'language': 'en', 'url': item[1], 'info': info, 'direct': False, 'debridonly': False, 'cached': True})
                except:
                    pass
                    
            return sources
        except:
            log_utils.log('>>>> %s TRACE <<<<\n%s' % (__file__.upper().split('\\')[-1].split('.')[0], traceback.format_exc()), log_utils.LOGDEBUG)
            return sources


    def resolve(self, url):
        try:
            if self.base_link in url:
                r = client.request(url)
                items = json.loads(r)
                if not items['status'] == 'success': raise Exception()
                items = items['content']
                items = [i for i in items if i['type'] == 'file']
                items = [i for i in items if not i['stream_link'] == False]
                items = [(i['link'], i['size']) for i in items]
                items = sorted(items, key=lambda x: int(x[1]), reverse = True)
                url = items[0][0]
                return url
            else:
                return url
        except:
            return
