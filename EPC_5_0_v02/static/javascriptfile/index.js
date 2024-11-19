// Esegui il codice solo dopo che la pagina è stata completamente caricata
document.addEventListener("DOMContentLoaded", function () {
    /*=============== SHOW HIDE PASSWORD LOGIN ===============*/
    const passwordAccess = (loginPass, loginEye) => {
        const input = document.getElementById(loginPass),
              iconEye = document.getElementById(loginEye);

        iconEye.addEventListener('click', () => {
            // Cambia la password in testo
            if (input.type === 'password') {
                input.type = 'text';
            } else {
                input.type = 'password';
            }

            // Cambia icona
            iconEye.classList.toggle('ri-eye-fill');
            iconEye.classList.toggle('ri-eye-off-fill');
        });
    };
    passwordAccess('password', 'loginPassword');

    /*=============== SHOW HIDE PASSWORD CREATE ACCOUNT ===============*/
    const passwordRegister = (loginPass, loginEye) => {
        const input = document.getElementById(loginPass),
              iconEye = document.getElementById(loginEye);

        iconEye.addEventListener('click', () => {
            // Cambia la password in testo
            if (input.type === 'password') {
                input.type = 'text';
            } else {
                input.type = 'password';
            }

            // Cambia icona
            iconEye.classList.toggle('ri-eye-fill');
            iconEye.classList.toggle('ri-eye-off-fill');
        });
    };
    passwordRegister('passwordCreate', 'loginPasswordCreate');

    /*=============== SHOW HIDE LOGIN & CREATE ACCOUNT ===============*/
    const loginAccessRegister = document.getElementById('loginAccessRegister'),
          buttonRegister = document.getElementById('loginButtonRegister'),
          buttonAccess = document.getElementById('loginButtonAccess');

    if (buttonRegister) {
        buttonRegister.addEventListener('click', () => {
            loginAccessRegister.classList.add('active');
        });
    }

    if (buttonAccess) {
        buttonAccess.addEventListener('click', () => {
            loginAccessRegister.classList.remove('active');
        });
    }

    /*=============== ANIMAZIONE PER MESSAGE BOX ===============*/
    // Seleziona il bottone "Invia"
    const sendButton = document.querySelector('button[type="submit"]');

    // Seleziona il box del messaggio
    const messageBox = document.getElementById('messageBox');

    // Controlla se il message box esiste nella pagina
    if (messageBox) {
        // Aggiungi un'animazione al caricamento
        messageBox.classList.add('show');
    }

    // Aggiungi un evento al bottone "Invia"
    if (sendButton) {
        sendButton.addEventListener('click', function (event) {
            // Impedisci il comportamento di default se necessario
            // event.preventDefault();

            // Aggiungi la classe 'show' per attivare l'animazione
            if (messageBox) {
                messageBox.classList.add('show');
            }
        });
    }
});
