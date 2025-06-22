// frontend/src/js/api.js
// API_BASE_URL'in sonundaki '/' işaretini kaldırdık, endpoint'lerde '/' kullanacağız
const API_BASE_URL = "http://localhost:8000"; // Backend adresiniz buraya geldi (SONUNDAKİ '/' İŞARETİNİ KONTROL EDİN)

// Helper function to get JWT token from localStorage
function getAuthToken() {
    return localStorage.getItem("access_token");
}

async function fetchWithAuth(url, options = {}) {
    const token = getAuthToken();
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers
    };

    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(url, { ...options, headers });

    if (!response.ok) {
        // Handle unauthorized or forbidden responses globally
        if (response.status === 401 || response.status === 403) {
            console.error("Authentication or Authorization Error:", response.status);
            // Optionally redirect to login or show an error message
            // app.js'de showLoginScreen() çağrılabilir
            throw new Error("Unauthorized or Forbidden");
        }
        const errorData = await response.json();
        throw new Error(errorData.detail || `HTTP error! Status: ${response.status}`);
    }
    return response.json();
}

// API Çağrıları (Örnekler)
export const api = {
    // api.js içindeki login fonksiyonu
login: async (username, password) => {
    const response = await fetch(`${API_BASE_URL}/api/token`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json' // DEĞİŞTİ!
        },
        body: JSON.stringify({ username, password }) // DEĞİŞTİ!
    });

    console.log("Login API response status:", response.status); 

    if (!response.ok) {
        let errorData;
        try {
            errorData = await response.json();
            console.error("API error response data:", errorData); 
        } catch (e) {
            console.error("Error parsing API error response:", e); 
            throw new Error(`HTTP error! Status: ${response.status}. Yanıt JSON formatında değil.`);
        }
        throw new Error(errorData.detail || errorData.message || `Giriş başarısız oldu. Durum: ${response.status}`);
    }
    const data = await response.json();
    console.log("API login success response data:", data); 
    return data;
},

    // Düzeltmeler: Ters tırnak (`) kullanıldı ve '/api' öneki eklendi
    getStockItems: async () => {
        return fetchWithAuth(`${API_BASE_URL}/api/products`); // /api/products olarak düzeltildi
    },

    getTedarikList: async () => {
        return fetchWithAuth(`${API_BASE_URL}/api/supply/planning`); // Örnek endpoint, '/api' eklendi
    },

    updateStock: async (productId, warehouseId, quantity, movementType, description) => {
        return fetchWithAuth(`${API_BASE_URL}/api/stock/update`, { // '/api' eklendi
            method: 'POST',
            body: JSON.stringify({ product_id: productId, warehouse_id: warehouseId, quantity: quantity, movement_type: movementType, description: description })
        });
    },

    // Diğer API çağrıları buraya eklenecek (lojistik, üretim raporları vb.)
    getProductionReports: async () => {
        return fetchWithAuth(`${API_BASE_URL}/api/production/reports`); // '/api' eklendi
    },
    
    getRequiredProductionParts: async () => {
        return fetchWithAuth(`${API_BASE_URL}/api/production/required-parts`); // '/api' eklendi
    },

    // Yeni eklenen servis metodlarına karşılık gelen API endpoint'leri
    checkPartStatus: async (productId, requiredQuantity) => {
        return fetchWithAuth(`${API_BASE_URL}/api/stock/check-part-status`, { // '/api' eklendi
            method: 'POST',
            body: JSON.stringify({ product_id: productId, required_quantity: requiredQuantity })
        });
    },
    procureMissingParts: async (productId, missingQuantity) => {
        return fetchWithAuth(`${API_BASE_URL}/api/supply/procure-missing-parts`, { // '/api' eklendi
            method: 'POST',
            body: JSON.stringify({ product_id: productId, missing_quantity: missingQuantity })
        });
    },
    planLogistics: async (productId, quantity, deliveryDate) => {
        return fetchWithAuth(`${API_BASE_URL}/api/logistics/plan`, { // '/api' eklendi
            method: 'POST',
            body: JSON.stringify({ product_id: productId, quantity: quantity, delivery_date: deliveryDate })
        });
    },
    reportUpcomingProducts: async () => {
        return fetchWithAuth(`${API_BASE_URL}/api/production/upcoming-products-report`); // '/api' eklendi
    },
    deliverPartsToProduction: async (productId, warehouseId, quantity) => {
        return fetchWithAuth(`${API_BASE_URL}/api/stock/deliver-to-production`, { // '/api' eklendi
            method: 'POST',
            body: JSON.stringify({ product_id: productId, warehouse_id: warehouseId, quantity: quantity })
        });
    }
};