import sqlite3
from requests import get
import re

DBNAME = "spacifyDB.db"

#=================================================
def _select(requete, params=None):               #
    """ Exécute une requête type select"""       #
    with sqlite3.connect(DBNAME) as db:          #
        c = db.cursor()                          #
        if params is None:                       #
            c.execute(requete)                   #
        else:                                    #
            c.execute(requete, params)           #
        res = c.fetchall()                       #
    return res                                   #
#=================================================

def create_item(name,typeName,imagePath):
    if not does_type_exist(typeName):
        create_type(typeName)
    _select(f"""insert into IMAGE (filename) values ({imagePath})""")
    requete = f"""insert into ITEM (name,description,prix,uScore,date,image,achievements,idDev,idEditeur,idPlat) values ()""" 
    return _select(requete)

def count_sorted():
    return _select(f"select count(id) from ITEM where categoryId IS NOT NULL")[0][0]

def count_table_entries(tableName: str):
    return _select(f"select count(id) from {tableName}")[0][0]

def get_progress():
    return f"{count_sorted()}/{count_table_entries("ITEM")}"

def get_unsorted_item_ids():
    return _select(f"select id from ITEM where categoryId IS NULL")

def get_type_by_id(id):
    return _select(f"""select name from TYPE where id = {id}""")

def get_type_id(typeName):
    return _select(f"""select name from TYPE where name = "{typeName}" """)

def get_image_id(imagePath):
    return _select(f"""select filename from IMAGE where filename = "{imagePath}" """)

def get_item_image(itemId) -> str:
    print(_select(f"""select filename from IMAGE 
                       inner join ITEM on ITEM.imageId = IMAGE.id 
                       where ITEM.id = {itemId}"""))
    return _select(f"""select filename from IMAGE 
                       inner join ITEM on ITEM.imageId = IMAGE.id 
                       where ITEM.id = {itemId}""")[0][0]

def get_type_names():
    return _select(f"""select name from TYPE""")

def does_type_exist(typeName):
    return len(get_type_id(typeName)) != 0

def does_image_exist(imagePath):
    return len(get_image_id(imagePath)) != 0

def create_type(typeName):
    if not does_type_exist(typeName):
        _select(f"""insert into TYPE (name) values ("{typeName}")""")

def create_image(imagePath):
    if not does_image_exist(imagePath):
        _select(f"""insert into IMAGE (filename) values ({imagePath})""")

def get_jeux_by_annee(annee):
    """Renvoie une liste des jeux sortis pendant l'année précisée"""
    requete = """select * from jeu
                        where year(jeu.date)=?
                        order by jeu.date asc""" # on trie par la date de sortie du jeu
    return _select(requete, params=(annee,))

def get_jeux_by_plat(plat):
    """Renvoie une liste des jeux jouables sur la platforme précisée"""
    requete = """select nomJeu,idJeu,prix,uScore,date,achievements,developpeur.nomDev,editeur.nomEditeur,jeu.idPlat,platformes.nomPlat from jeu
                        inner join developpeur on developpeur.idDev = jeu.idDev
                        inner join editeur on editeur.idEditeur = jeu.idEditeur
                        inner join platformes on platformes.idPlat = jeu.idPlat
                        where platformes.idPlat = ?
                        order by jeu.uScore desc"""
    return _select(requete, params=(plat,))

def get_all_jeux():
    """Renvoie (avec une limite de 100) les jeux sans les trier et les filtrer"""
    requete = """select nomJeu,idJeu,prix,image,uScore,date,achievements,developpeur.nomDev,editeur.nomEditeur,jeu.idPlat,platformes.nomPlat,description from jeu
                 inner join developpeur on developpeur.idDev = jeu.idDev
                 inner join editeur on editeur.idEditeur = jeu.idEditeur
                 inner join platformes on platformes.idPlat = jeu.idPlat
                 limit 100""" # on y ajoute aussi le nom du développeur et celui de l'éditeur, avec les platformes sur lesquelles le jeu est disponible
    return _select(requete)

def get_jeu_by_id(idJeu):
    """Renvoie le jeu dont le id a été précisé"""
    requete = """select nomJeu,idJeu,prix,image,uScore,date,achievements,developpeur.nomDev,editeur.nomEditeur,platformes.nomPlat from jeu
                 inner join developpeur on developpeur.idDev = jeu.idDev
                 inner join editeur on editeur.idEditeur = jeu.idEditeur
                 inner join platformes on platformes.idPlat = jeu.idPlat
                 where idJeu = ?
                 limit 1"""
    return _select(requete, params=(idJeu,))

def get_jeu_by_filter(keyword,prix):
    requete = f"""select nomJeu,idJeu,prix,image,uScore,date,achievements,developpeur.nomDev,editeur.nomEditeur,jeu.idPlat,platformes.nomPlat,description from jeu
                 inner join developpeur on developpeur.idDev = jeu.idDev
                 inner join editeur on editeur.idEditeur = jeu.idEditeur
                 inner join platformes on platformes.idPlat = jeu.idPlat 
                 """  
    print("keyword : "+keyword)
    print("prix : "+prix)
    if len(keyword) != 0: requete += f"where (UPPER(nomJeu) LIKE UPPER('%{keyword}%') OR UPPER(description) LIKE UPPER('%{keyword}%')) "
    if len(prix) != 0: 
        if len(keyword) == 0:
            requete += f"where prix <= {prix}"
        else:
            requete += f"and prix <= {prix}"
    return _select(requete)
    

