# -*- coding: utf-8 -*-

import re, urllib, urlparse, json, traceback
from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import cache
from resources.lib.modules import log_utils

class source:
    def __init__(self):
        self.priority = 1
        self.language = ['hu']
        self.domains = ['dmdamedia.hu']
        self.base_link = 'https://dmdamedia.hu'

    def movie(self, imdb, title, localtitle, aliases, year):
        url_content = client.request('%s/filmek' % self.base_link)
        center = client.parseDOM(url_content, 'div', attrs={'class': 'center'})[0].encode('utf-8')
        movies = center.replace('</div>', '</div>\n')
        for line in movies.splitlines():
            matches = re.search(r'^<div class="([^"]*) ([^"]*)"(.*)data-cim="([^"]*)"(.*)href="([^"]*)"(.*)data-src="([^"]*)(.*)$', line.strip())
            if matches:
                if title.lower() in line.lower() or localtitle.lower() in line.lower():                  
                    url = '%s%s' % (self.base_link, matches.group(6))
                    url_content = client.request(url)
                    base = client.parseDOM(url_content, 'div', attrs={'class': 'base'})[0]
                    stand = client.parseDOM(base, 'div', attrs={'class': 'stand'})[0]
                    info = client.parseDOM(stand, 'div', attrs={'class': 'info'})[0]
                    time = client.parseDOM(info, 'div', attrs={'class': 'time'})
                    localyear = client.parseDOM(time[1], 'h1')[0].strip()
                    localimdb = client.parseDOM(info, 'a', attrs={'class': 'imdb'}, ret='href')[0]
                    if imdb in localimdb and year == localyear:
                        return url
        return

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        url_content = client.request(self.base_link)
        center = client.parseDOM(url_content, 'div', attrs={'class': 'center'})[0].encode('utf-8')
        movies = center.replace('</div>', '</div>\n')
        for line in movies.splitlines():
            matches = re.search(r'^<div class="([^"]*) ([^"]*)"(.*)data-cim="([^"]*)"(.*)href="([^"]*)"(.*)data-src="([^"]*)(.*)$', line.strip())
            if matches:
                if tvshowtitle.lower() in line.lower() or localtvshowtitle.lower() in line.lower():                  
                    url = '%s%s' % (self.base_link, matches.group(6))
                    url_content = client.request(url)
                    base = client.parseDOM(url_content, 'div', attrs={'class': 'base'})[0]
                    stand = client.parseDOM(base, 'div', attrs={'class': 'stand'})[0]
                    info = client.parseDOM(stand, 'div', attrs={'class': 'info'})[0]
                    localimdb = client.parseDOM(info, 'a', attrs={'class': 'imdb'}, ret='href')[0]
                    if imdb in localimdb:
                        return url
        return

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if url == None: return
            url = "%s/%s.evad/%s.resz" % (url, season, episode)
            return url
        except:
            log_utils.log('>>>> %s TRACE <<<<\n%s' % (__file__.upper().split('\\')[-1].split('.')[0], traceback.format_exc()), log_utils.LOGDEBUG)
            return

    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []

            if url == None: return sources

            url_content = client.request(url)
            base = client.parseDOM(url_content, 'div', attrs={'class': 'base'})[0]
            #stand = client.parseDOM(base, 'div', attrs={'class': 'stand'})[0]
            #filmalt = client.parseDOM(stand, 'div', attrs={'class': 'filmalt'})[0]
            srcs = client.parseDOM(base, 'div', attrs={'class': 'video'})[0].replace('</a>', '</a>\n')
            for source in srcs.splitlines():
                matches = re.search(r'^<a(.*)href="(.*)">(.*)</a>$', source.strip())
                if matches:
                    host=[x for x in hostDict if matches.group(3).lower() in x][0]
                    host = client.replaceHTMLCodes(host)
                    host = host.encode('utf-8')
                    srcurl = '%s%s' % (url, matches.group(2))
                    scurl = client.replaceHTMLCodes(srcurl)
                    srcurl = srcurl.encode('utf-8')
                    sources.append({'source': host, 'quality': 'SD', 'language': 'hu', 'info': '', 'url': srcurl, 'direct': False, 'debridonly': False, 'sourcecap': True})
            return sources
        except:
            log_utils.log('>>>> %s TRACE <<<<\n%s' % (__file__.upper().split('\\')[-1].split('.')[0], traceback.format_exc()), log_utils.LOGDEBUG)
            return sources

    def resolve(self, url):
        try:
            url_content = client.request(url)
            base = client.parseDOM(url_content, 'div', attrs={'class': 'base'})[0]
            video = client.parseDOM(base, 'div', attrs={'class': 'video'})[0]
            source = client.parseDOM(video, 'iframe', ret='src')[0]
            source = client.replaceHTMLCodes(source)
            source = source.encode('utf-8')
            return source
        except:
            return