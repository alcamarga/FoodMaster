setInterval(() => {
    fetch('/estado_mesa')
        .then(response => response.json())
        .then(data => {
            this.estadoMesa = data.estado;
        });
}, 5000);