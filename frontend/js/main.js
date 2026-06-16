$(document).ready(function () {
  const BASE_URL = "http://127.0.0.1:8000";

  let paginaAtual = 1;
  const itensPorPagina = 10;

  let paginaProcessoAtual = 1;
  const itensPorPaginaProcesso = 10;

  const token = localStorage.getItem("token_legaltech");

  if (!token) {
    alert("Sessão inválida ou expirada. Por favor, refaça o login.");
    window.location.href = "login.html";
    return;
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
  // GERENCIAMENTO DE FORMULÁRIOS (CLIENTES)
  // ==========================================

  // Criar Cliente
  $("#form-criar-cliente").on("submit", function (e) {
    e.preventDefault();

    fetch(`${BASE_URL}/clientes/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        nome: document.getElementById("nome").value,
        cpf_cnpj: document.getElementById("cpf").value,
        email: document.getElementById("email").value,
        telefone: document.getElementById("telefone").value,
      }),
    })
      .then(async (response) => {
        if (response.ok) {
          alert("Cliente cadastrado com sucesso!");
          window.location.href = "index-clientes.html";
        } else {
          const erroDados = await response.json();
          alert(
            `Erro do Servidor: ${erroDados.detail || "Falha ao cadastrar"}`,
          );
        }
      })
      .catch((error) => console.error("Erro na requisição:", error));
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
        alert("Por favor, selecione um cliente válido antes de salvar.");
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
          alert("Processo criado com sucesso!");
          window.location.href = "lista-processos.html";
        },
        error: function (xhr) {
          alert(
            "Erro ao criar o processo. Verifique as informações preenchidas.",
          );
        },
      });
    },
  );

  // B. Editar Processo (PUT)
  $(document).on("submit", "#editar-form", function (e) {
    e.preventDefault();

    let rawId = $("#proc-id").val() || "";
    const id = parseInt(rawId.toString().replace(/\D/g, ""));

    if (!id || isNaN(id)) {
      alert("Erro: ID do processo inválido.");
      return;
    }

    const payload = {
      descricao: $("#descricao").val().trim(),
      status: $("#status-select").val(),
    };

    console.log("Enviando atualização compatível com ProcessoUpdate:", payload);

    $.ajax({
      url: `${BASE_URL}/processos/${id}`,
      method: "PUT",
      contentType: "application/json",
      data: JSON.stringify(payload),
      success: function (data) {
        alert("Processo updated com sucesso!");
        window.location.href = "lista-processos.html";
      },
      error: function (xhr) {
        $("#mensagem").html(
          `<div class="alert alert-danger">Erro ao atualizar processo. (${xhr.status})</div>`,
        );
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

    $.get(
      `${BASE_URL}/clientes/?limit=${itensPorPagina}&offset=${offset}`,
      function (resposta) {
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
                      <button class="btn btn-sm btn-danger btn-deletar-cliente fw-bold shadow-sm" data-id="${c.id}" data-nome="${c.nome}">
                        Excluir
                      </button>
                    </div>
                  </td>
              </tr>`;
          tbody.append(row);
        });

        renderizarPaginacaoGoogle(totalRegistros);
      },
    ).fail(function (xhr) {
      tratarErroAutenticacao(xhr);
    });
  }

  function renderizarPaginacaoGoogle(totalRegistros) {
    let container = $("#container-paginacao-google");
    if (!container.length) return;
    container.empty();

    const totalPaginas = Math.ceil(totalRegistros / itensPorPagina);
    if (totalPaginas <= 1) return;

    let htmlBotoes = `<nav><ul class="pagination pagination-sm justify-content-center shadow-sm">`;

    htmlBotoes += `
      <li class="page-item ${paginaAtual === 1 ? "disabled" : ""}">
        <a class="page-link ir-para-pagina" href="#" data-pagina="${paginaAtual - 1}">Anterior</a>
      </li>
    `;

    for (let i = 1; i <= totalPaginas; i++) {
      htmlBotoes += `
        <li class="page-item ${i === paginaAtual ? "active" : ""}">
          <a class="page-link ir-para-pagina" href="#" data-pagina="${i}">${i}</a>
        </li>
      `;
    }

    htmlBotoes += `
      <li class="page-item ${paginaAtual === totalPaginas ? "disabled" : ""}">
        <a class="page-link ir-para-pagina" href="#" data-pagina="${paginaAtual + 1}">Próxima</a>
      </li>
    `;

    htmlBotoes += `</ul></nav>`;
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

  function carregarDadosCliente(id) {
    if (!id) return;
    $.get(`${BASE_URL}/clientes/${id}`, function (data) {
      $("#cliente-id").val(data.id);
      $("#nome").val(data.nome);
      $("#cpf_cnpj").val(data.cpf_cnpj);
      $("#email").val(data.email);
      $("#telefone").val(data.telefone || "");
    }).fail(function (xhr) {
      alert("Erro ao carregar dados do cliente.");
      tratarErroAutenticacao(xhr);
    });
  }

  function atualizarCliente(id, payload) {
    $.ajax({
      url: `${BASE_URL}/clientes/${id}`,
      method: "PUT",
      contentType: "application/json",
      data: JSON.stringify(payload),
      success: function (data) {
        $("#mensagem").html(
          `<div class="alert alert-success mt-3">Cliente atualizado com sucesso! <a href="index-clientes.html" class="alert-link">Voltar para a listagem</a></div>`,
        );
      },
      error: function (xhr) {
        if (xhr.status === 401 || xhr.status === 403) {
          tratarErroAutenticacao(xhr);
          return;
        }
        let msg = "Erro ao atualizar cliente.";
        if (xhr.status === 422)
          msg = "Dados inválidos ou e-mail mal formatado.";
        $("#mensagem").html(
          `<div class="alert alert-danger mt-3">${msg}</div>`,
        );
      },
    });
  }

  // REQUISITO 2 & 3: Listagem Dinâmica Estilo Google
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

    $.get(url, function (resposta) {
      const lista = resposta.dados || [];
      const totalRegistros = resposta.total || 0;

      renderizarTabelaProcessos(lista);
      renderizarPaginacaoProcessos(totalRegistros);
    }).fail(function (xhr) {
      console.error("Erro ao carregar processos do servidor:", xhr);
      tratarErroAutenticacao(xhr);
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

      // Mapeamento seguro do nome do cliente embutido
      let nomeExibicao = "Não informado";
      if (p.cliente && p.cliente.nome) {
        nomeExibicao = p.cliente.nome;
      } else if (p.cliente_nome) {
        nomeExibicao = p.cliente_nome;
      }

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

  // EVENTOS DE BUSCA INSTANTÂNEA
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
  // EXCLUSÃO E SISTEMA GLOBAL
  // ==========================================

  $(document)
    .off("click", ".btn-deletar-processo")
    .on("click", ".btn-deletar-processo", function () {
      const id = $(this).data("id");
      const numero = $(this).data("numero");

      if (confirm(`Deseja remover o processo CNJ: ${numero}?`)) {
        $.ajax({
          url: `${BASE_URL}/processos/${id}`,
          method: "DELETE",
          success: function () {
            alert("Processo removido com sucesso!");
            listarProcessos();
          },
          error: function (xhr) {
            if (xhr.status === 403) {
              alert(
                "Acesso negado. Apenas administradores podem excluir processos.",
              );
            } else {
              alert("Erro ao tentar remover o processo.");
            }
            console.error(xhr);
          },
        });
      }
    });

  $(document)
    .off("click", ".btn-deletar-cliente")
    .on("click", ".btn-deletar-cliente", function () {
      const id = $(this).data("id");
      const nome = $(this).data("nome");

      if (confirm(`Tem certeza que deseja excluir o cliente "${nome}"?`)) {
        $.ajax({
          url: `${BASE_URL}/clientes/${id}`,
          method: "DELETE",
          success: function () {
            alert("Cliente excluído com sucesso!");
            listarClientes();
          },
          error: function (xhr) {
            if (xhr.status === 403) {
              alert(
                "Acesso negado. Apenas administradores podem excluir clientes.",
              );
            } else {
              alert(
                "Erro ao excluir cliente. Verifique se ele possui processos vinculados.",
              );
            }
            console.error(xhr);
          },
        });
      }
    });

  $(document).on("click", "#btn-logout", function (e) {
    e.preventDefault();
    localStorage.removeItem("token_legaltech");
    alert("Sessão encerrada!");
    window.location.href = "login.html";
  });

  function tratarErroAutenticacao(xhr) {
    if (xhr.status === 401 || xhr.status === 403) {
      alert(
        "Sessão expirada ou nível de acesso insuficiente. Por favor, faça login novamente.",
      );
      window.location.href = "login.html";
    }
  }

  // Inicializações automáticas
  listarClientes();
  listarProcessos();
  popularSelectClientes("#select-clientes");

  // Escopo Global
  window.listarClientes = listarClientes;
  window.popularSelectClientes = popularSelectClientes;
  window.listarProcessos = listarProcessos;
  window.renderizarTabelaProcessos = renderizarTabelaProcessos;
  window.carregarDadosCliente = carregarDadosCliente;
  window.atualizarCliente = atualizarCliente;
});
