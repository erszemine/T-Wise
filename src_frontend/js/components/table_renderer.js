// frontend/src/js/components/tableRenderer.js
export function createTable(headers, rows) {
    const table = document.createElement("table");
    const thead = document.createElement("thead");
    const thr = document.createElement("tr");
    headers.forEach(hdr => {
        const th = document.createElement("th");
        th.textContent = hdr;
        thr.appendChild(th);
    });
    thead.appendChild(thr);
    table.appendChild(thead);

    const tbody = document.createElement("tbody");
    rows.forEach(row => {
        const tr = document.createElement("tr");
        row.forEach(cell => {
            const td = document.createElement("td");
            // Eğer hücre içeriği bir objeyse ve 'name' özelliği varsa, 'name'ini göster. Aksi takdirde stringe çevir.
            const cellContent = (typeof cell === 'object' && cell !== null && 'name' in cell) ? cell.name : String(cell);
            td.textContent = cellContent;
            tr.appendChild(td);
        });
        tbody.appendChild(tr);
    });
    table.appendChild(tbody);
    return table;
}