# -*- coding: utf-8 -*-

import urlparse
import re
import requests

from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import dom_parser
from resources.lib.modules import source_utils


class source:
    def __init__(self):
        self.priority = 1
        self.language = ['de']
        self.domains = ['szene-streamz.com']
        self.base_link = 'http://www.szene-streamz.com'
        self.search_link=self.base_link+'/publ/'
        

    def movie(self, imdb, title, localtitle, aliases, year):
        try:

            url = self.__search([localtitle] + source_utils.aliases_to_array(aliases), year)
                        
            return url
            
        except:
            return

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        try:
            
            return 
        except:
            return

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        try:
            if not url:
                return

            return 
        except:
            return

    def sources(self, url, hostDict, hostprDict):
        sources = []
        try:
            if not url:                
                return sources
            
            sHtmlContent = requests.get(urlparse.urljoin(self.base_link,url))

            
            pattern1= 'blank"[^>]*href="([^"]+)">'
            hoster = re.compile(pattern1).findall(sHtmlContent.content)

            hosters = []

            if "1080p" in url:
                q="1080p"
            elif "720p" in url:
                q="720p"
            else:
                q='SD'
            
            for link in hoster:
                link = link.strip()
                print "loop",link
            
                if 'openload' in link:
                    sources.append({'source': 'openload.com', 'quality':q, 'language': 'de', 'url': link, 'direct': False, 'debridonly': False})
                elif 'streamango' in link:
                    sources.append({'source': 'streamango.com', 'quality': q, 'language': 'de', 'url': link, 'direct': False, 'debridonly': False})
                elif 'vidzi' in link:
                    sources.append({'source': 'vidzi.tv', 'quality': 'SD', 'language': 'de', 'url': link, 'direct': False, 'debridonly': False})
                elif 'flashx' in link:
                    sources.append({'source': 'flashx.tv', 'quality': 'SD', 'language': 'de', 'url': link, 'direct': False, 'debridonly': False})
                elif 'streamcloud' in link:
                    sources.append({'source': 'streamcloud.eu', 'quality': 'SD', 'language': 'de', 'url': link, 'direct': False, 'debridonly': False})
                
               

            
            return sources
        except:
            return sources


    def resolve(self, url):
        return url

    def __search(self,titles, year):
        try:
            t = [cleantitle.get(i) for i in set(titles) if i] # Mit diesen alternativtiteln können wir vergleichen

            url = ""
            #Wenn ein Titel bei der suche nix findet können wir nach dem nächsten Suchen. Thor: Ragnarok z.B. braucht 3 Versuche (Thor 3, Thor: Raganroek...)
            for title in titles:
                params={'a':'2', 'query':title}
                sHtmlContent = client.request(self.search_link,post=params) # Am besten immer die client-Klasse für requests verwenden. Hat schon logik für Redirects und Kekse drinnen

                if sHtmlContent == None or "noEntry" in sHtmlContent: continue; #noEntry steht im Quelltext, wenn keiner gefunden wird. continue lasst die schleife mit dem nächsten titel weitermachen

                #Das is jetzt ein bisschen ein hack, aber die haben einen Syntax-Fehler (oder Absicht?) in ihrem html-code. Für den dom-parser müssen wir den vorher fixen
                sHtmlContent = sHtmlContent.replace('entryLink" <a=""','entryLink"')

                #Ich persönlich finde Patterns schwer zu lesen, dom_parser ist da angenehmer:
                entryLinks = dom_parser.parse_dom(sHtmlContent,'a',attrs={"class":"entryLink"}) #Wir suchen ein a-element mit dem Klassen-Attribut entryLink
                if len(entryLinks) == 0: continue

                for link in entryLinks: #Alle gefundenen entryLinks
                    title = cleantitle.get(link.content) #Cleantitle aus dem Link-text
                    if title in t:
                        return source_utils.strip_domain(link.attrs['href']) #Der Link-Text stimmt mit dem gesuchten überein, also Done.

            return url

            
            
                        
        except:
            return
