// Configuration
const API_URL = "https://openfaas.home-maurras.fr/function";
const ENDPOINTS = {
  AUTH: "/auth-user",
  GENERATE_PASSWORD: "/generate-password",
  GENERATE_2FA: "/generate-2fa"
};

// Error messages
const ERROR_MESSAGES = {
  REQUIRED_FIELDS: "Champs requis.",
  PASSWORD_EXPIRED: "Mot de passe expiré. Génération en cours...",
  GENERATING_PASSWORD: "Génération du mot de passe en cours...",
  GENERATING_2FA: "Génération du code 2FA en cours..."
};

/**
 * Redirects to success page with confetti
 * @param {string} username - The authenticated username
 */
function redirectToSuccess(username) {
  // Store username in sessionStorage for the success page
  sessionStorage.setItem('authenticatedUser', username);
  // Redirect to success page
  window.location.href = '/frontend/auth-success.html';
}

/**
 * Fetches data from the API
 * @param {string} endpoint - The API endpoint to call
 * @param {string} body - The request body
 * @returns {Promise<string>} The response text
 */
async function fetchFromAPI(endpoint, body) {
  const response = await fetch(`${API_URL}${endpoint}`, {
    method: "POST",
    headers: { "Content-Type": "text/plain" },
    body
  });
  return response.text();
}

/**
 * Displays QR codes for password and 2FA reset
 * @param {string} qrPwd - Base64 encoded QR code for password
 * @param {string} qr2fa - Base64 encoded QR code for 2FA
 * @returns {string} HTML content to display
 */
function generateQRCodeHTML(qrPwd, qr2fa) {
  return `
    <p><strong>Nouveau mot de passe généré :</strong></p>
    <img src="data:image/png;base64,${qrPwd}" alt="QR Code Password">
    <p><strong>Configurer de nouveau le 2FA :</strong></p>
    <img src="data:image/png;base64,${qr2fa}" alt="QR Code 2FA">
  `;
}

/**
 * Handles the login form submission
 * @param {Event} e - The form submission event
 */
async function handleLogin(e) {
  e.preventDefault();

  const username = document.getElementById("username").value.trim();
  const password = document.getElementById("password").value.trim();
  const otp = document.getElementById("otp").value.trim();
  const resultDiv = document.getElementById("login-result");
  const submitButton = document.querySelector('#login-form button[type="submit"]');

  submitButton.disabled = true;
  submitButton.setAttribute("aria-busy", "true");
  submitButton.textContent = "Connexion en cours...";

  // Validate required fields
  if (!username || !password || !otp) {
    resultDiv.innerHTML = `<strong>${ERROR_MESSAGES.REQUIRED_FIELDS}</strong>`;
    return;
  }

  try {
    // Attempt authentication
    const authResponse = await fetchFromAPI(
      ENDPOINTS.AUTH,
      `${username},${password},${otp}`
    );

    if (authResponse.includes("expired")) {
      resultDiv.innerHTML = `<strong>${ERROR_MESSAGES.PASSWORD_EXPIRED}</strong>`;

      // First generate password
      resultDiv.innerHTML = `<strong>${ERROR_MESSAGES.GENERATING_PASSWORD}</strong>`;
      const qrPwd = await fetchFromAPI(ENDPOINTS.GENERATE_PASSWORD, username);

      // Then generate 2FA
      resultDiv.innerHTML = `<strong>${ERROR_MESSAGES.GENERATING_2FA}</strong>`;
      const qr2fa = await fetchFromAPI(ENDPOINTS.GENERATE_2FA, username);

      // Display both QR codes
      resultDiv.innerHTML = generateQRCodeHTML(qrPwd, qr2fa);

    } else if (authResponse.includes("Authenticated")) {
      // Redirect to success page with confetti
      redirectToSuccess(username);
    } else {
      resultDiv.innerHTML = `<strong>${authResponse}</strong>`;
    }
  } catch (err) {
    resultDiv.innerHTML = `<strong>Erreur:</strong> ${err.message}`;
  } finally {
    submitButton.textContent = "Se connecter";
    submitButton.disabled = false;
    submitButton.removeAttribute("aria-busy");
  }
}

// Event listener for form submission
document.getElementById("login-form").addEventListener("submit", handleLogin);
