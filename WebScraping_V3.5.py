#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 10 12:21:07 2019

@author: shikshik
"""
import requests, re, os, configparser
from bs4 import BeautifulSoup
from sqlalchemy import create_engine, text
from urllib import parse
import time # Librairie qui decompte le temps d'execution du script
from requests import get
from datetime import datetime


###############################################################################METTRE ECOMMENTAIRE#############################################
# Debut du decompte du temps
start_time = time.time()

poste = []
address = []
dept = []
ville = []
date_publication = []
offre_number= []
description = []
Qualification = []
secteur_activity = []       
entreprise = []
partenaire = []
contrat = []
horaire =[]
salaire = []
lien_propre = []
listebis = []
listeter=[]
dico = {}

BASE = 'https://candidat.pole-emploi.fr'

config = configparser.ConfigParser()
#config.read_file(open(os.path.expanduser("~/Téléchargements/.datalab.cnf")))  # Pour le bon dossier...
config.read_file(open(os.path.expanduser(".datalab.cnf")))  # VERSION SERVEUR
DB = "Bot_Job?charset=utf8"
TBL = "BOT_JOB"
CNF="myBDD"
engine = create_engine("mysql://%s:%s@%s/%s" % (config[CNF]['user'], parse.quote_plus(config[CNF]['password']), config[CNF]['host'], DB))

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

statement = text("""
INSERT INTO BOT_JOB (offre_number, poste, address, dept, ville, date_publication, description, skills, xp, Qualification, secteur_activity, entreprise, url, horaire, contrat, salaire, date1, dateLast)
  VALUES(:offre_number, :poste, :address, :dept, :ville, :date_publication, :description, :skills, :xp, :Qualification, :secteur_activity, :entreprise, :url , :horaire, :contrat, :salaire, CURRENT_DATE(), CURRENT_DATE())
ON DUPLICATE KEY
UPDATE
  offre_number = :offre_number,
  poste = :poste,
  address = :address,
  date_publication = :date_publication,
  description = :description,
  skills = :skills,
  xp = :xp,
  Qualification = :Qualification,
  secteur_activity = :secteur_activity,
  entreprise = :entreprise,
  horaire = :horaire,
  contrat = :contrat,
  salaire = :salaire,
  dateLast = CURRENT_DATE()
