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


def dialogtext(name, txt):
    from resources.lib.modules import control
    try:
        return control.dialog.textviewer(name, txt)
    except:
        return


### AdflyUrlGrabber ###
#Author:D4Vinci
#rewrited by MGF15
#algorithm from StoreClerk

def adfly_crack(code):
    import base64

    try:
        zeros = ''
        ones = ''
        for n,letter in enumerate(code):
            if n % 2 == 0:
                zeros += code[n]
            else:
                ones = code[n] + ones
        key = zeros + ones
        key = list(key)
        i = 0
        while i < len(key):
            if key[i].isdigit():
                for j in range(i+1,len(key)):
                    if key[j].isdigit():
                        u = int(key[i])^int(key[j])
                        if u < 10:
                            key[i] = str(u)
                        i = j
                        break
            i+=1
        key = ''.join(key).decode('base64')[16:-16]
        return key
    except:
        return


def captcha_resolve(response, cap_cookie):
    import os
    from resources.lib.modules import client
    from resources.lib.modules import control

    try:
        i = os.path.join(control.dataPath,'img')
        f = control.openFile(i, 'w')
        f.write(client.request(response, cookie=cap_cookie))
        f.close()
        f = control.image(450,5,375,115, i)
        d = control.windowDialog
        d.addControl(f)
        control.deleteFile(i)
        d.show()
        t = ''
        k = control.keyboard('', t)
        k.doModal()
        c = k.getText() if k.isConfirmed() else None
        if c == '': c = None
        d.removeControl(f)
        d.close()
        return c
    except:
        return


def changelog_textbox():
    import os, xbmc, xbmcgui, xbmcaddon, xbmcvfs

    try:
        path = xbmcaddon.Addon().getAddonInfo('path').decode('utf-8')

        logfile = xbmcvfs.File(os.path.join(path, 'changelog.txt'))
        text = logfile.read()
        logfile.close()

        dialog = xbmcgui.Dialog()
        dialog.textviewer(xbmc.getLocalizedString(24036), text)
        return
    except:
        return


