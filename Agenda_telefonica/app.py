from flask import Flask, render_template, request, redirect, url_for, session
import json
import os
import uuid
from json import JSONDecodeError

app = Flask(__name__)
app.secret_key = "chave-secreta-do-app"

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


def get_user_path(username):
    if not username:
        return None

    filename = f"{username}_users.json"
    return os.path.join("data", "users", filename)


def carregar_usuario(username):
    caminho = get_user_path(username)
    if not caminho or not os.path.exists(caminho):
        return None

    return carregar_json(caminho)


def salvar_usuario(username, dados):
    caminho = get_user_path(username)
    if not caminho:
        return False

    salvar_json(caminho, dados)
    return True


def get_contatos(usuario):
    return usuario.get("contatos") or usuario.get("agenda") or []

Agenda = carregar_json(AGENDA)

ddds = carregar_json(DDD)

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

    usuario = carregar_usuario(username)
    if not usuario or usuario.get("password") != password:
        return redirect(url_for("loginerro"))

    session["username"] = username
    return redirect(url_for("principal"))

@app.route("/agenda", methods=["GET"])
def agenda_page():
    return redirect(url_for("principal"))

@app.route("/principal")
def principal():
    username = session.get("username")
    if not username:
        return redirect(url_for("home"))

    usuario = carregar_usuario(username)
    if not usuario:
        return redirect(url_for("home"))

    contatos = get_contatos(usuario)
    ddds = request.args.get("DDD")

    if ddds:
        contatos = [
            c for c in contatos
            if str(c.get("ddd")) == str(ddds)
        ]

    return render_template(
        "principal.html",
        agenda=contatos,
        username=username
    )

@app.route("/criar")
def criar():
    username = session.get("username")
    if not username:
        return redirect(url_for("home"))

    return render_template(
        "criar.html",
        ddds=ddds
    )

@app.route("/salvar", methods=["POST"])
def salvar():
    username = session.get("username")
    if not username:
        return redirect(url_for("home"))

    nome = (request.form.get("nome") or "").strip()
    descricao = (request.form.get("descricao") or "").strip()
    ddd_val = (request.form.get("ddd") or "").strip()
    numero = (request.form.get("numero") or "").strip()

    if not nome or not descricao or not ddd_val or not numero:
        erro = "Todos os campos são obrigatórios."
        return render_template("criar_erro.html", erro=erro, ddds=ddds)

    usuario = carregar_usuario(username)
    if not usuario:
        return redirect(url_for("home"))

    contatos = usuario.setdefault("contatos", [])
    estado = next(
        (item["estado"] for item in ddds if str(item.get("ddd")) == str(ddd_val)),
        ""
    )

    novo_contato = {
        "id": str(uuid.uuid4()),
        "nome": nome,
        "descricao": descricao,
        "ddd": ddd_val,
        "estado": estado,
        "numero": numero
    }

    contatos.append(novo_contato)
    salvar_usuario(username, usuario)

    return redirect(url_for("principal"))

@app.route("/deletar/<string:id>")
def deletar(id):
    username = session.get("username")
    if not username:
        return redirect(url_for("home"))

    usuario = carregar_usuario(username)
    if usuario:
        contatos = get_contatos(usuario)
        contato = next((c for c in contatos if c.get("id") == id), None)

        if contato:
            contatos.remove(contato)
            salvar_usuario(username, usuario)

    return redirect(url_for("principal"))

@app.route("/editar/<string:id>", methods=["GET", "POST"])
def editar(id):
    username = session.get("username")
    if not username:
        return redirect(url_for("home"))

    usuario = carregar_usuario(username)
    if not usuario:
        return redirect(url_for("home"))

    contatos = get_contatos(usuario)
    contato = next((c for c in contatos if c.get("id") == id), None)

    if not contato:
        return redirect(url_for("principal"))

    if request.method == "POST":
        contato["nome"] = (request.form.get("nome") or "").strip()
        contato["descricao"] = (request.form.get("descricao") or "").strip()
        contato["ddd"] = (request.form.get("ddd") or "").strip()
        contato["numero"] = (request.form.get("numero") or "").strip()

        contato["estado"] = next(
            (item["estado"] for item in ddds if str(item.get("ddd")) == str(contato["ddd"])),
            contato.get("estado", "")
        )

        salvar_usuario(username, usuario)
        return redirect(url_for("principal"))

    return render_template(
        "editar.html",
        contato=contato,
        ddds=ddds
    )

@app.route("/gerenciar")
def gerenciar():

    return render_template(
        "gerenciar.html",
        ddds=ddds
    )

@app.route("/criar_erro")
def criar_erro():
    return render_template("criar_erro.html")

if __name__ == "__main__":
    app.run(debug=True)
