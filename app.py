from flask import Flask, render_template, request, redirect, url_for
import json
import os
import uuid

app = Flask(__name__)

DDD = "database/ddd.json"
AGENDA = "database/agenda.json"

def carregar_json(arquivo):

    if not os.path.exists(arquivo):
        return []

    with open(arquivo, "r", encoding="utf-8") as f:
        return json.load(f)

def salvar_json(arquivo, dados):

    with open(arquivo, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

Agenda = carregar_json(AGENDA)

ddd = carregar_json(DDD)

#tratamento tiago vai colocar aqui depois

@app.route("/")
def home():
    return render_template("home.html")

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
        "agenda.html",
        agenda=agenda_filtrada,
        ddds=ddd
    )

@app.route("/criar", methods=["POST"])
def criar():

    numero = request.form.get("numero")
    descricao = request.form.get("descricao")
    DDD = request.form.get("DDD")

    if numero:

        Agenda.append({
            "id": str(uuid.uuid4()),
            "numero": numero,
            "descricao": descricao,
            "DDD": DDD,
        })

        salvar_json(AGENDA, Agenda)

    return redirect(url_for("agenda_page"))
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

if __name__ == "__main__":
    app.run(debug=True)
