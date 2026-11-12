# -*- coding: utf-8 -*-
"""
Umbra Nox - Banco de dados dos 10 casos (série PECCATORES).

Cada caso é autocontido no dicionário CASOS[<id>] e carrega:
  meta (id, titulo, objetivo, introducao, etapa, mecanica, pergunta_trama),
  vitima, evidencias, provas_chave, linha_tempo, hipoteses, acusaveis,
  culpado, solucao, e "personagens" (suspeitos + peritos, cada um com
  tópicos de diálogo).

Formato de um personagem:
  {
    "id": str, "nome": str, "papel": str, "retrato": str,
    "tipo": "suspeito" | "pericia" | "legista",
    "culpado": bool,                 # só relevante p/ suspeitos
    "abertura": str,
    "topicos": { nome: {gatilhos:[...], respostas:[...] | resposta:str,
                        sensivel?:bool, revela?:id, contradicao?:{limite,texto}} },
    "genericas": [...],
    "confissao": str | None,         # confissão via confronto (culpado)
  }

O Dr. Adrian Kael (legista) aparece em TODOS os casos. É o vilão oculto: no
início é um aliado confiável; ao longo da série suas respostas deixam
sementes (conhece arquivos antigos, direciona linhas de investigação, conhece
informações que não deveria). No Caso 010 ele é confrontável.
"""

# ===========================================================================
# LORE / MORSE / ENIGMAS
# ===========================================================================
PALAVRA_SERIE = "PECCATORES"

VITIMAS_SERIE = [
    {"letra": "P", "nome": "Elias Voss", "pecado": "Perversão"},
    {"letra": "E", "nome": "Augusto Valença", "pecado": "Ganância"},
    {"letra": "C", "nome": "Beatriz Nogueira", "pecado": "Falso Testemunho"},
    {"letra": "C", "nome": "Samuel Figueredo", "pecado": "Soberba"},
    {"letra": "A", "nome": "Lívia Montenegro", "pecado": "Adultério e Traição"},
    {"letra": "T", "nome": "Vicente Alencar", "pecado": "Hipocrisia"},
    {"letra": "O", "nome": "Matheus Silva", "pecado": "Omissão"},
    {"letra": "R", "nome": "Thomas Lima", "pecado": "Ressentimento e Vingança"},
    {"letra": "E", "nome": "Clara Aguiar", "pecado": "Egoísmo"},
    {"letra": "S", "nome": "Marcelle Lopez", "pecado": "Sacrilégio"},
]

MORSE = {
    "A": ".-", "B": "-...", "C": "-.-.", "D": "-..", "E": ".", "F": "..-.",
    "G": "--.", "H": "....", "I": "..", "J": ".---", "K": "-.-", "L": ".-..",
    "M": "--", "N": "-.", "O": "---", "P": ".--.", "Q": "--.-", "R": ".-.",
    "S": "...", "T": "-", "U": "..-", "V": "...-", "W": ".--", "X": "-..-",
    "Y": "-.--", "Z": "--..",
}

ENIGMAS = [
    {"id": 1,
     "texto": ("A sala está escura. Há uma vela apagada, uma caixa de fósforos e "
               "uma porta trancada. O bilhete diz: 'Eu existo quando tudo "
               "desaparece.'"),
     "dica": "Aparece quando não há luz.",
     "respostas": ["escuro", "escuridao", "a escuridao", "o escuro"],
     "resposta_exibicao": "Escuro"},
    {"id": 2,
     "texto": ("Na mesa existe um copo com água pela metade. Ao lado dele, uma "
               "mensagem: 'Quanto mais eu tiro, maior eu fico.'"),
     "dica": "Aumenta quando algo é removido.",
     "respostas": ["buraco", "o buraco", "um buraco"],
     "resposta_exibicao": "Buraco"},
    {"id": 3,
     "texto": ("O relógio parou às 03:00. No chão, há três letras: L U Z. A "
               "porta final pede a palavra contrária."),
     "dica": "O contrário de luz.",
     "respostas": ["sombra", "a sombra", "sombras", "escuridao"],
     "resposta_exibicao": "Sombra"},
    {"id": 4,
     "texto": ("Um bilhete diz: 'Tenho cidades, mas não casas. Tenho rios, mas "
               "não água. Tenho estradas, mas ninguém anda por mim.'"),
     "dica": "Você consulta para encontrar lugares.",
     "respostas": ["mapa", "o mapa", "um mapa"],
     "resposta_exibicao": "Mapa"},
    {"id": 5,
     "texto": ("A gaveta contém uma chave, mas nenhuma fechadura. O investigador "
               "percebe: a chave não abre portas, abre respostas."),
     "dica": "É uma informação que resolve algo.",
     "respostas": ["pista", "a pista", "uma pista", "pistas"],
     "resposta_exibicao": "Pista"},
    {"id": 6,
     "texto": "Na parede está escrito: 'Falo sem boca e respondo sem corpo.'",
     "dica": "Você ouve depois de gritar em um lugar vazio.",
     "respostas": ["eco", "o eco", "um eco"],
     "resposta_exibicao": "Eco"},
]


def para_morse(texto):
    return " ".join(MORSE.get(c.upper(), "") for c in texto if c.upper() in MORSE)


def _perita(nome, abertura, topicos, genericas=None):
    """Monta a perita de cena de um caso."""
    return {
        "id": "perito_cena", "nome": nome,
        "papel": "Perícia criminal — cena do crime",
        "retrato": "Objetiva, luvas nas mãos, anota tudo em um caderno.",
        "tipo": "pericia", "culpado": False, "abertura": abertura,
        "topicos": topicos,
        "genericas": genericas or ["Isso foge da minha parte técnica, detetive.",
                                   "Registrei o que vi. O resto é com a investigação."],
        "confissao": None,
    }


def _kael(abertura, topicos, genericas=None):
    """Monta o Dr. Adrian Kael (legista) para um caso."""
    return {
        "id": "legista", "nome": "Dr. Adrian Kael",
        "papel": "Médico-legista · Departamento de Medicina Forense",
        "retrato": ("Preciso, educado, pausado. Raramente afirma algo sem uma "
                    "justificativa técnica. Mãos impecavelmente limpas."),
        "tipo": "legista", "culpado": False, "abertura": abertura,
        "topicos": topicos,
        "genericas": genericas or ["O corpo só responde o que sabemos perguntar.",
                                   "Fatos, não suposições. Fique com os fatos."],
        "confissao": None,
    }


CASOS = {}

# ===========================================================================
# CASO 001 - O RELÓGIO PARADO  (Elias Voss — Perversão)
# ===========================================================================
CASOS["001"] = {
    "id": "001",
    "titulo": "O RELÓGIO PARADO",
    "etapa": 1,
    "objetivo": "Reconstruir as últimas horas de Elias Voss.",
    "mecanica": "Interrogatórios guiados e a primeira Linha do Tempo.",
    "pergunta_trama": "Por que o horário do relógio não bate com o corpo?",
    "introducao": ("O primeiro caso começa agora. Analise as evidências, ouça os "
                   "depoimentos, conecte fatos e descubra o que realmente aconteceu."),
    # Tutorial: dicas que o frontend exibe nos momentos indicados por "gatilho".
    # gatilhos: abrir_caso | aba_arquivo | iniciar_dialogo | coletar_evidencia |
    #           contradicao | provas_2 | aba_truthtrace
    "tutorial": [
        {"gatilho": "abrir_caso",
         "texto": ("Bem-vindo, detetive. Este é o seu primeiro caso. Comece pela aba "
                   "DOSSIÊ para conhecer a vítima e o objetivo. Depois vá em EVIDÊNCIAS "
                   "para falar com as pessoas.")},
        {"gatilho": "aba_arquivo",
         "texto": ("Aqui ficam as evidências (começam vazias), as PESSOAS DE INTERESSE "
                   "e a EQUIPE TÉCNICA. Clique em alguém para conversar. Comece pela "
                   "Perita Sofia Mendes e pelo Dr. Kael.")},
        {"gatilho": "iniciar_dialogo",
         "texto": ("Escolha as perguntas prontas na parte de baixo. Cada pergunta pode "
                   "revelar algo. As que você já fez ficam marcadas com ✓.")},
        {"gatilho": "coletar_evidencia",
         "texto": ("Você coletou sua primeira evidência! Ela aparece na aba EVIDÊNCIAS. "
                   "As marcadas com ★ são provas-chave; com ⚠, não são confiáveis "
                   "sozinhas (como o relógio).")},
        {"gatilho": "contradicao",
         "texto": ("Uma CONTRADIÇÃO! Quando um depoimento não bate com outro fato, ela "
                   "é registrada na LINHA DO TEMPO. Cruzar versões é como se pega quem "
                   "mente — pressione quem se contradiz.")},
        {"gatilho": "provas_2",
         "texto": ("Você reuniu as duas primeiras provas-chave. Agora volte ao suspeito "
                   "principal: surgirá a opção de CONFRONTAR com as provas, liberando a "
                   "confissão.")},
        {"gatilho": "aba_truthtrace",
         "texto": ("No TRUTHTRACE você acompanha hipóteses e o progresso. Com as 3 "
                   "provas-chave reunidas, use ACUSAR para fechar o caso.")},
    ],
    "vitima": {
        "nome": "Elias Voss", "idade": 45,
        "ocupacao": "Fotógrafo forense aposentado",
        "citacao": "Algumas imagens não deveriam ser reveladas.",
        "biografia": ("Fotógrafo forense por 17 anos, reservado e metódico, "
                      "assombrado por um antigo caso que ajudou a documentar. "
                      "Manteve por anos, em segredo, um relacionamento com outro "
                      "homem, após perseguição em um ambiente conservador. Pouco "
                      "antes de morrer, descobriu uma alteração em fotografias de "
                      "um antigo processo criminal."),
        "local": "Estúdio fotográfico (residência)", "data": "17 de outubro",
        "hora": "07h00", "estado": "Homicídio suspeito", "indice_serie": 0,
    },
    "evidencias": [
        {"id": "relogio", "nome": "Relógio de bolso parado às 22h41",
         "descricao": ("Relógio de bolso com o vidro danificado, parado às 22h41. "
                       "Parece indicar a hora da morte — mas o dano é suspeito. "
                       "Prova NÃO confiável sozinha."), "confiavel": False},
        {"id": "sem_luta", "nome": "Nenhum sinal de luta",
         "descricao": ("Sem confronto nem arrombamento. Quem entrou tinha acesso "
                       "— a vítima confiava nessa pessoa.")},
        {"id": "causa_morte", "nome": "Causa da morte (laudo de Kael)",
         "descricao": ("Laudo do Dr. Kael: asfixia, sem marcas de luta. O relógio "
                       "parado às 22h41 NÃO comprova a hora da morte.")},
        {"id": "caderno", "nome": "Número anotado no caderno",
         "descricao": ("No caderno de Elias, um número isolado. O mesmo código "
                       "reaparece em registros médicos antigos do departamento.")},
        {"id": "processo_antigo", "nome": "Processo antigo (nº 0443)",
         "descricao": ("Há seis anos, Renato Salles coordenou uma investigação com "
                       "sequência incompleta de fotografias. Elias omitiu o que "
                       "sabia para protegê-lo e acabou afastado.")},
        {"id": "negativos", "nome": "Negativos sendo digitalizados",
         "descricao": ("Elias descobriu que uma foto fora RETIRADA da sequência "
                       "oficial do processo 0443 e o registro, alterado.")},
        {"id": "imagem_tomas", "nome": "Imagem preservada por Tomás",
         "descricao": ("Tomás Leal copiou um negativo a pedido de Elias. A imagem "
                       "mostra o detalhe incompatível com a versão oficial."),
         "chave_prova": True},
        {"id": "registro_alteracao", "nome": "Registro da alteração documental",
         "descricao": ("Comparando a cópia com o inventário, prova-se que uma foto "
                       "foi removida e o registro da ausência, adulterado."),
         "chave_prova": True},
        {"id": "comunicacao", "nome": "Comunicação autenticada de Renato",
         "descricao": ("Mensagem que prova que Renato SABIA que Elias recuperara o "
                       "negativo e pretendia impedir a revisão."),
         "chave_prova": True, "bloqueada": True},
        {"id": "tatuagem", "nome": "Marcas recentes na nuca",
         "descricao": ("Pequenas marcas superficiais, sem ligação aparente com o "
                       "crime. Sem comparar com outros registros, não é possível "
                       "identificar um padrão.")},
    ],
    "provas_chave": ["imagem_tomas", "registro_alteracao", "comunicacao"],
    "linha_tempo": [
        {"hora": "18h40", "titulo": "Elias trabalha nos negativos",
         "descricao": "Tomás confirma que Elias digitalizava negativos de um processo antigo.",
         "tipo": "depoimento", "fonte": "Depoimento — Tomás Leal"},
        {"hora": "20h14", "titulo": "Mensagem enviada",
         "descricao": "Elias menciona ter recuperado o 'negativo original'.",
         "tipo": "registro", "fonte": "Registro de mensagens"},
        {"hora": "22h10", "titulo": "Renato vai ao estúdio",
         "descricao": "Renato afirma ter passado 'rapidamente'. Sem testemunha.",
         "tipo": "depoimento", "fonte": "Depoimento — Renato Salles"},
        {"hora": "22h41", "titulo": "Relógio de bolso parado",
         "descricao": "Horário registrado no objeto danificado. Cronologia suspeita.",
         "tipo": "evidencia", "fonte": "Evidência física (não confiável)"},
        {"hora": "—", "titulo": "Negativo original desaparece",
         "descricao": "O negativo que Elias recuperara não foi encontrado na cena.",
         "tipo": "evidencia", "fonte": "Perícia"},
        {"hora": "07h00", "titulo": "Corpo encontrado",
         "descricao": "Cena intacta, sem luta, simulando acidente ou roubo.",
         "tipo": "registro", "fonte": "Boletim de ocorrência"},
    ],
    "hipoteses": [
        {"id": "h1", "texto": "Renato matou Elias para impedir a revisão do negativo original.", "status": "em_analise"},
        {"id": "h2", "texto": "Elias foi vítima de um roubo que deu errado.", "status": "baixa"},
        {"id": "h3", "texto": "Helena, a irmã, agiu por causa da disputa de herança.", "status": "baixa"},
        {"id": "h4", "texto": "A tatuagem em Morse liga este caso a uma série maior.", "status": "em_analise"},
    ],
    "provas_para_confronto": ["imagem_tomas", "registro_alteracao"],
    "acusaveis": ["renato", "mara", "helena", "tomas"],
    "culpado": "renato",
    "solucao": {
        "culpado_nome": "Renato Salles",
        "resumo": ("Seis anos atrás, Renato aprovou um relatório com sequência "
                   "incompleta de fotografias. Elias o protegeu e foi afastado. Ao "
                   "digitalizar os negativos, Elias descobriu a foto retirada e o "
                   "registro alterado. Quando Renato soube que Elias levaria tudo a "
                   "uma revisão, foi ao estúdio, matou-o e simulou acidente/roubo. "
                   "O relógio foi forçado para confundir a cronologia."),
        "veredito": ("Juntas — a imagem de Tomás, o registro da alteração e a "
                     "comunicação autenticada — provam a adulteração, o "
                     "conhecimento de Renato e sua tentativa de impedir a revisão."),
        "gancho": ("Mas as marcas na nuca e o número do caderno, que reaparece em "
                   "registros médicos antigos do departamento, permanecem sem "
                   "explicação."),
    },
    "personagens": [
        {"id": "mara", "nome": "Mara Lensk",
         "papel": "Vizinha e ex-assistente de Elias",
         "retrato": "Nervosa, evita contato visual.", "tipo": "suspeito",
         "culpado": False,
         "abertura": "Eu só quero ajudar, detetive. O Elias era um bom homem.",
         "topicos": {
            "alibi": {"gatilhos": ["onde estava", "alibi", "noite", "22", "fazia"],
                      "respostas": ["Estava em casa a noite toda. Ouvi uma discussão "
                                    "abafada por volta das dez — ele recebia gente tarde.",
                                    "Tenho medo, só isso. Foi morto na porta ao lado."]},
            "relacao": {"gatilhos": ["conhecia", "relacao", "assistente", "elias", "trabalhava"],
                        "respostas": ["Fui assistente dele por dois anos. Eu o admirava.",
                                      "Ele andava mexendo em negativos antigos, dizendo "
                                      "que ia 'consertar um erro do passado'."]},
            "visita": {"gatilhos": ["visita", "viu", "chegou", "renato", "homem"],
                       "respostas": ["Vi um homem chegar: elegante, sério. Do tempo "
                                     "do instituto. Acho que o chamavam de Renato.",
                                     "Ele chegou tarde e saiu afobado."]},
            "horario": {"gatilhos": ["hora", "horario", "quando", "relogio", "barulho"],
                        "respostas": ["O barulho foi mais para as 23h, na verdade. Não "
                                      "às dez, como falei antes.",
                                      "Desculpe — eu me confundo com os horários, de tão nervosa."],
                        "contradicao": {"limite": 1,
                          "texto": ("Mara primeiro disse ter ouvido a discussão 'por "
                                    "volta das dez', agora fala em 23h. O horário dela é "
                                    "incerto — mas situa alguém no estúdio à noite.")}},
            "ciume": {"gatilhos": ["ciume", "briga", "discussao", "voces", "rixa", "inimigo"],
                      "sensivel": True,
                      "respostas": ["Eu e o Elias? Nunca brigamos. Ele me tratava como filha.",
                                    "Dizem que me viram discutindo com ele na semana passada. "
                                    "Era sobre um atraso no aluguel, nada demais."]},
         },
         "genericas": ["Eu só quero que encontrem quem fez isso.", "Não sei de mais nada."],
         "confissao": None},

        {"id": "helena", "nome": "Helena Voss",
         "papel": "Irmã da vítima · Historiadora",
         "retrato": "Formal, contida, controla cada gesto.", "tipo": "suspeito",
         "culpado": False,
         "abertura": "Meu irmão e eu tínhamos diferenças, mas ninguém merece isto.",
         "topicos": {
            "alibi": {"gatilhos": ["onde estava", "alibi", "22", "30", "sozinha", "casa"],
                      "respostas": ["Em casa, sozinha, desde as 22h30.",
                                    "Não tenho quem confirme, mas é a verdade."]},
            "motivo": {"gatilhos": ["heranca", "familia", "documento", "dinheiro", "motivo"],
                       "sensivel": True,
                       "respostas": ["Elias ia contestar um documento da herança. "
                                     "Discordávamos, mas isso não é motivo para isto.",
                                     "Dinheiro me interessa menos do que imagina."]},
            "escritorio": {"gatilhos": ["escritorio", "estudio", "visitava", "frequentava"],
                           "respostas": ["Eu não visitava o escritório dele havia meses."]},
            "chave": {"gatilhos": ["chave", "gaveta", "foto", "reconhece", "revelador"],
                      "sensivel": True,
                      "respostas": ["Essa chave... ficava na segunda gaveta, atrás do "
                                    "revelador, à esquerda. Sempre ali.",
                                    "Eu... como eu saberia? Lembranças antigas, só isso."],
                      "contradicao": {"limite": 1,
                        "texto": ("Disse que não ia ao escritório havia meses, mas "
                                  "apontou a posição exata de uma chave que só quem "
                                  "esteve lá recentemente conheceria.")}},
            "telefonema": {"gatilhos": ["telefone", "telefonema", "ligacao", "ligou", "falou"],
                           "sensivel": True,
                           "respostas": ["Não falei com o Elias naquele dia.",
                                         "Houve uma ligação rápida à tarde, só isso. "
                                         "Nada de importante."],
                           "contradicao": {"limite": 1,
                             "texto": ("Helena afirmou não ter falado com Elias naquele "
                                       "dia, mas depois admite uma ligação à tarde. Ela "
                                       "omite o contato com a vítima.")}},
            "relacao": {"gatilhos": ["relacao", "irmao", "irma", "proximos", "conviviam"],
                        "respostas": ["Éramos distantes. O segredo dele sobre a vida "
                                      "pessoal nos afastou anos atrás.",
                                      "Eu respeitava quem ele era. A família é que não."]},
         },
         "genericas": ["Isso não vem ao caso.", "Prefiro não especular."],
         "confissao": None},

        {"id": "tomas", "nome": "Tomás Leal",
         "papel": "Restaurador fotográfico · Parceiro de Elias",
         "retrato": "Discreto, escolhe as palavras, carrega um peso.",
         "tipo": "suspeito", "culpado": False,
         "abertura": "Eu trabalhava com o Elias. Pergunte o que precisar.",
         "topicos": {
            "trabalho": {"gatilhos": ["trabalho", "negativo", "digitalizar", "processo", "fazia"],
                         "revela": "negativos",
                         "respostas": ["Ele digitalizava negativos de um processo antigo, "
                                       "obcecado com uma imagem.",
                                       "Dizia que 'faltava uma foto' onde não deveria."]},
            "copia": {"gatilhos": ["copia", "guardou", "escondeu", "backup", "segredo", "pediu"],
                      "sensivel": True, "revela": "imagem_tomas",
                      "respostas": ["Eu... prometi não falar disso.",
                                    "Está bem. A pedido do Elias, copiei um negativo. É "
                                    "esta imagem — o detalhe que contradiz a versão oficial."]},
            "comparar": {"gatilhos": ["comparar", "inventario", "catalogo", "registro", "omitido", "falta"],
                         "revela": "registro_alteracao",
                         "respostas": ["Compare a cópia com o inventário: uma foto foi "
                                       "removida da sequência e o registro, alterado. "
                                       "Foi proposital."]},
            "alibi": {"gatilhos": ["onde estava", "alibi", "noite", "22", "oficina"],
                      "respostas": ["Fiquei na oficina de revelação até tarde. Há o "
                                    "registro de energia do laboratório, pode conferir.",
                                    "Não fui ao estúdio dele naquela noite."]},
            "renato": {"gatilhos": ["renato", "superior", "coordenador", "conhece", "salles"],
                       "respostas": ["O Renato? Era o antigo chefe do Elias. Aparecia "
                                     "às vezes, sempre tenso quando falavam do processo.",
                                     "O Elias tinha medo de contar a ele que mexia nos "
                                     "negativos. Agora entendo por quê."]},
         },
         "genericas": ["Eu só sei da parte técnica.", "O Elias guardava os porquês para si."],
         "confissao": None},

        {"id": "renato", "nome": "Renato Salles",
         "papel": "Ex-coordenador de investigação · Antigo superior de Elias",
         "retrato": "Calmo, respostas diretas, observa cada palavra.",
         "tipo": "suspeito", "culpado": True,
         "abertura": "Conheço o procedimento. Vamos ser objetivos — não escondo nada.",
         "topicos": {
            "alibi": {"gatilhos": ["onde estava", "alibi", "noite", "casa"],
                      "sensivel": True,
                      "respostas": ["Eu estava em casa a noite inteira. Não saí.",
                                    "Não tenho quem confirme o horário, mas não sou assassino.",
                                    "Pare de insinuar. Eu fui embora. Ponto."]},
            "visita_estudio": {"gatilhos": ["visita", "foi la", "estudio", "passou", "esteve"],
                               "sensivel": True,
                               "respostas": ["Eu não fui ao estúdio dele. Já disse que "
                                             "fiquei em casa.",
                                             "Está bem — passei lá rapidamente, só para "
                                             "conversar. Mas saí antes das dez."],
                               "contradicao": {"limite": 1,
                                 "texto": ("Renato disse ter ficado em casa a noite toda, "
                                           "mas agora admite ter ido ao estúdio. A vizinha "
                                           "Mara também viu um homem do instituto chegar.")}},
            "horario": {"gatilhos": ["hora", "horario", "quando", "relogio", "22h41", "dez"],
                        "sensivel": True,
                        "respostas": ["Se fui lá, saí bem antes das 22h.",
                                      "Como eu saberia a hora do relógio parado às 22h41, "
                                      "se 'nem estive' no estúdio, detetive?"],
                        "contradicao": {"limite": 1,
                          "texto": ("Renato citou o horário do relógio parado (22h41) sem "
                                    "que ninguém tivesse dito a ele. Só quem esteve na cena "
                                    "saberia desse detalhe.")}},
            "processo": {"gatilhos": ["processo", "relatorio", "0443", "seis anos", "afastamento"],
                         "sensivel": True, "revela": "processo_antigo",
                         "respostas": ["O processo 0443? Água passada. Tudo conforme as regras.",
                                       "O Elias se afastou por conta própria.",
                                       "Chega de falar daquele relatório."]},
            "fotografia": {"gatilhos": ["foto", "negativo", "sequencia", "alteracao", "adulteracao"],
                           "sensivel": True,
                           "respostas": ["O Elias guardava milhares de imagens.",
                                         "Se faltava uma foto, deve ter sido erro de catalogação.",
                                         "Eu não alterei registro nenhum. Cuidado, detetive."]},
         },
         "genericas": ["Isso não tem relação comigo.", "Pergunte algo que faça sentido."],
         "confissao": ("...Você reuniu tudo. A cópia do Tomás, o registro adulterado e "
                       "essa mensagem. Sim. Soube que o Elias ia levar o negativo a uma "
                       "revisão independente. Seis anos de carreira desmoronariam. Fui ao "
                       "estúdio recuperar os negativos. Ele se recusou. Não planejei que "
                       "terminasse assim. Forcei o relógio para confundir a hora.")},

        _perita("Perita Sofia Mendes",
                "Isolei a cena assim que cheguei. Pergunte o que precisar.",
                {
                    "cena": {"gatilhos": ["cena", "sala", "estudio", "encontrou", "achou"],
                             "revela": "relogio",
                             "resposta": ("Tudo no lugar, nada revirado. Caído perto do "
                                          "corpo, um relógio de bolso trincado, parado às "
                                          "22h41. Anotei, mas não confiaria nesse horário.")},
                    "luta": {"gatilhos": ["luta", "confronto", "porta", "arrombamento", "sinais"],
                             "revela": "sem_luta",
                             "resposta": ("Nenhum sinal de luta nem arrombamento. A vítima "
                                          "não reagiu. Quem entrou tinha acesso.")},
                    "caderno": {"gatilhos": ["caderno", "numero", "anotacao", "papel", "nota"],
                                "revela": "caderno",
                                "resposta": ("Um caderno. Numa página, só um número, sem "
                                             "contexto. Registrei mesmo assim.")},
                    "corpo": {"gatilhos": ["corpo", "morte", "causa", "legista"],
                              "resposta": ("A causa é com o legista. O Dr. Kael assumiu o "
                                           "laudo — fale com ele.")},
                }),

        _kael("Sou o Dr. Kael. Já examinei o corpo. Posso corrigir uma impressão "
              "precipitada sobre a hora. Pergunte — eu só leio o que o corpo conta.",
              {
                  "causa": {"gatilhos": ["causa", "como morreu", "morte", "laudo", "obito"],
                            "revela": "causa_morte",
                            "resposta": ("Causa: asfixia. Nenhuma marca de luta. "
                                         "Silenciosa, controlada — alguém que ele deixou "
                                         "se aproximar.")},
                  "relogio": {"gatilhos": ["relogio", "22", "41", "hora", "horario", "quando", "bolso"],
                              "resposta": ("O relógio parado às 22h41? Eu não daria peso. O "
                                           "vidro trincado sugere dano por impacto, não "
                                           "parada natural. Pode ter sido forçado. NÃO "
                                           "comprova a hora da morte.")},
                  "quem": {"gatilhos": ["quem", "culpado", "assassino", "matou", "suspeito"],
                           "resposta": ("Eu aponto fatos, não pessoas. Uma sugestão: siga "
                                        "primeiro o motivo — o que Elias descobriu nos "
                                        "negativos. Rende mais do que perguntar quem tinha "
                                        "a chave.")},
                  "caderno": {"gatilhos": ["caderno", "numero", "codigo", "registro medico", "departamento"],
                              "resposta": ("Esse número... tem o formato de uma referência "
                                           "de arquivo médico antigo. Provavelmente "
                                           "coincidência. Eu não me prenderia a isso.")},
                  "tatuagem": {"gatilhos": ["tatuagem", "marca", "nuca", "morse", "simbolo", "pele"],
                               "revela": "tatuagem",
                               "resposta": ("Há pequenas marcas recentes na nuca. "
                                            "Sozinhas, não formam um padrão que eu "
                                            "possa identificar. Vale comparar com "
                                            "outros registros.")},
              }),
    ],
}


