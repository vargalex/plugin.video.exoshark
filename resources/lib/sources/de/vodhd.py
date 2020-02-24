# -*- coding: utf-8 -*-

import json
import requests
import re
from resources.lib.modules import cleantitle
from resources.lib.modules import control

class source:
    def __init__(self):
        ## Required Init ##
        self.priority = 1
        self.language = ['de']
        
        ## User Specific ##
        self.user=control.setting('vodhd.user')
        self.password=control.setting('vodhd.pass')
        self.server='https://vodhd.to'
        self.host=self.server.replace("https://","")
                
        ## Generic ##
        self.login=self.server+"/login/authenticate"
        self.loginref=self.server+"/login/auth"
        self.search=self.server+"/dash/searchMedia.json?query=%s"
        self.showsearch=self.server+"/tvShow/episodesForTvShow.json?id=%s"
        self.episodesearch=self.server+"/video/show.json?id=%s"

        ## Requests Session ##
        self.session = requests.Session()
        self.header={'Referer':self.loginref,'Host':self.host,'User-Agent':'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36'}
        self.params={'username':self.user,'password':self.password,'remember_me':'on'}

        # Required Loging at init due Episode/Series caching not handling cookies, so global handling required. 3 Login Requests per scrape
        login=self.__login()


    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            
            url = self.__search(localtitle,imdb)
            if not url:
                url = self.__search(title,imdb)

            return url
        except:
            return

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        
        url = self.__searchtv(localtvshowtitle,imdb)        
      
        if not url:
            url = self.__searchtv(tvshowtitle,imdb)
                
        return url

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
        
        cookies=requests.utils.dict_from_cookiejar(self.session.cookies)
        sHtmlContent=self.session.get(self.showsearch %url,headers=self.header).json()
        for i in sHtmlContent:            
            if str(i['season_number'])==season and episode==str(i['episode_number']):                
                episodeid=i['id']
                break;                    
       
        sHtmlContent=self.session.get(self.episodesearch %episodeid,headers=self.header).json()        
        url=sHtmlContent['files'][0]['src']
        
        return url

    def sources(self, url, hostDict, hostprDict):
        sources = []
       
        try:
            if not url:
                return sources
            
            url=self.server+url
            cookies=requests.utils.dict_from_cookiejar(self.session.cookies)        
            
            sources.append({'source': 'CDN', 'quality': '4K', 'language': 'de', 'url': url+"|Cookie=JSESSIONID="+cookies['JSESSIONID']+";streama_remember_me="+cookies['streama_remember_me'], 'direct': True, 'debridonly': False})
                
            return sources
        except:
            return sources

    def resolve(self, url):
        try:

            if url:
                
                return url
        except:
            return

    def __login(self):
        try:           
            sHtmlContent=self.session.get(self.login)
            sHtmlContent=self.session.post(self.login,headers=self.header,data=self.params)         
            
            return 
        except:
            return

        
    def __search(self, localtitle,imdb):
        try:
            suchbegriff=cleantitle.getsearch(localtitle)           
            sHtmlContent=self.session.get(self.search %suchbegriff,headers=self.header).json()
                                     
            if sHtmlContent['movies']:                
                for i in sHtmlContent['movies']:
                    if i['imdb_id']==imdb:
                        url=i['files'][0]['src']
                        break
               
            return url
        except:
            return



        
    def __searchtv(self, localtvshowtitle,imdb):
        try:
            
            localtvshowtitle=re.sub(r"\([0-9]+\)","",localtvshowtitle )           
            suchbegriff=cleantitle.getsearch(localtvshowtitle)           
            sHtmlContent=self.session.get(self.search %suchbegriff,headers=self.header).json()
                        
            if sHtmlContent['shows']:                
                for i in sHtmlContent['shows']:                    
                    #if i['imdb_id']==imdb:
                    url=i['id']
                    break
           
            return url
        except:
            return

