# -*- coding: utf-8 -*-
"""
Umbra Nox - Motor de diálogo em tempo real (multi-caso).

Serve tanto interrogatórios de suspeitos quanto conversas técnicas
(perita/legista). O jogador escolhe uma PERGUNTA PRONTA (por tópico); o motor
responde conforme o estado (nervosismo, tópicos já abordados, contradições) e
revela evidências.

Também aceita texto livre como fallback (detecção por palavras-chave).

Mecânica de confronto: o suspeito culpado só confessa quando o jogador
(1) coletou as provas de provas_para_confronto e (2) escolhe a pergunta de
confronto. O confronto libera a prova bloqueada (3ª prova).
"""

import unicodedata

import casos

CONFRONTO_GATILHOS = [
    "confronto", "confrontar", "mentiu", "mentindo", "mente", "sei que",
    "provas", "prova", "flagrante", "acuso", "acusar", "voce matou",
    "você matou", "foi voce", "foi você", "voce sabia", "você sabia",
    "negativo original",
]

# Rótulos amigáveis de pergunta por nome de tópico. Se um tópico não estiver
# aqui, um rótulo genérico é gerado a partir do nome.
ROTULOS = {
    "alibi": "Onde você estava na noite do crime?",
    "relacao": "Qual era a sua relação com a vítima?",
    "visita": "Viu alguém chegar naquela noite?",
    "motivo": "Você tinha algum motivo contra a vítima?",
    "escritorio": "Costumava frequentar o local?",
    "chave": "O que pode me dizer sobre a chave / esta fotografia?",
    "trabalho": "No que a vítima estava trabalhando?",
    "copia": "Você guardou alguma cópia?",
    "comparar": "O que acontece se eu comparar com os registros?",
    "fonte": "Quem era a fonte dela?",
    "reputacao": "E a reputação envolvida nisso?",
    "retratacao": "Havia algum documento a ser revelado?",
    "laudo": "O que o laudo mostra?",
    "abuso": "Havia abuso de poder envolvido?",
    "dossie": "Existe algum dossiê guardado?",
    "familia": "Isso afetou a sua família?",
    "documentos": "E os documentos remexidos?",
    "livros": "O que os livros contábeis mostram?",
    "auditoria": "E a auditoria / o contrato?",
    "ameaca": "Houve alguma ameaça?",
    "heranca": "E a disputa de herança?",
    "fundacao": "O que sabe sobre a fundação?",
    "telefone": "E o telefone desaparecido?",
    "traicao": "Houve quebra de confiança?",
    "desvio": "Havia desvio de dinheiro?",
    "cameras": "O que houve com as câmeras?",
    "omissao": "O que foi omitido na investigação antiga?",
    "gravacao": "A vítima deixou alguma gravação?",
    "acesso": "Quem tinha acesso ao local?",
    "material": "E o material que sumiu dos registros?",
    "material_medico": "O que havia de material médico?",
    "codificacao": "O que significa essa codificação?",
    "codigo": "O que significa esse código?",
    "difamacao": "A vítima difamou alguém?",
    "rancor": "Havia rancor entre vocês?",
    "programa": "O que era o programa institucional?",
    "backup": "A vítima deixou um backup?",
    "horario": "A que horas isso aconteceu?",
    "ciume": "Vocês tinham alguma rixa ou desavença?",
    "telefonema": "Você falou com a vítima naquele dia?",
    "visita_estudio": "Você esteve no estúdio naquela noite?",
    "envelope": "O que aconteceu com o envelope?",
    "indice": "Por que o índice foi trocado?",
    "serie": "Como este caso se liga aos outros?",
    "morse": "O que as marcas em Morse significam?",
    "laudos": "Por que seus laudos não têm segunda assinatura?",
    # perícia / legista
    "cena": "Como estava a cena do crime?",
    "luta": "Houve sinais de luta?",
    "caderno": "Encontraram alguma anotação?",
    "corpo": "O que o corpo revela?",
    "causa": "Qual foi a causa da morte?",
    "relogio": "O relógio indica a hora da morte?",
    "quem": "Quem o senhor acha que fez isso?",
    "hora": "A que horas ocorreu a morte?",
    "arma": "Que arma ou método foi usado?",
    "tatuagem": "Havia alguma marca ou tatuagem no corpo?",
    "parecer": "Qual é o seu parecer?",
    "laudo_processo": "Há algo estranho no laudo do processo?",
    "pagamentos": "E esses pagamentos suspeitos?",
    "programa_medico": "O que era o programa de assistência médica?",
    "relatorio": "O que diz o relatório financeiro?",
    "recuperacao": "Dá para recuperar a gravação?",
    "cofre": "Por que o cofre estava aberto?",
    "livro": "O que sumiu da cena?",
    "mensagem": "E a mensagem que cancelou a entrevista?",
    "versoes": "Os depoimentos batem entre si?",
    "cartao": "Por que o cartão estava em outro andar?",
    "consulta": "E essa consulta médica fora do protocolo?",
    "log": "O que diz o log de acesso?",
    "lista": "O que há na lista de participantes?",
    "custodia": "Quem controla a cadeia de custódia?",
    "ferimento": "Como foi o ferimento?",
    "kael": "O que acha do trabalho do legista?",
    "deposito": "O que achou no depósito?",
    "ficha": "E a ficha de custódia?",
    "prontuario": "O que houve com o prontuário?",
    "farmaco": "Que fármaco foi usado?",
}

