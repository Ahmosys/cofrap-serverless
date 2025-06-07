// Configuration
const API_URL = "https://openfaas.home-maurras.fr/function";
const ENDPOINTS = {
  GENERATE_PASSWORD: "/generate-password",
  GENERATE_2FA: "/generate-2fa"
};

// Error messages
const ERROR_MESSAGES = {
  USERNAME_REQUIRED: "Veuillez entrer un nom d'utilisateur.",
  PASSWORD_GENERATION_FAILED: "Échec de la génération du mot de passe",
  TWOFA_GENERATION_FAILED: "Échec de la génération du code 2FA"
};

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

  if (!response.ok) {
    throw new Error(`API call failed: ${response.statusText}`);
  }

  return response.text();
}

/**
 * Generates HTML content for displaying QR codes
 * @param {string} qrPwd - Base64 encoded QR code for password
 * @param {string} qr2fa - Base64 encoded QR code for 2FA
 * @returns {string} HTML content to display
 */
function generateQRCodeHTML(qrPwd, qr2fa) {
  return `
    <p>QR code pour le mot de passe :</p>
    <img src="data:image/png;base64,${qrPwd}" alt="QR Code Password">
    <p>QR code pour configurer Google Authenticator :</p>
    <img src="data:image/png;base64,${qr2fa}" alt="QR Code 2FA">
  `;
}

/**
 * Handles the registration form submission
 * @param {Event} e - The form submission event
 */
async function handleRegistration(e) {
  e.preventDefault();

  const username = document.getElementById("reg-username").value.trim();
  const qrDiv = document.getElementById("qr-result");
  qrDiv.innerHTML = "";

  if (!username) {
    alert(ERROR_MESSAGES.USERNAME_REQUIRED);
    return;
  }

  try {
    // First generate password
    qrDiv.innerHTML = "<p>Génération du mot de passe en cours...</p>";
    const qrPwd = await fetchFromAPI(ENDPOINTS.GENERATE_PASSWORD, username);

    // Then generate 2FA
    qrDiv.innerHTML = "<p>Génération du code 2FA en cours...</p>";
    const qr2fa = await fetchFromAPI(ENDPOINTS.GENERATE_2FA, username);

    // Display both QR codes
    qrDiv.innerHTML = generateQRCodeHTML(qrPwd, qr2fa);
  } catch (err) {
    qrDiv.innerHTML = `<strong>Erreur:</strong> ${err.message}`;
  }
}

// Event listener for form submission
document.getElementById("register-form").addEventListener("submit", handleRegistration);
