function updateClock() {
    const teraz = new Date();
    document.getElementById('clock').innerText = teraz.toLocaleTimeString('pl-PL');
    const opcje = { weekday: 'long', day: 'numeric', month: 'long' };
    document.getElementById('day-of-week').innerText = teraz.toLocaleDateString('pl-PL', opcje);
}

function getIcon(desc, temp, isDay) {
    const d = desc.toLowerCase();
    if (!isDay) return "🌙";
    if (temp <= 0 && d.includes("opady")) return "❄️";
    if (d.includes("deszcz")) return "🌧️";
    if (d.includes("zachmurzenie małe")) return "🌤️";
    if (d.includes("zachmurzenie")) return "☁️";
    return "☀️";
}

async function updateWeather() {
    try {
        const response = await fetch('wynik_pogoda.json?t=' + new Date().getTime());
        const data = await response.json();
        
        const temp = Math.round(data.main.temp);
        const desc = data.weather[0].description;
        const isDay = data.sys.sunrise < (Date.now()/1000) && (Date.now()/1000) < data.sys.sunset;

        // Podstawowe dane
        document.getElementById('temp-akt').innerText = temp;
        document.getElementById('pogoda-opis').innerText = desc;
        document.getElementById('weather-icon').innerText = getIcon(desc, temp, isDay);
        
        // Słońce i Księżyc
        const sunrise = new Date(data.sys.sunrise * 1000).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
        const sunset = new Date(data.sys.sunset * 1000).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
        document.getElementById('sun-info').innerText = `🌅 ${sunrise} | 🌇 ${sunset}`;
        document.getElementById('wind-info').innerText = `💨 Wiatr: ${data.wind.speed} m/s`;
        document.getElementById('moon-info').innerText = `🌙 ${data.moon || "Przybywający"}`;

        // Ostrzeżenie
        const alertBox = document.getElementById('weather-alert');
        if (temp <= 0) {
            alertBox.style.display = "block";
            alertBox.innerText = "⚠️ Uwaga: Ryzyko gołoledzi!";
        } else { alertBox.style.display = "none"; }

        // Jakość powietrza
        if (data.air_quality) {
            document.getElementById('air-status').innerText = data.air_quality.opis;
            document.getElementById('pm25-val').innerText = Math.round(data.air_quality.pm25);
        }
        
        if (data.kalendarz) {
            document.getElementById('imieniny').innerText = "Imieniny: " + data.kalendarz.imieniny;
        }

    } catch (e) { console.error("Błąd ładowania danych:", e); }
}

setInterval(updateClock, 1000);
setInterval(updateWeather, 300000);
updateClock();
updateWeather();