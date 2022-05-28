const lanIP = `${window.location.hostname}:5000`;
const socket = io(`http://${lanIP}`);

const listenToSocket = function(){
    socket.on("connected",function(){
        console.log("verbonden met socket webserver")
    })

    socket.on("Gebruikers",function(jsonObject){
        console.log(jsonObject)
    })
}





document.addEventListener("DOMContentLoaded", function () {
    console.info("DOM geladen");
    // listenToUI();
    listenToSocket();
});