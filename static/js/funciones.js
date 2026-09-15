let currentPedidoId = null;

function mostrarModalPedido(texto, id) {
  currentPedidoId = id;

  document.getElementById("pedidoTexto").value = texto;
  document.getElementById("pedidoForm").action = `/editar/${id}/`;

  const formEliminar = document.getElementById("formEliminar");
  if (formEliminar) {
    formEliminar.action = `/eliminar/${id}/`;
  }

  const modal = new bootstrap.Modal(document.getElementById("pedidoModal"));
  modal.show();
}

function confirmarDespacho(id) {
  // Cierra el modal de edición si está abierto
  const pedidoModal = bootstrap.Modal.getInstance(document.getElementById("pedidoModal"));
  if (pedidoModal) {
    pedidoModal.hide();
  }

  // Asigna las URLs dinámicamente a los formularios
  document.getElementById("formImprimir").action = `/despachar/${id}/`;
  document.getElementById("formDespachar").action = `/despachar/${id}/`;

  // Muestra el modal de confirmación
  const modal = new bootstrap.Modal(document.getElementById("confirmarDespachoModal"));
  modal.show();
}