def check_subtitle(tvshowtitle, year, season, episode):
    from resources.lib.modules import client
    from resources.lib.modules import control
    import urllib, xbmcgui, json, re

    try:
        tvshowtitle = re.sub('(\(\d{4}\))', '', tvshowtitle)
        tvshowtitle = tvshowtitle.strip()
        tvshowtitle2 = re.sub('\'', '’', tvshowtitle)
        titl = urllib.quote_plus(tvshowtitle)
        titl2 = urllib.quote_plus(tvshowtitle2)
        t = '%s (%s)' % (tvshowtitle, year)
        t2 = '%s (%s)' % (tvshowtitle2, year)

        tvdb_url = 'http://thetvdb.com/api/GetSeries.php?seriesname=%s' % (titl)
        supersub_url = 'https://www.feliratok.info'
        search_url = '/index.php?term=%s&nyelv=0&action=autoname'
        ssub_url = '/index.php?search=&nyelv=Magyar&sid=%s&complexsearch=true&evad=%s&epizod1=%s&evadpakk=%s&tab=all'

        subt_url0 = supersub_url + search_url % (titl)
        r = client.request(subt_url0)
        if 'Nincs tal\u00e1lat' in r:
            if not titl == titl2:
                subt_url0 = supersub_url + search_url % (titl2)
                r = client.request(subt_url0)
                if 'Nincs tal\u00e1lat' in r:
                    control.infoDialog(u'Nincs el\u00E9rhet\u0151 magyar felirat', sound=True, icon='INFO')
                    return
            else:
                control.infoDialog(u'Nincs el\u00E9rhet\u0151 magyar felirat', sound=True, icon='INFO')
                return
        subs = re.findall('\{[^\{\}]+\}', r)
        tvshow_id = ''

        for item in subs:
            name = json.loads(item)['name']
            name2 = re.sub('(\s*\([A-Z]{2}\))', '', name)
            name2 = name2.strip()
            if name.lower() == t.lower() or name2.lower() == t.lower():
                tvshow_id = json.loads(item)['ID']
            if name.lower() == t2.lower() or name2.lower() == t2.lower():
                tvshow_id = json.loads(item)['ID']

        if tvshow_id == '':
            r = client.request(tvdb_url, timeout='10')
            r = client.parseDOM(r, 'Series')
            r = [i for i in r if 'FirstAired>%s' % year in i]
            if len(r) == 0:
                control.infoDialog(u'Nincs el\u00E9rhet\u0151 magyar felirat', sound=True, icon='INFO')
                return
            try:
                aliasname = client.parseDOM(r, 'AliasNames')[0]
            except:
                control.infoDialog(u'Nincs el\u00E9rhet\u0151 magyar felirat', sound=True, icon='INFO')
                return
            t = '%s (%s)' % (aliasname, year)
            for item in subs:
                name = json.loads(item)['name']
                name2 = re.sub('(\s*\([A-Z]{2}\))', '', name)
                name2 = name2.strip()
                if name.lower() == t.lower() or name2.lower() == t.lower():
                    tvshow_id = json.loads(item)['ID']
                if name.lower() == t2.lower() or name2.lower() == t2.lower():
                    tvshow_id = json.loads(item)['ID']

        if tvshow_id == '':
            control.infoDialog(u'Nincs el\u00E9rhet\u0151 magyar felirat', sound=True, icon='INFO')
            return

        subt_url = supersub_url + ssub_url % (tvshow_id, season, episode, '0')
        subt_r = client.request(subt_url)
        subt_o = re.findall('(?s)<div class="eredeti">[^<>]+<\/div>.+?<td align="center"[^<>]+>\s*(.+?)\s*<\/td>\s*<td align[^<>]+>\s*\d{4}-\d{2}-\d{2}', subt_r)
        subt_m = re.findall('<div class="eredeti">([^"]+)<\/div>', subt_r)
        if len(subt_m) == 0:
            subt_url = supersub_url + ssub_url % (tvshow_id, season, episode, 'on')
            subt_r = client.request(subt_url)
            subt_o = re.findall('(?s)<div class="eredeti">[^<>]+<\/div>.+?<td align="center"[^<>]+>\s*(.+?)\s*<\/td>\s*<td align[^<>]+>\s*\d{4}-\d{2}-\d{2}', subt_r)
            subt_m = re.findall('<div class="eredeti">([^"]+)<\/div>', subt_r)
            subt_m = [u'[\u00C9vadpakk] ' + i for i in subt_m]
        if len(subt_m) == 0:
            control.infoDialog(u'Nincs el\u00E9rhet\u0151 magyar felirat', sound=True, icon='INFO')
            return

        subt = ['%s - (%s)' % (i, j) for i, j in zip(subt_m, subt_o)]
        subtext_r = '[CR]===================================================[CR][B][Magyar felirat][/B] '.join(subt)
        subtext = u'[COLOR lawngreen][B]%s SuperSubtitles felirat el\u00E9rhet\u0151:[/B][/COLOR][CR][B][Magyar felirat][/B] %s' % (len(subt), subtext_r)
        subtext = re.sub('<.+?>', '', subtext)
        try:
            subtext = subtext.encode('utf-8')
        except:
            pass

        subtitle_dialog = xbmcgui.Dialog()
        subtitle_dialog.textviewer('Feliratok', subtext)
        return
    except:
        return


