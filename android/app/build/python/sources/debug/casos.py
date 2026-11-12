# -*- coding: utf-8 -*-
"""
Umbra Nox - Camada de acesso aos dados (multi-caso).

Os dados de todos os casos ficam em dados_casos.CASOS. Este módulo expõe
helpers usados pelo servidor: enigmas, listagem/seleção de casos, evidências
públicas e normalização.
"""

import unicodedata

import dados_casos as dc

ENIGMAS = dc.ENIGMAS
VITIMAS_SERIE = dc.VITIMAS_SERIE
PALAVRA_SERIE = dc.PALAVRA_SERIE
CASOS = dc.CASOS
para_morse = dc.para_morse

# Ordem oficial dos casos.
ORDEM_CASOS = ["001", "002", "003", "004", "005",
               "006", "007", "008", "009", "010"]
# Mantém só os que já existem (permite construir incrementalmente).
ORDEM_CASOS = [cid for cid in ORDEM_CASOS if cid in CASOS]


def _norm(texto):
    texto = (texto or "").strip().lower()
    texto = "".join(
        c for c in unicodedata.normalize("NFD", texto)
        if unicodedata.category(c) != "Mn"
    )
    texto = "".join(c if c.isalnum() or c.isspace() else " " for c in texto)
    return " ".join(texto.split())


def verificar_enigma(enigma_id, resposta):
    alvo = _norm(resposta)
    for e in ENIGMAS:
        if e["id"] == enigma_id:
            return any(alvo == _norm(r) for r in e["respostas"])
    return False


def obter_caso(caso_id):
    return CASOS.get(caso_id)


def primeiro_caso():
    return ORDEM_CASOS[0] if ORDEM_CASOS else None


def proximo_caso(caso_id):
    if caso_id in ORDEM_CASOS:
        i = ORDEM_CASOS.index(caso_id)
        if i + 1 < len(ORDEM_CASOS):
            return ORDEM_CASOS[i + 1]
    return None


def evidencias_publicas(caso_id):
    caso = CASOS.get(caso_id)
    if not caso:
        return []
    return [
        {"id": e["id"], "nome": e["nome"], "descricao": e["descricao"],
         "chave_prova": e.get("chave_prova", False),
         "confiavel": e.get("confiavel", True)}
        for e in caso["evidencias"]
    ]


def suspeitos_do_caso(caso_id):
    caso = CASOS.get(caso_id)
    if not caso:
        return []
    return [p for p in caso["personagens"] if p.get("tipo") == "suspeito"]


def peritos_do_caso(caso_id):
    caso = CASOS.get(caso_id)
    if not caso:
        return []
    return [p for p in caso["personagens"] if p.get("tipo") in ("pericia", "legista")]


def personagem(caso_id, pid):
    caso = CASOS.get(caso_id)
    if not caso:
        return None
    for p in caso["personagens"]:
        if p["id"] == pid:
            return p
    return None


def lista_casos():
    """Resumo de todos os casos (para o Arquivo de Casos no frontend)."""
    out = []
    for cid in ORDEM_CASOS:
        c = CASOS[cid]
        v = c["vitima"]
        serie = VITIMAS_SERIE[v["indice_serie"]]
        out.append({
            "id": c["id"], "titulo": c["titulo"], "etapa": c.get("etapa", 1),
            "objetivo": c["objetivo"], "vitima": v["nome"],
            "letra": serie["letra"], "pecado": serie["pecado"],
        })
    return out
