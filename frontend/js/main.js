$(document).ready(function () {
  const BASE_URL = "http://127.0.0.1:8000";

  // === GERENCIAMENTO DE CLIENTES ===
  function listarClientes() {
    let tbody = $("#clientes-tbody");
    if (!tbody.length) return;

    $.get(`${BASE_URL}/clientes/`, function (data) {
      tbody.empty();
      if (data.length === 0) {
        tbody.append(
          '<tr><td colspan="6" class="text-center text-muted py-3">Nenhum cliente registrado.</td></tr>',
        );
        return;
      }
      data.forEach(function (c) {
        let telf = c.telefone
          ? c.telefone
          : `<span class="text-muted small">Não informado</span>`;
        let row = `<tr>
                  <td><strong>${c.id}</strong></td>
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
    });
  }

  function popularSelectClientes(selectSelector) {
    let selectElement = $(selectSelector);
    if (!selectElement.length) return;

    $.get(`${BASE_URL}/clientes/`, function (clientes) {
      selectElement.find("option:not(:first)").remove();
      clientes.forEach((c) => {
        selectElement.append(`<option value="${c.id}">${c.nome}</option>`);
      });
    });
  }

  function carregarDadosCliente(id) {
    if (!id) return;
    $.get(`http://127.0.0.1:8000/clientes/${id}`, function (data) {
      $("#cliente-id").val(data.id);
      $("#nome").val(data.nome);
      $("#cpf_cnpj").val(data.cpf_cnpj);
      $("#email").val(data.email);
      $("#telefone").val(data.telefone || "");
    }).fail(function () {
      alert("Erro ao carregar dados do cliente.");
    });
  }

  function atualizarCliente(id, payload) {
    $.ajax({
      url: `http://127.0.0.1:8000/clientes/${id}`,
      method: "PUT",
      contentType: "application/json",
      data: JSON.stringify(payload),
      success: function (data) {
        $("#mensagem").html(
          `<div class="alert alert-success mt-3">Cliente atualizado com sucesso! <a href="index-clientes.html" class="alert-link">Voltar para a listagem</a></div>`,
        );
      },
      error: function (xhr) {
        let msg = "Erro ao atualizar cliente.";
        if (xhr.status === 422)
          msg = "Dados inválidos ou e-mail mal formatado.";
        $("#mensagem").html(
          `<div class="alert alert-danger mt-3">${msg}</div>`,
        );
      },
    });
  }

  // === GERENCIAMENTO DE PROCESSOS ===
  function carregarProcessos() {
    $.get(`${BASE_URL}/processos/`, function (data) {
      renderizarTabelaProcessos(data);
    }).fail(function (err) {
      console.error("Erro ao puxar processos do servidor:", err);
    });
  }

  function renderizarTabelaProcessos(processos) {
    let tbody = $("#processos-tbody");
    if (!tbody.length) return;
    tbody.empty();

    if (processos.length === 0) {
      tbody.append(
        `<tr><td colspan="5" class="text-center text-muted py-4">Nenhum processo encontrado.</td></tr>`,
      );
      return;
    }

    processos.forEach((p) => {
      let statusBadge = "bg-secondary";
      if (p.status === "Ativo") statusBadge = "bg-success";
      if (p.status === "Suspenso") statusBadge = "bg-warning text-dark";
      if (p.status === "Arquivado") statusBadge = "bg-danger";

      const linha = `<tr>
          <td><strong>${p.id}</strong></td>
          <td class="font-monospace fw-bold text-secondary">${p.numero}</td>
          <td><span class="badge ${statusBadge}">${p.status}</span></td>
          <td><div class="text-truncate" style="max-width: 250px;" title="${p.descricao}">${p.descricao}</div></td>
          <td class="text-center">
              <div class="btn-group" role="group">
                <a href="editar-processo.html?id=${p.id}" class="btn btn-sm btn-info fw-bold text-white shadow-sm">Editar</a>
                <button class="btn btn-sm btn-danger btn-deletar-processo fw-bold shadow-sm" data-id="${p.id}" data-numero="${p.numero}">
                  Excluir
                </button>
              </div>
          </td>
      </tr>`;
      tbody.append(linha);
    });
  }
  // === DENTRO DE frontend/js/main.js (No final do arquivo, antes de fechar o }); ) ===

  // Escutador ÚNICO para deleção de processos
  $(document)
    .off("click", ".btn-deletar-processo")
    .on("click", ".btn-deletar-processo", function () {
      const id = $(this).data("id");
      const numero = $(this).data("numero");

      if (confirm(`Deseja remover o processo CNJ: ${numero}?`)) {
        $.ajax({
          url: `http://127.0.0.1:8000/processos/${id}`,
          method: "DELETE",
          success: function () {
            alert("Processo removido com sucesso!");
            carregarProcessos(); // Recarrega a listagem de processos
          },
          error: function (xhr) {
            alert("Erro ao tentar remover o processo.");
            console.error(xhr);
          },
        });
      }
    });

  // Escutador ÚNICO para deleção de clientes
  $(document)
    .off("click", ".btn-deletar-cliente")
    .on("click", ".btn-deletar-cliente", function () {
      const id = $(this).data("id");
      const nome = $(this).data("nome");

      if (confirm(`Tem certeza que deseja excluir o cliente "${nome}"?`)) {
        $.ajax({
          url: `http://127.0.0.1:8000/clientes/${id}`,
          method: "DELETE",
          success: function () {
            alert("Cliente excluído com sucesso!");
            listarClientes(); // Recarrega a listagem de clientes
          },
          error: function (xhr) {
            alert(
              "Erro ao excluir cliente. Verifique se ele possui processos ativos vinculados.",
            );
            console.error(xhr);
          },
        });
      }
    });

  // Garanta que as funções estão expostas
  window.listarClientes = listarClientes;
  window.popularSelectClientes = popularSelectClientes;
  window.carregarProcessos = carregarProcessos;
  window.renderizarTabelaProcessos = renderizarTabelaProcessos;
  window.carregarDadosCliente = carregarDadosCliente;
  window.atualizarCliente = atualizarCliente;
}); // Fim do documento main.js
