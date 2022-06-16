const lanIP = `${window.location.hostname}:5000`;
const socket = io(`http://${lanIP}`);
let gebruikers, ipadres,gewicht,dash,login

const listenToSocket = function () {
    socket.on("connect", function () {
        console.log("verbonden met socket webserver")
    })

    if (dash){
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
    socket.on("rfid_gebruiker", function (jsonObject) {
        console.log(jsonObject)
        if (historiek) {
            console.log(jsonObject.rfid)
            console.log(jsonObject.datetime)
            let html = ''
            html +=
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

    socket.on("gewicht", function (jsonObject) {
        if (historiek){
            // console.log(jsonObject.waarde)
            // console.log(jsonObject.datetime)
            let html=''
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
                html+= `<div class="o-layout">
                <article class="o-layout__item u-1-of-3 u-text-start c-lead--s js-name">${gebruiker.Naam}</article>
                <article class="o-layout__item u-1-of-3 u-text-start c-lead--s js-voornaam">
                ${gebruiker.Voornaam}
                </article>
                <article class="o-layout__item u-1-of-3 u-text-start c-lead--s js-rfid">
                ${gebruiker[`RFID-code`]}
                </article>
                </div>`
            }
            gebruikers.innerHTML = html
        }
    })


    socket.on("ipadres", function(jsonObject){
        if (ipadres){
        console.log(jsonObject.adres)
        ipadres.innerHTML = jsonObject.adres
        }
        // if (ipadres){
        //     console.log('eeee')
        //     console.log(jsonObject)
        // }
    })

    socket.on('History',function(jsonObject){
        if (historiek){
            // console.log(jsonObject)
            data = JSON.parse(jsonObject['history'])
            console.log(data)
        }
    })

}


const listenToUI = function () {
    if (dash){
    const open = document.querySelector(".js-open");
    const close = document.querySelector(".js-close");
    open.addEventListener("click",function(){
        console.log('OPEN')
        socket.emit("F2B_open", {data: 0 })
    })
    close.addEventListener("click", function () {
        console.log('TOE')
        socket.emit("F2B_close", { data: 1 })
    })
    }
    if(login){
        const signup = document.querySelector('.js-signup')
        const create = document.querySelector('.js-create')
        const login = document.querySelector('.js-login')
        const login_redirect = document.querySelector('.js-login-redirect')
        signup.addEventListener("click",function(){
            login.classList.add('u-hidden')
            create.classList.remove('u-hidden')
        })
        login_redirect.addEventListener("click", function () {
            login.classList.remove('u-hidden')
            create.classList.add('u-hidden')
        })
        socket.emit("F2B_RFID_read", { data:'ready to read' })

    }
    // for (const knop of knoppen) {
    //     knop.addEventListener("click", function () {
    //         const id = this.dataset.idlamp;
    //         let nieuweStatus;
    //         if (this.dataset.statuslamp == 0) {
    //             nieuweStatus = 1;
    //         } else {
    //             nieuweStatus = 0;
    //         }
    //         //const statusOmgekeerd = !status;
    //         clearClassList(document.querySelector(`.js-room[data-idlamp="${id}"]`));
    //         document.querySelector(`.js-room[data-idlamp="${id}"]`).classList.add("c-room--wait");
    //         socket.emit("F2B_switch_light", { lamp_id: id, new_status: nieuweStatus });
    //     });
    // }
};



document.addEventListener("DOMContentLoaded", function () {
    console.info("DOM geladen");
    gebruikers = document.querySelector('.js-gebruikers')
    ipadres = document.querySelector('.js-ip-address')
    historiek = document.querySelector('.js-historiek')
    dash = document.querySelector('.js-dashboard')
    login = document.querySelector('.js-login-page')
    home = document.querySelector('.js-home')
    listenToSocket();
    listenToUI();
});