document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById('main-form');
    const dynamicContentContainer = document.getElementById('dynamic-content');
    const modalResponseContent = document.getElementById('modalResponseContent');
  
    // Manejar la selección de un endpoint (dinámico)
    document.querySelectorAll('input[name="option"]').forEach(function (radio) {
        radio.addEventListener('change', function () {
            const selectedOption = this.value;
  
            // Solicitar contenido dinámico
            fetch(`/api/content?option=${selectedOption}`)
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`Error al cargar contenido dinámico: ${response.status}`);
                    }
                    return response.text();
                })
                .then(data => {
                    dynamicContentContainer.innerHTML = data; // Mostrar contenido dinámico
                })
                .catch(error => {
                    console.error("Error al cargar contenido dinámico:", error);
                    alert('Hubo un error al cargar el contenido dinámico. Inténtalo nuevamente.');
                });
        });
    });
  
    // Manejar el envío del formulario
    form.addEventListener('submit', function (e) {
        e.preventDefault(); // Evitar el envío estándar del formulario
  
        // Capturar los datos del formulario principal y dinámico
        const formData = new FormData(form);
        const formDataObj = Object.fromEntries(formData.entries());
  
        // Incluir los datos dinámicos
        const dynamicInputs = dynamicContentContainer.querySelectorAll('input, select, textarea');
        dynamicInputs.forEach(input => {
            if (input.name) {
                formDataObj[input.name] = input.value;
            }
        });
  
        // Enviar datos al backend
        fetch(form.action, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json', // Enviar como JSON
            },
            body: JSON.stringify(formDataObj), // Convertir a JSON
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`Error en la solicitud: ${response.status}`);
            }
            return response.json(); // Convertir la respuesta a JSON
        })
        .then(data => {

            // Mapear datos recibidos al modal
        document.getElementById("transaction-id").textContent =
        data.transactionId || "N/A";
        document.getElementById("transaction-status").textContent =
        data.status || "N/A";
        document.getElementById("transaction-amount").textContent =
        data.amount ? `$${data.amount} MXN` : "N/A";
        document.getElementById("transaction-datetime").textContent =
        data.dateTime || "N/A";

        // Mostrar el modal
        const modal = new bootstrap.Modal(
        document.getElementById("responseModal")
        );
        modal.show();
    })
    .catch((error) => {
        console.error("Error al enviar el formulario:", error);
        modalResponseContent.innerHTML = `<p class="text-danger">Hubo un error al enviar el formulario: ${error.message}</p>`;
        const modal = new bootstrap.Modal(document.getElementById("responseModal"));
        
        modal.show();
        });
    });
  });