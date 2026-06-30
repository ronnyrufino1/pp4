$(document).ready(function () {
  const BASE_URL = "http://127.0.0.1:8000";

  let paginaAtual = 1;
  const itensPorPagina = 10;

  let paginaProcessoAtual = 1;
  const itensPorPaginaProcesso = 10;

  const token = localStorage.getItem("token_legaltech");
  const urlAtual = window.location.pathname;

  function obterParametroUrl(nomeParametro) {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get(nomeParametro);
  }

  const ehPaginaPublica =
    urlAtual.endsWith("login.html") ||
    urlAtual.endsWith("cadastro.html") ||
    urlAtual === "/" ||
    urlAtual.endsWith("index.html");

  if (!token) {
    if (!ehPaginaPublica) {
      setTimeout(() => {
        exibirToast(
          "Sessão inválida ou expirada. Por favor, refaça o login.",
          "warning",
        );
      }, 500);
      window.location.href = "login.html";
      return;
    }
    if (ehPaginaPublica) {
      console.log("Acesso público detectado. Aguardando login...");
    }
  }

  $.ajaxSetup({
    beforeSend: function (xhr) {
      const tokenValido = localStorage.getItem("token_legaltech");
      if (tokenValido) {
        xhr.setRequestHeader("Authorization", `Bearer ${tokenValido}`);
      }
    },
  });

  // ==========================================
  // UTILITÁRIOS INTERFACES (TOASTS E MODALS)
  // ==========================================

  function exibirToast(mensagem, variante = "info") {
    $(".toast-container").remove();

    const titulos = {
      success: "Sucesso",
      danger: "Erro",
      warning: "Atenção",
      info: "Informação",
    };

    const toastHTML = `
        <div class="toast-container position-fixed bottom-0 end-0 p-3" style="z-index: 1100">
            <div id="liveToast" class="toast align-items-center text-white bg-${variante} border-0 shadow" role="alert" aria-live="assertive" aria-atomic="true">
                <div class="d-flex">
                    <div class="toast-body">
                        <strong>${titulos[variante] || "Aviso"}:</strong> ${mensagem}
                    </div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
                </div>
            </div>
        </div>
    `;

    $("body").append(toastHTML);
    const toastElement = document.getElementById("liveToast");
    const toast = new bootstrap.Toast(toastElement, { delay: 4000 });
    toast.show();
  }

  function exibirModalConfirmacao(titulo, mensagem, acaoConfirmar) {
    $("#modalConfirmacaoGlobal").remove();

    const modalHTML = `
        <div class="modal fade" id="modalConfirmacaoGlobal" tabindex="-1" aria-labelledby="modalConfirmacaoLabel" aria-hidden="true">
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content">
                    <div class="modal-header bg-light">
                        <h5 class="modal-title fw-bold text-dark" id="modalConfirmacaoLabel">${titulo}</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                    </div>
                    <div class="modal-body fs-5 text-secondary">
                        ${mensagem}
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary fw-bold" data-bs-dismiss="modal">Cancelar</button>
                        <button type="button" id="btnConfirmarAcaoGlobal" class="btn btn-danger fw-bold">Confirmar</button>
                    </div>
                </div>
            </div>
        </div>
    `;

    $("body").append(modalHTML);
    const modalElement = document.getElementById("modalConfirmacaoGlobal");
    const modal = new bootstrap.Modal(modalElement);
    modal.show();

    $("#btnConfirmarAcaoGlobal")
      .off("click")
      .on("click", function () {
        acaoConfirmar();
        modal.hide();
      });
  }

  // ==========================================
  // GERENCIAMENTO DE FORMULÁRIOS (CLIENTES)
  // ==========================================

  // Criar Cliente (Migrado para $.ajax robusto)
  $("#form-criar-cliente").on("submit", function (e) {
    e.preventDefault();

    const payload = {
      nome: $("#nome").val(),
      cpf_cnpj: $("#cpf").val(),
      email: $("#email").val(),
      telefone: $("#telefone").val(),
    };

    $.ajax({
      url: `${BASE_URL}/clientes/`,
      method: "POST",
      contentType: "application/json",
      data: JSON.stringify(payload),
      success: function (resposta) {
        exibirToast("Cliente cadastrado com sucesso!", "success");
        setTimeout(() => {
          window.location.href = "index-clientes.html";
        }, 1500);
      },
      error: function (xhr) {
        let erroMsg = "Falha ao cadastrar cliente.";
        if (xhr.responseJSON && xhr.responseJSON.detail) {
          erroMsg = xhr.responseJSON.detail;
        }
        exibirToast(`Erro do Servidor: ${erroMsg}`, "danger");
      },
    });
  });

  // ==========================================
  // GERENCIAMENTO DE FORMULÁRIOS (PROCESSOS)
  // ==========================================

  // A. Criar Processo (POST)
  $(document).on(
    "submit",
    "#form-criar-processo, #processo-form",
    function (e) {
      e.preventDefault();

      let rawNumero =
        $("#numero").val() || $("input[name='numero']").val() || "";
      let statusProc =
        $("#status").val() || $("#status_inicial").val() || "Ativo";
      let descProc =
        $("#descricao").val() || $("textarea[name='descricao']").val() || "";
      let rawClienteId =
        $("#select-clientes").val() || $("#cliente-select").val();
      let clienteId = parseInt(rawClienteId);

      if (!clienteId || isNaN(clienteId)) {
        exibirToast(
          "Por favor, selecione um cliente válido antes de salvar.",
          "warning",
        );
        return;
      }

      const payload = {
        cliente_id: clienteId,
        numero_cnj: rawNumero.trim(),
        descricao: descProc.trim(),
        status: statusProc,
      };

      $.ajax({
        url: `${BASE_URL}/processos/`,
        method: "POST",
        contentType: "application/json",
        data: JSON.stringify(payload),
        success: function (resposta) {
          exibirToast("Processo criado com sucesso!", "success");
          setTimeout(() => {
            window.location.href = "lista-processos.html";
          }, 1500);
        },
        error: function (xhr) {
          exibirToast(
            "Erro ao criar o processo. Verifique as informações preenchidas.",
            "danger",
          );
        },
      });
    },
  );

  // B. Editar Processo (PUT) - CORRIGIDO para coletar ID da URL caso input mudo
  $(document).on("submit", "#editar-form", function (e) {
    e.preventDefault();

    let rawId = $("#proc-id").val() || obterParametroUrl("id") || "";
    const id = parseInt(rawId.toString().replace(/\D/g, ""));

    if (!id || isNaN(id)) {
      exibirToast("Erro: ID do processo inválido para atualização.", "danger");
      return;
    }

    const payload = {
      descricao: $("#descricao").val().trim(),
      status: $("#status-select").val() || $("#status").val(),
    };

    $.ajax({
      url: `${BASE_URL}/processos/${id}`,
      method: "PUT",
      contentType: "application/json",
      data: JSON.stringify(payload),
      success: function (data) {
        exibirToast("Processo atualizado com sucesso!", "success");
        setTimeout(() => {
          window.location.href = "lista-processos.html";
        }, 1500);
      },
      error: function (xhr) {
        exibirToast(`Erro ao atualizar processo. (${xhr.status})`, "danger");
      },
    });
  });

  // ==========================================
  // LISTAGEM E PAGINAÇÃO DE CLIENTES
  // ==========================================

  function listarClientes() {
    let tbody = $("#clientes-tbody");
    if (!tbody.length) return;

    const offset = (paginaAtual - 1) * itensPorPagina;

    $.ajax({
      url: `${BASE_URL}/clientes/?limit=${itensPorPagina}&offset=${offset}`,
      method: "GET",
      success: function (resposta) {
        tbody.empty();
        const clientes = resposta.dados;
        const totalRegistros = resposta.total;

        if (!clientes || clientes.length === 0) {
          tbody.append(
            '<tr><td colspan="5" class="text-center text-muted py-3">Nenhum cliente registrado.</td></tr>',
          );
          renderizarPaginacaoGoogle(0);
          return;
        }

        clientes.forEach(function (c) {
          let telf = c.telefone
            ? c.telefone
            : `<span class="text-muted small">Não informado</span>`;
          let row = `<tr>
                  <td class="fw-bold">${c.nome}</td>
                  <td>${c.cpf_cnpj}</td>
                  <td><a href="mailto:${c.email}">${c.email}</a></td>
                  <td>${telf}</td>
                  <td class="text-center">
                    <div class="btn-group" role="group">
                      <a href="editar-cliente.html?id=${c.id}" class="btn btn-sm btn-info fw-bold text-white shadow-sm">Editar</a>
                      <button class="btn btn-sm btn-danger btn-deletar-cliente fw-bold shadow-sm" data-id="${c.id}" data-nome="${c.nome}">Excluir</button>
                    </div>
                  </td>
              </tr>`;
          tbody.append(row);
        });

        renderizarPaginacaoGoogle(totalRegistros);
      },
      error: function (xhr) {
        tratarErroAutenticacao(xhr);
      },
    });
  }

  function renderizarPaginacaoGoogle(totalRegistros) {
    let container = $("#container-paginacao-google");
    if (!container.length) return;
    container.empty();

    const totalPaginas = Math.ceil(totalRegistros / itensPorPagina);
    if (totalPaginas <= 1) return;

    let htmlBotoes = `<nav><ul class="pagination pagination-sm justify-content-center shadow-sm">`;
    htmlBotoes += `<li class="page-item ${paginaAtual === 1 ? "disabled" : ""}"><a class="page-link ir-para-pagina" href="#" data-pagina="${paginaAtual - 1}">Anterior</a></li>`;

    for (let i = 1; i <= totalPaginas; i++) {
      htmlBotoes += `<li class="page-item ${i === paginaAtual ? "active" : ""}"><a class="page-link ir-para-pagina" href="#" data-pagina="${i}">${i}</a></li>`;
    }

    htmlBotoes += `<li class="page-item ${paginaAtual === totalPaginas ? "disabled" : ""}"><a class="page-link ir-para-pagina" href="#" data-pagina="${paginaAtual + 1}">Próxima</a></li></ul></nav>`;
    container.append(htmlBotoes);
  }

  $(document).on("click", ".ir-para-pagina", function (e) {
    e.preventDefault();
    const paginaAlvo = $(this).data("pagina");
    if (paginaAlvo && paginaAlvo !== paginaAtual) {
      paginaAtual = paginaAlvo;
      listarClientes();
    }
  });

  // ==========================================
  // LISTAGEM, SELEÇÃO E BUSCA DE PROCESSOS
  // ==========================================

  function popularSelectClientes(seletor) {
    $.ajax({
      url: `${BASE_URL}/clientes/`,
      method: "GET",
      success: function (dados) {
        const lista = dados.dados || dados;
        const $select = $(seletor);
        $select.find("option:not(:first)").remove();

        lista.forEach(function (cliente) {
          $select.append(
            `<option value="${cliente.id}">${cliente.nome}</option>`,
          );
        });
      },
      error: function (xhr) {
        console.error("Erro ao carregar lista de clientes para o select:", xhr);
      },
    });
  }

  // Carregar Dados Cliente (Ajustado rota para /{id} sem underline)
  function carregarDadosCliente(id) {
    if (!id) return;
    $.ajax({
      url: `${BASE_URL}/clientes/${id}`,
      method: "GET",
      success: function (data) {
        $("#cliente-id").val(data.id);
        $("#nome").val(data.nome);
        $("#cpf_cnpj").val(data.cpf_cnpj);
        $("#email").val(data.email);
        $("#telefone").val(data.telefone || "");
      },
      error: function (xhr) {
        exibirToast("Erro ao carregar dados do cliente.", "danger");
        tratarErroAutenticacao(xhr);
      },
    });
  }

  // Atualizar Cliente (Ajustado rota para /{id} e formulário associado)
  function atualizarCliente(id, payload) {
    $.ajax({
      url: `${BASE_URL}/clientes/${id}`,
      method: "PUT",
      contentType: "application/json",
      data: JSON.stringify(payload),
      success: function (data) {
        exibirToast("Cliente atualizado com sucesso!", "success");
        setTimeout(() => {
          window.location.href = "index-clientes.html";
        }, 1500);
      },
      error: function (xhr) {
        if (xhr.status === 401 || xhr.status === 403) {
          tratarErroAutenticacao(xhr);
          return;
        }
        let msg = "Erro ao atualizar cliente.";
        if (xhr.status === 422)
          msg = "Dados inválidos ou e-mail mal formatado.";
        exibirToast(msg, "danger");
      },
    });
  }

  // Captura o envio do formulário específico de Editar Cliente
  $(document).on("submit", "#form-editar-cliente", function (e) {
    e.preventDefault();
    const idCliente = $("#cliente-id").val() || obterParametroUrl("id");
    const payload = {
      nome: $("#nome").val(),
      cpf_cnpj: $("#cpf_cnpj").val(),
      email: $("#email").val(),
      telefone: $("#telefone").val(),
    };
    if (idCliente) atualizarCliente(idCliente, payload);
  });

  function listarProcessos() {
    let tbody = $("#processos-tbody");
    if (!tbody.length) return;

    let termoBusca = $("#campo-busca-google").val() || "";
    let statusFiltro = $("#filtro-status-select").val() || "Todos";

    const offset = (paginaProcessoAtual - 1) * itensPorPaginaProcesso;

    let url = `${BASE_URL}/processos/?limit=${itensPorPaginaProcesso}&offset=${offset}`;
    if (termoBusca.trim() !== "")
      url += `&termo=${encodeURIComponent(termoBusca.trim())}`;
    if (statusFiltro !== "Todos")
      url += `&status=${encodeURIComponent(statusFiltro)}`;

    $.ajax({
      url: url,
      method: "GET",
      success: function (resposta) {
        const lista = resposta.dados || [];
        const totalRegistros = resposta.total || 0;
        renderizarTabelaProcessos(lista);
        renderizarPaginacaoProcessos(totalRegistros);
      },
      error: function (xhr) {
        exibirToast("Erro ao carregar processos da listagem.", "danger");
        tratarErroAutenticacao(xhr);
      },
    });
  }

  function renderizarTabelaProcessos(processos) {
    let tbody = $("#processos-tbody");
    if (!tbody.length) return;
    tbody.empty();

    if (!processos || processos.length === 0) {
      tbody.append(
        '<tr><td colspan="5" class="text-center text-muted py-4">Nenhum processo encontrado.</td></tr>',
      );
      return;
    }

    processos.forEach((p) => {
      let statusBadge = "bg-secondary";
      if (p.status === "Ativo") statusBadge = "bg-success";
      if (p.status === "Suspenso") statusBadge = "bg-warning text-dark";
      if (p.status === "Arquivado") statusBadge = "bg-danger";

      let nomeExibicao = p.cliente?.nome || p.cliente_nome || "Não informado";
      let numeroExibicao = p.numero_cnj || p.numero || "Não informado";

      let linha = `
            <tr>
                <td class="text-monospace fw-bold text-secondary">${numeroExibicao}</td>
                <td><span class="badge bg-light text-dark">${nomeExibicao}</span></td>
                <td><span class="badge ${statusBadge}">${p.status || "Sem Status"}</span></td>
                <td><div class="text-truncate" style="max-width: 250px;" title="${p.descricao || ""}">${p.descricao || "Sem descrição"}</div></td>
                <td class="text-center">
                    <div class="btn-group" role="group">
                        <a href="editar-processo.html?id=${p.id}" class="btn btn-sm btn-info fw-bold text-white">Editar</a>
                        <button class="btn btn-sm btn-danger btn-deletar-processo" data-id="${p.id}" data-numero="${numeroExibicao}">Excluir</button>
                    </div>
                </td>
            </tr>
        `;
      tbody.append(linha);
    });
  }

  function renderizarPaginacaoProcessos(totalRegistros) {
    let container = $("#container-paginacao-processos");
    if (!container.length) return;
    container.empty();

    const totalPaginas = Math.ceil(totalRegistros / itensPorPaginaProcesso);
    if (totalPaginas <= 1) return;

    let htmlBotoes = `<nav><ul class="pagination pagination-sm justify-content-center shadow-sm">`;
    htmlBotoes += `<li class="page-item ${paginaProcessoAtual === 1 ? "disabled" : ""}"><a class="page-link pg-processo" href="#" data-pagina="${paginaProcessoAtual - 1}">Anterior</a></li>`;

    for (let i = 1; i <= totalPaginas; i++) {
      htmlBotoes += `<li class="page-item ${i === paginaProcessoAtual ? "active" : ""}"><a class="page-link pg-processo" href="#" data-pagina="${i}">${i}</a></li>`;
    }

    htmlBotoes += `<li class="page-item ${paginaProcessoAtual === totalPaginas ? "disabled" : ""}"><a class="page-link pg-processo" href="#" data-pagina="${paginaProcessoAtual + 1}">Próxima</a></li></ul></nav>`;
    container.append(htmlBotoes);
  }

  $(document).on("input", "#campo-busca-google", function () {
    paginaProcessoAtual = 1;
    listarProcessos();
  });

  $(document).on("change", "#filtro-status-select", function () {
    paginaProcessoAtual = 1;
    listarProcessos();
  });

  $(document).on("click", ".pg-processo", function (e) {
    e.preventDefault();
    paginaProcessoAtual = $(this).data("pagina");
    listarProcessos();
  });

  // ==========================================
  // EXCLUSÕES INTERATIVAS COM MODAL
  // ==========================================

  $(document).on("click", ".btn-deletar-cliente", function (e) {
    e.preventDefault();
    const idCliente = $(this).data("id");
    const nomeCliente = $(this).data("nome") || "este cliente";

    exibirModalConfirmacao(
      "Confirmar Exclusão de Cliente",
      `Tem certeza de que deseja remover o cliente <strong>${nomeCliente}</strong>? <br><small class="text-danger">Aviso: Isso pode quebrar vínculos caso ele possua processos ativos.</small>`,
      function () {
        $.ajax({
          url: `${BASE_URL}/clientes/${idCliente}`,
          type: "DELETE",
          success: function () {
            exibirToast("Cliente removido com sucesso!", "success");
            listarClientes();
          },
          error: function (xhr) {
            exibirToast(
              "Erro ao excluir cliente. Verifique as restrições no servidor.",
              "danger",
            );
          },
        });
      },
    );
  });

  $(document).on("click", ".btn-deletar-processo", function (e) {
    e.preventDefault();
    let idProcesso = $(this).data("id");
    let numeroCNJ = $(this).data("numero") || "este processo";

    if (!idProcesso) {
      exibirToast("Erro: ID do processo não localizado.", "danger");
      return;
    }

    exibirModalConfirmacao(
      "Confirmar Exclusão de Registro",
      `Tem certeza que deseja excluir o processo <strong>Nº ${numeroCNJ}</strong>? <br><small class="text-danger">Esta ação é irreversível e não pode ser desfeita.</small>`,
      function () {
        $.ajax({
          url: `${BASE_URL}/processos/${idProcesso}`,
          type: "DELETE",
          success: function () {
            exibirToast("Processo removido com sucesso!", "success");
            listarProcessos();
          },
          error: function (xhr) {
            if (xhr.status === 403 || xhr.status === 401) {
              exibirToast(
                "Erro: Você não tem permissão para realizar essa exclusão.",
                "danger",
              );
            } else {
              exibirToast("Erro ao tentar remover o processo.", "danger");
            }
          },
        });
      },
    );
  });

  $(document).on("click", "#btn-logout", function (e) {
    e.preventDefault();
    localStorage.removeItem("token_legaltech");
    exibirToast("Sessão encerrada!", "info");
    setTimeout(() => {
      window.location.href = "login.html";
    }, 1000);
  });

  function tratarErroAutenticacao(xhr) {
    if (xhr.status === 401 || xhr.status === 403) {
      exibirToast(
        "Sessão expirada ou nível de acesso insuficiente. Redirecionando...",
        "danger",
      );
      localStorage.removeItem("token_legaltech");
      setTimeout(() => {
        window.location.href = "login.html";
      }, 2000);
    }
  }

  // ==========================================
  // CICLO DE VIDA E INICIALIZAÇÃO AUTOMÁTICA
  // ==========================================
  const idUrl = obterParametroUrl("id");
  const paginaNome = window.location.pathname;

  if (token && !ehPaginaPublica) {
    if (paginaNome.includes("index-clientes.html")) {
      listarClientes();
    }

    if (paginaNome.includes("lista-processos.html")) {
      listarProcessos();
      popularSelectClientes("#select-clientes");
    }

    if (paginaNome.includes("editar-processo.html") && idUrl) {
      console.log("Buscando dados do processo ID:", idUrl);
      $.ajax({
        url: `${BASE_URL}/processos/${idUrl}`,
        method: "GET",
        success: function (processo) {
          $("#proc-id").val(processo.id);
          $("#numero, input[name='numero']").val(
            processo.numero_cnj || processo.numero,
          );
          $("#descricao").val(processo.descricao);
          $("#status-select, #status").val(processo.status);
        },
        error: function () {
          exibirToast(
            "Erro ao resgatar dados do processo para edição.",
            "danger",
          );
        },
      });
    }

    if (paginaNome.includes("editar-cliente.html") && idUrl) {
      carregarDadosCliente(idUrl);
    }
  }

  // Escopo Global para chamadas inline herdadas
  window.listarClientes = listarClientes;
  window.popularSelectClientes = popularSelectClientes;
  window.listarProcessos = listarProcessos;
  window.renderizarTabelaProcessos = renderizarTabelaProcessos;
  window.carregarDadosCliente = carregarDadosCliente;
  window.atualizarCliente = atualizarCliente;
  window.exibirToast = exibirToast;
  window.exibirModalConfirmacao = exibirModalConfirmacao;
});