# ===========================================================================
# CASO 002 - O PREÇO DO SILÊNCIO  (Augusto Valença — Ganância)
# ===========================================================================
CASOS["002"] = {
    "id": "002",
    "titulo": "O PREÇO DO SILÊNCIO",
    "etapa": 1,
    "objetivo": "Distinguir roubo, motivação e homicídio no caso Augusto Valença.",
    "mecanica": "Comparar documentos financeiros — e notar o que desaparece.",
    "pergunta_trama": "Por que um ladrão deixaria o dinheiro e levaria um livro contábil?",
    "introducao": ("Augusto Valença, filantropo do setor hospitalar, foi encontrado "
                   "morto em seu escritório. O cofre está aberto, o dinheiro intacto. "
                   "O que sumiu foi um livro contábil."),
    "vitima": {
        "nome": "Augusto Valença", "idade": 61,
        "ocupacao": "Empresário do setor hospitalar · investidor em clínicas",
        "citacao": "Caridade também é um bom investimento.",
        "biografia": ("Construiu reputação de filantropo, mas desviava recursos de "
                      "uma fundação beneficente e manipulava contratos para adquirir "
                      "clínicas por preços fraudulentos. Parte do dinheiro financiava "
                      "um programa clandestino de pesquisas."),
        "local": "Escritório particular", "data": "29 de outubro",
        "hora": "08h20", "estado": "Homicídio suspeito", "indice_serie": 1,
    },
    "evidencias": [
        {"id": "cofre", "nome": "Cofre aberto, dinheiro intacto",
         "descricao": ("O cofre foi aberto sem arrombamento e o dinheiro continua "
                       "lá. Não foi roubo comum. Pista que engana: sugere assalto "
                       "frustrado, mas o alvo era outro."), "confiavel": False},
        {"id": "livro_sumido", "nome": "Livro contábil desaparecido",
         "descricao": ("O único objeto ausente é um livro contábil físico — onde "
                       "Augusto registrava o que não entrava nos sistemas oficiais.")},
        {"id": "causa_morte", "nome": "Causa da morte (laudo de Kael)",
         "descricao": ("Laudo do Dr. Kael: parada cardíaca induzida por uma "
                       "substância. Kael sugere priorizar 'a origem do dinheiro' "
                       "antes de checar quem teve acesso ao escritório.")},
        {"id": "fundacao", "nome": "Desvios da fundação beneficente",
         "descricao": ("Recursos da fundação eram desviados e reaplicados na compra "
                       "fraudulenta de clínicas. Vários sócios lucravam com o silêncio.")},
        {"id": "pagamentos", "nome": "Pagamentos a uma empresa de fachada",
         "descricao": ("Pagamentos da fundação vinculados a uma empresa que prestava "
                       "serviços ao departamento médico-legista. Um fio que não "
                       "deveria existir neste caso.")},
        {"id": "copia_livro", "nome": "Cópia digital do livro contábil",
         "descricao": ("Daniela guardou uma cópia digital do livro — a escrituração "
                       "paralela de Augusto, com nomes e valores."),
         "chave_prova": True},
        {"id": "contrato", "nome": "Contrato de compra fraudulenta",
         "descricao": ("Um contrato assinado por Augusto e pelo sócio Bruno Tavares "
                       "comprova a aquisição de clínica abaixo do valor, mediante "
                       "propina."), "chave_prova": True},
        {"id": "ameaca", "nome": "Ameaça autenticada de Bruno",
         "descricao": ("Mensagem autenticada em que Bruno exige que Augusto 'resolva "
                       "antes que a auditoria chegue' — e avisa que irá 'pessoalmente'."),
         "chave_prova": True, "bloqueada": True},
    ],
    "provas_chave": ["copia_livro", "contrato", "ameaca"],
    "linha_tempo": [
        {"hora": "19h00", "titulo": "Augusto dispensa a equipe",
         "descricao": "Daniela diz que ele a mandou embora mais cedo, agitado.",
         "tipo": "depoimento", "fonte": "Depoimento — Daniela Rós"},
        {"hora": "20h30", "titulo": "Reunião não registrada",
         "descricao": "Bruno afirma que 'nem foi ao escritório'. A portaria discorda.",
         "tipo": "depoimento", "fonte": "Depoimento — Bruno Tavares"},
        {"hora": "21h05", "titulo": "Cofre aberto",
         "descricao": "Aberto sem arrombamento. Dinheiro intacto; livro ausente.",
         "tipo": "evidencia", "fonte": "Perícia"},
        {"hora": "08h20", "titulo": "Corpo encontrado",
         "descricao": "A faxina encontra Augusto caído sobre a mesa.",
         "tipo": "registro", "fonte": "Boletim de ocorrência"},
    ],
    "hipoteses": [
        {"id": "h1", "texto": "Bruno matou Augusto para encerrar a fraude antes da auditoria.", "status": "em_analise"},
        {"id": "h2", "texto": "Foi um assalto que deu errado.", "status": "baixa"},
        {"id": "h3", "texto": "Daniela desviou dinheiro e eliminou a testemunha.", "status": "baixa"},
        {"id": "h4", "texto": "Os pagamentos ao departamento médico-legista não são deste caso.", "status": "em_analise"},
    ],
    "provas_para_confronto": ["copia_livro", "contrato"],
    "acusaveis": ["bruno", "daniela", "lorena"],
    "culpado": "bruno",
    "solucao": {
        "culpado_nome": "Bruno Tavares",
        "resumo": ("Sócio de Augusto nas aquisições fraudulentas, Bruno soube de uma "
                   "auditoria iminente. Augusto, acuado, ameaçou entregar tudo para "
                   "se salvar. Bruno foi ao escritório, induziu a parada cardíaca com "
                   "uma substância e levou o livro contábil físico para destruir a "
                   "prova — deixando o dinheiro para simular um assalto frustrado."),
        "veredito": ("A cópia digital do livro, o contrato fraudulento e a ameaça "
                     "autenticada ligam Bruno ao motivo, ao método e à intenção."),
        "gancho": ("Resta a trilha dos pagamentos da fundação a uma empresa que "
                   "servia ao departamento médico-legista — e o laudo de Kael, que "
                   "insistiu em afastar a investigação do acesso ao escritório."),
    },
    "personagens": [
        {"id": "daniela", "nome": "Daniela Rós",
         "papel": "Secretária executiva de Augusto",
         "retrato": "Eficiente, leal, assustada com o que viu nos livros.",
         "tipo": "suspeito", "culpado": False,
         "abertura": "Trabalhei dez anos para o Sr. Valença. Eu vi coisas... pergunte.",
         "topicos": {
            "alibi": {"gatilhos": ["onde estava", "alibi", "noite", "saiu", "19"],
                      "respostas": ["Ele me dispensou cedo, agitado. Fui para casa.",
                                    "Juro que não voltei. Tinha medo dele quando ficava assim."]},
            "livros": {"gatilhos": ["livro", "contabil", "conta", "financeiro", "numeros"],
                       "revela": "fundacao",
                       "respostas": ["Havia dois conjuntos de números. O oficial... e o outro.",
                                     "A fundação 'doava', mas o dinheiro voltava por outra porta."]},
            "copia": {"gatilhos": ["copia", "guardou", "backup", "digital", "escondeu", "prova"],
                      "sensivel": True, "revela": "copia_livro",
                      "respostas": ["Eu não deveria ter isso...",
                                    "Fiz uma cópia digital do livro, com medo. Está aqui. "
                                    "Nomes, valores, tudo."]},
            "bruno": {"gatilhos": ["bruno", "socio", "tavares", "visita", "quem"],
                      "respostas": ["O Sr. Tavares vinha muito. Nas últimas semanas, "
                                    "brigavam. Ouvi a palavra 'auditoria'."]},
         },
         "genericas": ["Eu só quero sair dessa viva.", "Não sei de mais nada."],
         "confissao": None},

        {"id": "lorena", "nome": "Lorena Valença",
         "papel": "Sobrinha e herdeira de Augusto",
         "retrato": "Impaciente, fala alto, parece calcular cada resposta.",
         "tipo": "suspeito", "culpado": False,
         "abertura": "Meu tio tinha inimigos de sobra. Não percam tempo comigo.",
         "topicos": {
            "alibi": {"gatilhos": ["onde estava", "alibi", "noite", "21"],
                      "respostas": ["Estava num jantar, com vinte testemunhas. Confira."]},
            "heranca": {"gatilhos": ["heranca", "dinheiro", "herdeira", "motivo", "testamento"],
                        "sensivel": True,
                        "respostas": ["Sim, eu herdo. E daí? Eu já tenho dinheiro.",
                                      "Não precisava matá-lo. Ele ia afundar sozinho."]},
            "fundacao": {"gatilhos": ["fundacao", "caridade", "fraude", "desvio"],
                         "respostas": ["Aquela 'caridade' era fachada. Todo mundo sabia, "
                                       "menos os jornais."]},
         },
         "genericas": ["Já disse o que sei.", "Procurem o sócio dele."],
         "confissao": None},

        {"id": "bruno", "nome": "Bruno Tavares",
         "papel": "Sócio de Augusto nas aquisições",
         "retrato": "Sorriso treinado, aperto de mão firme, olhos frios.",
         "tipo": "suspeito", "culpado": True,
         "abertura": "Augusto era meu amigo e sócio. Que tragédia. Em que posso ajudar?",
         "topicos": {
            "alibi": {"gatilhos": ["onde estava", "alibi", "noite", "escritorio", "20"],
                      "sensivel": True,
                      "respostas": ["Nem fui ao escritório naquela noite.",
                                    "A portaria? Devem ter confundido. Eu estava em casa.",
                                    "Já respondi isso. Chega."]},
            "auditoria": {"gatilhos": ["auditoria", "contrato", "fraude", "clinica", "negocio"],
                          "sensivel": True, "revela": "contrato",
                          "respostas": ["Nossos negócios eram legítimos.",
                                        "Esse contrato... o valor estava dentro do mercado.",
                                        "Tudo bem, havia uma auditoria. Não é crime ter contador."]},
            "ameaca": {"gatilhos": ["ameaca", "mensagem", "briga", "discussao", "medo"],
                       "sensivel": True,
                       "respostas": ["Eu nunca ameacei o Augusto.",
                                     "Discussões de sócios. Nada além disso."]},
         },
         "genericas": ["Isso é absurdo.", "Fale com meus advogados."],
         "confissao": ("Chega. Sim — a cópia do livro, o contrato, e agora essa "
                       "mensagem. A auditoria ia nos destruir e o Augusto quis me "
                       "entregar para se salvar. Fui lá para negociar. Ele riu de mim. "
                       "Eu só queria o livro. Levei o livro e deixei o dinheiro: quem "
                       "procura ladrão não procura sócio. Não imaginei que o coração "
                       "dele não aguentaria o que coloquei no copo.")},

        _perita("Perita Sofia Mendes",
                "Cena preservada. O cofre foi o que mais me intrigou. Pergunte.",
                {
                    "cofre": {"gatilhos": ["cofre", "dinheiro", "roubo", "assalto", "aberto"],
                              "revela": "cofre",
                              "resposta": ("Cofre aberto sem arrombamento, com o dinheiro "
                                           "dentro. Ladrão nenhum deixa o dinheiro. O alvo "
                                           "era outra coisa.")},
                    "livro": {"gatilhos": ["sumiu", "falta", "levou", "livro", "objeto"],
                              "revela": "livro_sumido",
                              "resposta": ("Só um objeto desapareceu: um livro contábil "
                                           "físico. Quem matou veio buscar justamente isso.")},
                    "acesso": {"gatilhos": ["acesso", "porta", "entrou", "portaria", "entrada"],
                               "resposta": ("Sem arrombamento. E a portaria registrou uma "
                                            "visita naquela noite — confira os nomes.")},
                }),

        _kael("Examinei o corpo. Posso lhe dar a causa. E, se me permite, uma "
              "orientação sobre por onde começar.",
              {
                  "causa": {"gatilhos": ["causa", "morte", "como morreu", "laudo", "coracao"],
                            "revela": "causa_morte",
                            "resposta": ("Parada cardíaca induzida por uma substância. Não "
                                         "foi natural. Eu, no seu lugar, seguiria primeiro a "
                                         "origem do dinheiro — antes de perder tempo com quem "
                                         "tinha a chave do escritório.")},
                  "pagamentos": {"gatilhos": ["pagamento", "empresa", "fundacao", "departamento", "servico"],
                                 "revela": "pagamentos",
                                 "resposta": ("Há pagamentos da fundação a uma prestadora de "
                                              "serviços... inclusive ao nosso departamento. "
                                              "Burocracia comum. Não perderia tempo com isso.")},
                  "quem": {"gatilhos": ["quem", "culpado", "matou", "suspeito"],
                           "resposta": ("Fatos, detetive. O método aponta para alguém com "
                                        "acesso a substâncias e motivo financeiro.")},
              }),
    ],
}


