/* ====================================================================
   UMBRA NOX - fluxo do jogo (multi-caso, série PECCATORES)
   ==================================================================== */

const Jogo = {
  enigmas: [],
  enigmaAtual: 0,
  // Série
  serie: null,            // {palavra, vitimas, casos, primeiro}
  resolvidos: [],         // ids de casos resolvidos
  // Caso ativo
  casoId: null,
  caso: null,
  suspeitos: [],
  peritos: [],
  evidenciasDescobertas: [], // por caso (reiniciado ao abrir um caso)
  contradicoes: [],
  hipoteseAtual: null,
  proximoCaso: null,
  tutorial: [],            // dicas do caso (só o 001 tem)
  tutorialVistos: [],      // gatilhos já exibidos
};

const ORDEM_MARCAS_MORSE = [4, 1, 7, 0, 6, 3, 9, 2, 5, 8];

/* --------------------------- Tutorial ------------------------------ */
function tutorialDica(gatilho) {
  if (!Jogo.tutorial || !Jogo.tutorial.length) return;       // só no Caso 001
  if (Jogo.tutorialVistos.includes(gatilho)) return;          // uma vez só
  const dica = Jogo.tutorial.find((d) => d.gatilho === gatilho);
  if (!dica) return;
  Jogo.tutorialVistos.push(gatilho);
  const balao = document.getElementById("tutorial-balao");
  document.getElementById("tutorial-texto").textContent = dica.texto;
  balao.classList.remove("oculto");
}

function fecharTutorial() {
  document.getElementById("tutorial-balao").classList.add("oculto");
}

/* --------------------------- Salvar / Continuar -------------------- */
function montarSnapshot() {
  return {
    versao: 2,
    enigmaAtual: Jogo.enigmaAtual,
    resolvidos: Jogo.resolvidos,
    casoId: Jogo.casoId,
    evidenciasDescobertas: Jogo.evidenciasDescobertas,
    contradicoes: Jogo.contradicoes,
    hipoteseAtual: Jogo.hipoteseAtual,
  };
}

async function salvarJogo(silencioso) {
  try {
    const r = await (await fetch("/api/salvar", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify(montarSnapshot()),
    })).json();
    if (!silencioso) feedbackSalvar(r.ok ? "Progresso salvo." : "Falha ao salvar.");
    return r.ok;
  } catch (e) {
    if (!silencioso) feedbackSalvar("Falha ao salvar.");
    return false;
  }
}

function feedbackSalvar(msg) {
  ["salvar-feedback", "salvar-feedback-casos"].forEach((id) => {
    const el = document.getElementById(id);
    if (!el) return;
    el.textContent = msg;
    el.classList.add("visivel");
    setTimeout(() => el.classList.remove("visivel"), 2000);
  });
}

function feedbackMenu(msg) {
  const el = document.getElementById("menu-feedback");
  if (!el) return;
  el.textContent = msg;
  el.classList.add("visivel");
  clearTimeout(feedbackMenu._t);
  feedbackMenu._t = setTimeout(() => el.classList.remove("visivel"), 3000);
}

async function existeSave() {
  try {
    const r = await (await fetch("/api/carregar")).json();
    return r.existe ? r.estado : null;
  } catch (e) { return null; }
}

async function continuarJogo() {
  const estado = await existeSave();
  if (!estado) {
    feedbackMenu('Nenhum jogo salvo. Use "Novo Jogo" para começar.');
    return false;
  }
  Jogo.enigmaAtual = estado.enigmaAtual || 0;
  Jogo.resolvidos = estado.resolvidos || [];
  Jogo.evidenciasDescobertas = estado.evidenciasDescobertas || [];
  Jogo.contradicoes = estado.contradicoes || [];
  Jogo.hipoteseAtual = estado.hipoteseAtual || null;

  await carregarSerie();
  // Continuar abre o Arquivo de Casos (hub da série).
  if (estado.casoId) {
    await abrirCaso(estado.casoId, true);
    irPara("caso");
    trocarAba("arquivo");
  } else {
    irPara("arquivocasos");
  }
  return true;
}

/* --------------------------- Navegação ----------------------------- */
function irPara(nome) {
  document.querySelectorAll(".tela").forEach((t) => t.classList.remove("ativa"));
  const alvo = document.getElementById("tela-" + nome);
  if (alvo) alvo.classList.add("ativa");
}

/* --------------------------- Enigmas ------------------------------- */
async function carregarEnigmas() {
  try { Jogo.enigmas = await (await fetch("/api/enigmas")).json(); }
  catch (e) { console.error("Falha ao carregar enigmas", e); }
}