def movierls(title, year):
    from resources.lib.modules import client
    from resources.lib.modules import cleantitle
    from resources.lib.modules import control
    import xbmcgui, re

    try:
        dvdrls_url = 'https://www.newdvdreleasedates.com'
        search_url = '/ajaxsearch.php?q=%s'

        t = title.replace(' ', '%20')
        query = dvdrls_url + search_url % t
        r = client.request(query)
        result = re.findall('(<a.+?>.+?<\/a>)', r)

        result = [(client.parseDOM(i, 'a')[0], client.parseDOM(i, 'a', ret = 'href')[0]) for i in result]
        result = [i[1] for i in result if cleantitle.get(title) == cleantitle.get(i[0].rsplit('(%s' % year, 1)[0].strip().encode('utf-8')) and year in i[0]]
        if not len(result) == 1:
            control.infoDialog(u'Nem tal\u00E1lhat\u00F3 inform\u00E1ci\u00F3 a megjelen\u00E9sekr\u0151l', sound=True, icon='INFO')
            return

        r1 = client.request(dvdrls_url + result[0])
        items_table = client.parseDOM(r1, 'table')[0]
        items = re.findall('<span class=\'name\'>([^<>]+)<.+?((?:Digital (?:<\/span>)Download|DVD rental|DVD.+?Blu-ray.+?4K|DVD.+?Blu-ray|DVD|Blu-ray|4K|not available)).+?(\w+\s*\d{1,2},\s*\d{4}).+?<\/tr>', items_table)
        if items == []:
            control.infoDialog(u'Nem tal\u00E1lhat\u00F3 inform\u00E1ci\u00F3 a megjelen\u00E9sekr\u0151l', sound=True, icon='INFO')
            return

        releases = []

        monthDict = {'January': u'janu\u00E1r',
                     'February': u'febru\u00E1r',
                     'March': u'm\u00E1rcius',
                     'April': u'\u00E1prilis',
                     'May': u'm\u00E1jus',
                     'June': u'j\u00FAnius',
                     'July': u'j\u00FAlius',
                     'August': 'augusztus',
                     'September': 'szeptember',
                     'October': u'okt\u00F3ber',
                     'November': 'november',
                     'December': 'december'}

        for hoster, media, date in items:
            try:
                media = re.sub('<.+?>', '', media)
                if 'dvd' in media.lower() and 'blu-ray' in media.lower() and '4k' in media.lower(): media = 'DVD, BLU-RAY, 4K'
                elif 'dvd' in media.lower() and 'blu-ray' in media.lower() and not '4k' in media.lower(): media = 'DVD, BLU-RAY'
                elif 'digital download' in media.lower(): media = 'VOD'
                elif 'dvd rental' in media.lower(): media = u'K\u00F6lcs\u00F6n\u00F6zhet\u0151 DVD'
                elif 'not available' in media.lower(): media = u'Nem el\u00E9rhet\u0151'
                date = date.replace(',', '').split(' ')
                month = monthDict[date[0]]
                date = '%s. %s %s.' % (date[2], month, date[1])
                text = u'[B]%s[/B] | %s\nMegjelen\u00E9s: %s' % (hoster.strip(), media.strip(), date.strip())
                releases.append(text)
            except:
                control.infoDialog(u'Nem tal\u00E1lhat\u00F3 inform\u00E1ci\u00F3 a megjelen\u00E9sekr\u0151l', sound=True, icon='INFO')
                return

        rlstext = '[CR][CR]'.join(releases)

        try:
            rlstext = rlstext.encode('utf-8')
        except:
            pass

        rls_dialog = xbmcgui.Dialog()
        rls_dialog.textviewer(u'Megjelen\u00E9sek', rlstext)
        return
    except:
        control.infoDialog(u'Nem tal\u00E1lhat\u00F3 inform\u00E1ci\u00F3 a megjelen\u00E9sekr\u0151l', sound=True, icon='INFO')
        return


