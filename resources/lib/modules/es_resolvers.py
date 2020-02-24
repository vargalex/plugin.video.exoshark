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


import re, json, requests
from resources.lib.modules import client

def resolve_url(url):
    try:
        if 'filescdn.net' in url:
            stream_id = re.findall('(?://|\.)(filescdn\.net)/(?:embed-)?([0-9a-zA-Z]+)(?:\.|)', url)
            stream_id = [i[1] for i in stream_id if i[0] == 'filescdn.net'][0]
            link = 'https://filescdn.net/embed-%s.html' % stream_id
            result = client.request(link)
            url = client.parseDOM(result, 'source', ret='src')[0]
            return url
        elif 'sendit.cloud' in url:
            stream_id = re.findall('(?://|\.)(sendit\.cloud)/(?:embed-)?([0-9a-zA-Z]+)(?:\.|)', url)
            stream_id = [i[1] for i in stream_id if i[0] == 'sendit.cloud'][0]
            link = 'https://sendit.cloud/embed-%s.html' % stream_id
            result = client.request(link)
            url = re.findall('file:\s*"([^"]+)"', result)[0]
            return url
        elif 'uploadhaven.com' in url:
            stream_id = re.findall('(?://|\.)(uploadhaven\.com)/(?:video/)(?:embed/)?([0-9a-zA-Z]+)', url)
            stream_id = [i[1] for i in stream_id if i[0] == 'uploadhaven.com'][0]
            link = 'https://uploadhaven.com/video/%s' % stream_id
            result = requests.get(link).content
            token = re.findall('(?:\'|")token(?:\'|")\s*\:\s*(?:\'|")([^\'"]+)(?:\'|")', result)[0]
            headers = {'origin': 'https://uploadhaven.com', 'Content-Type': 'application/json;charset=UTF-8', 'referer': url}
            payload = {'token': token, 'referrer': ''}
            r = requests.post('https://uploadhaven.com/video/getSource', headers=headers, data=json.dumps(payload)).content
            json_src = json.loads(r)
            url = json_src['source']
            return url
        elif 'megadrive.co' in url:
            stream_id = re.findall('(?://|\.)(megadrive\.co)/(?:embed/|e/)?([0-9a-zA-Z]+)', url)
            stream_id = [i[1] for i in stream_id if i[0] == 'megadrive.co'][0]
            link = 'https://megadrive.co/embed/%s' % stream_id
            result = client.request(link)
            url = re.findall('(?s)videos:.+?mp4:"([^"]+)"', result)[0]
            return url
        else: raise Exception()
    except:
        return False
