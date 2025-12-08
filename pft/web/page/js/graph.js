function build_dataset(timestamps, type_data, mesure, seed, label) {
    // Transformation des données pour Chart.js
    
    const dataPoints = timestamps.map((timestamp, index) => ({
        x: new Date(timestamp), // Convertir la date en objet Date
        y: type_data[mesure]["value"][index] // Valeur associée
    }));
    
    return {
        label: label,
        data: dataPoints,
        extraData: {},
        borderColor: randomColor(seed),
        borderWidth: 1,
        showLine: true, // Afficher une courbe entre les points
        pointRadius: 10, // Taille des flèches
        pointStyle: false // Si pas d'angle, mettre un point normal
    };
}

function build_row(timestamps, type_data, mesure, sensors=null, sensor=null) {
    var dataPoints = []
    
    for (const index in timestamps) {
        if (Object.prototype.hasOwnProperty.call(timestamps, index)) {
            if (sensors[index] == sensor) {
                const h = Math.floor(timestamps[index]/60);
                const m = Math.floor(timestamps[index]%60);
                
                dataPoints.push({
                    date: h + "h " + m + "min",
                    mesure: mesure,
                    sensor: sensors[index],
                    value: type_data[index]
                });
            }
        }
    }
    
    return dataPoints;
}

function build_chart(ctx, datasets, data_type) {
    new Chart(ctx, {
        type: 'scatter',
        data: {
            datasets: datasets
        },
        options: {
            responsive: true,
            plugins: {
                title: {
                    display: true,
                    text: data_type.toUpperCase() + ' :',
                },
                zoom: {
                    pan: {
                        enabled: true, // Activer le glisser-déposer (pan)
                        mode: 'xy',   // Permettre le pan sur les deux axes (X et Y)
                    },
                    zoom: {
                        wheel: {
                            enabled: true, // Activer le zoom avec la molette de la souris
                        },
                        pinch: {
                            enabled: true // Activer le zoom par pincement sur les écrans tactiles
                        },
                        mode: 'xy',   // Permettre le zoom sur les deux axes (X et Y)
                    }
                }
            },
            scales: {
                x: {
                    type: 'linear',
                    position: 'bottom',
                    ticks: {
                        callback: function (value, index, ticks) {
                            const h = Math.floor(value/60);
                            const m = Math.floor(value%60);
                            return h + "h " + m + "min";
                        }
                    }
                }
            }
        }
    });
}

function build_table(table_id, rows) {
    let text = ""
    rows.sort((a, b) => b.date - a.date);
    rows.forEach(element => {
        text=`
        <tr class="bg-white border-b dark:bg-gray-800 dark:border-gray-700 border-gray-200">
            <th class="w-4 p-4">
                <div class="flex items-center">
                    <input type="checkbox" class="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded-sm focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-gray-800 dark:focus:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600">
                </div>
            </th>
            <th scope="row" class="px-6 py-4 font-medium text-gray-900 whitespace-nowrap dark:text-white">${element.date}</th>
            <td class="px-6 py-4">${element.mesure}</td>
            <td class="px-6 py-4">${element.sensor}</td>
            <td class="px-6 py-4">${element.value}</td>
        </tr>` + text;
    })
    document.getElementById(table_id).innerHTML = text
    
}

function getTempsBySensor(data, sensors, timestamps) {
    const sensor_id = [...new Set(sensors)];
    const result = {};

    sensor_id.forEach(sensor => {
        result[sensor] = {timestamps: [], value: []}
        for (let i = 0; i < data.length; i++) {
            if (sensors[i] === sensor) {
              
              if (data[i] !== undefined) {
                result[sensor].timestamps.push(timestamps[i]);
                result[sensor].value.push(data[i]);
              }
            }
          }
    });
    
    return result;
  }

