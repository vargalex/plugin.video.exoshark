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
        domains_ = ['b25saW5lZmlsbWVrLnVjb3oub3Jn']
        self.domains = [x.decode('base64') for x in domains_]
        self.base_link = 'aHR0cDovL29ubGluZWZpbG1lay51Y296Lm9yZw=='.decode('base64')


    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            loctitle = localtitle
            titlefilter = ['-', ':', ';', ',', '.', '*', '?', '!', '"', '\'']
            for unw in titlefilter:
                if unw in localtitle: loctitle = localtitle.split(unw, 1)[0].strip()
            # query0 = urlparse.urljoin(self.base_link, '/forum/0-0-0-6')
            # r0 = client.request(query0)
            # s_post = client.parseDOM(r0, 'form', attrs={'name': 'searchform'})[0]
            # s_post_res = re.search('<input type="hidden" name="([^"]+)" value="([^"]+)"', s_post)
            # s_post_res1 = s_post_res.group(1); s_post_res2 = s_post_res.group(2)
            query = urlparse.urljoin(self.base_link, '/forum/')
            post = urllib.urlencode({'kw': loctitle, 'fid': '0', 'user': '', 'o1': '0', 'o2': '0', 'o3': '0', 'a': '6'})#s_post_res1: s_post_res2})
            r = client.request(query.rsplit('/', 1)[0], post=post)
            result = client.parseDOM(r, 'table', attrs={'class': 'gTable'})[0]
            result = client.parseDOM(result, 'tr')

            result = [i for i in result if '/forum/2' in i or '/forum/4' in i]
            result = [(client.parseDOM(i, 'a')[0], i) for i in result]
            result = [i[1] for i in result if cleantitle.get(localtitle) == cleantitle.get(i[0].split('(', 1)[0].strip().encode('utf-8'))]
            if len(result) == 0: raise Exception()

            result = [(re.search('(?:>\s*|\(\s*|\)\s*)(\d{4})(?:\s*\.|\s*\)|\s*)', i).group(1), i) for i in result]
            result = [i[1] for i in result if year == i[0]]

            urlr = client.parseDOM(result, 'a', ret='href')[0]
            url = urlparse.urljoin(self.base_link, urlr)
            url = url.encode('utf-8')
            return (url, '', '')
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

            episode = episode.zfill(2)
            seasont = u'%s.\xe9vad' % (season)
            seasontr = '%s.\\xe9vad' % (season)
            loctvshowtitle = localtvshowtitle

            titlefilter = ['-', ':', ';', ',', '.', '*', '?', '!', '"', '\'']
            for unw in titlefilter:
                if unw in localtvshowtitle: loctvshowtitle = localtvshowtitle.split(unw)[0].strip()
            # query0 = urlparse.urljoin(self.base_link, '/forum/0-0-0-6')
            # r0 = client.request(query0)
            # s_post = client.parseDOM(r0, 'form', attrs={'name': 'searchform'})[0]
            # s_post_res = re.search('<input type="hidden" name="([^"]+)" value="([^"]+)"', s_post)
            # s_post_res1 = s_post_res.group(1); s_post_res2 = s_post_res.group(2)
            query = urlparse.urljoin(self.base_link, '/forum/')
            post = urllib.urlencode({'kw': loctvshowtitle, 'fid': '0', 'user': '', 'o1': '0', 'o2': '0', 'o3': '0', 'a': '6'})#s_post_res1: s_post_res2})
            r = client.request(query, post=post)
            result = client.parseDOM(r, 'table', attrs={'class': 'gTable'})[0]
            result = client.parseDOM(result, 'tr')

            result = [i for i in result if '/forum/3' in i or '/forum/4' in i]
            result = [(client.parseDOM(i, 'a')[0], i) for i in result]
            result = [i[1] for i in result if cleantitle.get(localtvshowtitle) == cleantitle.get(i[0].split('(', 1)[0].split(seasontr, 1)[0].split(seasont.encode('utf-8'), 1)[0].strip().encode('utf-8'))]
            if len(result) == 0: raise Exception()

            result = [(re.search('(?:\(|)\s*(\d+)\.\s*[^.]+vad\s*(?:\)|)\s*<', i).group(1), i) for i in result]
            result = [i[1] for i in result if season == i[0]]

            urlr = client.parseDOM(result, 'a', ret='href')[0]
            url = urlparse.urljoin(self.base_link, urlr + '?s=s%se%s' % (season, episode))
            url = url.encode('utf-8')
            return (url, season, episode)
        except:
            log_utils.log('>>>> %s TRACE <<<<\n%s' % (__file__.upper().split('\\')[-1].split('.')[0], traceback.format_exc()), log_utils.LOGDEBUG)
            return


    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []
            if url[0] == None: return sources

            r = client.request(url[0])

            if url[1].isdigit():
                result = client.parseDOM(r, 'td', attrs={'class': 'posttdMessage'})[0]
                if '</a> <br /><br />' in result:
                    result = result.split('</a> <br /><br /')
                    result = [i for i in result if 'S%sE%s' % (url[1], url[2]) in i]
                    for i in result:
                        tag = re.search('>([^\>]+[\.]S\d+E\d+[\.][^\<]+)<br \/><a (?:class="link"|href=")', i).group(1)
                        items = re.findall('href="([^"]+)"', i)
                else:
                    tag = re.search('<b>(.+?)<br \/>', result).group(1)
                    items = re.findall('href="([^"]+)"', result)
            else:
                result = client.parseDOM(r, 'td', attrs={'class': 'posttdMessage'})[0]
                tag = client.parseDOM(r, 'span', attrs={'class': 'thDescr'})[0]
                items = re.findall('href="([^"]+)"', result)

            if items == None: return sources

            tag = tag.lower()

            if 'cam' in tag or 'hdts' in tag: quality = 'CAM'
            else: quality = 'SD'
            info = []
            if not 'sub' in tag: info.append('szinkron')

            locDict = [(i.rsplit('.', 1)[0], i) for i in hostDict]         

            for item in items:
                try: 
                    host = re.search('(?:\/\/|\.)([^www][\w]+[.][\w]+)\/', item).group(1)
                    host = host.split('.', 1)[0].strip().lower()
                    host = [x[1] for x in locDict if host == x[0]][0]
                    if not host in hostDict: raise Exception()
                    host = client.replaceHTMLCodes(host)
                    host = host.encode('utf-8')
                    url = client.replaceHTMLCodes(item)
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
