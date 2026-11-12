/* ====================================================================
   UMBRA NOX - interrogatórios e conversas técnicas
   ==================================================================== */

const Interr = {
  estado: null,
  nome: "",
  ocupado: false,
  modo: "suspeito",
  casoId: null,
  pid: null,
  perguntas: [],
  mensagens: [],
};

function chaveConversa(casoId, pid) {
  return `${casoId}:${pid}`;
}

async function salvarConversa() {
  if (!Interr.estado || !Interr.casoId || !Interr.pid) return false;
  const chave = chaveConversa(Interr.casoId, Interr.pid);
  Jogo.conversas[chave] = {
    estado: Interr.estado,
    mensagens: Interr.mensagens,
  };
  const salva = await salvarJogo(true);
  const status = document.getElementById("interr-save-status");
  if (status) {
    status.textContent = salva
      ? "Conversa salva"
      : "Não foi possível salvar. Verifique a conexão e tente novamente.";
    status.classList.toggle("erro", !salva);
  }
  return salva;
}

async function iniciarDialogo(pid, modo) {
  try {
    const chave = chaveConversa(Jogo.casoId, pid);
    const conversaSalva = Jogo.conversas[chave] || null;
    const estado = await (await fetch("/api/dialogo/iniciar", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        caso_id: Jogo.casoId, pid: pid,
        evidencias: Jogo.evidenciasDescobertas,
        estado: conversaSalva ? conversaSalva.estado : null,
      }),
    })).json();
    if (estado.erro) { alert(estado.erro); return; }

    Interr.modo = (estado.tipo === "suspeito") ? "suspeito" : "pericia";
    Interr.estado = estado;
    Interr.nome = estado.nome;
    Interr.casoId = Jogo.casoId;
    Interr.pid = pid;
    Interr.perguntas = estado.perguntas || [];
    Interr.mensagens = conversaSalva && Array.isArray(conversaSalva.mensagens)
      ? conversaSalva.mensagens : [];

    const comMedidor = (estado.tipo === "suspeito");
    const marca = comMedidor ? "INTERROGATÓRIO" : "CONVERSA TÉCNICA";
    document.getElementById("interr-marca").textContent = marca;
    document.getElementById("interr-nome").textContent = estado.nome;
    document.getElementById("interr-papel").textContent = estado.papel;
    document.getElementById("interr-avatar").textContent =
      estado.nome.trim().charAt(0).toLocaleUpperCase("pt-BR");
    document.getElementById("interr-retrato").textContent = estado.retrato;
    document.getElementById("medidor").style.display = comMedidor ? "flex" : "none";
    if (comMedidor) atualizarMedidor(estado.nervosismo || 0);

    const dialogo = document.getElementById("dialogo");
    dialogo.innerHTML = "";
    Interr.mensagens.forEach((fala) =>
      adicionarFala(fala.tipo, fala.autor, fala.texto, fala.hora, false));
    if (!Interr.mensagens.length) {
      adicionarFala("suspeito", estado.nome, estado.abertura);
      await salvarConversa();
    }
    renderizarPerguntas();
    irPara("interrogatorio");
    document.getElementById("pergunta-livre").focus();
    setTimeout(() => tutorialDica("iniciar_dialogo"), 400);
  } catch (e) { console.error("Falha ao iniciar diálogo", e); }
}

function renderizarPerguntas() {
  const box = document.getElementById("perguntas-prontas");
  if (!box) return;
  if (!Interr.perguntas.length) {
    box.innerHTML = '<p class="perguntas-vazia">As sugestões acabaram. ' +
      'Você ainda pode escrever uma pergunta.</p>';
    return;
  }
  box.replaceChildren();
  Interr.perguntas.forEach((q) => {
    const botao = document.createElement("button");
    botao.type = "button";
    botao.className = "pergunta-btn" + (q.confronto ? " confronto" : "");
    botao.dataset.topico = q.topico;
    botao.disabled = Interr.ocupado;
    botao.textContent = q.rotulo;
    botao.addEventListener("click", () => escolherPergunta(q.topico));
    box.appendChild(botao);
  });
}