# ===========================================================================
# CASO 003 - A TESTEMUNHA QUE MENTIU  (Beatriz Nogueira — Falso Testemunho)
# ===========================================================================
CASOS["003"] = {
    "id": "003",
    "titulo": "A TESTEMUNHA QUE MENTIU",
    "etapa": 1,
    "objetivo": "Identificar contradições entre as versões sobre o sumiço de Beatriz.",
    "mecanica": "Comparar depoimentos: uma mentira não torna tudo falso.",
    "pergunta_trama": "Qual laudo pericial tem duas versões que não coincidem?",
    "introducao": ("Beatriz Nogueira, jornalista investigativa, desapareceu depois "
                   "de marcar uma entrevista para revelar documentos que corrigiriam "
                   "sua reportagem mais famosa. Vários depoimentos se contradizem."),
    "vitima": {
        "nome": "Beatriz Nogueira", "idade": 39,
        "ocupacao": "Jornalista investigativa",
        "citacao": "A verdade publicada vale mais do que a verdade sabida.",
        "biografia": ("Famosa por expor escândalos políticos. Fabricou parte de um "
                      "depoimento para proteger a própria fonte; a mentira ajudou a "
                      "condenar um inocente e destruiu a carreira de quem tentou "
                      "desmenti-la. Arrependida, temia admitir a fraude publicamente."),
        "local": "Apartamento (desaparecimento)", "data": "12 de novembro",
        "hora": "Noite", "estado": "Desaparecimento / homicídio suspeito",
        "indice_serie": 2,
    },
    "evidencias": [
        {"id": "entrevista", "nome": "Entrevista marcada e cancelada",
         "descricao": ("Beatriz marcara uma entrevista para revelar documentos. Foi "
                       "cancelada de última hora por uma mensagem — que talvez não "
                       "tenha sido ela quem enviou."), "confiavel": False},
        {"id": "versoes", "nome": "Depoimentos contraditórios",
         "descricao": ("Três pessoas descrevem a mesma noite de formas incompatíveis. "
                       "Uma mentira não invalida tudo o que a pessoa disse — é preciso "
                       "separar o falso do verdadeiro.")},
        {"id": "causa_morte", "nome": "Parecer de Kael",
         "descricao": ("Sem corpo, Kael trabalha com o material disponível. Sugere "
                       "tratar o caso como fuga voluntária 'até prova em contrário' — "
                       "o que esfriaria a busca.")},
        {"id": "reportagem", "nome": "A reportagem premiada",
         "descricao": ("A matéria que fez a fama de Beatriz condenou um homem. Parte "
                       "do depoimento-chave foi fabricada para proteger a fonte dela.")},
        {"id": "retratacao", "nome": "Rascunho de retratação",
         "descricao": ("Beatriz escrevia uma retratação admitindo a fraude. Era o que "
                       "ela revelaria na entrevista cancelada."), "chave_prova": True},
        {"id": "laudo_duplo", "nome": "Laudo pericial com duas versões",
         "descricao": ("O processo que Beatriz investigava tem um laudo cuja versão "
                       "original NÃO coincide com a cópia arquivada. Alguém adulterou."),
         "chave_prova": True},
        {"id": "confissao_fonte", "nome": "Mensagem autenticada da fonte",
         "descricao": ("Comunicação autenticada em que a fonte, Otávio, exige que "
                       "Beatriz 'não publique nada' e marca de ir vê-la naquela noite."),
         "chave_prova": True, "bloqueada": True},
    ],
    "provas_chave": ["retratacao", "laudo_duplo", "confissao_fonte"],
    "linha_tempo": [
        {"hora": "17h00", "titulo": "Entrevista é marcada",
         "descricao": "Beatriz confirma a entrevista para revelar documentos.",
         "tipo": "registro", "fonte": "Agenda da redação"},
        {"hora": "21h30", "titulo": "Mensagem cancela a entrevista",
         "descricao": "Uma mensagem do celular dela cancela tudo. O estilo não é o dela.",
         "tipo": "evidencia", "fonte": "Registro de mensagens"},
        {"hora": "22h00", "titulo": "Visita não confirmada",
         "descricao": "Otávio diz que 'passou rápido'. O porteiro viu os dois discutindo.",
         "tipo": "depoimento", "fonte": "Depoimentos conflitantes"},
        {"hora": "—", "titulo": "Beatriz não é mais vista",
         "descricao": "Nenhum registro dela após a noite. O apartamento está em ordem.",
         "tipo": "registro", "fonte": "Investigação"},
    ],
    "hipoteses": [
        {"id": "h1", "texto": "Otávio (a fonte) silenciou Beatriz para impedir a retratação.", "status": "em_analise"},
        {"id": "h2", "texto": "Beatriz fugiu para escapar das consequências da fraude.", "status": "baixa"},
        {"id": "h3", "texto": "O editor Hélio agiu para proteger a reputação do jornal.", "status": "baixa"},
        {"id": "h4", "texto": "O laudo adulterado conecta este caso a algo maior.", "status": "em_analise"},
    ],
    "provas_para_confronto": ["retratacao", "laudo_duplo"],
    "acusaveis": ["otavio", "helio", "carla"],
    "culpado": "otavio",
    "solucao": {
        "culpado_nome": "Otávio Reis",
        "resumo": ("Otávio foi a fonte que Beatriz protegeu com um depoimento "
                   "fabricado. Quando ela decidiu se retratar e expor o laudo "
                   "adulterado, ele percebeu que seria arrastado junto. Enviou a "
                   "mensagem falsa cancelando a entrevista, foi ao apartamento e a "
                   "silenciou, forjando uma 'fuga voluntária'."),
        "veredito": ("O rascunho de retratação, o laudo com duas versões e a mensagem "
                     "autenticada de Otávio mostram o motivo, a fraude encoberta e a "
                     "presença dele na noite do desaparecimento."),
        "gancho": ("O laudo adulterado saiu do mesmo arquivo pericial dos casos "
                   "anteriores. E Kael tentou, de novo, esfriar a investigação."),
    },
    "personagens": [
        {"id": "carla", "nome": "Carla Nogueira",
         "papel": "Irmã de Beatriz", "retrato": "Angustiada, fala rápido, quer respostas.",
         "tipo": "suspeito", "culpado": False,
         "abertura": "Minha irmã não fugiria sem me avisar. Alguém fez algo com ela.",
         "topicos": {
            "relacao": {"gatilhos": ["irma", "relacao", "beatriz", "familia"],
                        "respostas": ["Éramos próximas. Ela andava atormentada por uma "
                                      "matéria antiga.",
                                      "Dizia que 'ia consertar uma injustiça', custasse o que custasse."]},
            "fonte": {"gatilhos": ["fonte", "otavio", "quem", "medo", "ameaca"],
                      "respostas": ["Ela tinha medo de um homem. Uma fonte antiga. "
                                    "Otávio, acho.",
                                    "Ela dizia: 'ele tem tanto a perder quanto eu'."]},
            "retratacao": {"gatilhos": ["retratacao", "documento", "revelar", "entrevista", "verdade"],
                           "revela": "retratacao",
                           "respostas": ["Ela me mostrou um rascunho. Uma retratação "
                                         "admitindo que mentiu na reportagem. Guardei uma cópia."]},
         },
         "genericas": ["Achem minha irmã, por favor.", "Não sei de mais nada."],
         "confissao": None},

        {"id": "helio", "nome": "Hélio Prado",
         "papel": "Editor-chefe do jornal", "retrato": "Político, mede cada palavra.",
         "tipo": "suspeito", "culpado": False,
         "abertura": "Beatriz é nossa melhor repórter. Isto é péssimo para todos nós.",
         "topicos": {
            "alibi": {"gatilhos": ["onde estava", "alibi", "noite", "22"],
                      "respostas": ["Fechando a edição, na redação, com a equipe toda."]},
            "reputacao": {"gatilhos": ["jornal", "reputacao", "reportagem", "fraude", "retratacao"],
                          "sensivel": True,
                          "respostas": ["Uma retratação arranharia o jornal, claro. Mas "
                                        "preferível a esconder um erro.",
                                        "Eu a aconselhei a esperar. Nunca a impedir."]},
            "laudo": {"gatilhos": ["laudo", "processo", "documento", "versao", "copia"],
                      "revela": "reportagem",
                      "respostas": ["A matéria dela condenou um homem. Se o depoimento "
                                    "foi forjado... é gravíssimo. Era disso que ela falava."]},
         },
         "genericas": ["O jornal colabora com a investigação.", "Pergunte à família."],
         "confissao": None},

        {"id": "otavio", "nome": "Otávio Reis",
         "papel": "Antiga fonte de Beatriz · Assessor político",
         "retrato": "Afável, bom de conversa, desconversa com elegância.",
         "tipo": "suspeito", "culpado": True,
         "abertura": "Eu e a Beatriz somos velhos conhecidos. Espero que esteja bem.",
         "topicos": {
            "alibi": {"gatilhos": ["onde estava", "alibi", "noite", "22", "apartamento", "visita"],
                      "sensivel": True,
                      "respostas": ["Passei rápido na casa dela, só para conversar. Saí logo.",
                                    "O porteiro deve ter se confundido. Não discutimos.",
                                    "Já respondi onde eu estava. Chega."]},
            "fonte": {"gatilhos": ["fonte", "depoimento", "reportagem", "reportagem antiga", "forjado"],
                      "sensivel": True, "revela": "reportagem",
                      "respostas": ["Fui fonte dela uma vez, sim. Faz tempo.",
                                    "O depoimento? Ela escreveu o que quis. Eu só contei a verdade.",
                                    "Se havia algo forjado, a responsabilidade é dela, não minha."]},
            "laudo": {"gatilhos": ["laudo", "versao", "copia", "arquivo", "adulterado", "processo"],
                      "sensivel": True,
                      "respostas": ["Não entendo de laudo pericial.",
                                    "Se um documento tem duas versões, pergunte a quem o arquiva."]},
         },
         "genericas": ["Isso é especulação.", "Procurem quem tinha motivo de verdade."],
         "confissao": ("Está bem. A retratação, o laudo, a minha mensagem. Ela ia me "
                       "citar pelo nome. Aquele depoimento me protegeu uma vez e ia me "
                       "enterrar agora. Mandei a mensagem cancelando a entrevista, fui "
                       "até lá para convencê-la. Ela não cedeu. Eu perdi a cabeça. "
                       "Fiz parecer que ela tinha fugido.")},

        _perita("Perita Sofia Mendes",
                "Sem corpo, trabalhamos com a cena e os registros. Pergunte.",
                {
                    "mensagem": {"gatilhos": ["mensagem", "cancelou", "celular", "entrevista", "cancelamento"],
                                 "revela": "entrevista",
                                 "resposta": ("A mensagem que cancelou a entrevista saiu do "
                                              "celular dela, mas o padrão de escrita não bate. "
                                              "Alguém escreveu no lugar dela.")},
                    "versoes": {"gatilhos": ["depoimento", "versao", "contradicao", "testemunha", "conflito"],
                                "revela": "versoes",
                                "resposta": ("Três depoimentos, três versões da mesma noite. "
                                             "Uma delas mente — mas não em tudo. Separe o "
                                             "falso do verdadeiro.")},
                    "cena": {"gatilhos": ["cena", "apartamento", "ordem", "sinais"],
                             "resposta": ("Apartamento em ordem demais. Arrumado para "
                                          "parecer uma saída planejada.")},
                }),

        _kael("Sem corpo, meu laudo é limitado. Mas posso orientar a leitura dos fatos.",
              {
                  "parecer": {"gatilhos": ["causa", "morte", "corpo", "parecer", "fuga"],
                              "revela": "causa_morte",
                              "resposta": ("Sem corpo, eu trataria como fuga voluntária até "
                                           "prova em contrário. Economiza recursos. Não me "
                                           "deteria em teorias de homicídio ainda.")},
                  "laudo_processo": {"gatilhos": ["laudo", "processo", "versao", "copia", "arquivo", "pericia"],
                                     "revela": "laudo_duplo",
                                     "resposta": ("Curioso: o laudo do processo que ela "
                                                  "investigava tem duas versões que não "
                                                  "coincidem. Erros de arquivamento acontecem. "
                                                  "Eu não daria tanto peso.")},
                  "quem": {"gatilhos": ["quem", "culpado", "suspeito", "matou"],
                           "resposta": ("Fatos, detetive. Comece pelas contradições dos "
                                        "depoimentos — não pela figura mais óbvia.")},
              }),
    ],
}