def get_admin(table):
    """Renvoie 200 entrés max de la table précisée
    Les tables possibles sont : (jeu,developpeur,editeur,plarformes)"""
    requete = f"""select * from {table}
                limit 200"""
    return _select(requete)

def get_admin_param(table,parametre,valeur):
    """Admin complexes, même tables que admin
    Les paramètres sont :
        - prix : renvoie les jeux dont le prix et égal ou inférieur à celui précisé
        - keyword : renvoie les jeux où le mot précisé est dans le titre ou la description, sinon dans le nom de l'éditeur, du développeur ou de la platforme
        - dev : relie la table developpeur à la table jeu, l'argument sert à renvoyer les jeux d'un certain développeur
        - editeur : pareil mais avec l'éditeur
    """
    plus = "" # variable pour rajouter certains paramètres spécifiques à certains filtres
    if parametre == "prix": param = f"where prix <= {int(valeur)}"
    elif parametre == "keyword": 
        param = f"where nom like '%{valeur.upper()}%'" # on met tout en majuscules pour que le filtre marche mieux
        nom = 'nomJeu' if table == 'jeu' else 'nomDev' if table == 'developpeur' else 'nomEditeur' if table == 'editeur' else "nomPlat" # définir la colonne où chercher dépendant de la table
        plus = f",upper({nom}) as nom" # la colonne en majuscules
        plus += ',upper(description) as desc' if table == 'jeu' else "" # quand on cherche dansl es jeux alors on cherche aussi dans la description
        param +=  "or desc like '%{valeur.upper()}%'" if table == 'jeu' else ''
    elif parametre == "dev":
        param = "inner join developpeur on jeu.idDev == developpeur.idDev"
        if valeur != "r" : param += f" where developpeur.nomDev == '{valeur}'" # on met r pour voir tous les jeux à la place de filtrer
    elif parametre == "editeur":
        param = "inner join editeur on jeu.idEditeur == editeur.idEditeur"
        if valeur != "r" : param += f" where editeur.nomEditeur == '{valeur}'"
    requete = f"""select *{plus} from {table}
                {param}
                limit 200"""
    return _select(requete)

def get_columns(table):
    requete = f"""PRAGMA table_info({table})""" # retourne les noms des colonnes d'une table
    return _select(requete)

def insert_jeu(nomJeu,description,prix,uScore,date,image,achievements,nomDev,nomEditeur,idPlat): # (nomJeu, description, prix, uScore, date, image, achievements, idDev, idEditeur, idPlatforme)
    print(nomJeu)
    if not dev_existe(nomDev):
        insert_dev(nomDev)
    idDev = _select(f"select idDev from developpeur where nomDev == '{nomDev}'")[0]
    if nomEditeur != None:
        if not editeur_existe(nomEditeur):
            insert_editeur(nomEditeur)
        idEditeur = _select(f"select idEditeur from editeur where nomEditeur == '{nomEditeur}'")[0]
    requete = f"""insert into jeu (nomJeu,description,prix,uScore,date,image,achievements,idDev,idEditeur,idPlat) values ('{nomJeu.replace("'","’")}','{description.replace("'","’")}',{prix},{uScore},'{date}','{image}',{achievements},{idDev[0]},{idEditeur[0]},{idPlat})"""
    return _select(requete)

def insert_dev(nomDev):
    """Insérer un développeur dans la table (pas besoin de présiser le id puisqu'il y a un autoincrement)"""
    requete = f"""insert into developpeur (nomDev) values ('{nomDev}')"""
    return _select(requete)

def insert_editeur(nomEditeur):
    requete = f"""insert into editeur (nomEditeur) values ('{nomEditeur}')"""
    return _select(requete)

def dev_existe(nomDev):
    """Retourne True si le développeur est dans la base de données sinon False"""
    return _select(f"select idDev from developpeur where nomDev == '{nomDev}'") != []

def editeur_existe(nomEditeur):
    return _select(f"select idEditeur from editeur where nomEditeur == '{nomEditeur}'") != []

# def format(description):
#     while '<img src' in description:
#         description = description.replace('<img src', '<img class="htmlImg" src')
#     return description

def format_all(jeux):
    for i in range(len(jeux)):
        jeux[i] = list(jeux[i])
        print(jeux[i])
        jeux[i][2] = format(jeux[i][2])
        jeux[i].append(reduire_desc(jeux[i][2]))
    return jeux

def reduire_desc(description):
    # l = re.sub(r'<a(.*</a>)','',re.sub(r'<img(.*/>)','', description))
    # return re.sub(r'<br>','', l) # on soustrait les liens et les images
    return re.sub(r'<a(.*</a>)','',re.sub(r'<img(.*/>)','', description))