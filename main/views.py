#encoding:utf-8
#from main.models import Usuario, Puntuacion, Pelicula
from main.models import Brawler, Poder, Gadget, Clase, Rareza

from main.populateDB import populateDatabase
#from main.forms import  UsuarioBusquedaForm, PeliculaBusquedaForm
from django.shortcuts import render, get_object_or_404
from django.http.response import HttpResponseRedirect
from django.conf import settings
from main.recommendations import  transformPrefs, calculateSimilarItems, getRecommendations, getRecommendedItems, topMatches, sim_pearson
import shelve

from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required

#Whoosh
from .whooshIndex import buscar_brawler_por_nombre

#Recomendaciones
from .forms import BrawlerBusquedaForm, FiltroAvanzadoForm, CompararBrawlersForm

#Funcion de acceso restringido que carga los datos en la BD  
#@login_required(login_url='/ingresar')
def populate(request):
    populateDatabase(request)
    #logout(request)  # se hace logout para obligar a login cada vez que se vaya a poblar la BD
    return HttpResponseRedirect('/brawlers')

def inicio(request):
    return render(request, 'inicio.html',{'STATIC_URL':settings.STATIC_URL})

#Listados
def lista_brawlers(request):
    brawlers=Brawler.objects.all()
    return render(request,'brawlers.html', {'datos':brawlers})

def detalle_brawler(request, nombre_brawler):
    brawler = get_object_or_404(Brawler, nombre=nombre_brawler)
    recomendaciones = recomendaciones_brawlers_detalles(brawler)

    return render(request, 'brawler.html', {
        'brawler': brawler,
        'recomendaciones': recomendaciones,
    })
def lista_clases(request):
    clases = Clase.objects.prefetch_related('brawler_set').all()
    return render(request,'clases.html', {'datos':clases})

def lista_rarezas(request):
    rarezas=Rareza.objects.prefetch_related('brawler_set').all()
    return render(request,'rarezas.html', {'datos':rarezas})

def lista_poderes(request):
    brawlers = Brawler.objects.prefetch_related('poderes').all()  
    return render(request,'poderes.html', {'brawlers':brawlers})

def lista_gadgets(request):
    brawlers = Brawler.objects.prefetch_related('gadgets').all()  
    return render(request,'gadgets.html', {'brawlers':brawlers})

#Whoosh
def buscar_brawler_nombre(request):

    if request.method == "GET":
        nombre = request.GET.get("nombre", "")
        
        if nombre:
            resultados = buscar_brawler_por_nombre(nombre)

        else:
            resultados = []
        return render(request, "buscar_brawler_nombre.html", {"resultados": resultados})

#Recomendaciones
def normalize_and_enhance(prefs, min_value=0.001):
    enhanced_prefs = {}
    
    for person in prefs:
        person_prefs = prefs[person]
        max_val = max(person_prefs.values(), default=0)
        min_val = min(person_prefs.values(), default=0)
        
        if max_val == min_val:
            max_val += 1  
        enhanced_prefs[person] = {
            item: max(value if value > 0 else min_value, 0) / (max_val - min_val)
            for item, value in person_prefs.items()
        }
    
    return enhanced_prefs

def recomendaciones_brawlers_detalles(brawler_actual):
    recomendaciones = []

    try:
        brawlers = Brawler.objects.all()

        prefs = {}
        for brawler in brawlers:
            prefs[brawler.nombre] = {
                'winRate': brawler.winRate,
                'useRate': brawler.useRate,
            }
        prefs = normalize_and_enhance(prefs)

        if brawler_actual.nombre in prefs:
            recomendaciones_raw = topMatches(prefs, brawler_actual.nombre, similarity=sim_pearson)
            
            recomendaciones = [
                {
                    'nombre': rec[1],
                    'score': rec[0],
                    'brawler': Brawler.objects.get(nombre=rec[1])
                }
                for rec in recomendaciones_raw
            ]

    except Brawler.DoesNotExist:
        pass

    return recomendaciones

def filtro_avanzado(request):
    resultados = []
    form = FiltroAvanzadoForm(request.GET or None)

    if form.is_valid():
        clase = form.cleaned_data.get('clase')
        rareza = form.cleaned_data.get('rareza')
        winRate_min = form.cleaned_data.get('winRate_min')
        winRate_max = form.cleaned_data.get('winRate_max')
        useRate_min = form.cleaned_data.get('useRate_min')
        useRate_max = form.cleaned_data.get('useRate_max')
        selecciones_min = form.cleaned_data.get('selecciones_min')

        query = Brawler.objects.all()
        
        if clase:
            query = query.filter(clase=clase)
        if rareza:
            query = query.filter(rareza=rareza)
        if winRate_min is not None:
            query = query.filter(winRate__gte=winRate_min)
        if winRate_max is not None:
            query = query.filter(winRate__lte=winRate_max)
        if useRate_min is not None:
            query = query.filter(useRate__gte=useRate_min)
        if useRate_max is not None:
            query = query.filter(useRate__lte=useRate_max)
        if selecciones_min is not None:
            query = query.filter(seleccionesRegistradas__gte=selecciones_min)

        resultados = query

    return render(request, 'filtro_avanzado.html', {
        'form': form,
        'resultados': resultados,
    })

def comparar_brawlers(request):
    brawler_1 = None
    brawler_2 = None
    diferencias = None
    
    if request.method == 'POST':
        form = CompararBrawlersForm(request.POST)
        if form.is_valid():
            brawler_1 = form.cleaned_data['brawler_1']
            brawler_2 = form.cleaned_data['brawler_2']
            
            diferencias = {
                'winRate': (brawler_1.winRate, brawler_2.winRate),
                'useRate': (brawler_1.useRate, brawler_2.useRate),
                'seleccionesRegistradas': (brawler_1.seleccionesRegistradas, brawler_2.seleccionesRegistradas),
                'clase': (brawler_1.clase.nombre, brawler_2.clase.nombre),
                'rareza': (brawler_1.rareza.nombre, brawler_2.rareza.nombre),
            }
            
    else:
        form = CompararBrawlersForm()

    return render(request, 'comparar_brawlers.html', {
        'form': form,
        'brawler_1': brawler_1,
        'brawler_2': brawler_2,
        'diferencias': diferencias
    })
