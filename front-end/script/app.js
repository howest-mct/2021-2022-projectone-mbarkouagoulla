const lanIP = `${window.location.hostname}:5000`;
const socket = io(`http://${lanIP}`);
let gebruikers, ipadres, gewicht, dash, create, confirm

const listenToSocket = function () {
    socket.on("connect", function () {
        console.log("verbonden met socket webserver")
    })
    if (create) {
        console.log("listen to rfid user")
        socket.on("rfid_new", function (jsonObject) {
            console.log(jsonObject)
            const rfid_nummer = jsonObject.rfid
            document.querySelector(".js-rfid").value = rfid_nummer
        })
        socket.on("B2F_adduser_done", function () {
            // go to index.html
            // window.location.href = "index.html"
            document.querySelector(".js-confirm").classList.remove('u-hidden')
            document.querySelector('.js-fname').value = ''
            document.querySelector('.js-lname').value = ''
            document.querySelector('.js-email').value = ''
            document.querySelector('.js-rfid').value = ''

        })
    }
    if (dash) {
        socket.on("magneetcontact_nok", function (jsonObject) {
            console.log(jsonObject)
            document.querySelector(".js-flap").classList.remove('u-color-none')
            document.querySelector(".js-flap").classList.add('u-color-warning')
            document.querySelector(".js-flap").innerHTML = 'Open'
        })

        socket.on("magneetcontact_ok", function (jsonObject) {
            console.log(jsonObject)
            document.querySelector(".js-flap").classList.add('u-color-none')
            document.querySelector(".js-flap").classList.remove('u-color-warning')
            document.querySelector(".js-flap").innerHTML = 'Closed'
        })

        socket.on("leegpost", function (jsonObject) {
            console.log(jsonObject)
            document.querySelector(".js-inside").classList.remove('u-color-warning')
            document.querySelector(".js-inside").classList.add('u-color-none')
            document.querySelector(".js-inside").innerHTML = 'Empty'
        })

        socket.on("post", function (jsonObject) {
            console.log(jsonObject)
            document.querySelector(".js-inside").classList.remove('u-color-none')
            document.querySelector(".js-inside").classList.add('u-color-warning')
            document.querySelector(".js-inside").innerHTML = 'Mail available'
        })

        socket.on("B2F_open", function (jsonObject) {
            console.log(jsonObject)
            document.querySelector(".js-back").classList.remove('u-color-none')
            document.querySelector(".js-back").classList.add('u-color-warning')
            document.querySelector(".js-back").innerHTML = 'Open'
        })

        socket.on("B2F_close", function (jsonObject) {
            console.log(jsonObject)
            document.querySelector(".js-back").classList.remove('u-color-warning')
            document.querySelector(".js-back").classList.add('u-color-none')
            document.querySelector(".js-back").innerHTML = 'Closed'
        })

    }

    socket.on("gewicht", function (jsonObject) {
        if (historiek) {
            // console.log(jsonObject.waarde)
            // console.log(jsonObject.datetime)
            let html = ''
            html =
                `<div class="o-layout">
            <article class="o-layout__item u-1-of-3 u-text-center c-lead--s js-datum">${jsonObject.datetime}</article>
            <article class="o-layout__item u-1-of-3 u-text-center c-lead--s js-voornaam">
            Name
            </article>
            <article class="o-layout__item u-1-of-3 u-text-center c-lead--s js-action">${jsonObject.waarde}
            </article>
            </div>`
            historiek.innerHTML += html
        }
    })

    socket.on("Gebruikers", function (jsonObject) {
        if (gebruikers) {
            console.log(jsonObject)
            let html = ''
            for (const gebruiker of jsonObject.gebruikers) {
            html+=`<div class="o-layout">
            <article class="o-layout__item u-1-of-4 u-text-start c-lead--s js-name">${gebruiker['Naam']}</article>
            <article class="o-layout__item u-1-of-4 u-text-start c-lead--s js-voornaam">${gebruiker['Voornaam']}</article>
            <article  class="o-layout__item u-1-of-4 u-text-start c-lead--s js-rfid">${gebruiker['RFID-code']}</article>
            <article class="o-layout__item u-1-of-4 u-text-start c-lead--s c-delete js-delete">
            <div >
            <svg data-rfid=${gebruiker['RFID-code']}  class="c-nav_icon c-delete-symbol" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512">
            <path
            d="M135.2 17.69C140.6 6.848 151.7 0 163.8 0H284.2C296.3 0 307.4 6.848 312.8 17.69L320 32H416C433.7 32 448 46.33 448 64C448 81.67 433.7 96 416 96H32C14.33 96 0 81.67 0 64C0 46.33 14.33 32 32 32H128L135.2 17.69zM31.1 128H416V448C416 483.3 387.3 512 352 512H95.1C60.65 512 31.1 483.3 31.1 448V128zM111.1 208V432C111.1 440.8 119.2 448 127.1 448C136.8 448 143.1 440.8 143.1 432V208C143.1 199.2 136.8 192 127.1 192C119.2 192 111.1 199.2 111.1 208zM207.1 208V432C207.1 440.8 215.2 448 223.1 448C232.8 448 240 440.8 240 432V208C240 199.2 232.8 192 223.1 192C215.2 192 207.1 199.2 207.1 208zM304 208V432C304 440.8 311.2 448 320 448C328.8 448 336 440.8 336 432V208C336 199.2 328.8 192 320 192C311.2 192 304 199.2 304 208z"
            />
            </svg>
            </div>
            </article>
            </div>`
            }
            gebruikers.innerHTML = html
            listenToDeleteKnop()
        }
    })

    socket.on("B2F_deleteuser_done" ,function(){
        window.location.href = 'index.html'
        document.querySelector(".js-delete-confirm").classList.remove('u-hidden')
        // go to users.html
    })
    socket.on("ipadres", function (jsonObject) {
        if (ipadres) {
            console.log(jsonObject.adres)
            ipadres.innerHTML = jsonObject.adres
        }
        // if (ipadres){
        //     console.log('eeee')
        //     console.log(jsonObject)
        // }
    })

    socket.on('History', function (jsonObject) {
        if (historiek) {
            // console.log(jsonObject)
            data = JSON.parse(jsonObject['history'])
            console.log(data)
            let html= ''
            for (const item of data) {
                console.log(item['ActieBeschrijving'])
                html += `<div class="o-layout">
                    <article class="o-layout__item u-1-of-3 u-text-center c-lead--s js-datum">${item['datum']}</article>
                    <article class="o-layout__item u-1-of-3 u-text-center c-lead--s js-voornaam">
                    ${item['voornaam']}
                    </article>
                    <article class="o-layout__item u-1-of-3 u-text-center c-lead--s js-action">${item['ActieBeschrijving']}
                    </article>
                </div>`
        }
        historiek.innerHTML = html
    }
    })

}