function mostrarEnigma(i) {
  const e = Jogo.enigmas[i];
  if (!e) return;
  document.getElementById("enigma-progresso").textContent =
    `Enigma ${i + 1} de ${Jogo.enigmas.length}`;
  document.getElementById("enigma-texto").textContent = e.texto;
  document.getElementById("enigma-dica").textContent = "Dica: " + e.dica;
  document.getElementById("enigma-input").value = "";
  const fb = document.getElementById("enigma-feedback");
  fb.textContent = ""; fb.className = "feedback";
  document.getElementById("enigma-input").focus();
}

async function verificarEnigma(resposta) {
  const e = Jogo.enigmas[Jogo.enigmaAtual];
  const fb = document.getElementById("enigma-feedback");
  try {
    const r = await (await fetch("/api/enigmas/verificar", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id: e.id, resposta }),
    })).json();
    if (r.correto) {
      fb.textContent = `Correto. "${r.resposta}".`;
      fb.className = "feedback certo";
      setTimeout(avancarEnigma, 1100);
    } else {
      fb.textContent = "Não é isso. Pense na dica.";
      fb.className = "feedback erro";
    }
  } catch (err) {
    fb.textContent = "Erro de conexão com o servidor.";
    fb.className = "feedback erro";
  }
}

function avancarEnigma() {
  Jogo.enigmaAtual += 1;
  if (Jogo.enigmaAtual >= Jogo.enigmas.length) irPara("transicao");
  else mostrarEnigma(Jogo.enigmaAtual);
}

/* --------------------------- Série / Arquivo de Casos -------------- */
async function carregarSerie() {
  if (Jogo.serie) return;
  try { Jogo.serie = await (await fetch("/api/casos")).json(); }
  catch (e) { console.error("Falha ao carregar a série", e); }
}

function renderizarArquivoCasos() {
  if (!Jogo.serie) return;
  // Fragmentos aparecem embaralhados e sem associação visível a um caso.
  const letras = ORDEM_MARCAS_MORSE.map((i) => {
    const v = Jogo.serie.vitimas[i];
    const cid = Jogo.serie.casos[i] ? Jogo.serie.casos[i].id : null;
    const revelada = cid && Jogo.resolvidos.includes(cid);
    return `<span class="peccatores-letra ${revelada ? "revelada" : ""}">` +
           `${revelada ? v.letra : "?"}</span>`;
  }).join("");
  document.getElementById("peccatores").innerHTML = letras;

  const grade = document.getElementById("casos-grade");
  grade.innerHTML = Jogo.serie.casos.map((c, idx) => {
    const resolvido = Jogo.resolvidos.includes(c.id);
    // Desbloqueado se for o primeiro ou o anterior já foi resolvido.
    const anterior = idx === 0 ? null : Jogo.serie.casos[idx - 1].id;
    const desbloqueado = idx === 0 || Jogo.resolvidos.includes(anterior);
    const cls = resolvido ? "resolvido" : (desbloqueado ? "" : "bloqueado");
    const estado = resolvido ? "RESOLVIDO" : (desbloqueado ? "EM ABERTO" : "BLOQUEADO");
    return `
      <div class="caso-card ${cls}" data-caso="${desbloqueado ? c.id : ""}">
        <div class="caso-card-topo">
          <span class="caso-card-id">CASO ${c.id}</span>
        </div>
        <h4>${c.titulo}</h4>
        <p class="caso-card-vitima">${c.vitima}</p>
        <p class="caso-card-objetivo">${c.objetivo}</p>
        <span class="caso-card-estado ${cls}">${estado}</span>
      </div>`;
  }).join("");

  grade.querySelectorAll(".caso-card[data-caso]").forEach((card) => {
    const id = card.dataset.caso;
    if (!id) return;
    card.addEventListener("click", async () => {
      await abrirCaso(id);
      irPara("caso");
      trocarAba("dossie");
    });
  });
}

