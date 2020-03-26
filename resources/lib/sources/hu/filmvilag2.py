# -*- coding: utf-8 -*-

import re, urllib, urlparse, json, traceback
from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import cache
from resources.lib.modules import log_utils
from resources.lib.modules import control

class source:
    def __init__(self):
        self.priority = 1
        self.language = ['hu']
        self.domains = ['onlinefilmvilag2.eu']
        self.base_link = 'https://www.onlinefilmvilag2.eu'

    def movie(self, imdb, title, localtitle, aliases, year):
        url_content = client.request(self.base_link)
        searchDiv = client.parseDOM(url_content, 'div', attrs={'id': 'search'})
        innerFrameDiv = client.parseDOM(searchDiv, 'div', attrs={'class': 'inner_frame'})
        searchURL = client.parseDOM(innerFrameDiv, 'form', ret='action')[0]
        uid = client.parseDOM(innerFrameDiv, 'input', attrs={'id': 'uid'}, ret='value')[0]
        for str in [localtitle, title]:
            url_content = client.request(searchURL, post="uid=%s&key=%s" % (uid, urllib.quote_plus(str)))
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
                            matches=re.search(r'^(.*)<meta property="og:description" content="(.*), ([0-9]*) perc, ([1-2][0-9]{3})(.*)"(.*)$', url_content, re.M)
                            if matches != None and year ==  matches.group(4):
                                self.writelog("movie - href:%s\n" % href)
                                return href
        return

    def sources(self, url, hostDict, hostprDict):
        try:
            sources = []

            if url == None: return sources
            url_content = client.request(url)
            if 'class="locked' in url_content:
                password = self.getText(u'Add meg a Cinema World facebook oldalról\nüzenetben kapott kódot!', True)
                if password == '':
                    return
                url_content = client.request('%s%s' %(base_url, url), post="password=%s&submit=Küldés" % password)
                while 'class="locked' in url_content:
                    password = self.getText(u'Hibás jelszó! Kérlek pontosan add meg a Cinema World\nfacebook oldalról üzenetben kapott kódot!', True)
                    if password == '':
                        return
                    url_content = client.request('%s%s' %(self.base_link, url), post="password=%s&submit=Küldés" % password)
            article = client.parseDOM(url_content, 'div', attrs={'class': 'article'})[0]
            header = client.parseDOM(article, 'h2')[0]
            title = client.parseDOM(header, 'span')[0]
            editorArea = client.parseDOM(article, 'div', attrs={'class': 'editor-area'})[0]
            paragraphs = client.parseDOM(editorArea, 'p')
            plot = ''
            for paragraph in paragraphs:
                if "<span" in paragraph:
                    plot = "%s%s%s" % (plot, "" if plot == "" else "\n", client.replaceHTMLCodes(client.parseDOM(paragraph, 'span')[0]))    
                elif "</" not in paragraph:
                    plot = "%s%s%s" % (plot, "" if plot == "" else "\n", client.replaceHTMLCodes(paragraph))
            #plot = plot.replace("&nbsp;", "")
            srcs = client.parseDOM(editorArea, 'iframe', ret='src')
            for src in srcs:
                host=[x for x in hostDict if x in src][0]
                sources.append({'source': host, 'quality': 'SD', 'language': 'hu', 'info': '', 'url': src, 'direct': False, 'debridonly': False, 'sourcecap': True})
            return sources
        except:
            log_utils.log('>>>> %s TRACE <<<<\n%s' % (__file__.upper().split('\\')[-1].split('.')[0], traceback.format_exc()), log_utils.LOGDEBUG)
            return sources

    def resolve(self, url):
        try:
            return ("http:%s" % url)
        except:
            return

    def getText(self, title, hidden=False):
        entered_text = ''
        keyb = control.keyboard('', title, hidden)
        keyb.doModal()

        if (keyb.isConfirmed()):
            entered_text = keyb.getText()

        return entered_text

    def writelog(self, msg):
        file = open("/home/gavarga/filmvilag2.txt", "a")
        file.write(msg)
        file.close()

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