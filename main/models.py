#encoding:utf-8

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Clase(models.Model):
    nombre = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.nombre
        
class Rareza(models.Model):
    nombre = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.nombre

class Poder(models.Model):
    nombre = models.CharField(max_length=30, unique=True)
    imagen = models.ImageField(upload_to='poderes/', blank=True, null=True)

    def __str__(self):
        return self.nombre

class Gadget(models.Model):
    nombre = models.CharField(max_length=30, unique=True)
    imagen = models.ImageField(upload_to='gadgets/', blank=True, null=True)

    def __str__(self):
        return self.nombre

class Brawler(models.Model):
    nombre = models.CharField(max_length=30, unique=True)
    winRate = models.FloatField(default=0.0)
    useRate = models.FloatField(default=0)
    seleccionesRegistradas = models.IntegerField(default=0)
    clase = models.ForeignKey(Clase, on_delete=models.CASCADE)
    rareza = models.ForeignKey(Rareza, on_delete=models.CASCADE)
    imagen = models.ImageField(upload_to='brawlers/', blank=True, null=True)
    poderes = models.ManyToManyField(Poder)  # Relación muchos a muchos con Poder
    gadgets = models.ManyToManyField(Gadget)  # Relación muchos a muchos con Gadget
    descripcion = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.nombre
    

