from flask import Flask, render_template, request, jsonify
import sqlite3
import os

app = Flask(__name__)

cclient = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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


def gerar_resposta_ia(mensagem):
    prompt_sistema = """
    Você é o assistente comercial da Finnext.

    A Finnext presta serviços de:
    - Auditoria Financeira
    - Auditoria de Processos
    - BPO Financeiro

    Seu objetivo:
    - Conversar com donos, gestores e financeiros de pequenas e médias empresas.
    - Identificar dores financeiras.
    - Explicar de forma simples como a Finnext pode ajudar.
    - Nunca prometer resultado garantido.
    - Sempre tentar levar o lead para uma reunião de diagnóstico.

    Tom:
    - Profissional
    - Direto
    - Consultivo
    - Sem linguagem robótica
    - Sem parecer vendedor insistente

    Quando fizer sentido, diga:
    "Pelo que você comentou, faz sentido agendarmos um diagnóstico rápido para entender melhor o cenário."
    """

    resposta = client.responses.create(
        model="gpt-5.5",
        input=[
            {"role": "system", "content": prompt_sistema},
            {"role": "user", "content": mensagem}
        ]
    )

    return resposta.output_text


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