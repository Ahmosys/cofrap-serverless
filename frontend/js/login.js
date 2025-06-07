const url = "https://openfaas.home-maurras.fr/function";

document.getElementById("login-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const username = document.getElementById("username").value.trim();
  const password = document.getElementById("password").value.trim();
  const otp = document.getElementById("otp").value.trim();

  const resultDiv = document.getElementById("login-result");

  if (!username || !password || !otp) {
    resultDiv.innerHTML = "<strong>Champs requis.</strong>";
    return;
  }

  try {
    const res = await fetch(`${url}/auth-user`, {
      method: "POST",
      headers: { "Content-Type": "text/plain" },
      body: `${username},${password},${otp}`
    });

    const text = await res.text();
    resultDiv.innerHTML = `<strong>${text}</strong>`;
  } catch (err) {
    resultDiv.innerHTML = `<strong>Erreur:</strong> ${err.message}`;
  }
});
