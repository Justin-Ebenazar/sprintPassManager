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

function changeMasterPassword() {
  let currentPassword = window.prompt("Enter your current password:");
  let newPassword = window.prompt("Enter your new password:");
  fetch("/change_master_password", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      current_password: currentPassword,
      new_password: newPassword,    
    }),
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.status === "success") {
        alert("Master password changed successfully.");
      } else {
        alert(data.message);
      }
    });
}