# ===========================================================================
# CASO 004 - O TRONO DE CINZAS  (Samuel Figueredo — Soberba)
# ===========================================================================
CASOS["004"] = {
    "id": "004",
    "titulo": "O TRONO DE CINZAS",
    "etapa": 2,
    "objetivo": "Furar a reputação intocável de Samuel e achar o que ele escondia.",
    "mecanica": "Evidências só liberadas ao confrontar alguém com o que já sabe.",
    "pergunta_trama": "Por que os documentos dele foram reorganizados após a morte?",
    "introducao": ("Samuel Figueredo, dirigente religioso respeitado, foi encontrado "
                   "morto numa sala reservada de sua instituição. Os documentos que "
                   "mantinha sob chave estavam organizados de forma diferente do habitual."),
    "vitima": {
        "nome": "Samuel Figueredo", "idade": 52,
        "ocupacao": "Dirigente de instituição religiosa",
        "citacao": "Quem serve a uma causa maior não presta contas aos homens.",
        "biografia": ("Acreditava-se acima de qualquer julgamento. Encobriu denúncias "
                      "contra pessoas influentes e perseguiu quem ameaçava sua "
                      "autoridade, sempre em nome de uma 'causa sagrada' — justificativa "
                      "para o abuso de poder."),
        "local": "Sala reservada da instituição", "data": "03 de dezembro",
        "hora": "06h30", "estado": "Homicídio suspeito", "indice_serie": 3,
    },
    "evidencias": [
        {"id": "documentos_reorg", "nome": "Documentos reorganizados",
         "descricao": ("Os arquivos sob chave de Samuel estavam em ordem diferente da "
                       "habitual. Quem matou procurou (ou plantou) algo. Pista que "
                       "engana: parece bagunça de luta, mas foi busca metódica."),
         "confiavel": False},
        {"id": "denuncias", "nome": "Denúncias encobertas",
         "descricao": ("Pastas com denúncias contra figuras influentes, arquivadas "
                       "por Samuel para proteger a instituição — e a si mesmo.")},
        {"id": "causa_morte", "nome": "Laudo de Kael",
         "descricao": ("Kael: golpe único na nuca, sem hesitação. Recomenda tratar o "
                       "documento reorganizado como 'preliminar', não como prova.")},
        {"id": "programa_medico", "nome": "Programa de assistência com códigos",
         "descricao": ("Entre os papéis, referências a um antigo programa de "
                       "assistência médica cujos participantes foram registrados sob "
                       "CÓDIGOS, não nomes. Um fio recorrente.")},
        {"id": "dossie_irene", "nome": "Dossiê escondido por Irene",
         "descricao": ("Irene, secretária, guardou um dossiê que Samuel usava para "
                       "chantagear dissidentes — prova do abuso de poder."),
         "chave_prova": True},
        {"id": "registro_visitas", "nome": "Registro de visitas adulterado",
         "descricao": ("O livro de visitas da sala reservada teve uma página trocada. "
                       "A entrada original mostra quem esteve com Samuel por último."),
         "chave_prova": True},
        {"id": "ultimato", "nome": "Ultimato autenticado de Daniel",
         "descricao": ("Mensagem autenticada em que o diácono Daniel exige que Samuel "
                       "'devolva o que tirou da minha família' e avisa que irá cobrá-lo "
                       "pessoalmente."), "chave_prova": True, "bloqueada": True},
    ],
    "provas_chave": ["dossie_irene", "registro_visitas", "ultimato"],
    "linha_tempo": [
        {"hora": "21h00", "titulo": "Instituição fecha ao público",
         "descricao": "Irene afirma ter trancado tudo e deixado Samuel sozinho.",
         "tipo": "depoimento", "fonte": "Depoimento — Irene Souto"},
        {"hora": "22h15", "titulo": "Entrada não registrada",
         "descricao": "Alguém entrou pela porta lateral. A página do livro foi trocada.",
         "tipo": "evidencia", "fonte": "Perícia"},
        {"hora": "—", "titulo": "Documentos remexidos",
         "descricao": "Arquivos reorganizados metodicamente. Não foi pânico.",
         "tipo": "evidencia", "fonte": "Perícia"},
        {"hora": "06h30", "titulo": "Corpo encontrado",
         "descricao": "O zelador encontra Samuel na sala reservada.",
         "tipo": "registro", "fonte": "Boletim de ocorrência"},
    ],
    "hipoteses": [
        {"id": "h1", "texto": "Daniel matou Samuel por vingança pessoal e familiar.", "status": "em_analise"},
        {"id": "h2", "texto": "Um assalto à sala de documentos valiosos.", "status": "baixa"},
        {"id": "h3", "texto": "Irene eliminou o chefe que a oprimia por anos.", "status": "baixa"},
        {"id": "h4", "texto": "O programa médico com códigos liga este caso aos demais.", "status": "em_analise"},
    ],
    "provas_para_confronto": ["dossie_irene", "registro_visitas"],
    "acusaveis": ["daniel", "irene", "paulo"],
    "culpado": "daniel",
    "solucao": {
        "culpado_nome": "Daniel Mares",
        "resumo": ("Diácono e antigo aliado, Daniel teve a família destruída por uma "
                   "denúncia que Samuel encobriu para proteger um doador influente. "
                   "Ao saber que Samuel manipularia mais uma vez, foi à sala reservada, "
                   "cobrou-o e o golpeou. Depois reorganizou os documentos buscando o "
                   "dossiê que o incriminava — e trocou a página do livro de visitas."),
        "veredito": ("O dossiê guardado por Irene, o registro de visitas adulterado e "
                     "o ultimato autenticado de Daniel reúnem motivo, presença e intenção."),
        "gancho": ("As referências ao programa de assistência médica — participantes "
                   "sob códigos, não nomes — voltam a aparecer. E Kael pediu para tratar "
                   "a cena como 'preliminar'."),
    },
    "personagens": [
        {"id": "irene", "nome": "Irene Souto",
         "papel": "Secretária da instituição", "retrato": "Cansada, discreta, guarda segredos.",
         "tipo": "suspeito", "culpado": False,
         "abertura": "Servi ao Sr. Figueredo por quinze anos. Vi coisas que não devia.",
         "topicos": {
            "alibi": {"gatilhos": ["onde estava", "alibi", "noite", "21", "trancou"],
                      "respostas": ["Tranquei tudo às nove e fui embora. Ele ficou.",
                                    "Eu não aguentava mais aquele homem, mas não o matei."]},
            "abuso": {"gatilhos": ["denuncia", "abuso", "encobriu", "poder", "chantagem", "dossie"],
                      "sensivel": True, "revela": "denuncias",
                      "respostas": ["Ele arquivava denúncias contra os poderosos. Chamava "
                                    "isso de 'proteger a obra'.",
                                    "Tinha um dossiê para controlar quem ousasse falar."]},
            "dossie": {"gatilhos": ["guardou", "copia", "escondeu", "prova", "segredo"],
                       "sensivel": True, "revela": "dossie_irene",
                       "respostas": ["Eu peguei uma coisa, com medo...",
                                     "Guardei o dossiê dele. É a prova de tudo o que ele fazia."]},
            "daniel": {"gatilhos": ["daniel", "diacono", "visita", "quem", "familia"],
                       "respostas": ["O diácono Daniel brigou feio com ele. A família do "
                                     "Daniel foi destruída por uma denúncia engavetada."]},
         },
         "genericas": ["Já contei o que vi.", "Que Deus me perdoe o silêncio."],
         "confissao": None},

        {"id": "paulo", "nome": "Paulo Crê",
         "papel": "Doador influente da instituição", "retrato": "Arrogante, impaciente.",
         "tipo": "suspeito", "culpado": False,
         "abertura": "Sou um benfeitor, não um suspeito. Sejam rápidos.",
         "topicos": {
            "alibi": {"gatilhos": ["onde estava", "alibi", "noite", "22"],
                      "respostas": ["Em um jantar de gala. Cem pessoas me viram."]},
            "denuncia": {"gatilhos": ["denuncia", "encobriu", "protegeu", "favor"],
                         "sensivel": True,
                         "respostas": ["Samuel me devia favores, não o contrário.",
                                       "Sim, ele engavetou uma denúncia que me citava. E daí?"]},
            "motivo": {"gatilhos": ["motivo", "dinheiro", "poder", "por que"],
                       "respostas": ["Eu financiava o homem. Morto, ele não me serve. "
                                     "Por que eu o mataria?"]},
         },
         "genericas": ["Falem com meus advogados.", "Isto é perda de tempo."],
         "confissao": None},

        {"id": "daniel", "nome": "Daniel Mares",
         "papel": "Diácono · antigo aliado de Samuel",
         "retrato": "Contido, voz baixa, olhar de quem carrega um luto.",
         "tipo": "suspeito", "culpado": True,
         "abertura": "Eu servi ao lado dele por anos. É triste o que aconteceu.",
         "topicos": {
            "alibi": {"gatilhos": ["onde estava", "alibi", "noite", "22", "sala", "entrou"],
                      "sensivel": True,
                      "respostas": ["Estava em casa, orando. Sozinho.",
                                    "A porta lateral? Eu tinha a chave, mas não entrei.",
                                    "Já respondi. Deixe minha família fora disso."]},
            "familia": {"gatilhos": ["familia", "denuncia", "filho", "vinganca", "destruiu"],
                        "sensivel": True, "revela": "denuncias",
                        "respostas": ["Ele engavetou a denúncia que teria salvado meu filho.",
                                      "Chamou de 'sacrifício pela obra'. Chamei de covardia.",
                                      "Perdi tudo. E ele dormia tranquilo."]},
            "documentos": {"gatilhos": ["documento", "dossie", "arquivo", "reorganizou", "procurou"],
                           "sensivel": True,
                           "respostas": ["Não mexi nos papéis dele.",
                                         "Se alguém remexeu naquilo, procurava se livrar de "
                                         "um segredo. Não fui eu."]},
         },
         "genericas": ["Deus conhece meu coração.", "Não tenho mais o que dizer."],
         "confissao": ("Sim. O dossiê, o livro de visitas, a mensagem que mandei. Ele "
                       "destruiu a minha família e dormia como um justo. Fui cobrar o "
                       "que ele tirou de nós. Ele riu e disse que eu era pó diante da "
                       "'obra'. Eu o golpeei. Depois procurei o dossiê que ele usava "
                       "contra mim e troquei a página do livro. Que Deus me julgue.")},

        _perita("Perita Sofia Mendes",
                "A sala estava arrumada demais para uma cena de crime. Pergunte.",
                {
                    "documentos": {"gatilhos": ["documento", "arquivo", "reorganiz", "ordem", "remexido"],
                                   "revela": "documentos_reorg",
                                   "resposta": ("Os arquivos foram reorganizados com método, "
                                                "não revirados. Quem matou procurava algo "
                                                "específico — ou plantava.")},
                    "entrada": {"gatilhos": ["entrada", "porta", "visita", "livro", "registro"],
                                "revela": "registro_visitas",
                                "resposta": ("A porta lateral foi usada. E há uma página "
                                             "trocada no livro de visitas — a original diz "
                                             "quem esteve com ele por último.")},
                    "golpe": {"gatilhos": ["golpe", "ferimento", "morte", "arma", "corpo"],
                              "resposta": ("Um golpe único, preciso, na nuca. Sem hesitação. "
                                           "A causa fica com o legista.")},
                }),

        _kael("Examinei Samuel. Um caso limpo, à primeira vista. Pergunte.",
              {
                  "causa": {"gatilhos": ["causa", "morte", "golpe", "laudo", "ferimento"],
                            "revela": "causa_morte",
                            "resposta": ("Golpe único na nuca, sem sinais de luta. Eu "
                                         "trataria a cena reorganizada como preliminar — não "
                                         "a elevaria a prova ainda.")},
                  "programa": {"gatilhos": ["programa", "codigo", "assistencia", "medico", "registro", "participantes"],
                               "revela": "programa_medico",
                               "resposta": ("Há referências a um programa de assistência "
                                            "médica com participantes sob códigos. Papelada "
                                            "antiga do departamento, imagino. Nada deste caso.")},
                  "quem": {"gatilhos": ["quem", "suspeito", "culpado", "matou"],
                           "resposta": ("Alguém com acesso e rancor. Eu não me fixaria no "
                                        "benfeitor óbvio.")},
              }),
    ],
}


