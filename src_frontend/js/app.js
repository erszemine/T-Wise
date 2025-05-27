// frontend/src/js/app.js
import { createTable } from './components/tableRenderer.js';
import { api } from './api.js';
import { showLoginScreen, setUiCallbacks } from './auth.js';

// DOM referansları
const mainContent = document.getElementById("mainContent");
const navButtons = document.querySelectorAll("nav button");

// Demo verileri (şimdilik, daha sonra API'den çekilecek)
let parcalar = []; // API'den gelecek
let tedarikListesi = []; // API'den gelecek
let lojistikPlan = []; // API'den gelecek
let uretimRaporlari = []; // API'den gelecek
let uretimParcalari = []; // API'den gelecek


function clearContent() {
    mainContent.innerHTML = "";
}

// Data fetching functions
async function fetchStokItems() {
    try {
        parcalar = await api.getStockItems(); // Backend'den ürün/parça stoklarını çeker
    } catch (error) {
        console.error("Stok bilgileri çekilemedi:", error);
        if (error.message === "Unauthorized or Forbidden") {
            showLoginScreen(); // Yetki hatası durumunda login ekranına yönlendir
        }
        parcalar = []; // Hata durumunda boş liste
        const notif = document.createElement('div');
        notif.className = 'notification error';
        notif.textContent = 'Stok bilgileri yüklenirken bir hata oluştu.';
        mainContent.appendChild(notif);
    }
}

async function fetchTedarikList() {
    try {
        tedarikListesi = await api.getTedarikList();
    } catch (error) {
        console.error("Tedarik listesi çekilemedi:", error);
        tedarikListesi = [];
        const notif = document.createElement('div');
        notif.className = 'notification error';
        notif.textContent = 'Tedarik listesi yüklenirken bir hata oluştu.';
        mainContent.appendChild(notif);
    }
}

async function fetchLojistikPlan() {
    try {
        lojistikPlan = await api.planLogistics(); // API'den gelen planlama verisi
    } catch (error) {
        console.error("Lojistik plan çekilemedi:", error);
        lojistikPlan = [];
        const notif = document.createElement('div');
        notif.className = 'notification error';
        notif.textContent = 'Lojistik plan yüklenirken bir hata oluştu.';
        mainContent.appendChild(notif);
    }
}

async function fetchUretimRaporlari() {
    try {
        uretimRaporlari = await api.getProductionReports();
    } catch (error) {
        console.error("Üretim raporları çekilemedi:", error);
        uretimRaporlari = [];
        const notif = document.createElement('div');
        notif.className = 'notification error';
        notif.textContent = 'Üretim raporları yüklenirken bir hata oluştu.';
        mainContent.appendChild(notif);
    }
}

async function fetchUretimParcalari() {
    try {
        uretimParcalari = await api.getRequiredProductionParts(); // Varsayılan endpoint
    } catch (error) {
        console.error("Üretim parçaları çekilemedi:", error);
        uretimParcalari = [];
        const notif = document.createElement('div');
        notif.className = 'notification error';
        notif.textContent = 'Üretim parçaları yüklenirken bir hata oluştu.';
        mainContent.appendChild(notif);
    }
}


// --- Bölüm Render Fonksiyonları ---

export async function renderStokTakip() {
    clearContent();
    const title = document.createElement('h2');
    title.textContent = 'Stok Takibi';
    mainContent.appendChild(title);

    await fetchStokItems(); // API'den veriyi çek
    const headers = ['Parça ID', 'Parça Adı', 'Stok Adedi'];
    // API'den gelen veriye göre map'leme yapın
    const rows = parcalar.map(p => [p.id, p.name, p.quantity]); 
    mainContent.appendChild(createTable(headers, rows));
}

export async function renderTedarikPlanlama() {
    clearContent();
    const title = document.createElement('h2');
    title.textContent = 'Tedarik Planlama';
    mainContent.appendChild(title);

    await fetchTedarikList();
    const headers = ['Parça ID', 'Parça Adı', 'Eksik Adet', 'Planlanan Teslim Tarihi'];
    const rows = tedarikListesi.map(t => [t.id, t.name, t.missing_quantity, t.planned_delivery_date]);
    mainContent.appendChild(createTable(headers, rows));

    const notif = document.createElement('div');
    notif.className = 'notification';
    notif.textContent = 'Eksik parçaların tedarik durumları buradan takip edilir.';
    mainContent.appendChild(notif);
}

export async function renderLojistikPlanlama() {
    clearContent();
    const title = document.createElement('h2');
    title.textContent = 'Lojistik Planlama';
    mainContent.appendChild(title);

    await fetchLojistikPlan();
    const headers = ['Ürün', 'Adet', 'Teslim Tarihi'];
    const rows = lojistikPlan.map(l => [l.product_name, l.quantity, l.delivery_date]);
    mainContent.appendChild(createTable(headers, rows));
}

export async function renderUretimRapor() {
    clearContent();
    const title = document.createElement('h2');
    title.textContent = 'Üretim Raporları';
    mainContent.appendChild(title);

    await fetchUretimRaporlari();
    const headers = ['Ürün', 'Adet', 'Teslim Tarihi'];
    const rows = uretimRaporlari.map(r => [r.product_name, r.quantity, r.delivery_date]);
    mainContent.appendChild(createTable(headers, rows));
}

