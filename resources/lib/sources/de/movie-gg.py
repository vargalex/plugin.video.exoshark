# -*- coding: utf-8 -*-

import json
import urllib3
import base64
from resources.lib.modules import source_utils

class source:
    def __init__(self):
        ## Required Init ##
        self.priority = 1
        self.language = ['de']
        self.base_link_api = 'https://movies.gg/MovieAPI?'
        self.getimdb='movie_info_imdb=%s'
        self.getlinks='get_links=%s'        
        self.key=base64.b64decode('JmtleT15a0RGS2JOSlpwSUF5NGZYc1dYWA==')
        

    def movie(self, imdb, title, localtitle, aliases, year):
        try:
            
            url=(self.base_link_api+self.getimdb %imdb+self.key)
            #print "print movie.gg self search",url      

            return url
        except:
            return

    def tvshow(self, imdb, tvdb, tvshowtitle, localtvshowtitle, aliases, year):
        
        
        return url

    def episode(self, url, imdb, tvdb, title, premiered, season, episode):
   
        
        return url

    def sources(self, url, hostDict, hostprDict):
        sources = []
        try:
            if not url:
                return sources

            ## urllib 3 ##

            ## getmovieID & Quality from imdbID ##
            http = urllib3.PoolManager()
            request = http.request('GET', url )
            request_json=json.loads(request.data.decode('utf8'))
            request.release_conn()
            movie_id=request_json['id']
            movie_type=request_json['movie_type']
                        
            ## getlinks from movieID ##
            url=(self.base_link_api+self.getlinks %movie_id+self.key)            
            http = urllib3.PoolManager()
            request = http.request('GET',url)
            request_json=json.loads(request.data.decode('utf8'))
            request.release_conn()

            if movie_type=='movie':
                q='HD'
            else:
                q='SD'
                        
            ## return list with links ##
            
            for link in request_json:
                valid, host = source_utils.is_host_valid(link, hostDict)
                if not valid: continue
                                
                sources.append({'source': host, 'quality': q, 'language': 'de', 'url': link, 'direct': False, 'debridonly': False,'checkquality':True})
                
            return sources
        except:
            return sources
        

    def resolve(self, url):
        return url


  
