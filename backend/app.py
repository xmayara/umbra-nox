# -*- coding: utf-8 -*-
"""
Umbra Nox - Servidor Flask (multi-caso, série PECCATORES).

API:
  GET  /                              -> página do jogo
  GET  /api/enigmas                   -> enigmas (sem respostas)
  POST /api/enigmas/verificar         -> valida resposta de um enigma
  GET  /api/casos                     -> lista resumida dos casos + lore
  GET  /api/caso/<caso_id>            -> dados completos de um caso
  POST /api/dialogo/iniciar           -> inicia interrogatório/conversa
  POST /api/dialogo/perguntar         -> pergunta livre (tempo real)
  POST /api/acusar                    -> fecha um caso acusando alguém
  POST /api/salvar / GET /api/carregar-> progresso
"""

import json
import os

from flask import Flask, jsonify, request, send_from_directory

import casos
import dialogo

FRONTEND_DIR = os.path.abspath(
    os.environ.get(
        "UMBRA_NOX_FRONTEND_DIR",
        os.path.join(os.path.dirname(__file__), "..", "frontend"),
    )
)
SAVE_PATH = os.path.join(
    os.environ.get("UMBRA_NOX_DATA_DIR", os.path.dirname(__file__)),
    "savegame.json",
)

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path="")


# --------------------------- Frontend ------------------------------------
@app.route("/")
def index():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.route("/<path:caminho>")
def estaticos(caminho):
    return send_from_directory(FRONTEND_DIR, caminho)


# --------------------------- Enigmas -------------------------------------
@app.route("/api/enigmas")
def listar_enigmas():
    return jsonify([
        {"id": e["id"], "texto": e["texto"], "dica": e["dica"]}
        for e in casos.ENIGMAS
    ])


@app.route("/api/enigmas/verificar", methods=["POST"])
def verificar_enigma():
    dados = request.get_json(force=True) or {}
    enigma_id = dados.get("id")
    correto = casos.verificar_enigma(enigma_id, dados.get("resposta", ""))
    saida = {"correto": correto}
    if correto:
        for e in casos.ENIGMAS:
            if e["id"] == enigma_id:
                saida["resposta"] = e["resposta_exibicao"]
                break
    return jsonify(saida)


# --------------------------- Casos ---------------------------------------
@app.route("/api/casos")
def listar_casos():
    return jsonify({
        "palavra": casos.PALAVRA_SERIE,
        "vitimas": casos.VITIMAS_SERIE,
        "casos": casos.lista_casos(),
        "primeiro": casos.primeiro_caso(),
    })


@app.route("/api/caso/<caso_id>")
def obter_caso(caso_id):
    c = casos.obter_caso(caso_id)
    if not c:
        return jsonify({"erro": "Caso não encontrado."}), 404
    v = c["vitima"]
    serie = casos.VITIMAS_SERIE[v["indice_serie"]]
    caso_publico = {
        "id": c["id"], "titulo": c["titulo"], "etapa": c.get("etapa", 1),
        "objetivo": c["objetivo"], "mecanica": c.get("mecanica", ""),
        "introducao": c["introducao"], "vitima": v,
        "evidencias": casos.evidencias_publicas(caso_id),
        "provas_chave": c["provas_chave"],
        "linha_tempo": c["linha_tempo"], "hipoteses": c["hipoteses"],
        "acusaveis": c["acusaveis"],
        "letra": serie["letra"], "pecado": serie["pecado"],
        "vitima_morse": casos.para_morse(serie["letra"]),
        "proximo": casos.proximo_caso(caso_id),
        "tutorial": c.get("tutorial", []),
    }
    suspeitos = [
        {"id": s["id"], "nome": s["nome"], "papel": s["papel"], "retrato": s["retrato"]}
        for s in casos.suspeitos_do_caso(caso_id)
    ]
    peritos = [
        {"id": p["id"], "nome": p["nome"], "papel": p["papel"],
         "retrato": p["retrato"], "tipo": p["tipo"]}
        for p in casos.peritos_do_caso(caso_id)
    ]
    return jsonify({"caso": caso_publico, "suspeitos": suspeitos, "peritos": peritos})


