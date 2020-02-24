# -*- coding: utf-8 -*-

import urlparse
import re
import requests

from resources.lib.modules import cfscrape
from resources.lib.modules import dom_parser
from resources.lib.modules import source_utils
from resources.lib.modules import cleantitle


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['de']
        self.domains = ['cinematrix.to']
        self.base_link = 'http://cinematrix.to/'
        self.search_link = 'de/suche.html?q=%s'
        self.hoster_link = self.base_link + 'ajax/getHoster%s.php'
        self.hoster_mirror_link = self.base_link + 'ajax/refresh%sMirror.php'
        self.stream_link = self.base_link + 'ajax/get%sStream.php'
        self.scraper = cfscrape.create_scraper()

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            url = self.__search(imdb, [title, localtitle] + source_utils.aliases_to_array(aliases))
            return url
        except:
            return

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            url = self.__search(imdb, [tvshowtitle, localtvshowtitle] + source_utils.aliases_to_array(aliases))
            return url
        except:
            return

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            urlparts = re.findall('(.*staffel\/)\d+(.*?)\d+(.*)', url)[0]
            url = urlparts[0] + season + urlparts[1] + episode + urlparts[2]
            return url
        except:
            return

    def sources(self, url, hostDict, hostprDict):
        sources = []
        try:
            if not url:
                return sources
            url = urlparse.urljoin(self.base_link, url)
            content = self.scraper.get(url).content
            cookies = requests.utils.dict_from_cookiejar(self.scraper.cookies)

            content_id = re.findall('\d+', dom_parser.parse_dom(content, 'body')[0].attrs['onload'])[0]

            link = self.hoster_link % ('Filme' if 'film' in url else 'Serien')
            if 'film' in url:
                params = self.getParams(content_id, cookies)
            else:
                temp = re.findall('.*staffel\/(\d+).*?(\d+)', url)[0]
                params = self.getParams(content_id, cookies, s=temp[0], e=temp[1])

            content = self.scraper.post(link, headers=self.getHeader(url), data=params).content

            links = dom_parser.parse_dom(content, 'li')
            links = [(i.attrs['title'], i.attrs['onclick'], dom_parser.parse_dom(i, 'img')[0].attrs['title'], re.findall('/(\d+)', dom_parser.parse_dom(i, 'div', attrs={'class': 'col2'})[0].content)[0]) for i in links]

            for hoster, params, quality, mirrorcount in links:
                valid, hoster = source_utils.is_host_valid(hoster, hostDict)
                if not valid: continue

                url_dict = self.get_url_dict(params, url, True if 'film' in url else False)
                quality = source_utils.get_release_quality(quality)[0]
                for i in range(1, int(mirrorcount)+1):
                    url_dict['zm'] = unicode(i)
                    sources.append({'source': hoster, 'quality': quality, 'language': 'de', 'url': url_dict.copy(), 'direct': False, 'debridonly': False, 'checkquality': False})

            return sources
        except:
            return sources

    def resolve(self, url):
        try:
            content = self.scraper.get(url['url']).content
            cookies = requests.utils.dict_from_cookiejar(self.scraper.cookies)
            link = self.hoster_mirror_link % ('Movie' if url['isMovie'] else 'Series')

            params = self.getParams(url['content_id'], cookies, h=url['h'], ut=url['ut'], zm=url['zm'], bq=url['bq'], sq=url['sq'], st=url['bq'], fo=url['sq'])

            content = self.scraper.post(link, headers=self.getHeader(url['url']), data=params).content
            link = self.stream_link % ('Movie' if url['isMovie'] else 'Series')

            params = self.getParams(url['content_id'], cookies, h=url['h'], m=content, s=url['bq'], e=url['sq'])

            content = self.scraper.post(link, headers=self.getHeader(url['url']), data=params).content
            link = dom_parser.parse_dom(content, 'a')[0].attrs['href']

            return link
        except:
            return

    def __search(self, imdb, titles):
        try:
            t = [cleantitle.get(i) for i in set(titles) if i]
            result = self.scraper.get(urlparse.urljoin(self.base_link, self.search_link % imdb)).content

            links = dom_parser.parse_dom(result, 'ul', attrs={'id': 'dataHover'})
            links = dom_parser.parse_dom(links, 'li')
            links = [(dom_parser.parse_dom(i, 'a')[0].attrs['href'], dom_parser.parse_dom(i, 'span')[0]) for i in links]
            links = [(i[0], re.findall('(.*?)<', i[1].content)[0]) for i in links]

            links = [i[0] for i in links if cleantitle.get(i[1]) in t]

            if len(links) > 0:
                return source_utils.strip_domain(links[0])
            return
        except:
            return

    def getHeader(self, url):
        return {'Referer': url, 'Host': 'www.%s' % self.domains[0], 'Origin': 'http://www.%s' % self.domains[0]}

    def getParams(self, content_id, cookies, h='', ut='', zm='', bq='', sq='', st='', fo='', s='', e='', m=''):
        return {'c': cookies, 'v': content_id, 'h': h, 'ut': ut, 'zm': zm, 'bq': bq, 'sq': sq, 'st': st, 'fo': fo, 's': s, 'e': e, 'm': m}

    def get_url_dict(self, params, url, isMovie):
        url_dict = {}
        onclick = params.split(';')
        splitted = re.findall('\((.*?)\)', onclick[0])[0].split(',')
        url_dict['content_id'] = splitted[0]
        url_dict['h'] = splitted[1]
        splitted = re.findall('\((.*?)\)', onclick[1])[0].split(',')
        url_dict['ut'] = splitted[5]
        url_dict['bq'] = splitted[6]
        url_dict['sq'] = splitted[7]
        url_dict['isMovie'] = isMovie
        url_dict['url'] = url
        return url_dict
