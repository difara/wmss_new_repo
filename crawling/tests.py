from django.test import TestCase

from bs4 import BeautifulSoup
import requests, re, string
import urllib.request
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from jst.models import *
import numpy as np

list_news = []
def scrap_detik_page(url):
    try:
        page = urllib.request.urlopen(url)
        html = page.read()
        soup = BeautifulSoup(html, "html.parser")
        judul = soup.find('a',{'data-title': True})
        judul_berita = judul['data-title']
        konten = soup.find('div',attrs={'id':'detikdetailtext'})
#         konten_berita = konten.text.strip().splitlines()[0]
        konten_berita = konten.get_text()
        lihat_tambahan = konten.find_all("div", class_="lihatjg")
        for row in lihat_tambahan:
            bajug = row.get_text()
            
        

            konten_berita = re.sub(bajug, ' ', konten_berita)
        konten_berita = konten_berita.strip().splitlines()[0]
        konten_berita = re.sub(r'(Foto:.+detikcom)', '', konten_berita)
        return {'judul_berita': judul_berita, 'konten_berita': konten_berita}
    except:
        pass
#     list_berita.append({'judul_berita':judul_berita, 'konten_berita':konten_berita})

def scrap_detik(keyword, jumlah):
    url = 'https://www.detik.com/search/searchall?query='+keyword
    return get_link_detik(url, jumlah, list())

def scrap_detik1(keyword, jumlah, date_start, date_end):
    url = 'https://www.detik.com/search/searchall?query='+keyword+'&sortby=time&fromdatex='+date_start+'&todatex='+date_end
    return get_link_detik(url, jumlah, list()) 

def get_link_detik(url, jumlah, data):
    page = requests.get(url)
    content = page.content
    soup_page = BeautifulSoup(content, 'html.parser')
    for article in soup_page.select('div.list-berita > article'):
        if article.has_attr('class'):
            continue
        berita = scrap_detik_page(article.find('a')['href'])
        data.append(berita) #ganti dengan method scarp halaman berita detik
        if len(data)==jumlah:
            break
    if len(data)<jumlah:
        next_page = soup_page.find('div', class_='paging')
        next_page= next_page.find('a', class_='last')['href']
        return get_link_detik(next_page, jumlah, data)
    else:
        return data

def crawl_kompas(keyword, jumlah, data = list()):
    jum = 0
    driver = webdriver.Chrome()
    driver.get('http://www.kompas.com')
    elem = driver.find_element_by_id('search')
    elem.send_keys(keyword)
    elem.send_keys(Keys.RETURN)
    html = driver.page_source
    soup_page = BeautifulSoup(html, 'html.parser')
    tek = soup_page.findAll('a', attrs={'class':'gs-title'})
    for row in tek:
        berita = scrap_kompas(row['href'])
        data.append(berita)
        jum +=1
        if jum == jumlah:
                return data
    driver.quit()
            
def scrap_kompas(url):
    page = urllib.request.urlopen(url)
    html = page.read()
    soup = BeautifulSoup(html, "html.parser")
    judul = soup.find('h1', class_='read__title')
    judul_berita = judul.text.strip()
    konten = soup.find('div',attrs={'class':'read__content'})
    konten_berita = konten.text.strip()
    return {'judul_berita': judul_berita, 'konten_berita': konten_berita}

def scrap_liputan6_page(url):
    page = urllib.request.urlopen(url)
    html = page.read()
    soup = BeautifulSoup(html, "html.parser")
    judul = soup.find('h1', class_='read-page--header--title')
    judul_berita = judul.text.strip()
    konten = soup.find('div',attrs={'class':'article-content-body__item-content'})
    konten_berita = konten.text.strip()
    return {'judul_berita': judul_berita, 'konten_berita': konten_berita}

def crawl_liputan6(keyword, jumlah, data = list()):
    jum = 0
    driver = webdriver.Chrome()
    driver.get('http://www.liputan6.com')
    elem = driver.find_element_by_id('q')
    elem.send_keys(keyword)
    elem.send_keys(Keys.RETURN)
    html = driver.page_source
    soup_page = BeautifulSoup(html, 'html.parser')
    tek = soup_page.findAll('h4', attrs={'class':'articles--iridescent-list--text-item__title'})
    for div in tek:
        links = div.findAll('a', attrs={'data-template-var':'url'})
        for a in links:
            berita = scrap_liputan6_page(a['href'])
            data.append(berita)
            jum +=1
            if jum == jumlah:
                return data
    driver.quit()

def scrap_kumparan(url):
    page = urllib.request.urlopen(url)
    html = page.read()
    soup = BeautifulSoup(html, "html.parser")
    judul = soup.find('h1', class_='marg-ver-none')
    judul_berita = judul.text.strip()
    konten = soup.findAll('span',attrs={'data-text':'true'})
    konten_berita = ""
    for kon in konten:
        konten_berita = konten_berita + ", " + kon.text.strip() 