function prebuit(chart_id, table_id, mesure, data_type, dtime) {
    mesure = decodeURIComponent(mesure);
    return get_data(mesure, data_type, dtime).then(function (json) {
        
        let rows = [];
        let datasets = [];
        
        if (!mesure) {
            const ctx = document.getElementById(chart_id).getContext('2d');
            let seed = 0
            let data = {};
            const template = (mesure, sonde) => `
            <li>
                <div class="flex items-center w-full p-2 text-gray-900 transition duration-75 rounded-lg pl-11 group hover:bg-gray-100 dark:text-white dark:hover:bg-gray-700">
                    <input id="checkbox-${mesure}-${sonde}" type="checkbox" value="" class="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded-sm focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600">
                    <label for="checkbox-${mesure}-${sonde}" class="ms-2 text-sm font-medium text-gray-900 dark:text-gray-300">${sonde}</label>
                </div>
            </li>
            `;

            for (let mes in json) {
                const ul = document.getElementById('dropdown-'+mes);
                ul.innerHTML = "";

                if (!showed_data[mes]) {
                    showed_data[mes] = [];
                }
                
                data = getTempsBySensor(json[mes][data_type], json[mes]["sensor_id"], json[mes]["time"])
                sensor_id = [...new Set(json[mes]["sensor_id"])]
                sensor_id.forEach(sensor => {
                    ul.insertAdjacentHTML('beforeend', template(mes, sensor));

                    const checkbox = document.getElementById(`checkbox-${mes}-${sensor}`);

                    if (showed_data[mes].includes(sensor)) {
                        checkbox.checked = true;
                    }

                    checkbox.addEventListener('change', function () {
                        if (checkbox.checked) {
                            showed_data[mes].push(sensor)
                        } else {
                            showed_data[mes].splice(showed_data[mes].indexOf(sensor), 1)
                        }
                        
                        update_view(chart_id, table_id, mesure, data_type, dtime)
                    });
                });  
                showed_data[mes].forEach(sensor => {
                    datasets.push(build_dataset(json[mes]["time"], data, sensor, seed, 'Mesure ' + mes + " : " + sensor))
                    rows = rows.concat(build_row(json[mes]["time"], json[mes]["temperature"], mes, sensors=json[mes]["sensor_id"], sensor=sensor));
                });

                seed+=1
            }
                
            
        } else {
            for (let data_type in json[mesure]) {
                data = getTempsBySensor(json[mesure][data_type], json[mesure]["sensor_id"], json[mesure]["time"])
                if (["sensor_id", "time", "latitude", "longitude", "date"].includes(data_type)) {
                    continue
                }

                const timestamps = [...new Set(json[mesure]["time"])]
                const sensor_id = [...new Set(json[mesure]["sensor_id"])];
                let seed = 0

                sensor_id.forEach(sensor => {
                    datasets.push(build_dataset(timestamps, data, sensor, seed, 'Mesure ' + mesure + " : " + sensor));
                    rows = rows.concat(build_row(timestamps, data[sensor]["value"], mesure, sensors=json[mesure]["sensor_id"], sensor=sensor));
                    seed+=1;
                });                
            }
        }
        return { datasets: datasets, rows: rows }
    });
}

function gen_view(chart_id, table_id, mesure, data_type, dtime) {

    prebuit(chart_id, table_id, mesure, data_type, dtime).then(function (result) {
        const ctx = document.getElementById(chart_id).getContext('2d');
        build_chart(ctx, result.datasets, data_type);
        build_table(table_id, result.rows);
    })
};

function update_view(chart_id, table_id, mesure, data_type, dtime) {
    prebuit(chart_id, table_id, mesure, data_type, dtime).then(function (result) {
        let chart = Chart.getChart(document.getElementById(chart_id).getContext('2d'))
        chart.data.datasets = result.datasets
        chart.update('none')
        build_table(table_id, result.rows);
    })
}

function switch_view(event) {
    if (event.target.id) {
        view_type = event.target.id.split("-")[1]
        view_data_type = event.target.id.split("-")[2]
        
        let graph = document.getElementById("view-graph-"+view_data_type);
        let table = document.getElementById("view-table-"+view_data_type);

        if (view_type === "graph") {
            graph.classList.add("active");
            table.classList.remove("active");
        } else if (view_type === "table") {
            graph.classList.remove("active");
            table.classList.add("active");
        }
    }
};