/* --------------------------- Abrir um caso ------------------------- */
async function abrirCaso(casoId, manterProgresso) {
  try {
    const dados = await (await fetch("/api/caso/" + casoId)).json();
    if (dados.erro) { feedbackMenu(dados.erro); return; }
    Jogo.casoId = casoId;
    Jogo.caso = dados.caso;
    Jogo.suspeitos = dados.suspeitos;
    Jogo.peritos = dados.peritos || [];
    Jogo.proximoCaso = dados.caso.proximo;
    Jogo.tutorial = dados.caso.tutorial || [];
    if (!manterProgresso) Jogo.tutorialVistos = [];
    if (!manterProgresso) {
      // Novo caso: zera a coleta (mantém a de save ao continuar).
      Jogo.evidenciasDescobertas = [];
      Jogo.contradicoes = [];
      Jogo.hipoteseAtual = null;
    }
    if (!Jogo.hipoteseAtual && Jogo.caso.hipoteses.length) {
      const p = Jogo.caso.hipoteses.find((h) => h.status === "plausivel");
      Jogo.hipoteseAtual = (p || Jogo.caso.hipoteses[0]).id;
    }
    preencherDossie();
    preencherArquivo();
    preencherAcusacao();
    salvarJogo(true);
    setTimeout(() => tutorialDica("abrir_caso"), 400);
  } catch (e) { console.error("Falha ao abrir caso", e); }
}

function preencherDossie() {
  const c = Jogo.caso, v = c.vitima;
  document.getElementById("caso-id").textContent =
    `CASO ${c.id} • ${c.titulo}  ·  Etapa ${c.etapa}`;
  document.getElementById("caso-objetivo").textContent = c.objetivo;
  document.getElementById("vitima-nome").textContent = v.nome;
  document.getElementById("vitima-sub").textContent = `${v.idade} anos • ${v.ocupacao}`;
  document.getElementById("vitima-citacao").textContent = `“${v.citacao}”`;
  document.getElementById("vitima-bio").textContent = v.biografia;
  const dados = [
    ["Local", v.local], ["Data", v.data],
    ["Hora", v.hora], ["Estado do caso", v.estado],
  ];
  document.getElementById("vitima-dados").innerHTML = dados
    .map(([k, val]) => `<li><b>${k}</b>${val}</li>`).join("");
}

function preencherArquivo() {
  renderizarEvidencias();
  document.getElementById("lista-suspeitos").innerHTML = Jogo.suspeitos.map((s) => `
    <div class="card suspeito" data-suspeito="${s.id}">
      <h4>${s.nome}</h4><p>${s.papel}</p>
      <p style="margin-top:.5rem;opacity:.75">${s.retrato}</p>
      <span class="acao">Interrogar →</span>
    </div>`).join("");
  document.querySelectorAll(".card.suspeito[data-suspeito]").forEach((card) =>
    card.addEventListener("click", () => iniciarDialogo(card.dataset.suspeito, "suspeito")));

  document.getElementById("lista-peritos").innerHTML = Jogo.peritos.map((p) => `
    <div class="card suspeito perito" data-perito="${p.id}">
      <h4>${p.nome}</h4><p>${p.papel}</p>
      <p style="margin-top:.5rem;opacity:.75">${p.retrato}</p>
      <span class="acao">Conversar →</span>
    </div>`).join("");
  document.querySelectorAll(".card.perito[data-perito]").forEach((card) =>
    card.addEventListener("click", () => iniciarDialogo(card.dataset.perito, "pericia")));
}

/* --------------------------- Evidências ---------------------------- */
function renderizarEvidencias() {
  const alvo = document.getElementById("lista-evidencias");
  if (!alvo || !Jogo.caso) return;
  const desc = Jogo.caso.evidencias.filter((e) =>
    Jogo.evidenciasDescobertas.includes(e.id));
  if (desc.length === 0) {
    alvo.innerHTML = `<p class="evidencia-vazia">Nenhuma evidência coletada ainda. ` +
      `Converse com a equipe técnica e ouça os depoimentos para revelá-las.</p>`;
    return;
  }
  alvo.innerHTML = desc.map((e) => {
    const cls = e.chave_prova ? "prova" : (e.confiavel === false ? "nao-confiavel" : "");
    return `<div class="card evidencia-nova ${cls}"><h4>${e.nome}</h4><p>${e.descricao}</p></div>`;
  }).join("");
}

function revelarEvidencia(id) {
  if (!id || !Jogo.caso || Jogo.evidenciasDescobertas.includes(id)) return;
  if (!Jogo.caso.evidencias.some((e) => e.id === id)) return;
  Jogo.evidenciasDescobertas.push(id);
  renderizarEvidencias();
  salvarJogo(true);
  tutorialDica("coletar_evidencia");
  // Quantas provas-chave já foram reunidas?
  const provas = (Jogo.caso.provas_chave || []).filter(
    (p) => Jogo.evidenciasDescobertas.includes(p)).length;
  if (provas >= 2) tutorialDica("provas_2");
}

