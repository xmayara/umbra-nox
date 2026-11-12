<<<<<<< HEAD
# Umbra Nox

Jogo de investigação de clima sombrio, construído sobre o roteiro **PECCATORES**.
O jogador resolve 6 enigmas de aquecimento e depois investiga uma **série de 10
homicídios** (Casos 001 a 010). Em cada caso: analisa o dossiê, conversa com a
perícia e o legista, **interroga suspeitos em tempo real** (perguntas livres),
coleta provas, monta a Linha do Tempo, testa hipóteses no TruthTrace e **fecha o
caso** apontando o culpado.

- **Frontend:** HTML, CSS e JavaScript (telas e interface).
- **Backend:** Python + Flask (enigmas, diálogos e lógica dos casos).

 *"Nem toda evidência revela a verdade."*

---

## Como rodar

Requer **Python 3.10+**.

```bash
pip install -r requirements.txt
python backend/app.py
```

Abra **http://127.0.0.1:5000** no navegador. Para encerrar: `Ctrl + C`.

### APK Android offline

O APK inclui o frontend, o Flask e os dados do jogo. Depois de instalado, o
servidor roda dentro do celular; não é necessário computador, Wi-Fi ou internet
para jogar.

Para compilar, abra a pasta `android/` no Android Studio e gere um APK de
depuração em **Build > Build Bundle(s) / APK(s) > Build APK(s)**. O arquivo fica
em `android/app/build/outputs/apk/debug/app-debug.apk`. Transfira-o para o
Android e instale-o; talvez seja necessário permitir a instalação pelo app que
abriu o arquivo. É preciso conexão à internet na primeira compilação para o
Gradle baixar as ferramentas e dependências.



## Como jogar

1. **Aquecimento:** resolva os 6 enigmas (Escuro, Buraco, Sombra, Mapa, Pista, Eco).
2. **Arquivo de Casos:** escolha um caso. Eles se desbloqueiam em ordem — resolva
   um para liberar o próximo. A barra de fragmentos revela letras em posições
   embaralhadas conforme os casos são resolvidos; cruze-as para descobrir a palavra.
3. Dentro de um caso, use as abas:
   - **Dossiê** — perfil da vítima e objetivo.
   - **Evidências** — o que você já coletou (★ = prova-chave; ⚠ = prova não confiável).
   - **Linha do Tempo** — eventos e contradições.
   - **TruthTrace** — hipóteses, progresso e o botão **Acusar**.
4. **Coletar provas:** converse com a **perícia** e o **legista** e interrogue as
   **pessoas de interesse** digitando perguntas livres. Cada assunto pode revelar
   uma evidência.
5. **Confronto:** reunidas as duas primeiras provas-chave, **confronte o suspeito
   principal** (ex.: "sei que você mentiu", "tenho provas") para liberar a última
   prova e a confissão.
6. **Fechar o caso:** com as **3 provas-chave**, escolha o responsável em *Acusar*.
   Acusar sem provas ou apontar o inocente não encerra o caso.

Há **Salvar** (na mesa e no arquivo) e **Continuar** (no menu), com auto-save ao
coletar evidências.



## A série PECCATORES

Dez vítimas, dez "pecados" aos olhos de um assassino que se crê um profeta. Cada
corpo traz uma letra em código Morse; as marcas são reveladas gradualmente e em
ordem embaralhada. Reorganizadas pela ordem das mortes, formam **PECCATORES**
("pecadores").

| Caso | Título | Vítima | Letra |
|------|--------|--------|:----:|
| 001 | O Relógio Parado | Elias Voss | P |
| 002 | O Preço do Silêncio | Augusto Valença | E |
| 003 | A Testemunha que Mentiu | Beatriz Nogueira | C |
| 004 | O Trono de Cinzas | Samuel Figueredo | C |
| 005 | A Chave do Quarto 17 | Lívia Montenegro | A |
| 006 | O Santo de Fachada | Vicente Alencar | T |
| 007 | O Peso da Omissão | Matheus Silva | O |
| 008 | O Prontuário Perdido | Thomas Lima | R |
| 009 | O Envelope Vazio | Clara Aguiar | E |
| 010 | O Arquivo dos Mortos | Marcelle Lopez | S |

O **Dr. Adrian Kael** (médico-legista) é o fio condutor oculto da série: começa
como aliado confiável e, caso a caso, deixa sementes de suspeita, até o confronto
final no Caso 010.



## Estrutura

```
Umbra Nox/
├── backend/
│   ├── app.py            # servidor Flask + API (multi-caso)
│   ├── casos.py          # camada de acesso (enigmas, séries, seleção)
│   ├── dados_casos.py    # os 10 casos (dossiês, evidências, personagens)
│   └── dialogo.py        # motor de diálogo em tempo real + confronto
├── frontend/
│   ├── index.html
│   ├── css/style.css
│   └── js/
│       ├── game.js             # fluxo, casos, evidências, timeline, truthtrace
│       └── interrogatorio.js   # diálogos em tempo real
├── requirements.txt
└── README.md
```

# umbra-nox
Umbra Nox é um jogo de investigação e mistério focado em narrativa, no qual os jogadores solucionam casos criminais, analisam evidências, interrogam suspeitos e desvendam uma sombria conspiração que conecta todos os acontecimentos..

