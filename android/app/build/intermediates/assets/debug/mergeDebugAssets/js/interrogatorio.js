/* ====================================================================
   UMBRA NOX - diálogos em tempo real (multi-caso, PERGUNTAS PRONTAS)
   iniciarDialogo(pid, modo) -> o jogador escolhe perguntas de uma lista
   ==================================================================== */

const Interr = {
  estado: null, nome: "", ocupado: false, modo: "suspeito",
  perguntas: [], feitas: [],
};

async function iniciarDialogo(pid, modo) {
  try {
    const estado = await (await fetch("/api/dialogo/iniciar", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        caso_id: Jogo.casoId, pid: pid,
        evidencias: Jogo.evidenciasDescobertas,
      }),
    })).json();
    if (estado.erro) { alert(estado.erro); return; }

    Interr.modo = (estado.tipo === "suspeito") ? "suspeito" : "pericia";
    Interr.estado = estado;
    Interr.nome = estado.nome;
    Interr.perguntas = estado.perguntas || [];
    Interr.feitas = [];

    const comMedidor = (estado.tipo === "suspeito");
    const marca = comMedidor ? "INTERROGATÓRIO" : "CONVERSA TÉCNICA";
    document.getElementById("interr-marca").textContent = marca;
    document.getElementById("interr-nome").textContent = estado.nome;
    document.getElementById("interr-papel").textContent = estado.papel;
    document.getElementById("interr-retrato").textContent = estado.retrato;
    document.getElementById("medidor").style.display = comMedidor ? "flex" : "none";
    if (comMedidor) atualizarMedidor(0);

    const dialogo = document.getElementById("dialogo");
    dialogo.innerHTML = "";
    adicionarFala("suspeito", estado.nome, estado.abertura);
    renderizarPerguntas();
    irPara("interrogatorio");
    setTimeout(() => tutorialDica("iniciar_dialogo"), 400);
  } catch (e) { console.error("Falha ao iniciar diálogo", e); }
}

function renderizarPerguntas() {
  const box = document.getElementById("perguntas-prontas");
  if (!box) return;
  if (!Interr.perguntas.length) {
    box.innerHTML = '<p class="perguntas-vazia">Não há mais o que perguntar. ' +
      'Volte à mesa e analise as evidências.</p>';
    return;
  }
  box.innerHTML = Interr.perguntas.map((q) => {
    const feita = Interr.feitas.includes(q.topico) && !q.confronto;
    const cls = (q.confronto ? "confronto " : "") + (feita ? "feita" : "");
    return `<button class="pergunta-btn ${cls}" data-topico="${q.topico}" ${Interr.ocupado ? "disabled" : ""}>` +
           `${q.rotulo}</button>`;
  }).join("");
  box.querySelectorAll(".pergunta-btn").forEach((b) =>
    b.addEventListener("click", () => escolherPergunta(b.dataset.topico)));
}

function adicionarFala(tipo, autor, texto) {
  const dialogo = document.getElementById("dialogo");
  const div = document.createElement("div");
  div.className = "fala " + tipo;
  div.innerHTML = (autor ? `<span class="autor">${autor}</span>` : "") + texto;
  dialogo.appendChild(div);
  dialogo.scrollTop = dialogo.scrollHeight;
}

function atualizarMedidor(n) {
  const pct = Math.min(100, Math.round((n / 6) * 100));
  document.getElementById("medidor-fill").style.width = pct + "%";
}

function rotuloDoTopico(topico) {
  const q = Interr.perguntas.find((x) => x.topico === topico);
  return q ? q.rotulo : topico;
}

async function escolherPergunta(topico) {
  if (Interr.ocupado || !Interr.estado) return;
  Interr.ocupado = true;
  // Mostra a pergunta escolhida como fala do detetive.
  adicionarFala("detetive", "Detetive", rotuloDoTopico(topico));
  // Perguntas normais ficam marcadas como "feitas"; confrontos não.
  const ehConfronto = topico.indexOf("__confront") === 0;
  if (!ehConfronto && !Interr.feitas.includes(topico)) {
    Interr.feitas.push(topico);
  }
  renderizarPerguntas(); // desabilita durante a espera

  const pensando = document.createElement("div");
  pensando.className = "fala suspeito";
  pensando.innerHTML = `<span class="autor">${Interr.nome}</span><em>...</em>`;
  document.getElementById("dialogo").appendChild(pensando);
  document.getElementById("dialogo").scrollTop = 1e9;

  try {
    const r = await (await fetch("/api/dialogo/perguntar", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ estado: Interr.estado, topico: topico }),
    })).json();
    await new Promise((res) => setTimeout(res, 480));
    pensando.remove();
    if (r.erro) { adicionarFala("suspeito", Interr.nome, r.erro); return; }

    Interr.estado = r.estado;
    Interr.perguntas = r.perguntas || Interr.perguntas;
    if (Interr.modo === "suspeito") atualizarMedidor(r.nervosismo || 0);

    if (r.confissao_disparada) adicionarFala("confissao", "CONFISSÃO", r.fala);
    else adicionarFala("suspeito", Interr.nome, r.fala);

    if (r.revela) revelarEvidencia(r.revela);
    if (r.contradicao) {
      adicionarFala("contradicao", "CONTRADIÇÃO DETECTADA", r.contradicao);
      registrarContradicao(r.contradicao);
    }
  } catch (e) {
    pensando.remove();
    adicionarFala("suspeito", Interr.nome, "(silêncio — falha de conexão)");
  } finally {
    Interr.ocupado = false;
    renderizarPerguntas();
  }
}