# --------------------------- Diálogo -------------------------------------
@app.route("/api/dialogo/iniciar", methods=["POST"])
def iniciar_dialogo():
    dados = request.get_json(force=True) or {}
    caso_id = dados.get("caso_id", "")
    pid = dados.get("pid", "")
    evidencias = dados.get("evidencias", [])
    estado_salvo = dados.get("estado")
    return jsonify(dialogo.iniciar(caso_id, pid, evidencias, estado_salvo))


@app.route("/api/dialogo/perguntar", methods=["POST"])
def perguntar_dialogo():
    dados = request.get_json(force=True) or {}
    estado = dados.get("estado") or {}
    pergunta = dados.get("pergunta")
    topico = dados.get("topico")
    return jsonify(dialogo.perguntar(estado, pergunta, topico))


# --------------------------- Acusar --------------------------------------
@app.route("/api/acusar", methods=["POST"])
def acusar():
    dados = request.get_json(force=True) or {}
    caso_id = dados.get("caso_id", "")
    suspeito = dados.get("suspeito", "")
    evidencias = set(dados.get("evidencias", []))

    c = casos.obter_caso(caso_id)
    if not c:
        return jsonify({"erro": "Caso não encontrado."}), 404

    provas = c["provas_chave"]
    tem_todas = all(p in evidencias for p in provas)
    acertou = (suspeito == c["culpado"])
    sol = c["solucao"]

    if acertou and tem_todas:
        resultado = "resolvido"
        mensagem = sol["resumo"] + "\n\n" + sol["veredito"] + "\n\n" + sol["gancho"]
    elif acertou and not tem_todas:
        resultado = "sem_provas"
        reunidas = len([p for p in provas if p in evidencias])
        mensagem = ("Sua intuição pode estar certa, mas acusações não se sustentam "
                    "em intuição. Faltam provas decisivas (%d de %d reunidas). Volte "
                    "às evidências e ao confronto." % (reunidas, len(provas)))
    else:
        resultado = "errado"
        mensagem = ("As provas não sustentam essa acusação. Reveja a linha do tempo "
                    "e cruze os depoimentos: quem tinha motivo, acesso e método?")

    return jsonify({
        "resultado": resultado, "acertou": acertou,
        "tem_todas_provas": tem_todas, "mensagem": mensagem,
        "culpado": c["culpado"] if resultado == "resolvido" else None,
        "culpado_nome": sol["culpado_nome"] if resultado == "resolvido" else None,
        "proximo": casos.proximo_caso(caso_id) if resultado == "resolvido" else None,
    })


# --------------------------- Salvar / Carregar ---------------------------
@app.route("/api/salvar", methods=["POST"])
def salvar():
    dados = request.get_json(force=True) or {}
    try:
        with open(SAVE_PATH, "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)
        return jsonify({"ok": True})
    except OSError as e:
        return jsonify({"ok": False, "erro": str(e)}), 500


@app.route("/api/carregar")
def carregar():
    if not os.path.exists(SAVE_PATH):
        return jsonify({"existe": False})
    try:
        with open(SAVE_PATH, "r", encoding="utf-8") as f:
            return jsonify({"existe": True, "estado": json.load(f)})
    except (OSError, ValueError):
        return jsonify({"existe": False})


if __name__ == "__main__":
    host = os.environ.get("UMBRA_NOX_HOST", "127.0.0.1")
    print("=" * 52)
    print("  UMBRA NOX  -  servidor iniciado")
    print("  Endereco do servidor:  http://%s:5000" % host)
    print("=" * 52)
    app.run(host=host, port=5000, debug=host in ("127.0.0.1", "localhost"))
