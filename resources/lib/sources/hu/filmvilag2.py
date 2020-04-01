# -*- coding: utf-8 -*-

import re, urllib, urlparse, json, traceback
from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import cache
from resources.lib.modules import log_utils
from resources.lib.modules import control
from resources.lib.modules import source_utils

class source:
    def __init__(self):
        self.priority = 1
        self.language = ['hu']
        self.domains = ['onlinefilmvilag2.eu']
        self.base_link = 'https://www.onlinefilmvilag2.eu'
        self.password = "" #control.setting('filmvilag2.pass')

    def movie(self, imdb, title, localtitle, aliases, year):
        url_content = client.request(self.base_link)
        searchDiv = client.parseDOM(url_content, 'div', attrs={'id': 'search'})
        innerFrameDiv = client.parseDOM(searchDiv, 'div', attrs={'class': 'inner_frame'})
        searchURL = client.parseDOM(innerFrameDiv, 'form', ret='action')[0]
        uid = client.parseDOM(innerFrameDiv, 'input', attrs={'id': 'uid'}, ret='value')[0]
        for sTitle in [localtitle, title]:
            url_content = client.request(searchURL, post="uid=%s&key=%s" % (uid, urllib.quote_plus(sTitle)))
            searchResult = client.parseDOM(url_content, 'div', attrs={'class': 'search-results'})
            resultsUser = client.parseDOM(searchResult, 'div', attrs={'class': 'results-user'})
            ul = client.parseDOM(resultsUser, 'ul')
            categoriesURL = cache.get(self.getCategoriesUrl, 720)
            if len(ul)>0:
                lis = client.parseDOM(ul, 'li')
                for li in lis:
                    href = client.parseDOM(li, 'a', ret='href')[0].replace('http://', 'https://')
                    if href not in categoriesURL:
                        if "filmkeres-es-hibas-link-jelentese.html" not in href:
                            url_content = client.request(href)
                            matches=re.search(r'^(.*)<meta property="og:title" content="(.*)"(.*)$', url_content, re.M)
                            if matches != None and cleantitle.get(sTitle) in cleantitle.get(matches.group(2)):
                                matches=re.search(r'^(.*)<meta property="og:description" content="(.*), ([0-9]*) perc, ([1-2][0-9]{3})(.*)"(.*)$', url_content, re.M)
                                if matches != None and int(year)-1<=int(matches.group(4))<=int(year)+1:# in years:
                                    return href
        return

    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []

            if url == None: return sources
            url_content = client.request(url)
            if 'class="locked' in url_content:
                if self.password == '':
                    self.password = self.getText(u'Add meg a Cinema World facebook oldalról\nüzenetben kapott kódot!', True)
                    if self.password == '':
                        return
                url_content = client.request('%s%s' %(base_url, url), post="password=%s&submit=Küldés" % self.password)
                while 'class="locked' in url_content:
                    self.password = self.getText(u'Hibás jelszó! Kérlek pontosan add meg a Cinema World\nfacebook oldalról üzenetben kapott kódot!', True)
                    if self.password == '':
                        return
                    url_content = client.request('%s%s' %(self.base_link, url), post="password=%s&submit=Küldés" % self.password)
                control.setting('filmvilag2.pass', self.password)
            quality = "SD"
            info = "szinkron"
            matches=re.search(r'^(.*)<meta property="og:description" content="(.*), ([0-9]*) perc, ([1-2][0-9]{3})(.*)"(.*)$', url_content, re.M)
            if matches != None:
                if 'KAMERÁS' in matches.group(5).upper():
                    quality = "CAM"
                else:
                    quality = "SD"
                if 'MOZIS' in matches.group(5).upper():
                    info = "szinkron (mozis hang)"
            if 'HD FILMEK' in client.parseDOM(url_content, 'title')[0]:
                quality = "HD"
            hostDict = hostprDict + hostDict
            title = client.parseDOM(url_content, 'title')[0]
            article = client.parseDOM(url_content, 'div', attrs={'class': 'article'})[0]
            header = client.parseDOM(article, 'h2')[0]
            title = client.parseDOM(header, 'span')[0]
            editorArea = client.parseDOM(article, 'div', attrs={'class': 'editor-area'})[0]
            srcs = client.parseDOM(editorArea, 'iframe', ret='src')
            sources2 = client.parseDOM(editorArea, 'a', ret='href')
            for src in srcs+sources2:
                valid, host = source_utils.is_host_valid(src, hostDict)
                if not valid: continue
                host = client.replaceHTMLCodes(host)
                host = host.encode('utf-8')
                #host=[x for x in (hostDict + hostprDict) if x in src][0]
                sources.append({'source': host, 'quality': quality, 'language': 'hu', 'info': info, 'url': src, 'direct': False, 'debridonly': False, 'sourcecap': True})
            return sources
        except:
            log_utils.log('>>>> %s TRACE <<<<\n%s' % (__file__.upper().split('\\')[-1].split('.')[0], traceback.format_exc()), log_utils.LOGDEBUG)
            return sources

    def resolve(self, url):
        try:
            if "http" not in url:
                return ("https:%s" % url)
            else:
                return url
        except:
            return

    def getText(self, title, hidden=False):
        entered_text = ''
        keyb = control.keyboard('', title, hidden)
        keyb.doModal()

        if (keyb.isConfirmed()):
            entered_text = keyb.getText()

        return entered_text

    def getCategoriesUrl(self):
        categories = []
        url_content = client.request(self.base_link)
        mainMenu=client.parseDOM(url_content, 'menu', attrs={'class': 'menu-type-onmouse'})[0].strip()
        menuItems = client.parseDOM(mainMenu, 'li')
        for menuItem in menuItems:
            text = client.replaceHTMLCodes(client.parseDOM(menuItem, 'a')[0]).encode('utf-8')
            url = client.parseDOM(menuItem, 'a', ret='href')[0]
            categories.append("%s%s" % (self.base_link, url))
        return categories