function adicionarFala(tipo, autor, texto, hora, registrar = true) {
  const dialogo = document.getElementById("dialogo");
  const div = document.createElement("div");
  div.className = "fala " + tipo;
  if (tipo === "suspeito" && autor) {
    const avatar = document.createElement("span");
    avatar.className = "fala-avatar";
    avatar.setAttribute("aria-hidden", "true");
    avatar.textContent = autor.trim().charAt(0).toLocaleUpperCase("pt-BR");
    div.appendChild(avatar);
  }
  if (autor) {
    const nome = document.createElement("span");
    nome.className = "autor";
    nome.textContent = autor;
    div.appendChild(nome);
  }
  const conteudo = document.createElement("p");
  conteudo.className = "fala-texto";
  conteudo.textContent = texto;
  div.appendChild(conteudo);

  const horario = hora || new Date().toLocaleTimeString("pt-BR", {
    hour: "2-digit", minute: "2-digit",
  });
  const marcaTempo = document.createElement("time");
  marcaTempo.className = "fala-hora";
  marcaTempo.textContent = horario;
  div.appendChild(marcaTempo);

  dialogo.appendChild(div);
  dialogo.scrollTop = dialogo.scrollHeight;
  if (registrar) Interr.mensagens.push({ tipo, autor, texto, hora: horario });
}

function atualizarMedidor(n) {
  const pct = Math.min(100, Math.round((n / 6) * 100));
  document.getElementById("medidor-fill").style.width = pct + "%";
}

function rotuloDoTopico(topico) {
  const q = Interr.perguntas.find((x) => x.topico === topico);
  return q ? q.rotulo : topico;
}

function escolherPergunta(topico) {
  return enviarPergunta({ topico, texto: rotuloDoTopico(topico) });
}

async function enviarPergunta({ topico = null, texto }) {
  if (Interr.ocupado || !Interr.estado || !texto.trim()) return;
  Interr.ocupado = true;
  const input = document.getElementById("pergunta-livre");
  const enviar = document.querySelector(".enviar-mensagem");
  adicionarFala("detetive", "Detetive", texto.trim());
  if (input) input.value = "";
  if (input) input.disabled = true;
  if (enviar) enviar.disabled = true;
  renderizarPerguntas();

  const pensando = document.createElement("div");
  pensando.className = "indicador-digitando";
  pensando.setAttribute("aria-label", `${Interr.nome} está respondendo`);
  pensando.innerHTML = "<span></span><span></span><span></span>";
  document.getElementById("dialogo").appendChild(pensando);
  document.getElementById("dialogo").scrollTop = 1e9;
  await salvarConversa();

  try {
    const resposta = await fetch("/api/dialogo/perguntar", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        estado: Interr.estado,
        topico: topico,
        pergunta: topico ? undefined : texto.trim(),
      }),
    });
    const r = await resposta.json();
    await new Promise((res) => setTimeout(res, 480));
    pensando.remove();
    if (r.erro) {
      adicionarFala("suspeito", Interr.nome, r.erro);
      return;
    }

    Interr.estado = r.estado;
    Interr.perguntas = r.perguntas || [];
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
    adicionarFala("suspeito", Interr.nome, "Não foi possível conectar. Tente novamente.");
  } finally {
    Interr.ocupado = false;
    if (input) input.disabled = false;
    if (enviar) enviar.disabled = false;
    renderizarPerguntas();
    await salvarConversa();
    if (input) input.focus();
  }
}

document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("form-pergunta-livre");
  if (!form) return;
  form.addEventListener("submit", (evento) => {
    evento.preventDefault();
    const input = document.getElementById("pergunta-livre");
    enviarPergunta({ texto: input.value });
  });
});