export async function renderStokGuncelleme() {
    clearContent();
    const title = document.createElement("h2");
    title.textContent = "Stok Güncelleme";
    mainContent.appendChild(title);

    await fetchStokItems(); // Güncel parça listesini çek

    const form = document.createElement("form");
    form.id = "stokGuncelleForm";

    // Dropdown parça seçimi
    const labelParca = document.createElement("label");
    labelParca.textContent = "Parça Seçiniz:";
    labelParca.setAttribute("for", "parcaSelect");
    form.appendChild(labelParca);

    const selectParca = document.createElement("select");
    selectParca.id = "parcaSelect";
    selectParca.required = true;
    parcalar.forEach(p => {
        const option = document.createElement("option");
        option.value = p.id;
        option.textContent = p.name + " (Stok: " + p.quantity + ")"; // API'den gelen 'name' ve 'quantity'
        selectParca.appendChild(option);
    });
    form.appendChild(selectParca);

    // Giriş türü (giriş/çıkış)
    const labelIslem = document.createElement("label");
    labelIslem.textContent = "İşlem Türü:";
    form.appendChild(labelIslem);

    const selectIslem = document.createElement("select");
    selectIslem.id = "islemTipi";
    selectIslem.required = true;
    const optGiris = document.createElement("option");
    optGiris.value = "ENTRY"; // Backend'deki karşılığı
    optGiris.textContent = "Parça Girişi";
    const optCikis = document.createElement("option");
    optCikis.value = "EXIT"; // Backend'deki karşılığı
    optCikis.textContent = "Parça Çıkışı (Üretim)";
    selectIslem.appendChild(optGiris);
    selectIslem.appendChild(optCikis);
    form.appendChild(selectIslem);

    // Adet girişi
    const labelAdet = document.createElement("label");
    labelAdet.textContent = "Adet:";
    labelAdet.setAttribute("for", "adetInput");
    form.appendChild(labelAdet);

    const inputAdet = document.createElement("input");
    inputAdet.type = "number";
    inputAdet.min = "1";
    inputAdet.id = "adetInput";
    inputAdet.required = true;
    form.appendChild(inputAdet);

    // Submit butonu
    const btnSubmit = document.createElement("button");
    btnSubmit.type = "submit";
    btnSubmit.className = "btn";
    btnSubmit.textContent = "Stok Güncelle";
    form.appendChild(btnSubmit);

    // Bildirim alanı
    const notif = document.createElement("div");
    notif.id = "stokGuncelleNotif";
    notif.style.marginTop = "1rem";

    mainContent.appendChild(form);
    mainContent.appendChild(notif);

    form.addEventListener("submit", async function(e) {
        e.preventDefault();
        const parcaId = parseInt(selectParca.value);
        const islemTipi = selectIslem.value;
        const adet = parseInt(inputAdet.value);
        const parca = parcalar.find(p => p.id === parcaId);

        if (!parca || isNaN(adet) || adet <= 0) {
            notif.textContent = "Lütfen geçerli bir seçim yapınız.";
            notif.className = "notification error";
            return;
        }

        if (islemTipi === "EXIT" && adet > parca.quantity) { // 'quantity' olarak güncellendi
            notif.textContent = "Çıkış yapmak için yeterli stok yok!";
            notif.className = "notification error";
            return;
        }

        try {
            // API çağrısı
            const response = await api.updateStock(parcaId, 1, adet, islemTipi, `${islemTipi.toLowerCase()} işlemi`); // Varsayılan warehouseId: 1
            notif.textContent = response.message || "Stok başarıyla güncellendi.";
            notif.className = "notification";
            
            // UI'ı güncelle
            if (islemTipi === "ENTRY") {
                parca.quantity += adet;
            } else if (islemTipi === "EXIT") {
                parca.quantity -= adet;
            }
            selectParca.querySelectorAll("option").forEach(opt => {
                if (parseInt(opt.value) === parca.id) {
                    opt.textContent = parca.name + " (Stok: " + parca.quantity + ")";
                }
            });

            // Stok Takip tablosu otomatik güncellensin
            if (document.querySelector("nav button.active").dataset.section === "stokTakip") {
                renderStokTakip();
            }

        } catch (error) {
            console.error("Stok güncelleme hatası:", error);
            notif.textContent = error.message || "Stok güncellenirken bir hata oluştu.";
            notif.className = "notification error";
        }
    });
}

export async function renderUretimParcalari() {
    clearContent();
    const title = document.createElement("h2");
    title.textContent = "Üretimde Gerekli Parçalar";
    mainContent.appendChild(title);

    await fetchUretimParcalari(); // Veriyi çek

    if (uretimParcalari.length === 0) {
        const info = document.createElement("p");
        info.textContent = "Şu an üretimde gerekli parça bilgisi bulunmamaktadır.";
        mainContent.appendChild(info);
        return;
    }

    const headers = ["Ürün", "Parça ID", "Parça Adı", "Gerekli Adet"];
    const rows = uretimParcalari.map(p => [p.product_name, p.part_id, p.part_name, p.required_quantity]); // API'den gelen verilere göre uyarlanacak
    mainContent.appendChild(createTable(headers, rows));

    const info = document.createElement("p");
    info.textContent = "Yukarıdaki parçalar üretime iletilmiştir.";
    info.style.marginTop = "1rem";
    info.style.fontWeight = "600";
    mainContent.appendChild(info);
}

// Menü butonlarına tıklamayla sayfa değişimi
navButtons.forEach(btn => {
    btn.addEventListener("click", () => {
        navButtons.forEach(b => b.classList.remove("active"));
        btn.classList.add("active");
        const section = btn.dataset.section;
        switch(section) {
            case "stokTakip":
                renderStokTakip();
                break;
            case "tedarikPlanlama":
                renderTedarikPlanlama();
                break;
            case "lojistikPlanlama":
                renderLojistikPlanlama();
                break;
            case "uretimRapor":
                renderUretimRapor();
                break;
            case "stokGuncelleme":
                renderStokGuncelleme();
                break;
            case "uretimParcalari":
                renderUretimParcalari();
                break;
            default:
                clearContent();
                break;
        }
    });
});