# ===========================================================================
# CASO 005 - A CHAVE DO QUARTO 17  (Lívia Montenegro — Adultério e Traição)
# ===========================================================================
CASOS["005"] = {
    "id": "005",
    "titulo": "A CHAVE DO QUARTO 17",
    "etapa": 2,
    "objetivo": "Reconstruir a noite de Lívia entre versões incompatíveis e acessos suspeitos.",
    "mecanica": "Cruzar horários de acesso com depoimentos que não batem.",
    "pergunta_trama": "Por que o cartão do quarto foi encontrado em outro andar?",
    "introducao": ("Lívia Montenegro, advogada, morre após um encontro em um hotel. "
                   "Seu telefone desaparece, mas o cartão de acesso ao quarto 17 é "
                   "encontrado em outro andar."),
    "vitima": {
        "nome": "Lívia Montenegro", "idade": 34,
        "ocupacao": "Advogada de disputas patrimoniais",
        "citacao": "Informação é a única moeda que nunca desvaloriza.",
        "biografia": ("Mantinha um caso com um cliente e usava informações sigilosas "
                      "do próprio escritório para favorecer seus interesses. A traição "
                      "não era só amorosa: entregou documentos privados de quem confiava nela."),
        "local": "Hotel — Quarto 17", "data": "20 de dezembro",
        "hora": "01h10", "estado": "Homicídio suspeito", "indice_serie": 4,
    },
    "evidencias": [
        {"id": "cartao", "nome": "Cartão de acesso em outro andar",
         "descricao": ("O cartão do quarto 17 foi achado no 9º andar. Sugere que "
                       "alguém saiu por outro caminho — ou plantou o cartão para "
                       "confundir. Pista enganosa sobre a rota de fuga."),
         "confiavel": False},
        {"id": "telefone", "nome": "Telefone desaparecido",
         "descricao": ("O celular de Lívia sumiu. Nele estariam as mensagens com o "
                       "amante e os documentos que ela usava como barganha.")},
        {"id": "causa_morte", "nome": "Laudo de Kael",
         "descricao": ("Kael: asfixia, horário entre 00h30 e 01h30. Oferece uma "
                       "explicação técnica para a divergência de horário dos acessos "
                       "— explicação ainda não confirmada por fonte independente.")},
        {"id": "caso_cliente", "nome": "Caso com o cliente",
         "descricao": ("Lívia mantinha um relacionamento com o cliente Rafael e "
                       "vazava informações do escritório para favorecê-lo.")},
        {"id": "log_acessos", "nome": "Log real de acessos do quarto",
         "descricao": ("O log eletrônico da fechadura mostra quem entrou e saiu do "
                       "quarto 17 — e contradiz o depoimento de um dos envolvidos."),
         "chave_prova": True},
        {"id": "documentos_vazados", "nome": "Documentos sigilosos vazados",
         "descricao": ("Prova de que Lívia entregou documentos confidenciais de uma "
                       "cliente, Teresa, traindo seu sigilo profissional."),
         "chave_prova": True},
        {"id": "mensagem_rafael", "nome": "Mensagem autenticada de Rafael",
         "descricao": ("Comunicação autenticada em que Rafael exige que Lívia "
                       "'apague tudo' e marca de subir ao quarto naquela madrugada."),
         "chave_prova": True, "bloqueada": True},
    ],
    "provas_chave": ["log_acessos", "documentos_vazados", "mensagem_rafael"],
    "linha_tempo": [
        {"hora": "23h40", "titulo": "Lívia sobe ao quarto 17",
         "descricao": "Recepção confirma a entrada dela, sozinha.",
         "tipo": "registro", "fonte": "Recepção do hotel"},
        {"hora": "00h20", "titulo": "Visita ao quarto",
         "descricao": "Rafael diz ter ido 'só até o saguão'. O log diz outra coisa.",
         "tipo": "depoimento", "fonte": "Depoimento — Rafael Dantas"},
        {"hora": "01h10", "titulo": "Horário estimado da morte",
         "descricao": "Asfixia, segundo o legista. Telefone já havia sumido.",
         "tipo": "evidencia", "fonte": "Perícia / Kael"},
        {"hora": "01h25", "titulo": "Cartão achado no 9º andar",
         "descricao": "O cartão do quarto 17 aparece longe do quarto. Rota confusa.",
         "tipo": "evidencia", "fonte": "Perícia"},
    ],
    "hipoteses": [
        {"id": "h1", "texto": "Rafael matou Lívia para apagar o vazamento que o beneficiava.", "status": "em_analise"},
        {"id": "h2", "texto": "Assalto no hotel — por isso o telefone sumiu.", "status": "baixa"},
        {"id": "h3", "texto": "Teresa, a cliente traída, se vingou.", "status": "baixa"},
        {"id": "h4", "texto": "A consulta médica fora do protocolo liga ao fio maior.", "status": "em_analise"},
    ],
    "provas_para_confronto": ["log_acessos", "documentos_vazados"],
    "acusaveis": ["rafael", "teresa", "marcos"],
    "culpado": "rafael",
    "solucao": {
        "culpado_nome": "Rafael Dantas",
        "resumo": ("Rafael era o cliente-amante que se beneficiava dos documentos que "
                   "Lívia vazava. Quando ela quis encerrar o caso e se proteger, ele "
                   "temeu ser exposto. Subiu ao quarto 17, asfixiou Lívia, levou o "
                   "telefone com as provas e deixou o cartão em outro andar para forjar "
                   "uma rota de fuga falsa."),
        "veredito": ("O log de acessos (que o coloca no quarto), os documentos vazados "
                     "em favor dele e a mensagem autenticada exigindo apagar tudo fecham "
                     "motivo, presença e intenção."),
        "gancho": ("Uma mensagem apagada menciona uma consulta médica feita fora do "
                   "protocolo do departamento. E Kael 'explicou' a divergência de "
                   "horário sem que ninguém confirmasse."),
    },
    "personagens": [
        {"id": "teresa", "nome": "Teresa Lund",
         "papel": "Cliente de Lívia", "retrato": "Ferida, direta, não esconde a mágoa.",
         "tipo": "suspeito", "culpado": False,
         "abertura": "Ela traiu meu sigilo. Mas eu queria justiça, não a morte dela.",
         "topicos": {
            "alibi": {"gatilhos": ["onde estava", "alibi", "noite", "hotel", "01"],
                      "respostas": ["Em casa, com meus filhos. A babá confirma."]},
            "traicao": {"gatilhos": ["documento", "sigilo", "vazou", "traiu", "confianca"],
                        "sensivel": True, "revela": "documentos_vazados",
                        "respostas": ["Ela entregou meus documentos privados a terceiros.",
                                      "Eu tenho cópias do que ela vazou. É prova da traição dela."]},
            "rafael": {"gatilhos": ["rafael", "cliente", "amante", "quem"],
                       "respostas": ["O cliente dela, Rafael, era o verdadeiro beneficiado. "
                                     "Ela vazava para ele."]},
         },
         "genericas": ["Eu queria vê-la na cadeia, não morta.", "Procurem o amante."],
         "confissao": None},

        {"id": "marcos", "nome": "Marcos Viana",
         "papel": "Sócio do escritório de Lívia", "retrato": "Formal, preocupado com a firma.",
         "tipo": "suspeito", "culpado": False,
         "abertura": "A morte da Lívia é uma tragédia e um escândalo para a firma.",
         "topicos": {
            "alibi": {"gatilhos": ["onde estava", "alibi", "noite", "01"],
                      "respostas": ["Em casa, dormindo. Acordei com a ligação da polícia."]},
            "escritorio": {"gatilhos": ["escritorio", "documento", "sigilo", "vazamento", "firma"],
                           "revela": "caso_cliente",
                           "respostas": ["Suspeitávamos que ela vazava informação. Faltavam "
                                         "documentos. Ela tinha um caso com um cliente, o Rafael."]},
            "log": {"gatilhos": ["log", "acesso", "cartao", "quarto", "fechadura"],
                    "respostas": ["Hotéis guardam o log eletrônico da fechadura. Peçam. "
                                  "Diz mais que qualquer álibi."]},
         },
         "genericas": ["A firma colabora totalmente.", "Falem com a recepção do hotel."],
         "confissao": None},

        {"id": "rafael", "nome": "Rafael Dantas",
         "papel": "Cliente e amante de Lívia", "retrato": "Charmoso, calculista, controla o tom.",
         "tipo": "suspeito", "culpado": True,
         "abertura": "Lívia era minha advogada e minha amiga. Estou arrasado.",
         "topicos": {
            "alibi": {"gatilhos": ["onde estava", "alibi", "noite", "quarto", "saguao", "00", "01"],
                      "sensivel": True,
                      "respostas": ["Fui só até o saguão do hotel. Não subi.",
                                    "O log? Deve ter erro. Eu não entrei no quarto.",
                                    "Já disse onde estava. Pare."]},
            "documentos": {"gatilhos": ["documento", "vazou", "beneficio", "processo", "informacao"],
                           "sensivel": True, "revela": "documentos_vazados",
                           "respostas": ["Ela me passava orientações, como qualquer advogada.",
                                         "Se havia documento de terceiros, a responsável era ela.",
                                         "Eu não pedi nada ilegal."]},
            "telefone": {"gatilhos": ["telefone", "celular", "mensagem", "apagar", "sumiu"],
                         "sensivel": True,
                         "respostas": ["Não sei do telefone dela.",
                                       "Por que eu levaria o celular dela?"]},
         },
         "genericas": ["Isso é calúnia.", "Meu advogado vai adorar isso."],
         "confissao": ("Chega. O log, os documentos, a mensagem. Ela ia encerrar tudo e "
                       "se blindar — e eu ficaria com o rastro do vazamento que me "
                       "favoreceu. Subi ao quarto para convencê-la a apagar as provas. "
                       "Ela recusou. Quando percebi, ela não respirava. Levei o telefone "
                       "e larguei o cartão longe para confundir a rota.")},

        _perita("Perita Sofia Mendes",
                "O hotel guarda mais do que parece. O cartão foi o que me intrigou.",
                {
                    "cartao": {"gatilhos": ["cartao", "andar", "quarto", "rota", "fuga"],
                               "revela": "cartao",
                               "resposta": ("O cartão do quarto 17 apareceu no 9º andar. Ou "
                                            "alguém fugiu por outro caminho, ou plantou o "
                                            "cartão para despistar.")},
                    "telefone": {"gatilhos": ["telefone", "celular", "sumiu", "levou", "objeto"],
                                 "revela": "telefone",
                                 "resposta": ("O celular dela desapareceu. Quem matou levou "
                                              "justamente o que tinha as mensagens e os documentos.")},
                    "log": {"gatilhos": ["log", "acesso", "fechadura", "entrou", "horario"],
                            "revela": "log_acessos",
                            "resposta": ("A fechadura eletrônica guarda cada entrada. O log "
                                         "real contradiz um dos depoimentos. Confira os horários.")},
                }),

        _kael("Asfixia, novamente. Posso situar o horário e esclarecer a cronologia.",
              {
                  "causa": {"gatilhos": ["causa", "morte", "asfixia", "laudo", "horario", "hora"],
                            "revela": "causa_morte",
                            "resposta": ("Asfixia, entre 00h30 e 01h30. Sobre a divergência "
                                         "dos acessos: há uma explicação técnica simples de "
                                         "defasagem do relógio da fechadura. Eu aceitaria isso.")},
                  "consulta": {"gatilhos": ["consulta", "medica", "protocolo", "departamento", "mensagem apagada"],
                               "resposta": ("Dizem haver uma mensagem sobre uma consulta médica "
                                            "fora do protocolo. Fofoca, provavelmente. Não "
                                            "misturaria isso ao caso.")},
                  "quem": {"gatilhos": ["quem", "culpado", "suspeito", "matou"],
                           "resposta": ("Comece pelo log da fechadura. Ele mente menos que "
                                        "as pessoas.")},
              }),
    ],
}


# ===========================================================================
# CASO 006 - O SANTO DE FACHADA  (Vicente Alencar — Hipocrisia)
# ===========================================================================
CASOS["006"] = {
    "id": "006",
    "titulo": "O SANTO DE FACHADA",
    "etapa": 2,
    "objetivo": "Separar a imagem pública de Vicente dos atos que ela escondia.",
    "mecanica": "Reputação deixa de ser prova de caráter; confronte para liberar fatos.",
    "pergunta_trama": "Quem autorizou despesas assinadas só por iniciais de um cargo médico?",
    "introducao": ("Vicente Alencar, diretor de uma ONG de apoio a vítimas de "
                   "violência, foi encontrado morto na sala de arquivos da própria "
                   "organização. As câmeras ficaram sem gravação num intervalo específico."),
    "vitima": {
        "nome": "Vicente Alencar", "idade": 47,
        "ocupacao": "Diretor de ONG de apoio a vítimas",
        "citacao": "A compaixão é o melhor dos palcos.",
        "biografia": ("Construía imagem pública de compaixão enquanto desviava "
                      "doações e intimidava funcionários que conheciam suas práticas. "
                      "Discursava sobre justiça usando o sofrimento alheio para obter "
                      "prestígio e influência."),
        "local": "Sala de arquivos da ONG", "data": "08 de janeiro",
        "hora": "09h00", "estado": "Homicídio suspeito", "indice_serie": 5,
    },
    "evidencias": [
        {"id": "cameras", "nome": "Câmeras sem gravação",
         "descricao": ("As câmeras ficaram offline exatamente no intervalo do crime. "
                       "Sugere invasor técnico — ou alguém de dentro que sabia desligá-las. "
                       "Pista enganosa sobre quem teve a oportunidade."),
         "confiavel": False},
        {"id": "desvios", "nome": "Desvio de doações",
         "descricao": ("Doações destinadas a vítimas eram desviadas por Vicente, que "
                       "intimidava quem percebia as contas erradas.")},
        {"id": "causa_morte", "nome": "Laudo de Kael",
         "descricao": ("Kael: ferimento perfurante, morte rápida. Pede que o relatório "
                       "financeiro encontrado seja tratado como 'preliminar' até "
                       "verificação institucional.")},
        {"id": "relatorio_iniciais", "nome": "Relatório com iniciais de cargo médico",
         "descricao": ("Um relatório financeiro cita despesas extraordinárias "
                       "autorizadas por alguém identificado apenas pelas INICIAIS de um "
                       "cargo médico. Um fio que atravessa os casos.")},
        {"id": "planilha_sonia", "nome": "Planilha guardada por Sônia",
         "descricao": ("Sônia, contadora, guardou a planilha real dos desvios — nomes, "
                       "valores e destinos das doações sumidas."), "chave_prova": True},
        {"id": "gravacao_recuperada", "nome": "Trecho de câmera recuperado",
         "descricao": ("A perícia recuperou segundos antes do blecaute: mostram quem "
                       "entrou na sala de arquivos pouco antes da morte."),
         "chave_prova": True},
        {"id": "bilhete_gustavo", "nome": "Bilhete autenticado de Gustavo",
         "descricao": ("Mensagem autenticada em que o voluntário Gustavo promete "
                       "'acabar com a farsa hoje à noite' e marca de ir à ONG."),
         "chave_prova": True, "bloqueada": True},
    ],
    "provas_chave": ["planilha_sonia", "gravacao_recuperada", "bilhete_gustavo"],
    "linha_tempo": [
        {"hora": "20h00", "titulo": "Equipe vai embora",
         "descricao": "Sônia afirma ter saído com os demais funcionários.",
         "tipo": "depoimento", "fonte": "Depoimento — Sônia Vaz"},
        {"hora": "21h12", "titulo": "Câmeras ficam offline",
         "descricao": "Blecaute das câmeras por 20 minutos. Intervalo preciso.",
         "tipo": "evidencia", "fonte": "Perícia"},
        {"hora": "21h20", "titulo": "Alguém na sala de arquivos",
         "descricao": "Gustavo diz que 'nem chegou a entrar'. O trecho recuperado discorda.",
         "tipo": "depoimento", "fonte": "Depoimentos conflitantes"},
        {"hora": "09h00", "titulo": "Corpo encontrado",
         "descricao": "A faxina encontra Vicente entre as caixas de arquivo.",
         "tipo": "registro", "fonte": "Boletim de ocorrência"},
    ],
    "hipoteses": [
        {"id": "h1", "texto": "Gustavo matou Vicente para expor e punir a farsa.", "status": "em_analise"},
        {"id": "h2", "texto": "Arrombamento externo durante o blecaute das câmeras.", "status": "baixa"},
        {"id": "h3", "texto": "Sônia silenciou o chefe que a ameaçava.", "status": "baixa"},
        {"id": "h4", "texto": "As iniciais de cargo médico conectam ao fio maior.", "status": "em_analise"},
    ],
    "provas_para_confronto": ["planilha_sonia", "gravacao_recuperada"],
    "acusaveis": ["gustavo", "sonia", "clovis"],
    "culpado": "gustavo",
    "solucao": {
        "culpado_nome": "Gustavo Henes",
        "resumo": ("Voluntário idealista, Gustavo descobriu que Vicente desviava as "
                   "doações destinadas às vítimas que a ONG dizia ajudar. Humilhado e "
                   "ameaçado ao tentar denunciar, foi à sede, aproveitou o blecaute das "
                   "câmeras (que ele sabia programar) e golpeou Vicente na sala de "
                   "arquivos, procurando as provas do desvio."),
        "veredito": ("A planilha de Sônia, o trecho de câmera recuperado e o bilhete "
                     "autenticado de Gustavo reúnem o motivo, a presença na cena e a "
                     "intenção declarada."),
        "gancho": ("O relatório aponta despesas autorizadas pelas iniciais de um cargo "
                   "médico. E Kael, de novo, pediu para tratar a prova como 'preliminar'."),
    },
    "personagens": [
        {"id": "sonia", "nome": "Sônia Vaz",
         "papel": "Contadora da ONG", "retrato": "Meticulosa, assustada com números.",
         "tipo": "suspeito", "culpado": False,
         "abertura": "Eu cuidava das contas. E as contas não fechavam, detetive.",
         "topicos": {
            "alibi": {"gatilhos": ["onde estava", "alibi", "noite", "20", "saiu"],
                      "respostas": ["Saí às oito com o pessoal. Fui para casa."]},
            "desvio": {"gatilhos": ["doacao", "desvio", "conta", "dinheiro", "financeiro"],
                       "sensivel": True, "revela": "desvios",
                       "respostas": ["As doações entravam e sumiam. Ele dizia que era "
                                     "'remanejamento'.",
                                     "Quem reclamava, ele intimidava. Eu tinha medo."]},
            "planilha": {"gatilhos": ["planilha", "guardou", "prova", "copia", "escondeu"],
                         "sensivel": True, "revela": "planilha_sonia",
                         "respostas": ["Eu guardei uma coisa...",
                                       "A planilha real dos desvios. Nomes, valores, destinos. "
                                       "É a prova que ele mandava eu apagar."]},
            "gustavo": {"gatilhos": ["gustavo", "voluntario", "quem", "ameaca"],
                        "respostas": ["O Gustavo descobriu tudo. Vicente o humilhou na "
                                      "frente de todos. O rapaz saiu transtornado."]},
         },
         "genericas": ["Os números não mentem, detetive.", "Eu só queria um emprego honesto."],
         "confissao": None},

        {"id": "clovis", "nome": "Clóvis Pena",
         "papel": "Presidente do conselho da ONG", "retrato": "Suave, protege a imagem da casa.",
         "tipo": "suspeito", "culpado": False,
         "abertura": "Vicente era o rosto da nossa missão. Uma perda irreparável.",
         "topicos": {
            "alibi": {"gatilhos": ["onde estava", "alibi", "noite", "21"],
                      "respostas": ["Num evento beneficente, cercado de gente."]},
            "reputacao": {"gatilhos": ["imagem", "reputacao", "doacao", "desvio", "escandalo"],
                          "sensivel": True,
                          "respostas": ["Rumores de desvio? Nunca comprovados.",
                                        "Preservar a ONG não é crime. Vítimas dependem dela."]},
            "cameras": {"gatilhos": ["camera", "gravacao", "seguranca", "blecaute"],
                        "revela": "cameras",
                        "respostas": ["As câmeras falharam justo naquele intervalo. "
                                      "Suspeito, eu sei. Só os funcionários sabiam reiniciá-las."]},
         },
         "genericas": ["A ONG colabora com tudo.", "Não arrastem nosso nome à lama."],
         "confissao": None},

        {"id": "gustavo", "nome": "Gustavo Henes",
         "papel": "Voluntário da ONG", "retrato": "Jovem, inflamado, mãos inquietas.",
         "tipo": "suspeito", "culpado": True,
         "abertura": "Eu entrei para ajudar vítimas. Descobri que o ajudado era ele.",
         "topicos": {
            "alibi": {"gatilhos": ["onde estava", "alibi", "noite", "21", "arquivo", "entrou"],
                      "sensivel": True,
                      "respostas": ["Passei na ONG, mas nem entrei na sala de arquivos.",
                                    "A câmera estava desligada? Então não há o que ver.",
                                    "Já respondi. Deixe-me em paz."]},
            "desvio": {"gatilhos": ["doacao", "desvio", "farsa", "descobriu", "denuncia"],
                       "sensivel": True, "revela": "desvios",
                       "respostas": ["Ele roubava das vítimas. Eu vi as contas.",
                                     "Tentei denunciar. Ele me humilhou e ameaçou acabar comigo.",
                                     "Aquele homem era uma fraude sagrada."]},
            "cameras": {"gatilhos": ["camera", "blecaute", "desligou", "gravacao", "seguranca"],
                        "sensivel": True,
                        "respostas": ["Eu ajudava na parte técnica, sim.",
                                      "Saber reiniciar as câmeras não faz de mim assassino."]},
         },
         "genericas": ["Ele merecia ser exposto, não isso.", "Vocês deviam prender os ladrões."],
         "confissao": ("Sim. A planilha, o vídeo, o bilhete que mandei. Ele roubava de "
                       "quem não tinha nada e me chamou de louco quando o enfrentei. "
                       "Desliguei as câmeras — eu sabia como — e fui cobrar as provas. "
                       "Ele riu na minha cara. Eu não aguentei. Só queria que a farsa "
                       "acabasse. Acabou do pior jeito.")},

        _perita("Perita Sofia Mendes",
                "O blecaute das câmeras foi cirúrgico demais. Pergunte.",
                {
                    "cameras": {"gatilhos": ["camera", "gravacao", "blecaute", "seguranca", "offline"],
                                "revela": "cameras",
                                "resposta": ("As câmeras caíram só no intervalo do crime. "
                                             "Quem fez isso sabia o sistema — ou era de dentro.")},
                    "recuperacao": {"gatilhos": ["recuperar", "trecho", "video", "antes", "imagem"],
                                    "revela": "gravacao_recuperada",
                                    "resposta": ("Recuperei segundos antes do blecaute. Mostram "
                                                 "quem entrou na sala de arquivos. Vale ouro.")},
                    "ferimento": {"gatilhos": ["ferimento", "golpe", "morte", "arma", "corpo"],
                                  "resposta": ("Ferimento perfurante, morte rápida. A causa "
                                               "exata é com o legista.")},
                }),

        _kael("Vicente teve morte rápida. Posso detalhar — e sugerir cautela com os papéis.",
              {
                  "causa": {"gatilhos": ["causa", "morte", "ferimento", "laudo", "golpe"],
                            "revela": "causa_morte",
                            "resposta": ("Ferimento perfurante único. Trataria o relatório "
                                         "financeiro achado como preliminar até verificação — "
                                         "não o elevaria a prova ainda.")},
                  "relatorio": {"gatilhos": ["relatorio", "iniciais", "cargo", "medico", "despesa", "autorizou"],
                                "revela": "relatorio_iniciais",
                                "resposta": ("Há despesas autorizadas por iniciais de um cargo "
                                             "médico. Formato burocrático comum. Eu não me "
                                             "prenderia a essas iniciais.")},
                  "quem": {"gatilhos": ["quem", "culpado", "suspeito", "matou"],
                           "resposta": ("Comece pela gravação recuperada. Imagens enganam "
                                        "menos que reputações.")},
              }),
    ],
}


