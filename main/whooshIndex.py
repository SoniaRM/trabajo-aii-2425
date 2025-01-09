import os
from whoosh.index import create_in, open_dir
from whoosh.fields import Schema, TEXT, ID
from whoosh.qparser import QueryParser
from whoosh.writing import IndexWriter
from .models import Brawler, Clase, Rareza, Poder, Gadget
from whoosh.analysis import LowercaseFilter, SimpleAnalyzer
from whoosh.query import Wildcard, Prefix

# Definir el esquema de Whoosh
schema = Schema(
    nombre=TEXT(stored=True, analyzer=SimpleAnalyzer() | LowercaseFilter()),
    clase=TEXT(stored=True),  
    rareza=TEXT(stored=True),  
    poderes=TEXT(stored=True), 
    gadgets=TEXT(stored=True),
    winRate=TEXT(stored=True), 
    useRate=TEXT(stored=True),
    seleccionesRegistradas=TEXT(stored=True), 
    imagen=ID(stored=True)
)

def crear_indice():
    if not os.path.exists("brawlers_index"):
        os.mkdir("brawlers_index")
    create_in("brawlers_index", schema=schema)

def agregar_a_indice(brawler):
    ix = open_dir("brawlers_index")
    writer = ix.writer()

    winRate = str(brawler.winRate) if brawler.winRate is not None else ""
    useRate = str(brawler.useRate) if brawler.useRate is not None else ""
    seleccionesRegistradas = str(brawler.seleccionesRegistradas) if brawler.seleccionesRegistradas is not None else ""
    imagen = str(brawler.imagen) if brawler.imagen is not None else ""

    writer.add_document(
        nombre=brawler.nombre,
        clase=brawler.clase.nombre,  
        rareza=brawler.rareza.nombre,  
        poderes=",".join([p.nombre for p in brawler.poderes.all()]),  
        gadgets=",".join([g.nombre for g in brawler.gadgets.all()]), 
        winRate=winRate,
        useRate=useRate,
        seleccionesRegistradas=seleccionesRegistradas,
        imagen=imagen
    )
    
    writer.commit()

def buscar_brawler_por_nombre(nombre):
    ix = open_dir("brawlers_index")
    with ix.searcher() as searcher:
        nombre = nombre.lower()
        query = Wildcard("nombre", f"*{nombre}*")
        results = searcher.search(query)
        
        brawlers_encontrados = []
        for result in results:
            brawler = {
                "nombre": result['nombre'],
                "clase": result['clase'],
                "rareza": result['rareza'],
                "poderes": result['poderes'],
                "gadgets": result['gadgets'],
                "winRate":result['winRate'],
                "useRate":result['useRate'],
                "seleccionesRegistradas":result['seleccionesRegistradas'],
                "imagen": result['imagen']
            }
            brawlers_encontrados.append(brawler)
        
        return brawlers_encontrados
