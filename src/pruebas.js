// Reloj dinámico
function clock() {
    const d = new Date();
    document.getElementById('clock').innerText = "Terminal activa: " + d.toLocaleString();
}
setInterval(clock, 1000);

// Función 1: Diagnóstico de Fuerza Relativa e IMC
function checkStats() {
    const w = 60.2;
    const h = 1.60;
    const b = 110;
    const imc = (w / (h * h)).toFixed(2);
    const ratio = (b / w).toFixed(2);
    
    document.getElementById('output').innerHTML = 
        `> Analizando datos de Jovany...<br>` +
        `> IMC calculado: ${imc} (Saludable/Atleta)<br>` +
        `> Ratio Fuerza/Peso: ${ratio} (Nivel Competitivo)`;
}

// Función 2: Conversión a Libras
function convertToLbs() {
    const kgToLb = 2.20462;
    const wLb = (60.2 * kgToLb).toFixed(1);
    const bLb = (110 * kgToLb).toFixed(1);
    
    document.getElementById('output').innerHTML = 
        `> Cambiando a Sistema Imperial...<br>` +
        `> Peso Corporal: ${wLb} lbs<br>` +
        `> Press Banca (PR): ${bLb} lbs`;
}

// Función 3: Alternar Modo Oscuro
function toggleDarkMode() {
    document.body.classList.toggle('dark-mode');
    const btn = document.getElementById('darkModeBtn');
    
    if (document.body.classList.contains('dark-mode')) {
        btn.textContent = 'Modo Claro';
        localStorage.setItem('darkMode', 'enabled');
    } else {
        btn.textContent = 'Modo Oscuro';
        localStorage.setItem('darkMode', 'disabled');
    }
}

// Restaurar preferencia de modo oscuro
if (localStorage.getItem('darkMode') === 'enabled') {
    document.body.classList.add('dark-mode');
    document.getElementById('darkModeBtn').textContent = 'Modo Claro';
}