def imdbinfo(imdbid):
    from resources.lib.modules import control
    from resources.lib.modules import client
    import re, xbmc, xbmcgui, json

    try:
        xbmc.executebuiltin( "ActivateWindow(busydialog)" )

        html = client.request('http://www.imdb.com/title/%s/' % imdbid)

        imdb_json = client.parseDOM(html, 'script', attrs={'type': 'application/ld\+json'})[0]
        r = json.loads(imdb_json)
        title = r['name']
        rating = r['aggregateRating']['ratingValue']
        votes = r['aggregateRating']['ratingCount']
        try:
            rated = r['contentRating']
        except:
            rated = 'Nincs'
        try:
            desc = r['description']
        except:
            desc = ''
        desc = re.sub('(?s)(<[^<>]+>|\[[^\[\]]+\])', '', desc)
        genre = r['genre']
        if isinstance(genre, list):
            genr = ', '.join(genre)
        else:
            genr = genre
        imdbtext = u'[B]%s[/B] | %s\n\n\u00C9rt\u00E9kel\u00E9s: %s (%s szavazat alapj\u00E1n)\nKorhat\u00E1r-besorol\u00E1s: %s\n\nBevezet\u0151:\n%s' \
                    % (title.strip(), genr.strip(), rating, votes, rated.strip(), desc.strip())
        try: imdbtext = client.replaceHTMLCodes(imdbtext)
        except: pass
        try: imdbtext = imdbtext.encode('utf-8')
        except: pass

        xbmc.executebuiltin( "Dialog.Close(busydialog)" )
        imdb_dialog = xbmcgui.Dialog()
        imdb_dialog.textviewer(u'IMDb Inf\u00F3', imdbtext)
    except:
        xbmc.executebuiltin( "Dialog.Close(busydialog)" )
        control.infoDialog(u'Az IMDb adatlap nem el\u00E9rhet\u0151', sound=True, icon='INFO')
        return


def refreshproviders():
    import re, os, traceback
    from os.path import isfile, join
    from resources.lib.modules import control
    from resources.lib.modules import log_utils

    try:
        mypath = os.path.join(control.addonPath, 'resources\lib\sources')

        dirs = [d for d in os.listdir(mypath) if os.path.isdir(os.path.join(mypath, d))]
        dirs = [d for d in dirs if not 'orion' in d]

        for dir in dirs:
            directory = os.path.join(mypath, dir)
            files = [i for i in os.listdir(directory) if isfile(join(directory, i))]
            files = [i for i in files if i.endswith('.py')]
            files = [i.split('.py')[0] for i in files if not 'init__.py' in i]

            if dir == 'en' or dir == 'hu': provdef = 'true'
            else: provdef = 'false'

            providers = ['<setting id="provider.%s" type="bool" label="%s" default="%s" />' % (i, i.upper(), provdef) for i in files]
            providers = '\n        '.join(providers)

            settingfile = os.path.join(control.addonPath, 'resources\settings.xml')

            file = open(settingfile, 'r').read()

            langdict = {'de': u'N\u00E9met',
                        'en': u'Angol',
                        'es': u'Spanyol',
                        'fr': u'Francia',
                        'gr': u'G\u00F6r\u00F6g',
                        'hu': u'Magyar',
                        'it': u'Olasz',
                        'ko': u'Koreai',
                        'pl': u'Lengyel',
                        'ru': u'Orosz'}

            lang = langdict[dir]

            set_providers = re.findall('(?s)setting label="%s" type="lsep"\s*\/>\s*(.+?>)\s*(?:<[^<>]+type="lsep"|<\/category)' % lang.encode('utf-8'), file)[0]
            t = re.sub(set_providers, providers, file)

            open(settingfile, 'wb').write(t)
            log_utils.log('A KISZOLGALOLISTA FRISSITESE SIKERES', log_utils.LOGNOTICE)
    except:
        log_utils.log('A KISZOLGALOLISTA FRISSITESE SIKERTELEN. A HIBA OKA:', log_utils.LOGNOTICE)
        log_utils.log(traceback.format_exc(), log_utils.LOGNOTICE)


