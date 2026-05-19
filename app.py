from flask import Flask, render_template, request, redirect, url_for
import uuid
import json
import os

app = Flask(__name__)

NUMERO_FILE = "database/ddd.json"
DDDS_FILE = "database/agenda.json"

def carregar_json(arquivo):

    if not os.path.exists(arquivo):
        return []

    with open(arquivo, "r", encoding="utf-8") as f:
        return json.load(f)

def salvar_json(arquivo, dados):

    with open(arquivo, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)

numero = carregar_json( NUMERO_FILE)

ddds = carregar_json(DDDS_FILE)


def numero_id():
    return ddds and numero[-1]["id"] + 1 or 1

def buscar_numero(id):
    return next((t for t in numero if t["id"] == id), None)

@app.route("/")
def home():
    return render_template("interface.html")

@app.route("/numeros", methods=["GET"])
def tarefas_page():

    numero = request.args.get("numero")
    ddd = request.args.get("ddd")

#filtragem tiago vai colocar aqui


@app.route("/criar", methods=["POST"])
def criar():

    numero = request.form.get("numero")
    descricao = request.form.get("descricao")



if __name__ == "__main__":
    app.run(debug=True)
