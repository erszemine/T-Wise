// frontend/src/index.js
import { checkAuthStatus, setUiCallbacks } from '/js/auth.js';
import { renderStokTakip } from '/js/app.js';

// app.js'deki UI render fonksiyonlarını auth.js'ye ilet
setUiCallbacks(renderStokTakip, showLoginScreenFromAuth);

// Helper function to call showLoginScreen from auth.js (avoids circular dependency)
function showLoginScreenFromAuth() {
    document.getElementById("loginError").style.display = "none";
    document.getElementById("loginForm").reset();
    document.getElementById("loginScreen").style.display = "flex";
    document.querySelector("nav").style.display = "none";
    document.getElementById("mainContent").style.display = "none";
    document.getElementById("logoutBtn").style.display = "none";
}

// Sayfa yüklendiğinde oturum durumunu kontrol et
window.addEventListener("DOMContentLoaded", () => {
    checkAuthStatus();
});