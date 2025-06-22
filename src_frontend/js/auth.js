// frontend/src/js/auth.js
import { api } from '/js/api.js'; // api.js'den API çağrılarını import edin

const loginScreen = document.getElementById("loginScreen");
const loginForm = document.getElementById("loginForm");
const loginError = document.getElementById("loginError");
const nav = document.querySelector("nav");
const mainContent = document.getElementById("mainContent");
const logoutBtn = document.getElementById("logoutBtn");

export let loggedIn = false; // auth durumu

// Kullanıcı arayüzü fonksiyonları (app.js'de tanımlanacak ama burada çağrılabilir)
let showMainAppCallback = null;
let showLoginScreenCallback = null;

export function setUiCallbacks(mainAppCb, loginScreenCb) {
    showMainAppCallback = mainAppCb;
    showLoginScreenCallback = loginScreenCb;
}

export function showLoginScreen() {
    loginError.style.display = "none";
    loginForm.reset();
    loginScreen.style.display = "flex";
    nav.style.display = "none";
    mainContent.style.display = "none";
    logoutBtn.style.display = "none";
    loggedIn = false;
    localStorage.removeItem("access_token"); // Token'ı temizle
    localStorage.removeItem("user_info"); // Kullanıcı bilgisini temizle (isteğe bağlı)
}

function showMainApp() {
    loginScreen.style.display = "none";
    nav.style.display = "flex";
    mainContent.style.display = "block";
    logoutBtn.style.display = "inline-block";
    loggedIn = true;
    if (showMainAppCallback) {
        showMainAppCallback();
    }
}

// Login form submit
loginForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const username = loginForm.username.value.trim();
    const password = loginForm.password.value;

    try {
        const data = await api.login(username, password);
        localStorage.setItem("access_token", data.access_token);
        // localStorage.setItem("user_info", JSON.stringify(data.user_info)); // Backend'den kullanıcı bilgisi geliyorsa
        showMainApp();
    } catch (error) {
        console.error("Login failed:", error);
        loginError.textContent = error.message || "Giriş başarısız oldu. Lütfen tekrar deneyin.";
        loginError.style.display = "block";
    }
});

// Çıkış butonu
logoutBtn.addEventListener("click", () => {
    showLoginScreen();
});

// Oturum kontrolü (sayfa yenilendiğinde token var mı kontrol et)
export function checkAuthStatus() {
    const token = localStorage.getItem("access_token");
    if (token) {
        // Token'ı doğrulamak için backend'e bir çağrı yapılabilir
        // Şimdilik sadece token varsa oturumu açık kabul edelim
        showMainApp();
    } else {
        showLoginScreen();
    }
}