""")

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
    # cette boucle est utile seulement pour le "href"
    for x in list:
        a = x.select('a.btn-reset')[0]
        title = a['title'][:80] # ATTENTION: VARCHAR(80) !
        href = a['href']
        href_unique = BASE+href
        id = href[25:]     # pour dire que l'id de l'offre commence au 25eme caractères, mais je ne l'utilise pas au finale...
        listebis.append(href_unique)
        
    i+=100

for i in listebis:
    skills=''
    xp=''
    liste=[]
    url = i
    response = get(url)
    soup = BeautifulSoup(response.text, "lxml")  
    poste = str(soup.find_all("h2")[1:2])
    poste = poste[31:len(poste)].replace("\n</h2>]","")
    if poste == "":
        continue
    elif poste =='belPopinDeconnexion"></h2>]':
        poste = poste2 = str(soup.find_all("h1", itemprop="title")).replace("</h1>]","")[39:]
#############################
    address = str(soup.find_all("span", itemprop={"name"}))
    address = address[23:len(address)].split('<')[0]
    dept = address[0:3]
#    try: 
#        dept = int(address[0:3])
#    except:
#        dept= 'Pas renseigné' 
    ville = address[5:]
#############################
    date_publication = str(soup.find_all("span", itemprop={"datePosted"}))
    date_publication = date_publication[51:len(date_publication)].replace("\n</span>]","") 
#############################
    offre_number = str(soup.find_all("span", itemprop={"value"})[0:1])
    offre_number = offre_number[24:len(offre_number)].replace("</span>]","") 
#############################         
    description = str(soup.find_all("div", itemprop={"description"}))
    description = description[70:len(description)].replace('</p></div>]',"")        
############################# 
    experience = str(soup.find_all('span', attrs={"class":"skill-name"})) 
    for x in experience.split('span'):
        """       on récupère les elements definit dans les elses dans des variables avant de les ajouter dans une liste"""
        if ("skills" in x):
            skills += x+"|"
            skills = skills.replace('class="skill-name" itemprop="skills">','').replace('</','')          
        elif ("experienceRequirements" in x):
            xp += x.replace('</','')
            xp = xp[54:len(xp)]  
#############################  
    Qualification = str(soup.find_all("span", itemprop={"qualifications"}))
    Qualification = Qualification[33:len(Qualification)].replace("</span>]","")
#############################
    secteur_activity = str(soup.find_all("span", itemprop={"industry"}))
    secteur_activity = secteur_activity[27:len(secteur_activity)].replace('</span>]',"")
#############################
    entreprise = str(soup.find_all('h4', attrs={"class":"t4 title"})[0:1]) 
    entreprise = entreprise[22:len(entreprise)].replace("</h4>]","").replace("\n","")
#############################
    horaire = soup.find('dd' , attrs =  {'itemprop':"workHours"})
    if horaire is None:
        horaire = ''
    else :
        horaire = horaire.text.replace('\n', '')
#############################
    contrat = soup.find('dd').text.replace('\n', '')[:28]
    if contrat == 'Profession libéraleEmploi no':
        contrat = 'Profession libérale Emploi non salarié'
#############################
    dl = soup.select('dl')[0]
    txt = dl.text
    salaire = re.sub(r'.*Salaire\s*:\s*', '', txt, flags=re.DOTALL).replace('\n', '')    
    if salaire == 'Type de contratContrat à durée indéterminéeContrat travail':
        salaire = 'Pas renseigné'
    elif salaire == 'Annuel de':
        salaire = 'Pas renseigné'
    elif salaire == 'Type de contratContrat à durée déterminée - 1 MoisContrat travail':
        salaire = 'Pas renseigné'
    elif salaire == 'Type de contratContrat à durée déterminée - 4 MoisContrat travail':
        salaire ='Pas renseigné'
    elif salaire =='Type de contratContrat à durée déterminée - 12 MoisContrat travail':
        salaire = 'Pas renseigné'
    elif salaire =='Type de contratMission intérimaire - 18 MoisContrat travail':
        salaire = 'Pas renseigné'
    elif salaire =='Type de contratMission intérimaire - 12 MoisContrat travail':
        salaire = 'Pas renseigné'
    elif salaire =='Type de contratContrat à durée déterminée - 24 MoisContrat travail':
        salaire = 'Pas renseigné'
    elif salaire =='Type de contratContrat à durée indéterminéeContrat apprentissage':
        salaire = 'Pas renseigné'
    elif salaire =='Type de contratContrat à durée déterminée - 12 MoisContrat apprentissage':
        salaire = 'Pas renseigné'
    elif salaire =='Type de contratContrat à durée déterminée - 12 MoisContrat travailDurée du travail35 H  Horaires normaux':
        salaire = 'Pas renseigné'
    elif salaire =='Type de contratMission intérimaire - 1 MoisContrat travail':
        salaire = 'Pas renseigné'
    elif salaire =='Type de contratContrat à durée déterminée - 6 MoisContrat apprentissage':
        salaire = 'Pas renseigné'
    elif salaire =='Type de contratProfession libéraleEmploi non salarié':
        salaire = 'Pas renseigné'
    elif salaire =='Type de contratContrat à durée déterminée - 1 MoisContrat apprentissage':
        salaire = 'Pas renseigné'
    elif salaire =='Type de contratContrat à durée déterminée - 24 MoisCont. professionnalisation':
        salaire = 'Pas renseigné'
    elif salaire =='Type de contratContrat à durée déterminée - 36 MoisContrat travail':
        salaire = 'Pas renseigné'
    elif salaire =='Type de contratContrat à durée déterminée - 6 MoisContrat travail':
        salaire = 'Pas renseigné'
    elif salaire =='Type de contratMission intérimaire - 6 MoisContrat travail':
        salaire = 'Pas renseigné'
    elif salaire =='Type de contratContrat à durée déterminée - 1 An(s)Contrat travail':
        salaire = 'Pas renseigné'
    elif salaire =='Type de contratContrat à durée déterminée - 10 MoisContrat travail':
        salaire = 'Pas renseigné'
    elif salaire =='Type de contratContrat à durée déterminée - 22 MoisContrat apprentissage':
        salaire = 'Pas renseigné'
    elif salaire =='Type de contratMission intérimaire - 4 MoisContrat travail':
        salaire = 'Pas renseigné'
    elif salaire =='Type de contratMission intérimaire - 2 MoisContrat travail':
        salaire = 'Pas renseigné'
    elif salaire =='Type de contratContrat à durée indéterminéeContrat travailDurée du travail35 H  Horaires normaux':
        salaire = 'Pas renseigné'
    elif salaire =='Type de contratContrat à durée indéterminéeContrat travailDurée du travailHoraires normaux':
        salaire = 'Pas renseigné'
    elif salaire =='Type de contratContrat à durée déterminée - 18 MoisContrat travail':
        salaire = 'Pas renseigné'
    elif salaire =='Type de contratContrat à durée indéterminéeContrat travailDurée du travailTemps pleinTemps plein':
        salaire = 'Pas renseigné'
    elif salaire =='Fonction publique territoriale':
        salaire = 'Pas renseigné'
    elif salaire =='Type de contratFranchiseContrat travail':
        salaire = 'Pas renseigné'
    elif salaire =='Type de contratContrat à durée déterminée - 1 An(s)Contrat apprentissage':
        salaire = 'Pas renseigné'
    
############################# 
    liste.append(poste)
    liste.append(address)
    liste.append(dept)
    liste.append(ville)
    liste.append(date_publication)
    liste.append(offre_number)
    liste.append(description)
    liste.append(skills)
    liste.append(xp)
    liste.append(Qualification)
    liste.append(secteur_activity)           
    liste.append(entreprise)
    liste.append(horaire)
    liste.append(contrat)
    liste.append(salaire)
    liste.append(i)
    """    ajout de chaque liste dans une autre liste"""
    listeter.append(liste)
    print("Ligne numéro", i)
    param = {'offre_number' :offre_number, 'poste' :poste,'address' :address, 'dept' :dept, 'ville' :ville, 'date_publication' :date_publication, 'description' :description, 'skills' :skills,'xp' :xp,'Qualification' :Qualification,'secteur_activity' :secteur_activity,'entreprise' :entreprise, 'url' :url, 'horaire' :horaire, 'contrat' :contrat, 'salaire' :salaire}
#    print(param)
    engine.execute(statement, param)

today = datetime.now()
print("Today's date:", today)
##################################################ou alors ajouter le fichier en local
##############################################################
### Partie du dessous a enlever si c'est pas sur le serveur###
##############################################################
fichier = open("Job_Bot_V3.4..txt", "a")                ######
fichier.write('\n' + str(today))                        ######
fichier.close()                                         ######
##############################################################
### Partie du dessus a enlever si c'est pas sur le serveur####
##############################################################



# Affichage du temps d execution
print("Temps d execution : %s secondes ---" % (time.time() - start_time))


