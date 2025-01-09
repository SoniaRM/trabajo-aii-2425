
from main.models import  Clase, Rareza, Poder, Gadget, Brawler
from .whooshIndex import agregar_a_indice, crear_indice 

from bs4 import BeautifulSoup
import urllib.request
import re
from io import BytesIO
from django.core.files import File
from django.http import HttpResponse
import requests

from django.core.files.base import ContentFile

import os, ssl
if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
getattr(ssl, '_create_unverified_context', None)):
    ssl._create_default_https_context = ssl._create_unverified_context


path = "data"

BASE_URL = "https://brawlify.com/es/brawlers/"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
}

api_url = "https://cube.brawltime.ninja/cubejs-api/v1/load?query=%7B%22measures%22%3A%5B%22map.winRateAdj_measure%22%2C%22map.useRate_measure%22%2C%22map.picks_measure%22%5D%2C%22dimensions%22%3A%5B%22map.brawler_dimension%22%5D%2C%22filters%22%3A%5B%7B%22member%22%3A%22map.season_dimension%22%2C%22operator%22%3A%22gte%22%2C%22values%22%3A%5B%222024-12-09%22%5D%7D%2C%7B%22member%22%3A%22map.mode_dimension%22%2C%22operator%22%3A%22equals%22%2C%22values%22%3A%5B%22wipeout5V5%22%5D%7D%5D%2C%22order%22%3A%7B%22map.winRateAdj_measure%22%3A%22desc%22%7D%7D&queryType=multi"

def guardarImagen(url, brawler):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            brawler.imagen.save(
                url.split('/')[-1], 
                ContentFile(response.content), 
                save=True
            )
            print(f"Imagen guardada para {brawler.nombre}")
        else:
            print(f"Error al obtener la imagen para {brawler.nombre}, status code: {response.status_code}")
    except Exception as e:
        print(f"Error al guardar la imagen para {brawler.nombre}: {e}")


def populateDatabase(request):
    crear_indice()

    Clase.objects.all().delete()
    Rareza.objects.all().delete()
    Poder.objects.all().delete()
    Gadget.objects.all().delete()
    Brawler.objects.all().delete()

    response_api = requests.get(api_url)
    if response_api.status_code == 200:
        data = response_api.json()

    response = requests.get(BASE_URL, headers=headers)
    s = BeautifulSoup(response.text,"lxml")

    brawlers = s.find_all("div", class_="d-flex flex-row align-items-center col-6 col-sm-4 col-md-3 col-lg-3 mb-2")
    for i, b in enumerate(brawlers):
        #if i >= 7: 
            #break
            
        #Nombre
        div_tag = b.find('div')
        a_tag = div_tag.find('a')  # Buscamos el primer enlace dentro del div
        h2_tag = a_tag.find('h2')  # Buscamos el h2 dentro del a
        nombre = h2_tag.text.strip()  # Extraemos el texto del h2

        brawler_link = "https://brawlify.com" + b.find('a', class_='mr-auto')['href']
        
        responseB = requests.get(brawler_link, headers=headers)
        soup = BeautifulSoup(responseB.text, "lxml")
        #Clase
        clase = soup.find('a', class_='link opacity shadow-normal').find('span').text.strip()
        if clase == 'Unknown':
            clase_obj, created = Clase.objects.get_or_create(nombre='Unknown')
        else:
            clase_obj, created = Clase.objects.get_or_create(nombre=clase)

        #Rareza
        rareza = soup.find('h2', class_=re.compile(".*rarity.*")).text.strip()
        if rareza == 'Unknown':
            rareza_obj, created = Rareza.objects.get_or_create(nombre='Unknown')
        else:
            rareza_obj, created = Rareza.objects.get_or_create(nombre=rareza)

        #Descripcion
        descripcion = soup.find('div', class_='brawler-desc pt-1 pl-2 pr-1 pb-0 mb-2 gray-border').find('p').text.strip()

        win_rate = 0.0
        use_rate = 0
        picks = 0

        found_match = False  

        for brawler in data.get("results", [])[0].get("data", []):

            if nombre.upper() == brawler.get("map.brawler_dimension"):

                win_rate = round(float(brawler.get("map.winRateAdj_measure", 0)) * 100, 2)  
                use_rate =round( float(brawler.get("map.useRate_measure", 0)) / 1000000 , 2) 
                picks = int(brawler.get("map.picks_measure", 0))  
    
                print(f"Nombre: {nombre}")
                print(f"Tasa de Victorias Ajustada: {win_rate}%")
                print(f"Tasa de Uso: {use_rate}")
                print(f"Selecciones Registradas: {picks}")
                print("-" * 30)
                found_match = True

                break  

            else:
                continue

            if not found_match:
                win_rate = 0.0
                use_rate = 0
                picks = 0

        #Imagen
        a_img = b.find('a') 
        imagen_url = a_img.find('img')['src']

        
        brawler, created = Brawler.objects.get_or_create(
            nombre=nombre,
            clase = clase_obj,
            rareza = rareza_obj,
            winRate = win_rate,
            useRate = use_rate,
            seleccionesRegistradas = picks,
            descripcion= descripcion
        )
        if created:
            guardarImagen(imagen_url, brawler)

        brawler.save()

        #Poderes
        poderes_container = soup.find('div',id='star-powers').find('div',class_='post-type4 gray-border p-1').find('div',class_='pt-2 pl-3 pr-3 pb-3')
        poderes = poderes_container.find_all('div', class_='row p-1')

        for p in poderes: 

            nombre = p.find('h4', class_='star-power-title text-warning pl-1').text.strip()
            imagen_poder = p.find('img')['src']
            p, created = Poder.objects.get_or_create(nombre=nombre)
            if created:
                guardarImagen(imagen_poder, p)
                if not crearPoder(nombre, p):
                    print("No se ha podido modificar el poder "+nombre)
            brawler.poderes.add(p) 
            brawler.save()

        
        #Gadgets
        gadgets_container = soup.find('div',id='gadgets').find('div',class_='post-type4 gray-border p-1').find('div',class_='pt-2 pl-3 pr-3 pb-3')
        gadgets = gadgets_container.find_all('div', class_='row p-1') 
        for g in gadgets: 
            nombre = g.find('h4', class_='gadget-title text-warning pl-1').text.strip()
            imagen_gadget = g.find('img')['src']
            g, created = Gadget.objects.get_or_create(nombre=nombre)
            if created:
                guardarImagen(imagen_gadget, g)
                if not crearGadget(nombre, g):
                    print("No se ha podido modificar el gadget "+nombre)
            brawler.gadgets.add(g) 
            brawler.save()

        agregar_a_indice(brawler)

    return HttpResponse("Base de datos poblada con éxito.")

def crearPoder(nombre, html):
    try:
        descripcion = html.find("p", class_="star-power-desc mb-0").text.strip()
        
        Poder.objects.filter(nombre=nombre).update(descripcion= descripcion)       
    except:
        return False
    else:
        return True

def crearGadget(nombre, html):
    try:
        descripcion = html.find("p", class_="gadget-desc mb-0").text.strip()
        
        Gadget.objects.filter(nombre=nombre).update(descripcion= descripcion)       
    except:
        return False
    else:
        return True