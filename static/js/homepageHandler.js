function deleteAccount() {

let prompt = window.prompt("Please enter your password to delete your account:");
console.log(prompt);
  fetch("/delete_account()", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ password: prompt }),
  })
    .then((response) => response.json()) // parses JSON
    .then((data) => {
      console.log(data.status); // "success"
    });
}