const listenToDeleteKnop = function (){
    if (users) {
        const buttons = document.querySelectorAll('.c-delete-symbol');
        for (const b of buttons) {
            b.addEventListener('click', function () {
                // console.log(this)
                const id = this.getAttribute('data-rfid');
                console.log(id)
                socket.emit('deleteGebruiker', {id: id})
                // console.log('verwijder ');
            })
        }
    }}
const listenToUI = function () {
    if (dash) {
        const open = document.querySelector(".js-open");
        const close = document.querySelector(".js-close");
        open.addEventListener("click", function () {
            console.log('OPEN')
            socket.emit("F2B_open", { data: 0 })
        })
        close.addEventListener("click", function () {
            console.log('TOE')
            socket.emit("F2B_close", { data: 1 })
        })
    }
    const poweroff = document.querySelectorAll(".js-poweroff");
    for (const b of poweroff) {
        b.addEventListener('click', function () {
                console.log('POWEROFF')
        socket.emit("F2B_poweroff", { data: 1 })
    })
    }
    if (create) {
        document.querySelector('.js-insert').addEventListener('click', function () {
            console.log('Ben getikt 😜')
            const payload = JSON.stringify({
                FNaam: document.querySelector('.js-fname').value,
                LName: document.querySelector('.js-lname').value,
                Email: document.querySelector('.js-email').value,
                RFID: document.querySelector('.js-rfid').value
            });
            socket.emit("F2B_adduser",payload)
        });
    }
}

document.addEventListener("DOMContentLoaded", function () {
    console.log(window.location.hostname)
    console.info("DOM geladen");
    gebruikers = document.querySelector('.js-gebruikers')
    users = document.querySelector('.js-gebruikers-page')
    ipadres = document.querySelector('.js-ip-address')
    historiek = document.querySelector('.js-historiek')
    dash = document.querySelector('.js-dashboard')
    home = document.querySelector('.js-home')
    create = document.querySelector('.js-create')
    confirm = document.querySelector('.js-confirm')
    listenToSocket();
    listenToUI();
});