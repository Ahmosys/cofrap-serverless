const url = "https://openfaas.home-maurras.fr/function";

document.getElementById("register-form").addEventListener("submit", async (e) => {
  e.preventDefault();

  const username = document.getElementById("reg-username").value.trim();
  const qrDiv = document.getElementById("qr-result");
  qrDiv.innerHTML = "";

  if (!username) {
    alert("Veuillez entrer un nom d'utilisateur.");
    return;
  }

  try {
    // Appel à generate-password
    const resPwd = await fetch(`${url}/generate-password`, {
      method: "POST",
      headers: { "Content-Type": "text/plain" },
      body: username
    });

    if (!resPwd.ok) throw new Error("Échec de la génération du mot de passe");
    const qrPwd = await resPwd.text();

    // Appel à generate-2fa
    const res2fa = await fetch(`${url}/generate-2fa`, {
      method: "POST",
      headers: { "Content-Type": "text/plain" },
      body: username
    });

    if (!res2fa.ok) throw new Error("Échec de la génération du code 2FA");
    const qr2fa = await res2fa.text();

    // Affichage des deux QR codes
    qrDiv.innerHTML = `
      <p>QR code pour le mot de passe :</p>
      <img src="data:image/png;base64,${qrPwd}" alt="QR Code Password">
      <p>QR code pour configurer Google Authenticator :</p>
      <img src="data:image/png;base64,${qr2fa}" alt="QR Code 2FA">
    `;
  } catch (err) {
    qrDiv.innerHTML = `<strong>Erreur:</strong> ${err.message}`;
  }
});