ROTULO_CONFRONTO = "⚠ Confrontar com as provas reunidas"


def _norm(texto):
    texto = (texto or "").strip().lower()
    texto = "".join(
        c for c in unicodedata.normalize("NFD", texto)
        if unicodedata.category(c) != "Mn"
    )
    texto = "".join(c if c.isalnum() or c.isspace() else " " for c in texto)
    return " ".join(texto.split())


def _rotulo(nome_topico):
    if nome_topico in ROTULOS:
        return ROTULOS[nome_topico]
    return "Fale sobre: " + nome_topico.replace("_", " ")


# Rótulo curto de cada confronto de contradição (o que o detetive aponta).
ROTULOS_CONFRONTO = {
    "horario": "o horário que não bate",
    "chave": "como conhece a chave",
    "telefonema": "a ligação que negou",
    "visita_estudio": "ter ido ao estúdio",
    "alibi": "o álibi furado",
}


def _rotulo_confronto_contradicao(nome_topico):
    return ROTULOS_CONFRONTO.get(nome_topico, nome_topico.replace("_", " "))


# Reações ao ser confrontado com uma contradição específica.
# Primeiro a fala específica (se existir); senão, uma genérica por culpa.
REACOES_CONFRONTO = {
    "renato": {
        "visita_estudio": ("...Está bem. Eu fui ao estúdio. Mas só para conversar! "
                           "Isso não prova nada."),
        "horario": ("Como eu sei do horário? Eu... li no seu relatório. Deve ter sido "
                    "isso. Pare de torcer minhas palavras."),
    },
    "helena": {
        "telefonema": ("Tudo bem! Eu liguei, sim. Ele me disse que ia expor um documento "
                       "da família. Fiquei furiosa, mas não pus os pés lá."),
    },
    "mara": {
        "horario": ("Eu me confundo com as horas, já disse! Ouvi o barulho, só não sei "
                    "cravar o minuto. Não transforme isso em crime."),
    },
}


def _reacao_confronto_contradicao(p, alvo):
    especificas = REACOES_CONFRONTO.get(p.get("id"), {})
    if alvo in especificas:
        return especificas[alvo]
    if p.get("culpado"):
        return ("Você... está me encurralando. Não tenho mais nada a dizer sobre isso, "
                "detetive.")
    return ("Eu entendo que pareça estranho, mas há uma explicação. Não estou mentindo "
            "para o senhor.")


def perguntas_de(caso_id, pid, evidencias=None, contradicoes=None,
                 topicos_abordados=None, perguntas_respondidas=None,
                 confessou=False):
    """Lista de perguntas prontas para um personagem.

    Cada item: {topico, rotulo, confronto(bool)}. Gera uma pergunta de
    confronto para cada contradição já exposta e, para o culpado, o confronto
    final quando as provas-chave já foram coletadas.
    """
    p = casos.personagem(caso_id, pid)
    if not p:
        return []
    topicos_abordados = topicos_abordados or {}
    perguntas_respondidas = set(perguntas_respondidas or [])
    perguntas = []
    for nt, dados in p["topicos"].items():
        vezes = topicos_abordados.get(nt, 0)
        respostas = dados.get("respostas")
        limite = len(respostas) if isinstance(respostas, list) else 1
        if vezes == 0:
            perguntas.append({
                "topico": nt, "rotulo": _rotulo(nt), "confronto": False,
            })
        elif vezes < limite:
            perguntas.append({
                "topico": "__retomar__" + nt,
                "rotulo": "Continuar: " + _rotulo(nt),
                "confronto": False, "continuacao": True,
            })

    # Confrontar cada contradição já exposta com este personagem.
    for tn in (contradicoes or []):
        topico_confronto = "__confrontar__" + tn
        if tn in p["topicos"] and topico_confronto not in perguntas_respondidas:
            perguntas.append({
                "topico": topico_confronto,
                "rotulo": "⚠ Confrontar: " + _rotulo_confronto_contradicao(tn),
                "confronto": True,
            })

    # Confronto final (só o culpado, exige as provas-chave).
    caso = casos.obter_caso(caso_id) or {}
    if (p.get("tipo") == "suspeito" and p.get("culpado") and p.get("confissao")
            and not confessou and "__confronto__" not in perguntas_respondidas):
        provas_req = caso.get("provas_para_confronto", [])
        tem_provas = all(pr in set(evidencias or []) for pr in provas_req)
        if tem_provas:
            perguntas.append({"topico": "__confronto__",
                              "rotulo": ROTULO_CONFRONTO, "confronto": True})
    return perguntas