/* --------------------------- Abas ---------------------------------- */
function trocarAba(nome) {
  document.querySelectorAll("#tela-caso .aba").forEach((a) =>
    a.classList.toggle("ativa", a.dataset.aba === nome));
  document.querySelectorAll("#tela-caso .painel").forEach((p) => p.classList.remove("ativo"));
  const painel = document.getElementById("painel-" + nome);
  if (painel) painel.classList.add("ativo");
  if (nome === "timeline") renderizarTimeline();
  if (nome === "truthtrace") renderizarTruthTrace();
  if (nome === "arquivo") tutorialDica("aba_arquivo");
  if (nome === "truthtrace") tutorialDica("aba_truthtrace");
}

/* --------------------------- Linha do Tempo ------------------------ */
function registrarContradicao(t) {
  if (t && !Jogo.contradicoes.includes(t)) {
    Jogo.contradicoes.push(t);
    tutorialDica("contradicao");
  }
}
function rotuloTipo(t) {
  return { registro: "Registro", depoimento: "Depoimento",
           evidencia: "Evidência", contradicao: "Contradição" }[t] || t;
}
function renderizarTimeline() {
  const ol = document.getElementById("timeline-lista");
  if (!ol || !Jogo.caso) return;
  const fixos = Jogo.caso.linha_tempo || [];
  const din = Jogo.contradicoes.map((c) => ({
    hora: "—", titulo: "Contradição detectada", descricao: c,
    tipo: "contradicao", fonte: "TruthTrace" }));
  ol.innerHTML = fixos.concat(din).map((e) => `
    <li class="evento ${e.tipo}">
      <span class="evento-hora">${e.hora}</span>
      <span class="evento-ponto"></span>
      <div class="evento-corpo">
        <div class="evento-titulo">${e.titulo}
          <span class="tag ${e.tipo}">${rotuloTipo(e.tipo)}</span></div>
        <p class="evento-desc">${e.descricao}</p>
        <span class="evento-fonte">${e.fonte || ""}</span>
      </div>
    </li>`).join("");
}

/* --------------------------- TruthTrace ---------------------------- */
function rotuloStatus(s) {
  return { em_analise: "Em análise", plausivel: "Plausível", baixa: "Baixa" }[s] || s;
}
function renderizarTruthTrace() {
  if (!Jogo.caso) return;
  const ul = document.getElementById("tt-hipoteses");
  ul.innerHTML = (Jogo.caso.hipoteses || []).map((h) => `
    <li class="tt-hip ${h.status} ${Jogo.hipoteseAtual === h.id ? "selecionada" : ""}"
        data-hip="${h.id}">
      <span class="tt-hip-dot"></span>
      <div><p class="tt-hip-texto">${h.texto}</p>
        <span class="tt-hip-status">${rotuloStatus(h.status)}</span></div>
    </li>`).join("");
  ul.querySelectorAll(".tt-hip").forEach((li) =>
    li.addEventListener("click", () => { Jogo.hipoteseAtual = li.dataset.hip; renderizarTruthTrace(); }));

  const hip = (Jogo.caso.hipoteses || []).find((h) => h.id === Jogo.hipoteseAtual);
  document.getElementById("tt-hipotese-texto").textContent =
    hip ? hip.texto : "Selecione uma hipótese ao lado.";

  const coletadas = Jogo.caso.evidencias.filter((e) =>
    Jogo.evidenciasDescobertas.includes(e.id));
  const ttEv = document.getElementById("tt-evidencias");
  ttEv.innerHTML = coletadas.length === 0
    ? '<p class="evidencia-vazia">Nenhuma evidência relacionada ainda.</p>'
    : coletadas.map((e) => `
      <div class="tt-ev-card"><span class="tt-ev-check">✓</span>
        <div><b>${e.nome}</b><p>${e.descricao}</p></div></div>`).join("");

  const total = Jogo.caso.evidencias.length;
  const col = Jogo.evidenciasDescobertas.length;
  const provas = Jogo.caso.provas_chave || [];
  const provasCol = provas.filter((p) => Jogo.evidenciasDescobertas.includes(p)).length;
  const pct = total ? Math.round((col / total) * 100) : 0;
  document.getElementById("tt-ev-coletadas").textContent = `${col} / ${total}`;
  document.getElementById("tt-provas").textContent = `${provasCol} / ${provas.length}`;
  document.getElementById("tt-contradicoes").textContent = String(Jogo.contradicoes.length);
  document.getElementById("tt-anel").style.background =
    `conic-gradient(var(--dourado) ${pct * 3.6}deg, rgba(255,255,255,0.06) 0deg)`;
  document.getElementById("tt-anel-pct").textContent = pct + "%";
  document.getElementById("tt-citacao").textContent =
    `"${Jogo.caso.vitima.citacao}"  — ${Jogo.caso.vitima.nome}`;

  const prox = document.getElementById("tt-proximo-texto");
  if (col === 0) prox.textContent = "Converse com a perícia e o legista para coletar as primeiras evidências.";
  else if (provasCol < 2) prox.textContent = "Interrogue as testemunhas e colete as provas-chave (marcadas com ★).";
  else if (provasCol < 3) prox.textContent = "Você tem as provas da acusação. Confronte o suspeito principal para liberar a última.";
  else prox.textContent = "Todas as provas reunidas. Formalize a acusação abaixo.";
}

