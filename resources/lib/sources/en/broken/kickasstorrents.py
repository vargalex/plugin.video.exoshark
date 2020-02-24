# -*- coding: utf-8 -*-

'''
    Gaia Add-on
    Copyright (C) 2016 Gaia

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

import re,urllib,urlparse,traceback
from resources.lib.modules import cleantitle
from resources.lib.modules import client
from resources.lib.modules import debrid
from resources.lib.modules import source_utils
from resources.lib.modules import es_resolvers
# from resources.lib.extensions import metadata
# from resources.lib.extensions import tools
from bs4 import BeautifulSoup

class source:
    def __init__(self):
        self.priority = 0
        self.language = ['en']
        self.domains = ['kat.li', 'kat.how', 'kickasstorrents.video', 'kickasstorrents.to', 'katcr.to', 'kat.am',  'kickass.cd', 'kickass.ukbypass.pro', 'kickass.unlockproject.review'] # Most of these links seem to have a different page layout than kat.how.
        self.base_link = 'https://kat.li' # Link must have the name for provider verification.
        self.search_link = '/usearch/%s/?field=seeders&sorder=desc'


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

            if not debrid.status(): raise Exception()

            data = urlparse.parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])

            title = data['tvshowtitle'] if 'tvshowtitle' in data else data['title']

            hdlr = 'S%02dE%02d' % (int(data['season']), int(data['episode'])) if 'tvshowtitle' in data else data['year']

            query = '%s S%02dE%02d' % (data['tvshowtitle'], int(data['season']), int(data['episode'])) if 'tvshowtitle' in data else '%s %s' % (data['title'], data['year'])
            query = re.sub('(\\\|/| -|:|;|\*|\?|"|\'|<|>|\|)', ' ', query)

            url = self.search_link % urllib.quote_plus(query)
            url = urlparse.urljoin(self.base_link, url)

            html = client.request(url)

            # KickassTorrents has major mistakes in their HTML. manually remove parts to create new HTML.
            indexStart = html.find('<', html.find('<!-- Start of Loop -->') + 1)
            indexEnd = html.rfind('<!-- End of Loop -->')
            html = html[indexStart : indexEnd]

            html = html.replace('<div class="markeredBlock', '</div><div class="markeredBlock') # torrentname div tag not closed.
            html = html.replace('</span></td>', '</td>') # Dangling </span> closing tag.

            html = BeautifulSoup(html)

            htmlRows = html.find_all('tr', recursive = False) # Do not search further down the tree (just the direct children).
            for i in range(len(htmlRows)):
                try:
                    htmlRow = htmlRows[i]
                    if 'firstr' in htmlRow['class']: # Header.
                        continue
                    htmlColumns = htmlRow.find_all('td')
                    htmlInfo = htmlColumns[0]

                    # Name
                    htmlName = htmlInfo.find_all('a', class_ = 'cellMainLink')[0].getText().strip()

                    # Size
                    htmlSize = htmlColumns[1].getText().replace('&nbsp;', ' ')

                    # Link
                    htmlLink = ''
                    htmlLinks = htmlInfo.find_all('a', class_ = 'icon16')
                    for j in range(len(htmlLinks)):
                        link = htmlLinks[j]
                        if link.has_attr('href'):
                            link = link['href']
                            if 'magnet' in link:
                                htmlLink = urllib.unquote(re.findall('(magnet.*)', link)[0]) # Starts with redirection url, eg: https://mylink.bz/?url=magnet...
                                break

                    # Seeds
                    try: htmlSeeds = int(htmlColumns[3].getText())
                    except: htmlSeeds = 'NA'
                    # Metadata
                    # meta = metadata.Metadata(name = htmlName, title = title, year = year, season = season, episode = episode, pack = pack, packCount = packCount, link = htmlLink, size = htmlSize, seeds = htmlSeeds)

                    # Ignore
                    # if meta.ignore(True): continue

                    # Add
                    # sources.append({'url' : htmlLink, 'debridonly' : False, 'direct' : False, 'source' : 'torrent', 'language' : self.language[0], 'quality':  meta.videoQuality(), 'metadata' : meta, 'file' : htmlName})
                    quality, info = source_utils.get_release_quality(htmlName)
                    info = ' | '.join(info)
                    try: info = '%s | %s | S: %s' % (info, htmlSize, htmlSeeds)
                    except: pass
                    sources.append({'source': 'torrent', 'quality': quality, 'language': 'en', 'url': htmlLink, 'info': info, 'direct': False, 'debridonly': False})
                    print '############### KICKASS sources', sources
                except:
                    print '############### KICKASS TRACE', traceback.format_exc()
                    pass

            return sources
        except:
            print '############### KICKASS TRACE', traceback.format_exc()
            return sources

    def resolve(self, url):
        try:
            urlr = es_resolvers.resolve_url(url)
            print '############### KICKASS URLR', urlr
            return urlr
        except:
            return