# ===========================================================================
# CASO 007 - O PESO DA OMISSÃO  (Matheus Silva — Omissão)
# ===========================================================================
CASOS["007"] = {
    "id": "007",
    "titulo": "O PESO DA OMISSÃO",
    "etapa": 3,
    "objetivo": "Descobrir o que Matheus deixou de registrar — e por quê.",
    "mecanica": "A ausência de um registro vale tanto quanto um registro.",
    "pergunta_trama": "Como Kael sabia de uma ficha de custódia que não estava no briefing?",
    "introducao": ("Matheus Silva, ex-policial, desaparece antes de depor sobre um "
                   "caso antigo. Seus pertences são achados num depósito que deveria "
                   "estar interditado."),
    "vitima": {
        "nome": "Matheus Silva", "idade": 42,
        "ocupacao": "Ex-policial (saiu após investigação disciplinar)",
        "citacao": "Às vezes o silêncio é a única coisa que ainda se pode controlar.",
        "biografia": ("Presenciou uma agressão de um colega e não denunciou. Depois "
                      "omitiu informações de uma investigação que inocentaria um "
                      "suspeito, convencido de que o silêncio evitaria um mal maior — "
                      "mas condenou um inocente."),
        "local": "Depósito interditado", "data": "22 de janeiro",
        "hora": "Indeterminada", "estado": "Desaparecimento / homicídio suspeito",
        "indice_serie": 6,
    },
    "evidencias": [
        {"id": "pertences", "nome": "Pertences num depósito interditado",
         "descricao": ("As coisas de Matheus apareceram num depósito oficialmente "
                       "fechado. Sugere ocultação planejada — mas o local aponta para "
                       "alguém com acesso institucional, não um estranho."),
         "confiavel": False},
        {"id": "ficha_custodia", "nome": "Ficha de custódia assinada por Matheus",
         "descricao": ("Uma ficha assinada por Matheus registra o recebimento de "
                       "material médico que NÃO aparece no inventário oficial. O que "
                       "ele recebeu — e omitiu — é a chave.")},
        {"id": "causa_morte", "nome": "Parecer de Kael (sem corpo)",
         "descricao": ("Sem corpo, Kael opina que é 'provável sumiço voluntário'. "
                       "Curiosamente, cita a ficha de custódia ANTES de ela constar no "
                       "briefing — como ele sabia?")},
        {"id": "caso_antigo", "nome": "Investigação antiga encoberta",
         "descricao": ("O depoimento que Matheus daria reabriria um caso em que sua "
                       "omissão condenou um inocente. Alguém não queria isso reaberto.")},
        {"id": "material_medico", "nome": "Material médico fora do inventário",
         "descricao": ("O material recebido por Matheus era de origem médica e "
                       "desapareceu dos registros oficiais. Rastro do programa com códigos."),
         "chave_prova": True},
        {"id": "gravacao_matheus", "nome": "Gravação deixada por Matheus",
         "descricao": ("Matheus deixou um áudio contando o que vira: quem o pressionou "
                       "a omitir e manejar o material médico."), "chave_prova": True},
        {"id": "ordem_bastos", "nome": "Ordem autenticada de Bastos",
         "descricao": ("Comunicação autenticada do delegado Bastos ordenando a Matheus "
                       "'fazer o material sumir' e marcando um encontro no depósito."),
         "chave_prova": True, "bloqueada": True},
    ],
    "provas_chave": ["material_medico", "gravacao_matheus", "ordem_bastos"],
    "linha_tempo": [
        {"hora": "—", "titulo": "Depoimento marcado",
         "descricao": "Matheus confirma que vai depor sobre o caso antigo.",
         "tipo": "registro", "fonte": "Intimação"},
        {"hora": "—", "titulo": "Último contato",
         "descricao": "Rita, ex-colega, recebe uma mensagem estranha dele e some o rastro.",
         "tipo": "depoimento", "fonte": "Depoimento — Rita Cunha"},
        {"hora": "—", "titulo": "Pertences no depósito",
         "descricao": "Encontrados num depósito interditado — local de acesso restrito.",
         "tipo": "evidencia", "fonte": "Perícia"},
        {"hora": "—", "titulo": "Kael cita a ficha",
         "descricao": "O legista menciona a ficha de custódia que não estava no briefing.",
         "tipo": "contradicao", "fonte": "Observação do investigador"},
    ],
    "hipoteses": [
        {"id": "h1", "texto": "Bastos silenciou Matheus para manter a omissão enterrada.", "status": "em_analise"},
        {"id": "h2", "texto": "Matheus fugiu por medo de ser responsabilizado.", "status": "baixa"},
        {"id": "h3", "texto": "Rita o eliminou para proteger o passado dos dois.", "status": "baixa"},
        {"id": "h4", "texto": "Kael conhece a ficha de custódia — como?", "status": "em_analise"},
    ],
    "provas_para_confronto": ["material_medico", "gravacao_matheus"],
    "acusaveis": ["bastos", "rita", "nilo"],
    "culpado": "bastos",
    "solucao": {
        "culpado_nome": "Delegado Bastos",
        "resumo": ("Bastos foi quem pressionou Matheus, anos atrás, a omitir e a "
                   "manejar material médico ligado a um programa clandestino. Quando "
                   "Matheus decidiu depor e revelar tudo, Bastos — com acesso ao "
                   "depósito interditado — marcou um encontro, silenciou-o e ocultou "
                   "os pertences para simular sumiço voluntário."),
        "veredito": ("O material médico fora do inventário, a gravação de Matheus e a "
                     "ordem autenticada de Bastos ligam o passado encoberto ao crime atual."),
        "gancho": ("O material era médico, de um programa com códigos — e o Dr. Kael "
                   "conhecia a ficha de custódia antes de ela aparecer no briefing. A "
                   "pergunta deixou de ser só 'quem matou'."),
    },
    "personagens": [
        {"id": "rita", "nome": "Rita Cunha",
         "papel": "Ex-colega de corporação de Matheus", "retrato": "Dura, leal ao antigo parceiro.",
         "tipo": "suspeito", "culpado": False,
         "abertura": "O Matheus era meu parceiro. Se sumiu, foi porque o acuaram.",
         "topicos": {
            "alibi": {"gatilhos": ["onde estava", "alibi", "noite", "deposito"],
                      "respostas": ["De plantão, com a equipe. Há registro."]},
            "omissao": {"gatilhos": ["omissao", "caso antigo", "depoimento", "silencio", "inocente"],
                        "sensivel": True, "revela": "caso_antigo",
                        "respostas": ["Ele carregava uma culpa antiga. Omitiu algo que "
                                      "condenou um inocente.",
                                      "Ia depor para limpar a consciência. Alguém temia isso."]},
            "gravacao": {"gatilhos": ["gravacao", "audio", "deixou", "mensagem", "prova"],
                         "sensivel": True, "revela": "gravacao_matheus",
                         "respostas": ["Ele me mandou um áudio, por garantia.",
                                       "Está aqui. Ele conta quem o mandou sumir com o material."]},
            "bastos": {"gatilhos": ["bastos", "delegado", "chefe", "pressao", "quem"],
                       "respostas": ["O delegado Bastos. Sempre foi ele quem apertava o Matheus."]},
         },
         "genericas": ["Achem meu parceiro.", "Não confio em quem está acima."],
         "confissao": None},

        {"id": "nilo", "nome": "Nilo Prado",
         "papel": "Almoxarife do depósito", "retrato": "Nervoso, evita o assunto do acesso.",
         "tipo": "suspeito", "culpado": False,
         "abertura": "O depósito está interditado faz meses. Eu só tenho a chave antiga.",
         "topicos": {
            "alibi": {"gatilhos": ["onde estava", "alibi", "noite", "deposito"],
                      "respostas": ["Em casa. Não ponho os pés lá desde a interdição."]},
            "acesso": {"gatilhos": ["acesso", "chave", "interditado", "entrou", "quem"],
                       "sensivel": True, "revela": "pertences",
                       "respostas": ["Só a corporação tem acesso ao depósito interditado.",
                                     "Eu vi o delegado pegar a chave reserva uma vez."]},
            "material": {"gatilhos": ["material", "medico", "inventario", "custodia", "ficha"],
                         "respostas": ["Entrava material que não constava no inventário. "
                                       "Eu só assinava o que mandavam."]},
         },
         "genericas": ["Eu só cumpro ordens.", "Não me metam nisso."],
         "confissao": None},

        {"id": "bastos", "nome": "Delegado Bastos",
         "papel": "Delegado · antigo superior de Matheus",
         "retrato": "Imponente, voz grave, trata o detetive de cima.",
         "tipo": "suspeito", "culpado": True,
         "abertura": "Matheus era problemático. Sumir combina com ele. Sejam objetivos.",
         "topicos": {
            "alibi": {"gatilhos": ["onde estava", "alibi", "noite", "deposito", "encontro"],
                      "sensivel": True,
                      "respostas": ["Eu estava na delegacia. Tenho subordinados que confirmam.",
                                    "No depósito? Não piso lá há meses.",
                                    "Cuidado com o tom, detetive."]},
            "omissao": {"gatilhos": ["omissao", "caso antigo", "pressao", "ordem", "material", "custodia"],
                        "sensivel": True, "revela": "caso_antigo",
                        "respostas": ["Aquele caso antigo foi encerrado. Legalmente.",
                                      "Eu nunca mandei ninguém omitir nada.",
                                      "A ficha de custódia dele? Rotina. Não sei do material."]},
            "material_medico": {"gatilhos": ["material", "medico", "inventario", "sumir", "programa"],
                                "sensivel": True,
                                "respostas": ["Não sei de material médico nenhum.",
                                              "Isso é invenção de um homem desesperado."]},
         },
         "genericas": ["Respeite a hierarquia.", "Essa conversa acabou."],
         "confissao": ("Chega. O material, a gravação, a minha ordem. Aquele programa "
                       "precisava de material e de silêncio, e o Matheus fornecia os "
                       "dois — até a consciência pesar. Quando ele decidiu depor, ia "
                       "arrastar tudo e todos. Marquei no depósito, onde só nós "
                       "entrávamos. Não me arrependo de proteger o que protegi. "
                       "Arrependo-me de ter deixado a gravação escapar.")},

        _perita("Perita Sofia Mendes",
                "Sem corpo, foquei no depósito e nos pertences. Pergunte.",
                {
                    "deposito": {"gatilhos": ["deposito", "pertences", "interditado", "acesso", "local"],
                                 "revela": "pertences",
                                 "resposta": ("Os pertences estavam num depósito interditado — "
                                              "acesso só da corporação. Não foi um estranho que "
                                              "escolheu esse esconderijo.")},
                    "ficha": {"gatilhos": ["ficha", "custodia", "material", "inventario", "assinatura"],
                              "revela": "material_medico",
                              "resposta": ("A ficha assinada por Matheus registra material "
                                           "médico que não aparece no inventário. O que ele "
                                           "recebeu simplesmente sumiu dos papéis.")},
                    "kael": {"gatilhos": ["kael", "legista", "briefing", "soube"],
                             "resposta": ("Uma coisa me incomoda: o Dr. Kael citou essa ficha "
                                          "antes de nós a incluirmos no briefing. Como ele sabia?")},
                }),

        _kael("Sem corpo, meu parecer é cauteloso. Mas há detalhes que reconheço.",
              {
                  "parecer": {"gatilhos": ["causa", "morte", "corpo", "parecer", "sumico", "fuga"],
                              "revela": "causa_morte",
                              "resposta": ("Sem corpo, eu trataria como sumiço voluntário. "
                                           "Aliás, a ficha de custódia dele já indicava alguém "
                                           "instável... — " 
                                           "e sim, sei da ficha; faz parte do meu ofício "
                                           "conhecer o que passa pelo departamento.")},
                  "material": {"gatilhos": ["material", "medico", "programa", "codigo", "custodia", "inventario"],
                               "revela": "material_medico",
                               "resposta": ("Material médico fora do inventário? Extravios "
                                            "acontecem. Eu não ligaria isso a uma conspiração.")},
                  "quem": {"gatilhos": ["quem", "culpado", "suspeito", "matou"],
                           "resposta": ("Fatos, detetive. Mas talvez esteja perguntando as "
                                        "coisas certas pela primeira vez.")},
              }),
    ],
}