def importproviders(type):
    from resources.lib.modules import control
    from resources.lib.modules import log_utils
    import re, os, requests, traceback, io
    import zipfile

    try:
        if type == 'file':
            import_file = control.setting('import.providersfile')
        elif type == 'url':
            import_file = control.setting('import.providersurl')
        if import_file == '': raise Exception()
        import_file1 = import_file.rsplit('\\')[-1]
        if not import_file1.startswith('es_providers_') and not import_file1.endswith('.zip'): raise Exception()
        lang = import_file1.split('es_providers_')[1][:2]
        if not any(x in lang for x in ['de', 'en', 'es', 'fr', 'gr', 'hu', 'it', 'ko', 'pl', 'ru']): raise Exception()

        import_path = os.path.join(control.addonPath, 'resources\lib\sources\%s' % lang)

        fileList = os.listdir(import_path)
        for fileName in fileList:
            if not '__init__.py' in fileName:
                os.remove(os.path.join(import_path, fileName))
        if type == 'file':
            with zipfile.ZipFile(import_file, "r") as z:
                z.extractall(import_path)
                filenames = z.namelist()
                filenames = [i.split('.py')[0].upper() for i in filenames]
                text = '%s kiszolgalo importalva (%s) | importalt fajl: ' % (len(filenames), lang)
                log_utils.log(text.upper() + import_file1, log_utils.LOGNOTICE)
                log_utils.log(', '.join(filenames), log_utils.LOGNOTICE)
        elif type == 'url':
            r = requests.get(import_file)
            with zipfile.ZipFile(io.BytesIO(r.content)) as z:
                z.extractall(import_path)
                filenames = z.namelist()
                filenames = [i.split('.py')[0].upper() for i in filenames]
                text = '%s kiszolgalo importalva (%s) | importalt fajl: ' % (len(filenames), lang)
                log_utils.log(text.upper() + import_file1, log_utils.LOGNOTICE)
                log_utils.log(', '.join(filenames), log_utils.LOGNOTICE)

        refreshproviders()
        control.infoDialog(u'Az import\u00E1l\u00E1s sikeres volt. R\u00E9szletek a hibanapl\u00F3ban.', sound=True, icon='INFO')
    except:
        log_utils.log('IMPORTALAS SIKERTELEN. A HIBA OKA:', log_utils.LOGNOTICE)
        log_utils.log(traceback.format_exc(), log_utils.LOGNOTICE)
        control.infoDialog(u'Import\u00E1l\u00E1s sikertelen. R\u00E9szletek a hibanapl\u00F3ban.', sound=True, icon='INFO')
        return


def checkproviders():
    from resources.lib.modules import cfscrape
    from resources.lib.modules import control
    from resources.lib.modules import log_utils
    import re, os, requests, traceback, xbmcvfs, xbmc

    try:
        scraper = cfscrape.create_scraper()
        langlist = ['de', 'en', 'es', 'fr', 'gr', 'hu', 'it', 'ko', 'pl', 'ru']
        dialogLangs = control.dialog.multiselect(u'Kiszolg\u00E1l\u00F3k ellen\u0151rz\u00E9se', langlist)
        if not dialogLangs: raise Exception()
        xbmc.executebuiltin( "ActivateWindow(busydialog)" )
        log_utils.log('AZ ELLENORZES ELINDULT', log_utils.LOGNOTICE)
        langs = []
        for i in dialogLangs:
            langs.append(langlist[i])

        for lang in langs:
            import_path = os.path.join(control.addonPath, 'resources\lib\sources\%s' % lang)

            fileList = os.listdir(import_path)
            for fileName in fileList:
                try:
                    if not '__init__.py' in fileName and fileName.endswith('.py'):
                        file = xbmcvfs.File(os.path.join(import_path, fileName))
                        filetext = file.read()
                        file.close()
                        baselink = re.findall('self\.base_link\s*\=\s*(?:\'|")([^[\'"]+)(?:\'|")\s*\n', filetext)[0]
                        r = requests.get(baselink)
                        cf = r.status_code
                        if not r.status_code == 200:
                            r1 = scraper.get(baselink)
                            cf = '%s | %s' % (r1.status_code, 'CFSCRAPE')

                        log_utils.log('%s | %s | %s | %s' % (lang, fileName, r.url, cf), log_utils.LOGNOTICE)
                except:
                    log_utils.log('%s | %s | Nem sikerult az ellenorzes ennel a kiszolgalonal' % (lang, fileName), log_utils.LOGNOTICE) 
                    pass
        xbmc.executebuiltin( "Dialog.Close(busydialog)" )
        log_utils.log('AZ ELLENORZES BEFEJEZODOTT', log_utils.LOGNOTICE)

        control.dialog.ok(control.addonInfo('name'), u'Az ellen\u0151rz\u00E9s sikeres volt.', u'R\u00E9szletek a hibanapl\u00F3ban.', '')
    except:
        xbmc.executebuiltin( "Dialog.Close(busydialog)" )
        log_utils.log('ELLENORZES SIKERTELEN. A HIBA OKA:', log_utils.LOGNOTICE)
        log_utils.log(traceback.format_exc(), log_utils.LOGNOTICE)
        control.infoDialog(u'Ellen\u0151rz\u00E9s sikertelen. R\u00E9szletek a hibanapl\u00F3ban.', sound=True, icon='INFO')
        return


