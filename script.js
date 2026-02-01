// --- FUNKCJA ZEGARA ---
function startClock() {
    const clockElement = document.getElementById('clock');
    
    function update() {
        const now = new Date();
        const timeString = now.toLocaleTimeString('pl-PL', {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });
        if (clockElement) {
            clockElement.innerText = timeString;
        }
    }
    
    setInterval(update, 1000);
    update(); // Start od razu
}

// --- FUNKCJA POGODY ---
async function updateWeather() {
    try {
        const response = await fetch('wynik_pogoda.json?t=' + Date.now());
        const d = await response.json();
        
        // Podstawowe dane
        document.getElementById('temp-akt').innerText = Math.round(d.main.temp);
        document.getElementById('pogoda-opis').innerText = d.weather[0].description;
        
        // Detale (jeśli istnieją w HTML)
        if(document.getElementById('sun')) {
            document.getElementById('sun').innerText = `🌅 ${new Date(d.sys.sunrise*1000).toLocaleTimeString([], {hour:'2-digit', minute:'2-digit'})} | 🌇 ${new Date(d.sys.sunset*1000).toLocaleTimeString([], {hour:'2-digit', minute:'2-digit'})}`;
        }
        if(document.getElementById('wind')) {
            document.getElementById('wind').innerText = `💨 Wiatr: ${d.wind.speed} m/s`;
        }
        if(document.getElementById('moon')) {
            document.getElementById('moon').innerText = `🌙 ${d.moon}`;
        }

        // Miasta wojewódzkie
        const wojElement = document.getElementById('woj');
        if (wojElement && d.wojewodztwa) {
            wojElement.innerHTML = d.wojewodztwa.map(m => ` ${m.city}: ${m.temp}°C `).join(' • ');
        }

        // Tło zależne od dnia/nocy
        document.body.className = d.is_day ? (d.season || 'lato') : 'night';

    } catch (e) {
        console.log("Czekam na dane z pliku JSON...");
    }
}

// --- START WSZYSTKIEGO ---
window.onload = () => {
    startClock();
    updateWeather();
    setInterval(updateWeather, 300000); // Pogoda co 5 min
};