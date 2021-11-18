from bs4 import BeautifulSoup
import requests
import libtorrent as lt
import time
import datetime
import re

#fonction trouvée sur internet pour télécharger un torrent en passant un lien magnet
def download(link):

    ses = lt.session()
    ses.listen_on(6881, 6891)
    params = {
        'save_path': '/home/faouzi/media',
        'storage_mode': lt.storage_mode_t(2)}

    print(link)

    handle = lt.add_magnet_uri(ses, link, params)
    ses.start_dht()

    begin = time.time()
    print(datetime.datetime.now())

    print ('Downloading Metadata...')
    while (not handle.has_metadata()):
        time.sleep(1)
    print ('Got Metadata, Starting Torrent Download...')

    print("Starting", handle.name())

    while (handle.status().state != lt.torrent_status.seeding):
        s = handle.status()
        state_str = ['queued', 'checking', 'downloading metadata', \
                'downloading', 'finished', 'seeding', 'allocating']
        print ('%.2f%% complete (down: %.1f kb/s up: %.1f kB/s peers: %d) %s ' % \
                (s.progress * 100, s.download_rate / 1000, s.upload_rate / 1000, \
                s.num_peers, state_str[s.state]))
        time.sleep(5)

    end = time.time()
    print(handle.name(), "COMPLETE")

    print("Elapsed Time: ",int((end-begin)//60),"min :", int((end-begin)%60), "sec")
    print(datetime.datetime.now())  


def scraper():
    #inputs
    choice = input('Which tracker do you want to use ( Choices : [1]piratebay [2]1337) ?')
    search = input('What do you want to download ? : ')
    number = input('How many torrents do you want to download ? : ')
    #soit 1 pour piratebay soit 2 pour 1337
    if choice == '1':
        #crée la soupe BS4 avec la requete
        url = 'https://thepiratebay.party/search/' + search
        page = requests.get(url)
        soup = BeautifulSoup(page.text, 'lxml')
        #toute la table de résultats ayant pour id searchResult
        torrents = soup.find(id="searchResult")
        #tous les torrents dans la page des résultats
        trs = torrents.find_all("tr")
        magnets = []
        names = []
        sizes = []
        seeds = []
        #boucle pour récuperer des données pour chaque torrent.
        #on commence par 1 parce que le premier tr est le "header" de la table
        #number+1 pour aller jusqu'au choix de l'utilisateur
        for tr in trs[1:int(number)+1]:
            #insére le lien magnet, le nom, la taille et le nbre de seeds du torrent dans des variables
            magnets.append(tr.nobr.a['href'])
            name = tr.find_all('td')
            names.append(name[1].a.text)
            sizes.append(name[4].text)
            seeds.append(name[5].text)
        #display tous les torrent trouvés avec les infos détaillées
        print("Torrents found : ")
        for key,val in enumerate(names):
            print("[" + str(key) + "]" + val + "[" + sizes[key] + "] (" + seeds[key] + " seeds)")
        #choisir les torrents à DL via leur index
        which = input('Which torrents do you want to download ? (0/1/2/3...) : ')
        #selectionne les nombre dans l'input de l'utilisateur. exemple '1/2,3' => 1 2 3
        choices = re.findall(r'\d+', which)
        #télécharge les torrents via leur index avec les nombres choisis par l'user
        print("Will download : ")
        for key,val in enumerate(choices):
            print("[" + str(val) + "]" + names[int(val)] + "[" + sizes[int(val)] + "] (" + seeds[int(val)] + " seeds)")
        for each in choices:
            download(magnets[int(each)])
    #meme procédé mais pour 1377 et à un détail près : premier foreach
    elif choice == '2':
        url = 'https://www.1377x.to/search/' + search + '/1/'
        page = requests.get(url)
        soup = BeautifulSoup(page.text, 'lxml')
        torrents = soup.find_all('tr')
        magnets = []
        names = []
        sizes = []
        seeds = []
        for each in torrents[1:int(number)+1]:
            #le lien du magnet link est dans la page de détails du torrent
            #pour chaque tour de boucle on saisit le lien du torrent et 
            #on reforme une nouvelle soupe avec cette nouvelle page pour 
            #aller récupérer les infos qu'on veut (magnet, nom etc)
            url = 'https://www.1377x.to' + each.find_all('a')[1].get('href')
            page = requests.get(url)
            soup = BeautifulSoup(page.text, 'lxml')
            magnet = soup.find(class_='col-9 page-content')
            magnet = magnet.li.a.get('href')
            magnets.append(magnet)
            name = soup.find(class_='box-info-heading clearfix')
            name = name.h1.text
            names.append(name)
            size = soup.find(class_='list')
            size = size.find_all('li')[3].span.text
            sizes.append(size)
            seed = soup.find(class_='seeds')
            seeds.append(seed.text)
        print("Torrents found : ")
        for key,val in enumerate(names):
            print("[" + str(key) + "]" + val + "[" + sizes[key] + "] (" + seeds[key] + " seeds)")
        which = input('Which torrents do you want to download ? (0/1/2/3...) : ')
        choices = re.findall(r'\d+', which)
        print("Will download : ")
        for key,val in enumerate(choices):
            print("[" + str(val) + "]" + names[int(val)] + "[" + sizes[int(val)] + "] (" + seeds[int(val)] + " seeds)")
        for each in choices:
            download(magnets[int(each)])
scraper()