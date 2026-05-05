from flask import Flask, render_template, request, jsonify
import sqlite3
import os

app = Flask(__name__)

def criar_banco():
    conn = sqlite3.connect("leads.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            empresa TEXT,
            telefone TEXT,
            faturamento TEXT,
            problema TEXT,
            score TEXT,
            resumo TEXT
        )
    """)

    conn.commit()
    conn.close()


def classificar_lead(faturamento, problema):
    if faturamento in ["acima_200k", "acima_500k"]:
        return "quente"
    elif faturamento == "entre_50k_200k":
        return "morno"
    else:
        return "frio"


def salvar_lead(nome, empresa, telefone, faturamento, problema, score, resumo):
    conn = sqlite3.connect("leads.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO leads 
        (nome, empresa, telefone, faturamento, problema, score, resumo)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (nome, empresa, telefone, faturamento, problema, score, resumo))

    conn.commit()
    conn.close()



@app.route("/")
def index():
    return render_template("index.html")


@app.route("/lead", methods=["POST"])
def lead():
    dados = request.json

    nome = dados.get("nome")
    empresa = dados.get("empresa")
    telefone = dados.get("telefone")
    faturamento = dados.get("faturamento")
    problema = dados.get("problema")

    score = classificar_lead(faturamento, problema)

    resumo = f"""
    Lead: {nome}
    Empresa: {empresa}
    Telefone: {telefone}
    Faturamento: {faturamento}
    Principal problema: {problema}
    Classificação: {score}
    """

    salvar_lead(nome, empresa, telefone, faturamento, problema, score, resumo)

    return jsonify({
        "mensagem": "Lead cadastrado com sucesso!",
        "score": score
    })


if __name__ == "__main__":
    criar_banco()
    app.run(debug=True)