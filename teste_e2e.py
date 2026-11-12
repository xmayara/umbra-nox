# -*- coding: utf-8 -*-
"""Teste end-to-end do Caso 001 (temporário)."""
import json, urllib.request as u
BASE = "http://127.0.0.1:5000"

def get(c):
    with u.urlopen(BASE + c) as r:
        return json.loads(r.read().decode("utf-8"))

def post(c, d):
    req = u.Request(BASE + c, data=json.dumps(d).encode("utf-8"),
                    headers={"Content-Type": "application/json"}, method="POST")
    with u.urlopen(req) as r:
        return json.loads(r.read().decode("utf-8"))

ok = []

# 1) Enigmas
en = get("/api/enigmas")
ok.append(("enigmas qtd", len(en) == 6))
v = post("/api/enigmas/verificar", {"id": 3, "resposta": "sombra"})
ok.append(("enigma 3 correto", v.get("correto") is True and v.get("resposta") == "Sombra"))
v2 = post("/api/enigmas/verificar", {"id": 3, "resposta": "errado"})
ok.append(("enigma 3 errado", v2.get("correto") is False))

# 2) Caso
caso = get("/api/caso")
c = caso["caso"]
ok.append(("hora 07h00", c["vitima"]["hora"] == "07h00"))
ok.append(("morse P", caso["caso"]["vitima_morse"] == ".--."))
ok.append(("suspeitos 4", len(caso["suspeitos"]) == 4))
ok.append(("peritos 2", len(caso["peritos"]) == 2))
ids = [s["id"] for s in caso["suspeitos"]]
ok.append(("tem tomas/helena/renato/mara", set(ids) == {"mara","helena","tomas","renato"}))

# 3) Legista explica o relógio
e = post("/api/pericia/iniciar", {"contato_id": "legista"})
r = post("/api/pericia/perguntar", {"estado": e, "pergunta": "o relogio parado prova a hora da morte?"})
ok.append(("legista relogio nao prova", "nao comprova" in r["fala"].lower() or "não comprova" in r["fala"].lower()))
r = post("/api/pericia/perguntar", {"estado": e, "pergunta": "qual a causa da morte?"})
ok.append(("legista revela causa", r["revela"] == "causa_morte"))

# 4) Tomás revela as 2 provas
e = post("/api/interrogatorio/iniciar", {"suspeito_id": "tomas", "evidencias": []})
r1 = post("/api/interrogatorio/perguntar", {"estado": e, "pergunta": "voce guardou uma copia do negativo?"})
ok.append(("tomas revela imagem", r1["revela"] == "imagem_tomas"))
e = r1["estado"]
r2 = post("/api/interrogatorio/perguntar", {"estado": e, "pergunta": "da pra comparar com o inventario do arquivo?"})
ok.append(("tomas revela registro", r2["revela"] == "registro_alteracao"))

# 5) Confronto com Renato SEM provas -> defende
e = post("/api/interrogatorio/iniciar", {"suspeito_id": "renato", "evidencias": []})
r = post("/api/interrogatorio/perguntar", {"estado": e, "pergunta": "sei que voce matou elias, tenho provas"})
ok.append(("renato sem provas nao confessa", r["confessou"] is False))

# 6) Confronto com Renato COM provas -> confessa + libera comunicacao
e = post("/api/interrogatorio/iniciar", {"suspeito_id": "renato",
        "evidencias": ["imagem_tomas", "registro_alteracao"]})
r = post("/api/interrogatorio/perguntar", {"estado": e, "pergunta": "sei que voce matou elias, tenho provas"})
ok.append(("renato confessa", r["confessou"] is True and r["confissao_disparada"] is True))
ok.append(("libera comunicacao", r.get("libera_comunicacao") is True and r.get("revela") == "comunicacao"))

# 7) Acusar culpado SEM todas as provas -> sem_provas
r = post("/api/acusar", {"suspeito": "renato", "evidencias": ["imagem_tomas"]})
ok.append(("acusar sem provas", r["resultado"] == "sem_provas"))

# 8) Acusar inocente -> errado
r = post("/api/acusar", {"suspeito": "mara",
        "evidencias": ["imagem_tomas","registro_alteracao","comunicacao"]})
ok.append(("acusar inocente errado", r["resultado"] == "errado"))

# 9) Acusar culpado COM todas as provas -> resolvido
r = post("/api/acusar", {"suspeito": "renato",
        "evidencias": ["imagem_tomas","registro_alteracao","comunicacao"]})
ok.append(("acusar culpado resolvido", r["resultado"] == "resolvido"))
ok.append(("desfecho menciona gancho morse", "morse" in r["mensagem"].lower() or "caderno" in r["mensagem"].lower()))

# 10) Salvar / carregar
post("/api/salvar", {"enigmaAtual": 6, "evidenciasDescobertas": ["relogio"], "encerrado": False})
car = get("/api/carregar")
ok.append(("salvar/carregar", car["existe"] is True and car["estado"]["evidenciasDescobertas"] == ["relogio"]))

print("\n=== RESULTADO DOS TESTES ===")
falhas = 0
for nome, passou in ok:
    print(("  OK  " if passou else " FALHA") + "  " + nome)
    if not passou:
        falhas += 1
print("\n%d/%d passaram." % (len(ok) - falhas, len(ok)))
