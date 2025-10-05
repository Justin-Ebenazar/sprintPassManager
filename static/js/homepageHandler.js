function deleteAccount() {
  
  let prompt = window.prompt(
    "Please enter your password to delete your account:"
  );
  console.log(prompt);
  fetch("/delete_account", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ password: prompt }),
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.status === "success") {
        window.location.href = data.redirect;
      } else {
        alert(data.message);
      }
    });
}
