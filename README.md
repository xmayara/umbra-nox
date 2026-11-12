🕯️ Umbra Nox

**Nem toda evidência revela a verdade.**

Umbra Nox é um jogo de investigação criminal e mistério narrativo, no qual o jogador assume o papel de um investigador responsável por solucionar uma série de crimes interligados.

Ao longo da jornada, será necessário analisar evidências, examinar dossiês, interrogar suspeitos, confrontar testemunhas e reconstruir os acontecimentos para descobrir quem está por trás de uma sombria conspiração.

O jogo apresenta uma narrativa progressiva composta por 10 casos criminais, conectados por um segredo que se revela gradualmente.

---

## 🎮 Sobre o jogo

A experiência começa com 6 enigmas introdutórios e evolui para uma investigação envolvendo uma série de 10 homicídios.

Cada caso apresenta uma nova vítima, diferentes suspeitos, evidências e contradições que precisam ser analisadas pelo jogador.

### Principais funcionalidades

- **Dossiê:** informações sobre a vítima e os objetivos da investigação.
- **Interrogatórios:** conversas com suspeitos e testemunhas por meio de perguntas livres.
- **Evidências:** coleta e análise de provas relacionadas ao crime.
- **Linha do Tempo:** organização dos acontecimentos e identificação de contradições.
- **TruthTrace:** construção de hipóteses e análise do progresso investigativo.
- **Confrontos:** utilização de evidências para pressionar suspeitos.
- **Progressão:** desbloqueio sequencial dos casos.
- **Salvamento:** sistema de progresso automático e opção de continuar a investigação.

## 🩸 A série PECCATORES

Dez vítimas. Dez crimes. Uma conexão oculta.

A série PECCATORES acompanha um assassino que acredita estar cumprindo uma missão divina, associando suas vítimas aos pecados humanos.

Cada vítima está relacionada a uma letra representada por um código Morse. Conforme os casos são solucionados, os fragmentos são revelados e precisam ser reorganizados para descobrir a palavra **PECCATORES** (pecadores).

| Caso | Título | Vítima | Letra |
|:---:|---|---|:---:|
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

Ao longo da investigação, o Dr. Adrian Kael, médico-legista, assume um papel importante na narrativa. Inicialmente apresentado como um aliado confiável, sua participação nos acontecimentos começa a levantar suspeitas, conduzindo a história até o confronto final.

---

## 🕹️ Como jogar

1. **Aquecimento:** resolva os seis enigmas introdutórios: Escuro, Buraco, Sombra, Mapa, Pista e Eco.
2. **Arquivo de Casos:** escolha o próximo caso disponível. Eles são desbloqueados conforme as investigações são concluídas.
3. **Investigação:** analise o dossiê, converse com a perícia e o médico-legista e interrogue pessoas de interesse.
4. **Coleta de evidências:** investigue os diálogos e descubra provas que ajudem a reconstruir o crime.
5. **Confronto:** utilize as provas-chave para confrontar o principal suspeito e desbloquear novas informações.
6. **TruthTrace:** construa suas hipóteses e organize as evidências.
7. **Acusação:** reúna as três provas-chave e identifique o verdadeiro responsável para concluir o caso.

**Atenção:** acusar sem provas suficientes ou apontar a pessoa errada não encerra corretamente a investigação.

---

## 🛠️ Tecnologias utilizadas

| Tecnologia | Aplicação |
|---|---|
| HTML5 | Estrutura das interfaces |
| CSS3 | Estilização e identidade visual |
| JavaScript | Interatividade e mecânicas do jogo |
| Python | Lógica e processamento do jogo |
| Flask | Servidor e comunicação com o frontend |

---

## 📂 Estrutura do projeto

```text
Umbra Nox/
├── backend/
│   ├── app.py
│   ├── casos.py
│   ├── dados_casos.py
│   └── dialogo.py
│
├── frontend/
│   ├── index.html
│   ├── css/
│   │   └── style.css
│   └── js/
│       ├── game.js
│       └── interrogatorio.js
│
├── android/
├── requirements.txt
└── README.md
```

---

## 🚀 Como executar

### Pré-requisitos

- Python 3.10 ou superior.
- Git.
- Navegador atualizado.

### Instalação

Clone o repositório:

```bash
git clone https://github.com/xmayara/umbra-nox.git
```

Entre na pasta:

```bash
cd umbra-nox
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

Inicie o servidor:

```bash
python backend/app.py
```

Acesse no navegador:

```text
http://127.0.0.1:5000
```

Para encerrar o servidor, pressione `Ctrl + C` no terminal.

---

## 📱 Versão Android

O projeto também possui uma versão Android preparada para execução offline.

O aplicativo inclui o frontend, o servidor Flask e os dados necessários para executar o jogo diretamente no dispositivo, sem depender de uma conexão com a internet durante a utilização.

Para gerar o APK de depuração:

1. Abra a pasta `android/` no Android Studio.
2. Aguarde a sincronização do Gradle.
3. Acesse **Build > Build Bundle(s) / APK(s) > Build APK(s)**.
4. Após a compilação, o arquivo estará disponível em:

```text
android/app/build/outputs/apk/debug/app-debug.apk
```

A primeira compilação requer conexão com a internet para baixar as ferramentas e dependências necessárias.

---

## 🎯 Objetivo do projeto

Umbra Nox é um projeto de desenvolvimento de jogos que explora narrativa interativa, investigação criminal, construção de personagens e mecânicas de resolução de mistérios.

O objetivo é proporcionar uma experiência investigativa na qual cada detalhe importa e cada descoberta pode mudar a interpretação dos acontecimentos.

---

**Umbra Nox**

*Nem toda evidência revela a verdade. Nem toda verdade deve ser descoberta.*
