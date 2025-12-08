dtime = null
let showed_data = {}
const types_data = ["temperature"]

document.addEventListener("DOMContentLoaded", function () {
    const mesure = ""
    const type_data = document.location.pathname.replace("/", "")

    document.getElementById("button-graph-"+type_data).addEventListener("click", switch_view)
    document.getElementById("button-table-"+type_data).addEventListener("click", switch_view)
    
    gen_view("graph-"+type_data, "table-body-"+type_data, mesure, type_data, dtime)

    const socket = new WebSocket("/api/data_ws")

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
        post_command("delete_mesure", {"mesures":showed_data}, url="/data").then(function (response) {
            document.location.reload()
        }); 
    });
    
});

function update_data() {
   
    const mesure = ""
    const type_data = document.location.pathname.replace("/", "")
     
    document.getElementById("button-graph-"+type_data).addEventListener("click", switch_view)
    document.getElementById("button-table-"+type_data).addEventListener("click", switch_view)
    
    update_view("graph-"+type_data, "table-body-"+type_data, mesure, type_data, dtime)        

};