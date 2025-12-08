dtime = null
const types_data = ["temperature"]
document.addEventListener("DOMContentLoaded", function () {
    const mesure = document.location.pathname.replace("/mesure/", "")

    document.getElementById("rename-modal-button").classList.remove("hidden")

    document.getElementById("mesure-title").innerHTML = decodeURIComponent(mesure)
    document.getElementById("mesure_name").setAttribute("value", decodeURIComponent(mesure))
    document.getElementById("mesure_name_submit").addEventListener("click", (event) => {
        var new_name = document.getElementById("mesure_name").value;
        post_command("rename_mesure", {"old_name": decodeURIComponent(mesure), "new_name": new_name}, url="/data").then(function (response) {
            document.location = "/mesure/"+new_name
        })
    })
    
    types_data.forEach(type_data => {
        document.getElementById("button-graph-"+type_data).addEventListener("click", switch_view)
        document.getElementById("button-table-"+type_data).addEventListener("click", switch_view) 
        gen_view("graph-"+type_data, "table-body-"+type_data, mesure, type_data, dtime)     
    });

    const socket = new WebSocket("/api/data_ws");

    socket.onopen = () => {
        console.log("Connecté au WebSocket");
    };

    socket.onmessage = (event) => {
        update_data()
    }
    socket.onclose = () => {
        console.log("Connexion WebSocket fermée");
    };

    document.getElementById("delete-button").addEventListener("click", (event) => {
        post_command("delete_mesure", {"mesure":decodeURIComponent(mesure)}, url="/data").then(function (response) {
            document.location = "/view"
        });
    });
});

function update_data() {
    const mesure = document.location.pathname.replace("/mesure/", "")
    types_data.forEach(type_data => {
        update_view("graph-"+type_data, "table-body-"+type_data, mesure, type_data, dtime)        
    })
};