# ===========================================================================
# CASO 008 - O PRONTUÁRIO PERDIDO  (Thomas Lima — Ressentimento e Vingança)
# ===========================================================================
CASOS["008"] = {
    "id": "008",
    "titulo": "O PRONTUÁRIO PERDIDO",
    "etapa": 3,
    "objetivo": "Rastrear o prontuário arrancado e a codificação que ele revela.",
    "mecanica": "Depoimentos entram em conflito com registros oficiais.",
    "pergunta_trama": "Como Kael reconhece de imediato uma codificação restrita de exames?",
    "introducao": ("Thomas Lima, cirurgião, é encontrado morto numa sala de descanso "
                   "de uma clínica desativada. Um prontuário foi arrancado de um "
                   "arquivo, deixando apenas a numeração de referência."),
    "vitima": {
        "nome": "Thomas Lima", "idade": 49,
        "ocupacao": "Cirurgião (hospitais conveniados ao departamento)",
        "citacao": "Quem controla o registro controla a história.",
        "biografia": ("Responsabilizava um antigo supervisor pelo fracasso da própria "
                      "carreira. Em vez de denunciar irregularidades pelas vias "
                      "corretas, manipulou prontuários e difamou um colega inocente "
                      "para se vingar."),
        "local": "Clínica desativada — sala de descanso", "data": "05 de fevereiro",
        "hora": "11h00", "estado": "Homicídio suspeito", "indice_serie": 7,
    },
    "evidencias": [
        {"id": "prontuario_arrancado", "nome": "Prontuário arrancado (só a numeração)",
         "descricao": ("Um prontuário foi arrancado do arquivo, restando apenas o "
                       "número de referência. Parece vingança pessoal — mas a "
                       "numeração aponta para algo maior. Pista que engana sobre o motivo."),
         "confiavel": False},
        {"id": "manipulacao", "nome": "Prontuários manipulados por Thomas",
         "descricao": ("Thomas adulterava prontuários para prejudicar um colega "
                       "inocente, Dr. Elvas, movido por ressentimento.")},
        {"id": "causa_morte", "nome": "Laudo de Kael",
         "descricao": ("Kael: intoxicação por fármaco de acesso restrito. Reconhece "
                       "de imediato a codificação do prontuário arrancado — um "
                       "conhecimento que, ele admite, 'poucos têm'.")},
        {"id": "codificacao", "nome": "Codificação restrita de exames post-mortem",
         "descricao": ("A numeração do prontuário usa um sistema de codificação "
                       "restrito a exames post-mortem do departamento. Thomas "
                       "reconheceu um padrão que deveria permanecer oculto.")},
        {"id": "copia_prontuario", "nome": "Cópia do prontuário (feita por Elvas)",
         "descricao": ("O Dr. Elvas, difamado por Thomas, guardou uma cópia do "
                       "prontuário arrancado — que revela o padrão de codificação."),
         "chave_prova": True},
        {"id": "registro_farmaco", "nome": "Registro de retirada do fármaco",
         "descricao": ("Um registro mostra quem retirou o fármaco de acesso restrito "
                       "usado no crime — e contradiz um álibi."), "chave_prova": True},
        {"id": "ameaca_vera", "nome": "Ameaça autenticada de Vera",
         "descricao": ("Mensagem autenticada da gestora Vera Luz exigindo que Thomas "
                       "'devolva e esqueça o que viu na numeração' antes que 'seja "
                       "tarde'."), "chave_prova": True, "bloqueada": True},
    ],
    "provas_chave": ["copia_prontuario", "registro_farmaco", "ameaca_vera"],
    "linha_tempo": [
        {"hora": "09h30", "titulo": "Thomas entra na clínica desativada",
         "descricao": "Zelador vê Thomas entrar sozinho, com uma pasta.",
         "tipo": "depoimento", "fonte": "Depoimento — zelador"},
        {"hora": "10h10", "titulo": "Fármaco restrito retirado",
         "descricao": "Registro de retirada do fármaco — assinatura contestada.",
         "tipo": "evidencia", "fonte": "Farmácia do departamento"},
        {"hora": "10h40", "titulo": "Prontuário arrancado",
         "descricao": "Resta só a numeração de referência no arquivo.",
         "tipo": "evidencia", "fonte": "Perícia"},
        {"hora": "11h00", "titulo": "Corpo encontrado",
         "descricao": "Thomas morto na sala de descanso.",
         "tipo": "registro", "fonte": "Boletim de ocorrência"},
    ],
    "hipoteses": [
        {"id": "h1", "texto": "Vera matou Thomas por causa do que a numeração revelava.", "status": "em_analise"},
        {"id": "h2", "texto": "Elvas se vingou do colega que o difamou.", "status": "baixa"},
        {"id": "h3", "texto": "Overdose acidental de automedicação.", "status": "baixa"},
        {"id": "h4", "texto": "A codificação restrita é a mesma dos casos anteriores.", "status": "em_analise"},
    ],
    "provas_para_confronto": ["copia_prontuario", "registro_farmaco"],
    "acusaveis": ["vera", "elvas", "bruno_sa"],
    "culpado": "vera",
    "solucao": {
        "culpado_nome": "Vera Luz",
        "resumo": ("Gestora de arquivos clínicos, Vera administrava a codificação "
                   "restrita que escondia registros de um programa clandestino. Ao "
                   "manipular prontuários por vingança, Thomas esbarrou nesse padrão e "
                   "percebeu o que não devia. Vera retirou o fármaco restrito, foi à "
                   "clínica desativada, intoxicou Thomas e arrancou o prontuário, "
                   "deixando a numeração para simular vingança pessoal entre médicos."),
        "veredito": ("A cópia do prontuário (com o padrão), o registro de retirada do "
                     "fármaco e a ameaça autenticada de Vera ligam o encobrimento ao "
                     "homicídio."),
        "gancho": ("A codificação é a mesma dos casos anteriores — e o Dr. Kael a "
                   "reconheceu instantaneamente, dizendo que 'poucos têm' esse "
                   "conhecimento. Ele é um deles."),
    },
    "personagens": [
        {"id": "elvas", "nome": "Dr. Elvas",
         "papel": "Colega difamado por Thomas", "retrato": "Amargurado, mas lúcido.",
         "tipo": "suspeito", "culpado": False,
         "abertura": "Thomas destruiu minha reputação com prontuários falsos. E agora quer que eu chore?",
         "topicos": {
            "alibi": {"gatilhos": ["onde estava", "alibi", "manha", "clinica", "10"],
                      "respostas": ["Em cirurgia, com a equipe toda. Há registro em vídeo."]},
            "difamacao": {"gatilhos": ["difamacao", "prontuario", "falso", "manipulou", "reputacao", "vinganca"],
                          "sensivel": True, "revela": "manipulacao",
                          "respostas": ["Ele adulterou prontuários para me culpar por erros "
                                        "que não cometi.",
                                        "Eu o odiava, admito. Mas guardei provas, não um bisturi."]},
            "copia": {"gatilhos": ["copia", "guardou", "prontuario", "backup", "prova"],
                      "sensivel": True, "revela": "copia_prontuario",
                      "respostas": ["Eu copiei o prontuário que ele usou contra mim.",
                                    "Nele há uma numeração estranha — um código que não é "
                                    "clínico comum."]},
         },
         "genericas": ["Minha vingança era limpar meu nome.", "Procurem quem tinha medo da numeração."],
         "confissao": None},

        {"id": "bruno_sa", "nome": "Dr. Bruno Sá",
         "papel": "Ex-supervisor de Thomas", "retrato": "Condescendente, distante.",
         "tipo": "suspeito", "culpado": False,
         "abertura": "Thomas me culpava por tudo. Paranoia de quem fracassou sozinho.",
         "topicos": {
            "alibi": {"gatilhos": ["onde estava", "alibi", "manha", "10", "11"],
                      "respostas": ["Num congresso em outra cidade. Centenas de testemunhas."]},
            "rancor": {"gatilhos": ["rancor", "carreira", "culpa", "supervisor", "fracasso"],
                       "respostas": ["Ele me responsabilizava pela própria queda.",
                                     "Eu o afastei de cirurgias de risco. Isso o enlouqueceu."]},
            "codigo": {"gatilhos": ["codigo", "numeracao", "prontuario", "exame", "restrito"],
                       "respostas": ["Numeração de post-mortem não é da minha área. "
                                     "Pergunte a quem administra os arquivos."]},
         },
         "genericas": ["Eu estava longe.", "Isso é perda de tempo."],
         "confissao": None},

        {"id": "vera", "nome": "Vera Luz",
         "papel": "Gestora de arquivos clínicos",
         "retrato": "Impecável, cordial, respostas ensaiadas.",
         "tipo": "suspeito", "culpado": True,
         "abertura": "Cuido dos arquivos há vinte anos. Que fim terrível para o Dr. Lima.",
         "topicos": {
            "alibi": {"gatilhos": ["onde estava", "alibi", "manha", "clinica", "10", "farmaco"],
                      "sensivel": True,
                      "respostas": ["No arquivo central, trabalhando. Sozinha boa parte da manhã.",
                                    "Retirar fármaco? Minha assinatura deve ter sido copiada.",
                                    "Já respondi. Não insista."]},
            "codificacao": {"gatilhos": ["codigo", "codificacao", "numeracao", "exame", "restrito", "post"],
                            "sensivel": True, "revela": "codificacao",
                            "respostas": ["Eu administro a codificação, sim. É sigilosa por lei.",
                                          "O Dr. Lima não deveria ter acesso àquela numeração.",
                                          "Alguns registros existem para não serem lidos."]},
            "programa": {"gatilhos": ["programa", "clandestino", "encobrir", "departamento", "medico"],
                         "sensivel": True,
                         "respostas": ["Não sei de programa nenhum.",
                                       "Eu só organizo papéis, detetive."]},
         },
         "genericas": ["Está tudo nos conformes.", "Meu trabalho é discrição."],
         "confissao": ("Chega. A cópia, o registro do fármaco, a minha mensagem. O Dr. "
                       "Lima, na sua vingança mesquinha, tropeçou numa numeração que "
                       "não devia enxergar — o padrão que protege nomes que não podem "
                       "aparecer. Avisei para ele devolver e esquecer. Ele ameaçou "
                       "expor. Fiz o necessário e deixei parecer rixa de médicos. Há "
                       "coisas maiores do que um cirurgião ressentido.")},

        _perita("Perita Sofia Mendes",
                "O prontuário arrancado é o centro de tudo. Pergunte.",
                {
                    "prontuario": {"gatilhos": ["prontuario", "arrancado", "arquivo", "numeracao", "falta"],
                                   "revela": "prontuario_arrancado",
                                   "resposta": ("Arrancaram o prontuário e deixaram só o "
                                                "número de referência. Quem matou queria o "
                                                "conteúdo — ou o que ele revelava.")},
                    "farmaco": {"gatilhos": ["farmaco", "fármaco", "retirada", "registro", "substancia"],
                                "revela": "registro_farmaco",
                                "resposta": ("O fármaco usado é de acesso restrito. Há um "
                                             "registro de retirada — e ele contradiz um álibi.")},
                    "codigo": {"gatilhos": ["codigo", "codificacao", "exame", "post", "restrito"],
                               "resposta": ("Aquela numeração não é clínica comum. É um "
                                            "código restrito. O legista reconheceu na hora — "
                                            "o que me pareceu estranho.")},
                }),

        _kael("O Dr. Lima era colega de ofício. Reconheci de pronto o que havia ali.",
              {
                  "causa": {"gatilhos": ["causa", "morte", "farmaco", "intoxicacao", "laudo"],
                            "revela": "causa_morte",
                            "resposta": ("Intoxicação por um fármaco de acesso restrito. "
                                         "Poucos saberiam dosá-lo assim. Eu, por exemplo.")},
                  "codificacao": {"gatilhos": ["codigo", "codificacao", "numeracao", "exame", "post", "restrito"],
                                  "revela": "codificacao",
                                  "resposta": ("Essa codificação? É de exames post-mortem do "
                                               "departamento. Restrita. Poucos a conhecem — "
                                               "faz parte do meu trabalho conhecê-la. Não leia "
                                               "demais nisso.")},
                  "quem": {"gatilhos": ["quem", "culpado", "suspeito", "matou"],
                           "resposta": ("Siga a numeração. Mas cuidado: alguns caminhos "
                                        "levam a portas que é melhor não abrir, detetive.")},
              }),
    ],
}


# ===========================================================================
# CASO 009 - O ENVELOPE VAZIO  (Clara Aguiar — Egoísmo)
# ===========================================================================
CASOS["009"] = {
    "id": "009",
    "titulo": "O ENVELOPE VAZIO",
    "etapa": 3,
    "objetivo": "Descobrir o que foi retirado do envelope antes de chegar ao destino.",
    "mecanica": "O TruthTrace precisa separar fatos de inferências; registros podem mentir.",
    "pergunta_trama": "Por que Kael tenta encerrar esta linha como 'inconclusiva'?",
    "introducao": ("Clara Aguiar, psicóloga, morre em seu apartamento após preparar "
                   "um pacote de documentos para uma autoridade externa. O envelope "
                   "chega vazio ao destinatário."),
    "vitima": {
        "nome": "Clara Aguiar", "idade": 36,
        "ocupacao": "Psicóloga · consultoria a instituições judiciais",
        "citacao": "Há verdades que custam a carreira inteira.",
        "biografia": ("Descobriu que um programa institucional causara danos a pessoas "
                      "vulneráveis. Em vez de expor, protegeu a própria carreira e "
                      "reteve informações que poderiam ajudar as vítimas — por medo de "
                      "perder tudo o que construíra."),
        "local": "Apartamento", "data": "19 de fevereiro",
        "hora": "22h50", "estado": "Homicídio suspeito", "indice_serie": 8,
    },
    "evidencias": [
        {"id": "envelope_vazio", "nome": "Envelope vazio no destinatário",
         "descricao": ("O envelope que Clara enviou chegou lacrado, porém VAZIO. O "
                       "conteúdo foi retirado antes do despacho. Pista que confunde: "
                       "parece extravio postal, mas foi interceptação."), "confiavel": False},
        {"id": "programa_danos", "nome": "Programa institucional que causou danos",
         "descricao": ("Clara descobrira que um programa feriu pessoas vulneráveis e "
                       "reteve as provas por medo de perder a carreira.")},
        {"id": "causa_morte", "nome": "Laudo de Kael",
         "descricao": ("Kael: parada respiratória por sedativo. Recomenda fechar a "
                       "linha dos documentos como 'inconclusiva' — há um registro "
                       "documental que contradiz essa avaliação.")},
        {"id": "lista_participantes", "nome": "Lista de participantes do programa",
         "descricao": ("Uma lista de participantes do programa traz o MESMO código de "
                       "referência encontrado no caso de Elias (001). O fio se fecha.")},
        {"id": "backup_clara", "nome": "Backup do conteúdo do envelope",
         "descricao": ("Clara guardou um backup digital do que colocou no envelope — "
                       "os documentos que alguém retirou antes do envio."),
         "chave_prova": True},
        {"id": "log_entrega", "nome": "Log da entrega e manuseio",
         "descricao": ("O log de manuseio do envelope mostra quem teve acesso a ele "
                       "entre o lacre e a entrega — e quando foi aberto."),
         "chave_prova": True},
        {"id": "mensagem_damiao", "nome": "Mensagem autenticada de Damião",
         "descricao": ("Comunicação autenticada do coordenador Damião instruindo que "
                       "'o pacote da Clara não pode chegar inteiro' e marcando visita "
                       "a ela naquela noite."), "chave_prova": True, "bloqueada": True},
    ],
    "provas_chave": ["backup_clara", "log_entrega", "mensagem_damiao"],
    "linha_tempo": [
        {"hora": "20h00", "titulo": "Clara prepara o envelope",
         "descricao": "Uma amiga confirma que Clara lacrou um pacote de documentos.",
         "tipo": "depoimento", "fonte": "Depoimento — amiga de Clara"},
        {"hora": "21h40", "titulo": "Visita ao apartamento",
         "descricao": "Damião diz que 'ligou, mas não foi'. O log de entrada discorda.",
         "tipo": "depoimento", "fonte": "Depoimentos conflitantes"},
        {"hora": "22h50", "titulo": "Horário da morte",
         "descricao": "Sedativo, segundo o legista. Envelope já esvaziado.",
         "tipo": "evidencia", "fonte": "Perícia / Kael"},
        {"hora": "+2 dias", "titulo": "Envelope chega vazio",
         "descricao": "O destinatário recebe o envelope lacrado, sem conteúdo.",
         "tipo": "registro", "fonte": "Protocolo de recebimento"},
    ],
    "hipoteses": [
        {"id": "h1", "texto": "Damião interceptou o envelope e silenciou Clara.", "status": "em_analise"},
        {"id": "h2", "texto": "Extravio postal e morte natural coincidentes.", "status": "baixa"},
        {"id": "h3", "texto": "A colega Bianca agiu por disputa profissional.", "status": "baixa"},
        {"id": "h4", "texto": "O código da lista é o mesmo do caso 001 — a série se fecha.", "status": "em_analise"},
    ],
    "provas_para_confronto": ["backup_clara", "log_entrega"],
    "acusaveis": ["damiao", "bianca", "nuno"],
    "culpado": "damiao",
    "solucao": {
        "culpado_nome": "Damião Fontes",
        "resumo": ("Coordenador do programa institucional que feriu pessoas "
                   "vulneráveis, Damião soube que Clara enviaria as provas a uma "
                   "autoridade externa. Foi ao apartamento, sedou-a até a parada "
                   "respiratória, retirou o conteúdo do envelope e o relacrou vazio — "
                   "forjando um extravio e uma morte natural."),
        "veredito": ("O backup do conteúdo, o log de manuseio do envelope e a mensagem "
                     "autenticada de Damião provam a interceptação e o homicídio."),
        "gancho": ("A lista de participantes carrega o mesmo código do caso de Elias. "
                   "E o Dr. Kael tentou encerrar esta linha como 'inconclusiva' — pela "
                   "primeira vez, contra as provas."),
    },
    "personagens": [
        {"id": "bianca", "nome": "Bianca Reis",
         "papel": "Colega de Clara", "retrato": "Competitiva, mas abalada.",
         "tipo": "suspeito", "culpado": False,
         "abertura": "A Clara e eu competíamos, sim. Mas eu a respeitava.",
         "topicos": {
            "alibi": {"gatilhos": ["onde estava", "alibi", "noite", "22"],
                      "respostas": ["Num plantão de atendimento. Registrado."]},
            "programa": {"gatilhos": ["programa", "danos", "vitimas", "institucional"],
                         "sensivel": True, "revela": "programa_danos",
                         "respostas": ["A Clara descobriu que um programa feria pessoas "
                                       "vulneráveis. Ficou obcecada com isso.",
                                       "Ela tinha medo de perder a carreira se falasse."]},
            "backup": {"gatilhos": ["backup", "copia", "guardou", "digital", "conteudo", "documento", "arquivo"],
                       "sensivel": True, "revela": "backup_clara",
                       "respostas": ["Ela me confiou uma coisa, por segurança...",
                                     "A Clara me deu um backup digital do que ia no envelope. "
                                     "Está comigo. É tudo o que tiraram de lá."]},
            "envelope": {"gatilhos": ["envelope", "pacote", "enviou", "autoridade", "correio"],
                         "respostas": ["Ela ia mandar tudo para fora da instituição. "
                                       "Alguém não deixou chegar inteiro."]},
         },
         "genericas": ["Eu queria vencê-la, não enterrá-la.", "Procurem o coordenador."],
         "confissao": None},

        {"id": "nuno", "nome": "Nuno Berg",
         "papel": "Porteiro do prédio de Clara", "retrato": "Observador, guarda os horários.",
         "tipo": "suspeito", "culpado": False,
         "abertura": "Eu vejo tudo que entra e sai, detetive. Pergunte.",
         "topicos": {
            "alibi": {"gatilhos": ["onde estava", "alibi", "noite", "portaria"],
                      "respostas": ["Na portaria, a noite toda. As câmeras confirmam."]},
            "visita": {"gatilhos": ["visita", "entrou", "quem", "damiao", "homem", "21"],
                       "revela": "log_entrega",
                       "respostas": ["Um homem subiu ao apartamento dela por volta das "
                                     "nove e meia. Registrei no log.",
                                     "Ele disse que não tinha ido? O log diz o contrário."]},
            "envelope": {"gatilhos": ["envelope", "pacote", "correio", "entrega"],
                         "respostas": ["Ela me entregou um envelope lacrado para o correio. "
                                       "Pesava. Não ia vazio quando saiu das mãos dela."]},
         },
         "genericas": ["Está tudo no log.", "Não invento o que não vi."],
         "confissao": None},

        {"id": "damiao", "nome": "Damião Fontes",
         "papel": "Coordenador do programa institucional",
         "retrato": "Cortês, paciente, sorriso que não alcança os olhos.",
         "tipo": "suspeito", "culpado": True,
         "abertura": "A Clara era uma profissional brilhante. Uma perda enorme.",
         "topicos": {
            "alibi": {"gatilhos": ["onde estava", "alibi", "noite", "apartamento", "21", "visita"],
                      "sensivel": True,
                      "respostas": ["Liguei para ela, mas não cheguei a ir.",
                                    "O log? Deve haver um engano no horário.",
                                    "Eu não subi. Ponto final."]},
            "programa": {"gatilhos": ["programa", "danos", "vitimas", "institucional", "encobrir"],
                         "sensivel": True, "revela": "programa_danos",
                         "respostas": ["O programa teve resultados mistos, como qualquer um.",
                                       "Danos? Exageros de quem não entende metodologia.",
                                       "A Clara dramatizava. Era o estilo dela."]},
            "envelope": {"gatilhos": ["envelope", "documento", "pacote", "interceptou", "conteudo", "backup"],
                         "sensivel": True,
                         "respostas": ["Não sei por que o envelope chegou vazio.",
                                       "Eu jamais tocaria na correspondência dela."]},
         },
         "genericas": ["Isso é difamação.", "Tenho uma instituição a dirigir."],
         "confissao": ("Chega. O backup, o log, a minha mensagem. O pacote dela "
                       "destruiria o programa — e a lista de participantes. Fui até lá "
                       "para dissuadi-la. Ela já tinha lacrado tudo. Usei o sedativo, "
                       "abri o envelope, tirei o conteúdo e relacrei vazio. Devia "
                       "parecer extravio. Eu protegia algo maior do que ela imaginava — "
                       "algo que vocês ainda não entenderam.")},

        _perita("Perita Sofia Mendes",
                "O envelope lacrado e vazio foi o que mais me intrigou. Pergunte.",
                {
                    "envelope": {"gatilhos": ["envelope", "vazio", "lacrado", "conteudo", "correio"],
                                 "revela": "envelope_vazio",
                                 "resposta": ("Chegou lacrado, mas vazio. Reabriram e "
                                              "relacraram. Não foi extravio — foi interceptação.")},
                    "log": {"gatilhos": ["log", "entrega", "manuseio", "acesso", "quem"],
                            "revela": "log_entrega",
                            "resposta": ("O log de manuseio mostra quem tocou no envelope "
                                         "entre o lacre e a entrega. Confira os horários.")},
                    "lista": {"gatilhos": ["lista", "participantes", "codigo", "referencia", "programa"],
                              "revela": "lista_participantes",
                              "resposta": ("A lista de participantes traz um código de "
                                           "referência... idêntico ao do caso do fotógrafo, "
                                           "o Elias. Isso não é coincidência.")},
                }),

        _kael("Clara teve morte discreta. Meu laudo é claro — mas cauteloso quanto ao resto.",
              {
                  "causa": {"gatilhos": ["causa", "morte", "sedativo", "laudo", "respiratoria"],
                            "revela": "causa_morte",
                            "resposta": ("Parada respiratória por sedativo. Quanto à história "
                                         "do envelope, eu encerraria como inconclusiva — não "
                                         "há como provar o que havia dentro.")},
                  "lista": {"gatilhos": ["lista", "codigo", "participantes", "referencia", "elias", "programa"],
                            "resposta": ("Um código repetido entre casos? Esses sistemas "
                                         "reaproveitam numeração o tempo todo. Eu não "
                                         "construiria uma conspiração sobre isso, detetive.")},
                  "quem": {"gatilhos": ["quem", "culpado", "suspeito", "matou"],
                           "resposta": ("Você tem insistido em linhas... incômodas. Nem toda "
                                        "porta precisa ser aberta.")},
              }),
    ],
}


