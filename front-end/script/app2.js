const lanIP = `${window.location.hostname}:5000`;
const socket = io(`http://${lanIP}`);
let gebruikers

const listenToSocket = function () {
    socket.on("connect", function () {
        console.log("verbonden met socket webserver")
    })

    socket.on("rfid_gebruiker", function (jsonObject) {
        console.log(jsonObject)
        if (sensors) {
            let html = sensors.innerHTML
            // console.log(sensor[1])
            html += `<div class="c-sensor">
                <div class="c-sensor__info">
                <h2 class="c-sensor__name">RFID</h2>
                </div>
                <div class="c-sensor__datum">${jsonObject["datetime"]}</div>
                <div class="c-sensor__waarde">${jsonObject["rfid"]}</div>
                </div>`
            sensors.innerHTML = html
        }
    })
    socket.on("magneetcontact", function (jsonObject) {
        console.log(jsonObject)
        html = sensors.innerHTML
        html += `<div class="c-sensor">
                <div class="c-sensor__info">
                <h2 class="c-sensor__name">Magneetcontact</h2>
                </div>
                <div class="c-sensor__datum">${jsonObject["datetime"]}</div>
                <div class="c-sensor__waarde">${jsonObject["waarde"]}</div>
                </div>`
        sensors.innerHTML = html
    })

    socket.on("Gebruikers", function (jsonObject) {
        if (gebruikers) {
            // console.log(jsonObject)
            let html = ''
            for (const gebruiker of jsonObject.gebruikers) {
                // console.log(gebruiker)
                // console.log(gebruiker['E-mail-adres'])
                html += `<div class="c-gebruiker">
                <div class="c-gebruiker__info">
                <h2 class="c-gebruiker__name">${gebruiker.Naam}</h2>
                </div>
                <div class="c-gebruiker__fname">${gebruiker.Voornaam}</div>`
                if (gebruiker['E-mail-adres']) {
                    html += `<div class="c-gebruiker__email">${gebruiker['E-mail-adres']}</div>
                    </div>`
                } else {
                    html += `<div class="c-gebruiker__email">Geen</div>
                    </div>`
                }
                //   <div class="c-sensor__track">${gebruiker['E-mail-adres']}</div>
                // </div>`
            }
            gebruikers.innerHTML = html
        }
    })

}





document.addEventListener("DOMContentLoaded", function () {
    console.info("DOM geladen");
    gebruikers = document.querySelector('.js-gebruikers')
    sensors = document.querySelector('.js-sensors')
    listenToSocket();
});