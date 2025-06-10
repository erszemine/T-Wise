// frontend/src/js/api.js
const API_BASE_URL = "http://localhost:8000"; // Backend adresiniz buraya geldi

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
    login: async (username, password) => {
        const response = await fetch(`${API_BASE_URL}/token`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: new URLSearchParams({ username, password })
        });
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || "Giriş başarısız.");
        }
        return response.json();
    },

    getStockItems: async () => {
        return fetchWithAuth('${API_BASE_URL}/stock/items'); // Örnek endpoint
    },

    getTedarikList: async () => {
        return fetchWithAuth('${API_BASE_URL}/supply/planning'); // Örnek endpoint
    },

    updateStock: async (productId, warehouseId, quantity, movementType, description) => {
        return fetchWithAuth(`${API_BASE_URL}/stock/update`, {
            method: 'POST',
            body: JSON.stringify({ product_id: productId, warehouse_id: warehouseId, quantity: quantity, movement_type: movementType, description: description })
        });
    },

    // Diğer API çağrıları buraya eklenecek (lojistik, üretim raporları vb.)
    getProductionReports: async () => {
        return fetchWithAuth('${API_BASE_URL}/production/reports');
    },
    
    getRequiredProductionParts: async () => {
        return fetchWithAuth('${API_BASE_URL}/production/required-parts');
    },

    // Yeni eklenen servis metodlarına karşılık gelen API endpoint'leri
    checkPartStatus: async (productId, requiredQuantity) => {
        return fetchWithAuth(`${API_BASE_URL}/stock/check-part-status`, {
            method: 'POST',
            body: JSON.stringify({ product_id: productId, required_quantity: requiredQuantity })
        });
    },
    procureMissingParts: async (productId, missingQuantity) => {
        return fetchWithAuth(`${API_BASE_URL}/supply/procure-missing-parts`, {
            method: 'POST',
            body: JSON.stringify({ product_id: productId, missing_quantity: missingQuantity })
        });
    },
    planLogistics: async (productId, quantity, deliveryDate) => {
        return fetchWithAuth(`${API_BASE_URL}/logistics/plan`, {
            method: 'POST',
            body: JSON.stringify({ product_id: productId, quantity: quantity, delivery_date: deliveryDate })
        });
    },
    reportUpcomingProducts: async () => {
        return fetchWithAuth('${API_BASE_URL}/production/upcoming-products-report');
    },
    deliverPartsToProduction: async (productId, warehouseId, quantity) => {
        return fetchWithAuth(`${API_BASE_URL}/stock/deliver-to-production`, {
            method: 'POST',
            body: JSON.stringify({ product_id: productId, warehouse_id: warehouseId, quantity: quantity })
        });
    }
};