# ===========================================================================
# CASO 010 - O ARQUIVO DOS MORTOS  (Marcelle Lopez — Sacrilégio)
#            >>> CONFRONTO FINAL: o Dr. Adrian Kael é o culpado da série. <<<
# ===========================================================================
# Aqui Kael deixa de ser apenas "perito": aparece como SUSPEITO confrontável.
# As provas-chave são as conexões acumuladas (código recorrente, custódia,
# padrão das tatuagens). Ao reunir tudo e confrontá-lo, o caso se transforma
# em "O Décimo Pecado" e revela PECCATORES.
CASOS["010"] = {
    "id": "010",
    "titulo": "O ARQUIVO DOS MORTOS",
    "etapa": 4,
    "objetivo": "Cruzar as dez investigações, decifrar as marcas e expor quem está por trás de tudo.",
    "mecanica": "Usar evidências acumuladas da série; não basta resolver um só homicídio.",
    "pergunta_trama": "O que as letras em Morse formam — e qual o papel do médico-legista?",
    "introducao": ("Marcelle Lopez é encontrada morta no arquivo subterrâneo de um "
                   "instituto médico. As caixas estão intactas, mas o índice de um ano "
                   "inteiro foi substituído por páginas sem assinatura. Os registros "
                   "ausentes apontam para as mesmas referências dos nove casos anteriores."),
    "vitima": {
        "nome": "Marcelle Lopez", "idade": 44,
        "ocupacao": "Administradora de arquivos clínicos e históricos",
        "citacao": "Os mortos não reclamam de quem mexe em seus nomes.",
        "biografia": ("Usava documentos de pacientes falecidos sem autorização para "
                      "obter vantagens e destruir registros que revelariam sua própria "
                      "participação em irregularidades. O assassino chama seus atos de "
                      "sacrilégio — por profanar a memória dos mortos. Era a única com "
                      "acesso regular à seção de registros antigos que inclui os casos "
                      "anteriores."),
        "local": "Arquivo subterrâneo do instituto", "data": "02 de março",
        "hora": "Madrugada", "estado": "Homicídio — vínculo com a série",
        "indice_serie": 9,
    },
    "evidencias": [
        {"id": "indice_trocado", "nome": "Índice de um ano substituído",
         "descricao": ("O índice de um ano inteiro foi trocado por páginas sem "
                       "assinatura. As caixas estão intactas: o alvo era o índice, "
                       "não o acervo. Pista que confunde sobre o motivo real."),
         "confiavel": False},
        {"id": "acesso_unico", "nome": "Acesso exclusivo de Marcelle",
         "descricao": ("Marcelle era a única com acesso regular à seção de registros "
                       "antigos que conecta os dez casos. Sabia demais sobre os códigos.")},
        {"id": "causa_morte", "nome": "Laudo (assinado por Kael)",
         "descricao": ("O laudo é assinado pelo próprio Dr. Kael: 'causa indeterminada'. "
                       "Pela primeira vez, o legista assina um laudo vago — e é o único "
                       "sem uma segunda assinatura de controle.")},
        {"id": "marcas_morse", "nome": "Padrão das tatuagens em Morse",
         "descricao": ("Reunindo as dez vítimas na ordem das mortes, as letras tatuadas "
                       "formam uma palavra: P-E-C-C-A-T-O-R-E-S. 'Pecadores'. O "
                       "assassino se crê um profeta que pune pecados.")},
        {"id": "dossie_serie", "nome": "Dossiê cruzado das dez vítimas",
         "descricao": ("Cruzando os nove casos com este, o mesmo código de referência "
                       "liga todas as vítimas a um antigo programa médico do "
                       "departamento — e a quem controlava os laudos."),
         "chave_prova": True},
        {"id": "custodia_kael", "nome": "Cadeia de custódia sob Kael",
         "descricao": ("A cadeia de custódia dos materiais sumidos e dos laudos vagos "
                       "passa toda pelas mãos do Dr. Adrian Kael. Ele teve acesso, "
                       "conhecimento e oportunidade em cada caso."), "chave_prova": True},
        {"id": "confissao_registrada", "nome": "Registro autenticado do profeta",
         "descricao": ("Um arquivo autenticado, escondido por Marcelle como seguro de "
                       "vida, contém anotações de Kael descrevendo sua 'missão' de "
                       "'restaurar a humanidade' punindo pecadores — e a chave Morse."),
         "chave_prova": True, "bloqueada": True},
    ],
    "provas_chave": ["dossie_serie", "custodia_kael", "confissao_registrada"],
    "linha_tempo": [
        {"hora": "01h00", "titulo": "Marcelle desce ao arquivo",
         "descricao": "Registro de acesso: ela entra sozinha na seção antiga.",
         "tipo": "registro", "fonte": "Controle de acesso"},
        {"hora": "01h30", "titulo": "Segundo acesso — sem nome",
         "descricao": "Uma segunda entrada no mesmo horário não tem identificação. O crachá usado é de serviço médico.",
         "tipo": "evidencia", "fonte": "Perícia"},
        {"hora": "—", "titulo": "Índice substituído",
         "descricao": "Um ano de índice trocado por páginas sem assinatura.",
         "tipo": "evidencia", "fonte": "Perícia"},
        {"hora": "—", "titulo": "Laudo vago assinado por Kael",
         "descricao": "Causa 'indeterminada', sem segunda assinatura de controle.",
         "tipo": "contradicao", "fonte": "Observação do investigador"},
        {"hora": "Manhã", "titulo": "Corpo encontrado",
         "descricao": "Marcelle morta entre as estantes do arquivo subterrâneo.",
         "tipo": "registro", "fonte": "Boletim de ocorrência"},
    ],
    "hipoteses": [
        {"id": "h1", "texto": "O Dr. Adrian Kael é o autor da série e matou Marcelle para encerrar o rastro.", "status": "em_analise"},
        {"id": "h2", "texto": "Marcelle foi morta por um cúmplice do programa, não pelo legista.", "status": "baixa"},
        {"id": "h3", "texto": "Suicídio encenado para incriminar o departamento.", "status": "baixa"},
        {"id": "h4", "texto": "As tatuagens formam PECCATORES — a série tem um único autor.", "status": "em_analise"},
    ],
    "provas_para_confronto": ["dossie_serie", "custodia_kael"],
    "acusaveis": ["legista", "reitor", "zelador"],
    "culpado": "legista",
    "solucao": {
        "culpado_nome": "Dr. Adrian Kael",
        "resumo": ("O Dr. Adrian Kael é o profeta por trás da série. Médico-legista "
                   "do departamento, ele usou sua posição para escolher vítimas que "
                   "considerava pecadoras, marcá-las com letras em Morse e controlar "
                   "cada laudo, selecionando o que o investigador veria. Marcelle, "
                   "administradora dos arquivos, era a única que podia cruzar os "
                   "códigos e expô-lo. Ele desceu ao arquivo, matou-a, substituiu o "
                   "índice de um ano e assinou um laudo vago — mas Marcelle já havia "
                   "escondido o registro que o condena."),
        "veredito": ("O dossiê cruzado das dez vítimas, a cadeia de custódia toda sob "
                     "Kael e o registro autenticado da 'missão' do profeta provam a "
                     "autoria da série. As dez letras formam PECCATORES: pecadores."),
        "gancho": ("CASO 010 — O DÉCIMO PECADO. A palavra está completa. Mas um "
                   "profeta preso ainda tem discípulos, e um departamento inteiro "
                   "precisou fechar os olhos para que dez pessoas morressem. Algumas "
                   "imagens não deveriam ser reveladas. Você revelou todas."),
    },
    "personagens": [
        {"id": "zelador", "nome": "Osmar Vidal",
         "papel": "Zelador do instituto", "retrato": "Velho de casa, conhece os corredores.",
         "tipo": "suspeito", "culpado": False,
         "abertura": "Trabalho aqui há trinta anos. Nunca vi nada igual, detetive.",
         "topicos": {
            "alibi": {"gatilhos": ["onde estava", "alibi", "noite", "madrugada", "arquivo"],
                      "respostas": ["Na ronda, lá em cima. O arquivo é zona restrita, não entro."]},
            "acesso": {"gatilhos": ["acesso", "quem", "entrou", "cracha", "cracha", "medico"],
                       "sensivel": True, "revela": "acesso_unico",
                       "respostas": ["Só a dona Marcelle entrava naquela seção antiga.",
                                     "Naquela noite, vi um crachá de serviço médico descer. "
                                     "Não era o dela."]},
            "indice": {"gatilhos": ["indice", "arquivo", "pagina", "trocado", "caixa"],
                       "respostas": ["As caixas estavam no lugar. Mas um fichário inteiro "
                                     "foi trocado. Quem fez isso sabia o que procurava."]},
         },
         "genericas": ["Eu só zelo pelo prédio.", "Procurem quem tinha o crachá certo."],
         "confissao": None},

        {"id": "reitor", "nome": "Reitor Haas",
         "papel": "Dirigente do instituto médico", "retrato": "Protege a instituição acima de tudo.",
         "tipo": "suspeito", "culpado": False,
         "abertura": "Esse escândalo pode destruir o instituto. Resolvam com discrição.",
         "topicos": {
            "alibi": {"gatilhos": ["onde estava", "alibi", "noite", "madrugada"],
                      "respostas": ["Em casa. Soube da morte pela manhã, horrorizado."]},
            "programa": {"gatilhos": ["programa", "codigo", "registro", "medico", "departamento", "encobrir"],
                         "sensivel": True, "revela": "acesso_unico",
                         "respostas": ["Houve um programa antigo, sim. Encerrado há anos.",
                                       "Se há irregularidades nos registros, não fui eu quem "
                                       "as guardou. Isso era com a perícia e o legista."]},
            "kael": {"gatilhos": ["kael", "legista", "laudo", "custodia", "suspeito"],
                     "revela": "custodia_kael",
                     "respostas": ["O Dr. Kael? Impecável. Assinava todos os laudos.",
                                   "Agora que menciona... todos eles passavam só por ele. "
                                   "Sem segunda assinatura. Eu confiava demais."]},
         },
         "genericas": ["Protejam o nome do instituto.", "Falem com o departamento médico."],
         "confissao": None},

        {"id": "legista", "nome": "Dr. Adrian Kael",
         "papel": "Médico-legista · Departamento de Medicina Forense",
         "retrato": ("Sereno como sempre. Pela primeira vez, você o olha como suspeito "
                     "— e ele parece quase... aliviado por ser visto."),
         "tipo": "suspeito", "culpado": True,
         "abertura": ("Detetive. Chegou longe — mais longe do que qualquer um antes. "
                      "Pergunte. Vou responder com a mesma precisão de sempre."),
         "topicos": {
            "alibi": {"gatilhos": ["onde estava", "alibi", "noite", "madrugada", "arquivo", "cracha"],
                      "sensivel": True,
                      "respostas": ["Eu tenho acesso a todo o instituto. Isso não é crime.",
                                    "Um crachá médico desceu ao arquivo? Há muitos médicos.",
                                    "Você ainda não perguntou o que realmente quer, detetive."]},
            "laudos": {"gatilhos": ["laudo", "custodia", "assinatura", "controle", "vago", "indeterminada"],
                       "sensivel": True, "revela": "custodia_kael",
                       "respostas": ["Assino muitos laudos. É o meu trabalho.",
                                     "Sem segunda assinatura? Confiavam em mim. Sempre confiaram.",
                                     "Eu decidia o que importava em cada caso. E você aceitava."]},
            "serie": {"gatilhos": ["serie", "vitimas", "codigo", "programa", "conexao", "dez", "padrao"],
                      "sensivel": True, "revela": "dossie_serie",
                      "respostas": ["Dez mortes, dez pecados. Você percebeu o padrão. Que raro.",
                                    "Todas passaram pela minha mesa. Eu as conhecia melhor "
                                    "do que elas a si mesmas.",
                                    "Não foram assassinatos. Foram correções."]},
            "morse": {"gatilhos": ["morse", "tatuagem", "marca", "letra", "peccatores", "palavra", "profeta"],
                      "sensivel": True, "revela": "marcas_morse",
                      "respostas": ["As marcas? Uma assinatura. Toda obra precisa de uma.",
                                    "Leia as letras na ordem, detetive. Você já sabe o que dizem.",
                                    "PECCATORES. Pecadores. Eu apenas devolvi a eles o peso "
                                    "que carregavam."]},
         },
         "genericas": ["Pergunte o que importa.", "Você está perto. Não pare agora."],
         "confissao": ("Sim. Fui eu. Todos eles. O relógio, o cofre, o envelope — cada "
                       "cena foi minha, cada laudo foi a minha voz guiando os seus olhos. "
                       "Escolhi pecadores que a justiça dos homens nunca tocaria e os "
                       "marquei para que, um dia, alguém lesse a palavra inteira. "
                       "Marcelle era a última letra e a única capaz de me expor — "
                       "profanou os mortos e, com eles, a minha obra. O dossiê, a "
                       "custódia, o registro que ela escondeu. Está tudo aí. "
                       "PECCATORES está completa. Eu sou o profeta. E você, detetive, "
                       "é a testemunha que eu esperava.")},

        _perita("Perita Sofia Mendes",
                "Este não é um caso comum, detetive. Ele conversa com todos os outros.",
                {
                    "indice": {"gatilhos": ["indice", "arquivo", "pagina", "trocado", "caixa", "cena"],
                               "revela": "indice_trocado",
                               "resposta": ("As caixas estão intactas, mas trocaram o índice de "
                                            "um ano inteiro. O alvo era o que liga os registros — "
                                            "não o acervo.")},
                    "serie": {"gatilhos": ["serie", "casos", "conexao", "codigo", "vitimas", "cruzar"],
                              "revela": "dossie_serie",
                              "resposta": ("Cruzei este caso com os outros nove. O mesmo código "
                                           "de referência aparece em todos. Não é coincidência: é "
                                           "um fio só. Monte o dossiê da série.")},
                    "morse": {"gatilhos": ["morse", "tatuagem", "marca", "letra", "padrao", "palavra"],
                              "revela": "marcas_morse",
                              "resposta": ("Alinhei as tatuagens na ordem das mortes. As letras "
                                           "formam uma palavra: PECCATORES. Pecadores. Há um "
                                           "único autor nisso tudo.")},
                    "custodia": {"gatilhos": ["custodia", "laudo", "legista", "kael", "assinatura", "quem"],
                                 "revela": "custodia_kael",
                                 "resposta": ("Segui a cadeia de custódia dos materiais sumidos e "
                                              "dos laudos vagos. Passa inteira por uma pessoa: o "
                                              "Dr. Kael. Ele teve tudo — acesso, saber, "
                                              "oportunidade — em cada caso.")},
                }),
    ],
}
