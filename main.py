from flask import render_template, Flask, send_file
import database as db

app = Flask(__name__)

@app.route('/test')
def test():
    print(db.get_unsorted_item_ids())
    return "ok"

@app.route('/')
def index():
    progress = db.get_progress()
    return render_template("index.html", progress=progress, itemIds=(',').join([str(i[0]) for i in db.get_unsorted_item_ids()]))

@app.route('/sort')
def sort():
    return render_template("sort.html")

@app.route('/add')
def add():
    return render_template("add.html")

@app.route('/image/<int:itemId>')
def image(itemId):
    # if image exists
    return send_file(f"static/images/{db.get_item_image(itemId)}")

# app.route('/font')
# def font():
#     return send_file("static/wonderbar.otf")

# @app.route('/jeu/<int:idJeu>')
# def jeu(idJeu):
#     print(idJeu)
#     jeu = db.get_jeu_by_id(idJeu)
#     return render_template("game.html", jeu=jeu)

# @app.route('/platforme/<int:idPlat>')
# def platforme(idPlat):
#     jeux = db.get_jeux_by_plat(idPlat)
#     return render_template("list_games.html", jeux=jeux)

# @app.route('/admin.<table>')
# def admin(table):
#     print("admin : ", table)
#     jeux = db.get_admin(table)
#     colonnes = db.get_columns(table)
#     return render_template("admin.html", jeux=jeux, colonnes=colonnes)

# @app.route('/admin.<table>/<parametre>.<valeur>')
# def admin_param(table,parametre,valeur):
#     print(f"admin : {table}, {parametre} : {valeur}")
#     jeux = db.get_admin_param(table,parametre,valeur)
#     colonnes = db.get_columns(table)
#     return render_template("admin.html", jeux=jeux, colonnes=colonnes)

# @app.route('/insert')
# def insert_page():
#     platformes = db.get_admin("platformes")
#     return render_template("insert.html", platformes=platformes)

# @app.route('/insertion', methods=["POST"])
# def insert_form():
#     if request.method == 'POST':
#         print(request.get_json())
#         jeu = request.get_json()
#         plat = ''
#         if jeu["win"]: plat += "WIN" # transformer la platforme en un string convenable à notre base de données
#         if jeu["mac"]: plat += "MAC" if plat == "" else ",MAC"
#         if jeu["lnx"]: plat += "LNX" if plat == "" else ",LNX"
#         plat = db.get_plat_id(plat)[0][0]
#         nomEditeur = jeu["nomEditeur"]
#         if nomEditeur == "":
#             nomEditeur = None
#         db.insert_jeu(jeu["nomJeu"],jeu["description"],jeu["prix"],jeu["uScore"],jeu["date"],jeu["image"],jeu["achievements"],jeu["nomDev"],nomEditeur,plat)
#         return str(db._select(f"select idJeu from jeu where nomJeu = '{jeu['nomJeu']}'")[0][0])

# @app.route('/chercher')
# def chercher():
#     keyword = request.args.get('keyword')
#     prix = request.args.get('prix')
#     jeux = db.get_jeu_by_filter(keyword,prix)
#     return render_template("list_games.html", jeux=jeux)

if __name__ == "__main__":
    app.run(host="localhost", port=8080, debug=True)