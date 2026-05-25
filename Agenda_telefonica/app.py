from flask import Flask, render_template, request, redirect, url_for
import json
import os
import uuid
from json import JSONDecodeError

app = Flask(__name__)

DDD = "data/DDDs.json"
AGENDA = "data/Agenda.json"

def carregar_json(arquivo):

    if not os.path.exists(arquivo):
        return []

    try:
        with open(arquivo, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                return []
            return json.loads(content)
    except JSONDecodeError:
        return []

def salvar_json(arquivo, dados):

    with open(arquivo, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

Agenda = carregar_json(AGENDA)

ddd = carregar_json(DDD)

@app.route("/")
def home():
    return render_template("login.html")

@app.route("/criarerro")
def criarerro():
    return render_template("criar_erro.html")

@app.route("/loginerro")
def loginerro():
    return render_template("login_erro.html")

@app.route("/login")
def login():

    username = request.args.get("user")
    password = request.args.get("senha")

    with open("data/usuarios.json", "r", encoding="utf-8") as f:
        usuarios = json.load(f)

    for usuario in usuarios:
        print(usuario["username"], usuario["password"])
        print(username, password)
        if usuario["username"] == username and usuario["password"] == password:
            return render_template("principal.html", Agenda=Agenda, username=username)
    
    return redirect(url_for("loginerro"))

@app.route("/agenda", methods=["GET"])
def agenda_page():

    ddds = request.args.get("DDD")

    agenda_filtrada = Agenda      

    if ddds:
        agenda_filtrada = [
            t for t in agenda_filtrada
            if t["DDD"] == ddds
        ]

    return render_template(
        "principal.html",
        Agenda=Agenda
    )

@app.route("/criar")
def criar():
    return render_template(
        "criar.html",
        ddds=ddd
    )

@app.route("/salvar", methods=["POST"])
def salvar():
    # lê campos do form
    ddd_value = request.form.get('ddd')      # ex: "11SP"
    numero = request.form.get('numero')
    nome = request.form.get('nome')
    descricao = request.form.get('descricao', '')

    # valida campos obrigatórios
    if not ddd_value or not numero or not nome:
        return redirect(url_for('criar_erro'))

    # separa parte numérica do DDD e o estado
    ddd_digits = ''.join(ch for ch in ddd_value if ch.isdigit())
    ddd_estado = ''.join(ch for ch in ddd_value if not ch.isdigit()).strip()

    try:
        ddd_numero = int(ddd_digits)
    except (ValueError, TypeError):
        return redirect(url_for('criar_erro'))

    # função para normalizar números (remover símbolos/espaços)
    def normalize(n):
        return ''.join(ch for ch in (n or '') if ch.isdigit())

    # verifica duplicata (mesmo DDD e mesmo número normalizado)
    for contato in Agenda:
        if contato.get('ddd') == ddd_numero and normalize(contato.get('numero')) == normalize(numero):
            return redirect(url_for('criar_erro'))

    # cria novo contato e salva em memória e no arquivo
    novo = {
        'id': str(uuid.uuid4()),
        'ddd': ddd_numero,
        'numero': numero,
        'estado': ddd_estado,
        'nome': nome,
        'descricao': descricao
    }

    Agenda.append(novo)
    salvar_json(AGENDA, Agenda)

    # redireciona para a página de agenda (ou troque para onde preferir)
    return redirect(url_for('agenda_page'))

def buscar_numero(id):

    for numero in Agenda:
        if numero["id"] == id:
            return numero

    return None

@app.route("/deletar/<string:id>")
def deletar(id):

    numero = buscar_numero(id)

    if numero:
        Agenda.remove(numero)

        salvar_json(AGENDA, Agenda)

    return redirect(url_for("agenda_page"))

@app.route("/editar/<string:id>", methods=["GET", "POST"])
def editar(id):
    numero = buscar_numero(id)

    if not numero:
        return redirect(url_for("agenda_page"))

    if request.method == "POST":

        numero["numero"] = request.form.get("numero")
        numero["descricao"] = request.form.get("descricao")
        numero["DDD"] = request.form.get("DDD")

        salvar_json(AGENDA, Agenda)

        return redirect(url_for("agenda_page"))

    return render_template(
        "editar.html",
        numero=numero,
        ddds=ddd
    )

@app.route("/gerenciar")
def gerenciar():

    return render_template(
        "gerenciar.html",
        ddds=ddd
    )

@app.route("/criar_erro")
def criar_erro():
    return render_template("criar_erro.html")

if __name__ == "__main__":
    app.run(debug=True)
