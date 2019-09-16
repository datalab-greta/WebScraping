#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep  4 15:58:09 2019
CE CODE FONCTIONNE POUR DU SCRAPING
@author: shikshik
"""

import requests, json, sys, re, os, configparser
from bs4 import BeautifulSoup
#from sqlalchemy.sql import text
from sqlalchemy import create_engine, text
from urllib import parse
import os,configparser
import pandas as pd
import datetime
import time # Librairie qui decompte le temps d'execution du script
from requests import get


# Debut du decompte du temps
start_time = time.time()

poste = []
address = []
date_publication = []
offre_number= []
description = []
Qualification = []
secteur_activity = []       
entreprise = []
partenaire = []
lien_propre = []
listebis = []
listeter=[]
dico = {}

BASE = 'https://candidat.pole-emploi.fr'

# Récupération du nombre d'offres
URL = BASE+'/offres/recherche?&motsCles=data&offresPartenaires=true&range=0-9&rayon=10&tri=0'####TRUE OR FALSE POUR LES PARTENAIRES
#print("URL: "+URL)
req = requests.get(URL)
soup = BeautifulSoup(req.text, "lxml")
#str = soup.select('h1.title')[0].text.replace('\n', '').replace(' offres', '')
#str = soup.select('h1.title')[0].text[:4]
stri = re.findall(r'\d+', soup.select('h1.title')[0].text)[0] # REGEX pour le 1er chiffre !
N=int(stri)
print("%d [%s]" % (N, URL))



i=0
while(i<N):
    imax = i+99 if (i+99<N) else N
    #if imax>N:
    #    imax=N
    rg="%d-%d" % (i, imax)
    print(rg)
    URL = BASE+'/offres/recherche?&motsCles=data&offresPartenaires=true&range='+rg+'&rayon=10&tri=0'####TRUE OR FALSE POUR LES PARTENAIRES
    #req = requests.get()
    print("URL: "+URL)
    req = requests.get(URL)
    soup = BeautifulSoup(req.text, "lxml")
    list = soup.select('li.result')
    if len(list)==0:
        #return
        continue
    print("Nombre de blocks: %d [%s]" % (len(list), soup.select('h1.title')[0].text))
    for x in list:
        a = x.select('a.btn-reset')[0]
        title = a['title'][:80] # ATTENTION: VARCHAR(80) !
        href = a['href']
        href_unique = BASE+href
        id = href[25:]     
        listebis.append(href_unique)
    i+=100### possible probleme lié a l'indentation


for i in listebis:
    skills=''
    xp=''
    liste=[]
    url = i
    response = get(url)
    soup = BeautifulSoup(response.text, "lxml")  
    poste = str(soup.find_all("h2")[1:2])
    poste = poste[31:len(poste)].replace("\n</h2>]","")        
    print("a" ,   poste)
    print("################################################")
    address = str(soup.find_all("span", itemprop={"name"}))
    address = address[23:len(address)].split('<')[0]
    print("b" ,   address)
    print("################################################")
    date_publication = str(soup.find_all("span", itemprop={"datePosted"}))
    date_publication = date_publication[51:len(date_publication)].replace("\n</span>]","") 
    print("c" ,   date_publication)
    print("################################################")
    offre_number = str(soup.find_all("span", itemprop={"value"})[0:1])
    offre_number=offre_number[24:len(offre_number)].replace("</span>]","") 
    print("d" ,   offre_number)
    print("################################################")           
    description = str(soup.find_all("div", itemprop={"description"}))
    description = description[70:len(description)].replace('</p></div>]',"")        
    print("e" ,   description)
    print("################################################")     
    experience = str(soup.find_all('span', attrs={"class":"skill-name"})) 
    
    for x in experience.split('span'):
        """       on récupère les elements definit dans les elses dans des variables avant de les ajouter dans une liste"""
        if ("skills" in x):
            skills += x+"|"
            skills = skills.replace('class="skill-name" itemprop="skills">','').replace('</','')          
        elif ("experienceRequirements" in x):
            xp += x.replace('</','')
            xp = xp[54:len(xp)]  
    print(skills)
    print("################################################")   
    print(xp)
    print("################################################")     
    Qualification = str(soup.find_all("span", itemprop={"qualifications"}))
    Qualification = Qualification[33:len(Qualification)].replace("</span>]","")
    print(Qualification)
    print("################################################")
    secteur_activity = str(soup.find_all("span", itemprop={"industry"}))
    secteur_activity = secteur_activity[27:len(secteur_activity)].replace('</span>]',"")
    print(secteur_activity)
    print("################################################")
    entreprise = str(soup.find_all('h4', attrs={"class":"t4 title"})[0:1]) 
    entreprise = entreprise[22:len(entreprise)].replace("</h4>]","").replace("\n","")
    print(entreprise)
    print("################################################")        

    liste.append(poste)
    liste.append(address)
    liste.append(date_publication)
    liste.append(offre_number)
    liste.append(description)
    liste.append(skills)
    liste.append(xp)
    liste.append(Qualification)
    liste.append(secteur_activity)           
    liste.append(entreprise)
    liste.append(i)
    """    ajout de chaque liste dans une autre liste"""
    listeter.append(liste)
    print("Ligne numéro", i)

c=0
for i in listeter:
    """    transformation de la liste en dictionnaire    """
    date = str(datetime.datetime.now())  
    c += 1
    dico[date] = i
"""transformation du dictionnaire en df avec les clés en index"""
df= pd.DataFrame.from_dict(dico,orient=u'index',columns=[u"Poste",u"Localisation",u"Date parution",u"Référence",u"Description",u"Competences",u"Experience",u"Qualification",u"Secteur",u"Entreprise",u"Lien de l'offre"])

print(df)

"""
print("### Début de l'import vers la BDD")
        
from sqlalchemy import create_engine
import argparse
import os,configparser

parser = argparse.ArgumentParser()
parser.add_argument("-v", action="store_true", help="Verbose SQL")
parser.add_argument("--base", help="Répertoire de movies")
parser.add_argument("--bdd", help="Base de donnée")
args = parser.parse_args()

config = configparser.ConfigParser()
config.read_file(open(os.path.expanduser("~/Téléchargements/.datalab.cnf")))

base = args.base 

DB="PASCALICOLA?charset=utf8"
con = create_engine("mysql://%s:%s@%s/%s" % (config['myBDD']['user'], config['myBDD']['password'], config['myBDD']['host'], DB), echo=args.v)
df.to_sql(con=con, name='PASCALICOLAS_FINALE_ULTIME', if_exists='append')
#df.to_csv('PASCALICOLAS_FINALE.csv')
print("### Import vers la BDD réussi")
"""


# Affichage du temps d execution
print("Temps d execution : %s secondes ---" % (time.time() - start_time))


