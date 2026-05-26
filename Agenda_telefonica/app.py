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

@app.route("/cadastro")
def cadastro():
    return render_template("cadastro.html")

@app.route("/salvarcadastro", methods=["POST"])
def salvarcadastro():
    username = (request.form.get("username") or "").strip()
    telefone = (request.form.get("telefone") or "").strip()
    password = (request.form.get("password") or "").strip()
    password2x = (request.form.get("passwordx2") or "").strip()

    if not username or not password or not telefone:
        erro = "Todos os campos são obrigatórios."
        return render_template("cadastro_erro.html", erro=erro)

    if password != password2x:
        erro = "As senhas não coincidem. Por favor, tente novamente."
        return render_template("cadastro_erro.html", erro=erro)

    if not telefone.startswith("+55 ") or len(telefone) != 17:
        erro = "O número de telefone é inválido. Use o formato +55 84 9xxxx-xxxx."
        return render_template("cadastro_erro.html", erro=erro)
    
    caracteres = ["_", ".", ",", "!", "@", "#", "$", "%", "¨", "&", "*", "(", ")", "=", "/", "?", ";", ":", "<", ">", "|", "\"", "'", "´", "`", "~", "^"]

    if any(ch.isalpha() for ch in telefone):
        if any(ch in telefone for ch in caracteres):
            erro = "O número de telefone contém caracteres inválidos."
            return render_template("cadastro_erro.html", erro=erro)
        erro = "O número de telefone contém caracteres inválidos."
        return render_template("cadastro_erro.html", erro=erro)

    users_dir = os.path.join("data", "users")
    os.makedirs(users_dir, exist_ok=True)

    for arquivo in os.listdir(users_dir):
        if not arquivo.endswith(".json"):
            continue
        caminho_arquivo = os.path.join(users_dir, arquivo)
        try:
            with open(caminho_arquivo, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except (JSONDecodeError, OSError):
            continue

        if data.get("username") == username:
            erro = "O nome de usuário já existe. Por favor, escolha outro."
            return render_template("cadastro_erro.html", erro=erro)
        if data.get("password") == password:
            erro = "A senha já está em uso. Por favor, escolha outra."
            return render_template("cadastro_erro.html", erro=erro)

    novo_id = str(uuid.uuid4())
    novo_usuario = {
        "id": novo_id,
        "username": username,
        "password": password,
        "telefone": telefone,
        "contatos": []
    }

    caminho_novo = os.path.join(users_dir, f"{username}_users.json")
    try:
        with open(caminho_novo, 'w', encoding='utf-8') as f:
            json.dump(novo_usuario, f, ensure_ascii=False, indent=4)
    except OSError:
        erro = "Falha ao gravar o arquivo de usuário."
        return render_template("cadastro_erro.html", erro=erro)

    return redirect(url_for("home"))
#@app.route

@app.route("/criarerro")
def criarerro():
    return render_template("criar_erro.html")

@app.route("/loginerro")
def loginerro():
    return render_template("login_erro.html")

@app.route("/login")
def login():

    username = (request.args.get("user") or "").strip()
    password = (request.args.get("senha") or "").strip()

    if not username or not password:
        return redirect(url_for("loginerro"))

    users_dir = os.path.join("data", "users")

    if not os.path.exists(users_dir):
        return redirect(url_for("loginerro"))

    for arquivo in os.listdir(users_dir):

        if not arquivo.endswith(".json"):
            continue

        caminho_arquivo = os.path.join(users_dir, arquivo)

        try:
            with open(caminho_arquivo, "r", encoding="utf-8") as f:
                usuario = json.load(f)

        except (json.JSONDecodeError, OSError):
            continue

        usuario_username = usuario.get("username")
        usuario_password = usuario.get("password")

        if usuario_username == username and usuario_password == password:

            agenda = usuario.get("agenda", [])

            return render_template(
                "principal.html",
                Agenda=agenda,
                username=username
            )

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
    username = (request.form.get("username") or "").strip()
    telefone = (request.form.get("telefone") or "").strip()
    password = (request.form.get("password") or "").strip()
    password2x = (request.form.get("passwordx2") or "").strip()

    if not username or not password or not telefone:
        erro = "Todos os campos são obrigatórios."
        return render_template("cadastro_erro.html", erro=erro)

    if password != password2x:
        erro = "As senhas não coincidem. Por favor, tente novamente."
        return render_template("cadastro_erro.html", erro=erro)

    if not telefone.startswith("+55 ") or len(telefone) != 17:
        erro = "O número de telefone é inválido. Use o formato +55 84 9xxxx-xxxx."
        return render_template("cadastro_erro.html", erro=erro)
    
    caracteres = ["_", ".", ",", "!", "@", "#", "$", "%", "¨", "&", "*", "(", ")", "=", "/", "?", ";", ":", "<", ">", "|", "\"", "'", "´", "`", "~", "^"]

    if any(ch.isalpha() for ch in telefone):
        if any(ch in telefone for ch in caracteres):
            erro = "O número de telefone contém caracteres inválidos."
            return render_template("cadastro_erro.html", erro=erro)
        erro = "O número de telefone contém caracteres inválidos."
        return render_template("cadastro_erro.html", erro=erro)

    users_dir = os.path.join("data", "users")
    os.makedirs(users_dir, exist_ok=True)

    for arquivo in os.listdir(users_dir):
        if not arquivo.endswith(".json"):
            continue
        caminho_arquivo = os.path.join(users_dir, arquivo)
        try:
            with open(caminho_arquivo, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except (JSONDecodeError, OSError):
            continue

        if data.get("username") == username:
            erro = "O nome de usuário já existe. Por favor, escolha outro."
            return render_template("cadastro_erro.html", erro=erro)
        if data.get("password") == password:
            erro = "A senha já está em uso. Por favor, escolha outra."
            return render_template("cadastro_erro.html", erro=erro)

    novo_id = str(uuid.uuid4())
    novo_usuario = {
        "id": novo_id,
        "username": username,
        "password": password,
        "telefone": telefone,
        "agenda": []
    }

    caminho_novo = os.path.join(users_dir, f"{username}_users.json")
    try:
        with open(caminho_novo, 'w', encoding='utf-8') as f:
            json.dump(novo_usuario, f, ensure_ascii=False, indent=4)
    except OSError:
        erro = "Falha ao gravar o arquivo de usuário."
        return render_template("cadastro_erro.html", erro=erro)

    return redirect(url_for("home"))

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