/* --------------------------- Acusação ------------------------------ */
function preencherAcusacao() {
  const sel = document.getElementById("acusar-select");
  if (!sel || !Jogo.caso) return;
  const porId = {};
  Jogo.suspeitos.forEach((s) => (porId[s.id] = s.nome));
  sel.innerHTML = '<option value="">— escolher suspeito —</option>' +
    (Jogo.caso.acusaveis || []).filter((id) => porId[id])
      .map((id) => `<option value="${id}">${porId[id]}</option>`).join("");
}

async function acusar() {
  const sel = document.getElementById("acusar-select");
  const fb = document.getElementById("acusar-feedback");
  const suspeito = sel.value;
  if (!suspeito) { fb.textContent = "Escolha quem acusar."; fb.className = "feedback erro"; return; }
  try {
    const r = await (await fetch("/api/acusar", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ caso_id: Jogo.casoId, suspeito, evidencias: Jogo.evidenciasDescobertas }),
    })).json();
    if (r.resultado === "resolvido") {
      if (!Jogo.resolvidos.includes(Jogo.casoId)) Jogo.resolvidos.push(Jogo.casoId);
      Jogo.proximoCaso = r.proximo;
      salvarJogo(true);
      mostrarDesfecho(r.mensagem, r.proximo);
    } else {
      fb.textContent = r.mensagem; fb.className = "feedback erro";
    }
  } catch (e) {
    fb.textContent = "Erro de conexão com o servidor."; fb.className = "feedback erro";
  }
}

function mostrarDesfecho(texto, proximo) {
  document.getElementById("desfecho-selo").textContent = "CASO ENCERRADO";
  document.getElementById("desfecho-titulo").textContent = `CASO ${Jogo.caso.id} • ${Jogo.caso.titulo}`;
  document.getElementById("desfecho-texto").textContent = texto;
  const btn = document.getElementById("btn-proximo-caso");
  if (proximo) {
    btn.classList.remove("oculto");
    btn.onclick = async () => { await abrirCaso(proximo); irPara("caso"); trocarAba("dossie"); };
  } else {
    btn.classList.add("oculto");
  }
  irPara("desfecho");
}

/* --------------------------- Eventos ------------------------------- */
document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll("[data-ir]").forEach((btn) => {
    btn.addEventListener("click", async () => {
      const destino = btn.dataset.ir;
      if (destino === "enigmas") {
        if (Jogo.enigmas.length === 0) await carregarEnigmas();
        Jogo.enigmaAtual = 0; mostrarEnigma(0);
      }
      if (destino === "arquivocasos") {
        await carregarSerie();
        renderizarArquivoCasos();
      }
      irPara(destino);
    });
  });

  document.querySelectorAll("[data-aba]").forEach((btn) =>
    btn.addEventListener("click", () => trocarAba(btn.dataset.aba)));

  const btnOpcoes = document.getElementById("btn-opcoes");
  if (btnOpcoes) btnOpcoes.addEventListener("click", () =>
    document.getElementById("caixa-opcoes").classList.toggle("oculto"));

  const btnTut = document.getElementById("tutorial-ok");
  if (btnTut) btnTut.addEventListener("click", fecharTutorial);

  const btnContinuar = document.getElementById("btn-continuar");
  if (btnContinuar) btnContinuar.addEventListener("click", continuarJogo);

  ["btn-salvar", "btn-salvar-casos"].forEach((id) => {
    const b = document.getElementById(id);
    if (b) b.addEventListener("click", () => salvarJogo(false));
  });

  const btnAcusar = document.getElementById("btn-acusar");
  if (btnAcusar) btnAcusar.addEventListener("click", acusar);

  const formEnigma = document.getElementById("form-enigma");
  if (formEnigma) formEnigma.addEventListener("submit", (ev) => {
    ev.preventDefault();
    const v = document.getElementById("enigma-input").value.trim();
    if (v) verificarEnigma(v);
  });

  existeSave().then((estado) => {
    if (estado && btnContinuar) btnContinuar.classList.add("tem-save");
  });
});