def testproviders():
    from resources.lib.modules import control
    import os

    try:
        langlist = ['de', 'en', 'es', 'fr', 'gr', 'hu', 'it', 'ko', 'pl', 'ru']
        select = control.dialog.select(u'Kiszolg\u00E1l\u00F3k nyelvenek kivalasztasa', langlist)
        if not select: raise Exception()
        selectedLang = langlist[select]
        path = os.path.join(control.addonPath, 'resources\lib\sources\%s' % selectedLang)
        fileList = os.listdir(path)
        fileList = [i for i in fileList if not '__init__.py' in i and i.endswith('.py')]
        selectproviders = control.dialog.multiselect(u'Kiszolg\u00E1l\u00F3k kivalasztasa', fileList)
        if not selectproviders: raise Exception()
        selectedProviders = [fileList[i].split('.')[0] for i in selectproviders]

        return selectedProviders
    except:
        return


def checkrepo():
    from resources.lib.modules import control
    import os

    try:
        curVersion = repoVer = control.addon('plugin.video.exoshark').getAddonInfo('version')
        versionFile = os.path.join(control.dataPath, 'repoversion.v')

        try:
            with open(versionFile, 'rb') as fh: repoVer = fh.read()
        except:
            pass

        if repoVer < curVersion:
            return True
        else:
            return False
    except:
        return False


def dialogrepo():
    from resources.lib.modules import control
    from resources.lib.modules import client
    import os, xbmcgui

    try:
        curVersion = repoVer = control.addon('plugin.video.exoshark').getAddonInfo('version')
        versionFile = os.path.join(control.dataPath, 'repoversion.v')

        try:
            with open(versionFile, 'rb') as fh: repoVer = fh.read()
        except:
            pass

        url = 'aHR0cHM6Ly9yYXcuZ2l0aHVidXNlcmNvbnRlbnQuY29tL2h1bnJlcG8vZXhzcmVwby9tYXN0ZXIvYWRkb25zLnhtbA=='
        try:
            r = client.request(url.decode('base64'))
            repoVer = client.parseDOM(r, 'addon', attrs={'id': 'plugin.video.exoshark'}, ret='version')[0]
        except:
            pass
        try:
            with open(versionFile, 'wb') as fh: fh.write(repoVer)
        except:
            pass

        text = []
        text += [u'Jelenlegi verzi\u00F3: [B]%s[/B]\nLegfrissebb verzi\u00F3: [B]%s[/B]' % (curVersion, repoVer)]
        if repoVer < curVersion:
            text += [u'Ezt a verzi\u00F3t nem a hivatalos fejleszt\u0151 k\u00E9sz\u00EDtette. ' + \
                     u'A hivatalos repository telep\u00EDt\u00E9s\u00E9hez l\u00E1togass el a kieg\u00E9sz\u00EDt\u0151 weboldal\u00E1ra: [B]bit.ly/exorepo[/B]']
        tt = '\n\n'.join(text)
        info_dialog = xbmcgui.Dialog()
        info_dialog.textviewer(u'Inform\u00E1ci\u00F3', tt)
    except:
        return
