const togglePassword = document.getElementById("togglePassword");
const passwordInput = document.getElementById("passwd");

togglePassword.addEventListener("click", (event) => {

    event.preventDefault();

    if (passwordInput.type === "password") {

        passwordInput.type = "text";
        togglePassword.textContent = "👁";

    } else {

        passwordInput.type = "password";
        togglePassword.textContent = "⌣";

    }

});