document.addEventListener("DOMContentLoaded", function(){
    const provinciaSelect = document.getElementById("provincia");
    const ciudadSelect = document.getElementById("ciudad");

    const ciudadesPorProvincia = {
        caba: ["CABA"],
        buenos_aires: ["La Plata", "Mar del Plata", "Bahía Blanca", "Tandil", "Quilmes", "Lomas de Zamora", "Morón", "San Isidro"],
        catamarca: ["San Fernando del Valle de Catamarca", "Belén", "Andalgalá", "Tinogasta"],
        chaco: ["Resistencia", "Presidencia Roque Sáenz Peña", "Villa Ángela", "Charata"],
        chubut: ["Rawson", "Comodoro Rivadavia", "Trelew", "Puerto Madryn"],
        cordoba: ["Córdoba", "Villa Carlos Paz", "Río Cuarto", "Alta Gracia", "Villa María", "Jesús María", "Cosquín"],
        corrientes: ["Corrientes", "Goya", "Mercedes", "Paso de los Libres"],
        entre_rios: ["Paraná", "Concordia", "Gualeguaychú", "Gualeguay"],
        formosa: ["Formosa", "Clorinda", "Pirané", "El Colorado"],
        jujuy: ["San Salvador de Jujuy", "Palpalá", "Humahuaca", "San Pedro de Jujuy"],
        la_pampa: ["Santa Rosa", "General Pico", "Toay", "General Acha"],
        la_rioja: ["La Rioja", "Chilecito", "Aimogasta", "Chamical"],
        mendoza: ["Mendoza", "San Rafael", "Godoy Cruz", "San Martín", "Luján de Cuyo", "Malargüe"],
        misiones: ["Posadas", "Oberá", "Eldorado", "Puerto Iguazú"],
        neuquen: ["Neuquén", "San Martín de los Andes", "Zapala", "Cutral Có"],
        rio_negro: ["Viedma", "San Carlos de Bariloche", "General Roca", "Cipolletti"],
        salta: ["Salta", "Cafayate", "Orán", "Tartagal"],
        san_juan: ["San Juan", "Jáchal", "Caucete", "Rodeo"],
        san_luis: ["San Luis", "Villa Mercedes", "Merlo", "La Punta"],
        santa_cruz: ["Río Gallegos", "El Calafate", "Caleta Olivia", "Pico Truncado"],
        santa_fe: ["Santa Fe", "Rosario", "Rafaela", "Reconquista", "Venado Tuerto"],
        santiago_del_estero: ["Santiago del Estero", "La Banda", "Termas de Río Hondo", "Añatuya"],
        tierra_del_fuego: ["Ushuaia", "Río Grande", "Tolhuin"],
        tucuman: ["San Miguel de Tucumán", "Yerba Buena", "Tafí Viejo", "Concepción"]
    };

    provinciaSelect.addEventListener("change", function(){
        const provinciaSeleccionada = provinciaSelect.value;

        ciudadSelect.innerHTML = '<option value="">Selecciona una ciudad</option>';

        if (provinciaSeleccionada && ciudadesPorProvincia[provinciaSeleccionada]){
            const ciudades = ciudadesPorProvincia[provinciaSeleccionada];
            
            ciudades.forEach(function(ciudad){
                const option = document.createElement("option");
                option.value = ciudad.toLowerCase().replace(/ /g,"_");
                option.textContent=ciudad;
                ciudadSelect.appendChild(option);
            });

        }
    });

});