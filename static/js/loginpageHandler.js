login_form = document.getElementById("login-form");
login_form.addEventListener("submit", function(event) {
    event.preventDefault();
    login();
});

function login(){
    let username = document.getElementById("login-username").value;
    let password = document.getElementById("login-password").value;
    fetch("/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ "username": username, "password": password }),
      }).then((response) => response.json())
      .then((data) => {
        if (data.status === "success") {
          window.location.href = data.redirect;
        } else {
          let flashContainer = document.querySelector(".flash-notifications");
          flashContainer.innerHTML = data.message;
          flashContainer.classList.add("password-error");
          setTimeout(() => {
            flashContainer.classList.remove("password-error");
          }, 3000);
        }
    });
}

signup_form = document.getElementById("signup-form");
signup_form.addEventListener("submit",() =>{
    e.preventDefault();
    signUp();
});

function signUp(){
  let user = document.getElementById("signup-username").value;
  let password = document.getElementById("signup-password").value;
  fetch("/register",{
    method : "POST",
    headers: {"Content-Type" : "application/json"},
    body: JSON.stringify({"username": user, "password": password})
  });
}