def iniciar(caso_id, pid, evidencias=None, estado_salvo=None):
    p = casos.personagem(caso_id, pid)
    if not p:
        return {"erro": "Personagem não encontrado."}
    if (isinstance(estado_salvo, dict)
            and estado_salvo.get("caso_id") == caso_id
            and estado_salvo.get("pid") == pid):
        estado = dict(estado_salvo)
        estado["evidencias"] = list(dict.fromkeys(
            list(estado.get("evidencias") or []) + list(evidencias or [])
        ))
        estado.setdefault("nervosismo", 0)
        estado.setdefault("topicos_abordados", {})
        estado.setdefault("contradicoes", [])
        estado.setdefault("perguntas_respondidas", [])
        estado.setdefault("confessou", False)
    else:
        estado = {
            "caso_id": caso_id,
            "pid": pid,
            "nome": p["nome"],
            "papel": p["papel"],
            "retrato": p["retrato"],
            "abertura": p["abertura"],
            "tipo": p["tipo"],
            "nervosismo": 0,
            "topicos_abordados": {},
            "contradicoes": [],
            "perguntas_respondidas": [],
            "confessou": False,
            "evidencias": list(evidencias or []),
        }
    estado["perguntas"] = perguntas_de(
        caso_id, pid, estado["evidencias"], estado["contradicoes"],
        estado["topicos_abordados"], estado["perguntas_respondidas"],
        estado["confessou"],
    )
    return estado


def _resposta_topico(dados, vezes):
    if "respostas" in dados:
        lst = dados["respostas"]
        return lst[min(vezes, len(lst) - 1)]
    return dados.get("resposta", "")


def _detectar_topico(p, texto):
    """Fallback: detecta o tópico por palavras-chave no texto livre."""
    pergunta_norm = _norm(texto)
    palavras = set(pergunta_norm.split())
    melhor, ranking_max = None, (0, 0)
    for nome_topico, dados in p["topicos"].items():
        pontos, prioridade = 0, 0
        for g in dados["gatilhos"]:
            gn = _norm(g)
            if " " in gn:
                posicao = pergunta_norm.find(gn)
                if posicao >= 0:
                    pontos += 2
                    prioridade += 1 / (posicao + 1)
            elif gn in palavras:
                pontos += 1
                prioridade += 1 / (pergunta_norm.find(gn) + 1)
        ranking = (pontos, prioridade)
        if ranking > ranking_max:
            ranking_max, melhor = ranking, nome_topico
    return melhor, pergunta_norm