#     return {'judul_berita': judul_berita, 'konten_berita': konten_berita
    konten_berita = konten_berita[2:]
    return {'judul_berita':judul_berita, 'konten_berita':konten_berita}

def crawl_kumparan(keyword, jumlah, data = list()):
    jum = 0
    url1 = 'https://kumparan.com/search/'+keyword
    page = requests.get(url1)
    content = page.content
    soup_page = BeautifulSoup(content, 'html.parser')
    tek = soup_page.findAll('a', attrs={'class':'btn-block'})
    link = set(tek)
    for row in link:
        url2 = 'https://kumparan.com'+row['href']
        berita = scrap_kumparan(url2)
        data.append(berita)
        jum +=1
        if jum == jumlah:
            return data

def toJst(statusMI, vocabSize, stopwords,arrCorpus):
    arrStopwords = StopwordsIDDB.objects.values_list('kataStopword', flat=True)
    remove = string.punctuation
    remove = remove.replace("#", "")
    remove = remove.replace("@", "")
    
    dictKata = {} #berisi TF dari masing2 kata
    indexDoc = 0
    dictData = {} #berisi raw dokumen
    dfjKata = {} #berisi banyak dokumen yang memuat suatu kata
    numDocs = len(arrCorpus)


    #Buat data untuk MI dan Formalisasi database
    arrDataMI = []
    formalisasi = FormalisasiKataDB.objects.values_list('kataInformal', 'kataFormal')
    kataFormalisasi = {}
    for i in range(0, len(formalisasi)):
        kataFormalisasi[str(formalisasi[i][0])] = str(formalisasi[i][1])

    #Menyimpan data mentahan dan formalisasi untuk ektraksi MI
    for reader in arrCorpus:
        #reader = ''.join(reader)
        line = str(reader).lower()
        baris = line.split()

        if (len(baris) > 0):
            dictData[indexDoc] = line
            indexDoc += 1

        if (len(baris) > 0):
            kalimat = ""
            for x in range(0, len(baris)):
                if baris[x] in kataFormalisasi.keys():
                    baris[x] = kataFormalisasi[baris[x]]
                kalimat = kalimat + " " + baris[x]
            arrDataMI.append(kalimat)

    #Hitung TF dari masing2 kata
    for line in arrDataMI:
        line = line.translate(str.maketrans('', '', remove)).lower()
        baris = line.split()
        if (len(baris) > 0):
            #TF untuk unigram
            for kata in baris:
                if kata not in dictKata.keys():
                    dictKata[kata] = 1
                    dfjKata[kata] = 0
                else:
                    dictKata[kata] += 1
            #TF untuk bigram
            for i in range(0, (len(baris) - 1)):
                kata = baris[i] + " " + baris[i + 1]
                if kata not in dictKata.keys():
                    dictKata[kata] = 1
                    dfjKata[kata] = 0
                else:
                    dictKata[kata] += 1

    for line in arrDataMI:
        line = line.translate(str.maketrans('', '', remove)).lower()
        baris = line.split()
        if (len(baris) > 0):
            for i in range(0, len(baris) - 1):
                kata = str(''.join(baris[i] + " " + baris[i + 1]))
                baris.append(kata)
        # Menghitung dfj
        for kata in dictKata.keys():
            if kata in baris:
                if (dfjKata[kata] == 0):
                    dfjKata[kata] = 1
                else:
                    dfjKata[kata] += 1

    # Inisialisasi dan hitung tf-idf
    tfidfKata = {}

    # Cek stopwords
#         stopwords = request.POST['stopwords']
    if (stopwords == 'yes'):
        for kata in arrStopwords:
            if kata in dictKata.keys():
                # logging.warning(str(kata))
                del dictKata[kata]

    for kata in dictKata.keys():
        # logging.warning(kata)
        if (dfjKata[kata] == numDocs):
            n = 0
        else:
            n = 1
        tfidfKata[kata] = dictKata[kata] * np.log(numDocs / (dfjKata[kata] + n))
        # logging.warning(str(kata) +" : "+str(tfidfKata[kata]))

    # arrKata = sorted(dictKata, key=dictKata.__getitem__, reverse=True)
    arrKata = sorted(tfidfKata, key=tfidfKata.__getitem__, reverse=True)

    # file.close()
    #arrKata = sorted(dictKata, key=dictKata.__getitem__, reverse=True)

    w = 0
    kata = {}
    for word in arrKata:
        kata[w] = word
        w += 1
#         vocabSize = int(request.POST['vocabSize'])
        if (w > vocabSize):
            w = vocabSize
    
    #logging.warning(str(kata[0]))
    kalimat = str(kata[0])
    for i in range(1, w):
        kalimat = kalimat +","+kata[i]
    if(statusMI == 'yes'):
        statusMI = True
    else:
        statusMI = False
    
    return dictData, kata, indexDoc,w, kalimat, statusMI