def perguntar(estado, pergunta=None, topico=None):
    """Processa uma pergunta. Prefira `topico` (pergunta pronta);
    `pergunta` (texto livre) é fallback."""
    caso_id = estado.get("caso_id")
    p = casos.personagem(caso_id, estado.get("pid"))
    if not p:
        return {"erro": "Personagem não encontrado.", "estado": estado}
    caso = casos.obter_caso(caso_id) or {}

    confissao_disparada = False
    libera_bloqueada = False
    revela = None
    contradicao = None

    # --- Confronto sobre uma CONTRADIÇÃO específica (__confrontar__<topico>) ---
    if topico and topico.startswith("__confrontar__"):
        alvo = topico[len("__confrontar__"):]
        fala = _reacao_confronto_contradicao(p, alvo)
        respondidas = estado.setdefault("perguntas_respondidas", [])
        if topico not in respondidas:
            respondidas.append(topico)
        if p.get("sensivel_confronto") is not False:
            estado["nervosismo"] += 1
        estado["perguntas"] = perguntas_de(
            caso_id, estado.get("pid"), estado.get("evidencias"),
            estado.get("contradicoes"), estado.get("topicos_abordados"),
            respondidas, estado.get("confessou"))
        return {
            "fala": fala, "topico": topico, "tipo": p["tipo"],
            "contradicao": None, "nervosismo": estado["nervosismo"],
            "confessou": estado["confessou"], "confissao_disparada": False,
            "libera_comunicacao": False, "revela": None,
            "perguntas": estado["perguntas"], "estado": estado,
        }

    # Tópicos com mais de uma resposta aparecem como pergunta de continuação.
    topico_selecionado = topico
    if topico and topico.startswith("__retomar__"):
        topico_selecionado = topico[len("__retomar__"):]

    # É um confronto final? (via botão de confronto ou via texto livre)
    eh_confronto = (topico_selecionado == "__confronto__")
    pergunta_norm = _norm(pergunta) if pergunta else ""
    if not eh_confronto and pergunta_norm:
        eh_confronto = any(g in pergunta_norm for g in CONFRONTO_GATILHOS)

    # Seleção do tópico a responder.
    if topico_selecionado and topico_selecionado != "__confronto__":
        melhor_topico = topico_selecionado if topico_selecionado in p["topicos"] else None
    elif eh_confronto:
        melhor_topico = None  # confronto não usa tópico comum
    else:
        melhor_topico, pergunta_norm = _detectar_topico(p, pergunta or "")

    if melhor_topico is None and not eh_confronto:
        gen = p.get("genericas") or ["..."]
        fala = gen[len(estado["topicos_abordados"]) % len(gen)]
    elif melhor_topico is not None:
        dados = p["topicos"][melhor_topico]
        vezes = estado["topicos_abordados"].get(melhor_topico, 0)
        estado["topicos_abordados"][melhor_topico] = vezes + 1
        respondidas = estado.setdefault("perguntas_respondidas", [])
        if melhor_topico not in respondidas:
            respondidas.append(melhor_topico)
        fala = _resposta_topico(dados, vezes)
        if dados.get("sensivel"):
            estado["nervosismo"] += 1
        revela = dados.get("revela")
        cont = dados.get("contradicao")
        if (cont and vezes + 1 >= cont["limite"]
                and melhor_topico not in estado["contradicoes"]):
            estado["contradicoes"].append(melhor_topico)
            contradicao = cont["texto"]
    else:
        fala = ""  # confronto preenche abaixo

    if eh_confronto:
        respondidas = estado.setdefault("perguntas_respondidas", [])
        if "__confronto__" not in respondidas:
            respondidas.append("__confronto__")

    # Confronto (suspeito culpado).
    if (eh_confronto and p.get("tipo") == "suspeito" and p.get("culpado")
            and p.get("confissao") and not estado["confessou"]):
        provas_req = caso.get("provas_para_confronto", [])
        tem_provas = all(pr in set(estado.get("evidencias", [])) for pr in provas_req)
        if tem_provas:
            estado["confessou"] = True
            confissao_disparada = True
            libera_bloqueada = True
            for ev in caso.get("evidencias", []):
                if ev.get("bloqueada"):
                    revela = ev["id"]
                    break
            fala = p["confissao"]
            contradicao = None
        else:
            fala = ("Confrontar-me com o quê, detetive? Suposições? Traga provas "
                    "concretas. Até lá, não tenho mais o que dizer.")
    elif eh_confronto and not fala:
        # Confronto com quem não é o culpado (ou já confessou).
        if estado.get("confessou"):
            fala = "Eu já disse tudo o que tinha a dizer, detetive."
        else:
            fala = ("Confrontar-me? Eu não tenho nada a esconder. Você está no "
                    "caminho errado.")

    if revela and revela not in estado.setdefault("evidencias", []):
        estado["evidencias"].append(revela)

    # Atualiza a lista de perguntas (contradição/confronto podem ter surgido).
    estado["perguntas"] = perguntas_de(caso_id, estado.get("pid"),
                                       estado.get("evidencias"),
                                       estado.get("contradicoes"),
                                       estado.get("topicos_abordados"),
                                       estado.get("perguntas_respondidas"),
                                       estado.get("confessou"))

    return {
        "fala": fala,
        "topico": melhor_topico if melhor_topico else (topico or None),
        "tipo": p["tipo"],
        "contradicao": contradicao,
        "nervosismo": estado["nervosismo"],
        "confessou": estado["confessou"],
        "confissao_disparada": confissao_disparada,
        "libera_comunicacao": libera_bloqueada,
        "revela": revela,
        "perguntas": estado["perguntas"],
        "estado": estado,
    }
