// Funkcja obsługująca zegar
function updateClock() {
    const teraz = new Date();
    const elementZegara = document.getElementById('clock');
    
    if (elementZegara) {
        elementZegara.innerText = teraz.toLocaleTimeString('pl-PL', {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });
    }
}

// Funkcja pobierająca dane pogodowe
async function updateWeather() {
    try {
        const response = await fetch('wynik_pogoda.json?t=' + Date.now());
        const d = await response.json();
        
        const desc = d.weather[0].description.toLowerCase();
        
        // Dane tekstowe
        document.getElementById('temp-akt').innerText = Math.round(d.main.temp);
        document.getElementById('pogoda-opis').innerText = desc;
        
        // Dane dodatkowe (Słońce, Wiatr, Księżyc)
        if(document.getElementById('sun')) {
            document.getElementById('sun').innerText = `🌅 ${new Date(d.sys.sunrise*1000).toLocaleTimeString([], {hour:'2-digit', minute:'2-digit'})} | 🌇 ${new Date(d.sys.sunset*1000).toLocaleTimeString([], {hour:'2-digit', minute:'2-digit'})}`;
        }
        if(document.getElementById('wind')) {
            document.getElementById('wind').innerText = `💨 Wiatr: ${d.wind.speed} m/s`;
        }
        if(document.getElementById('moon')) {
            document.getElementById('moon').innerText = `🌙 ${d.moon}`;
        }

        // Pasek miast wojewódzkich
        const woj = document.getElementById('woj');
        if (woj && d.wojewodztwa) {
            woj.innerHTML = d.wojewodztwa.map(m => ` ${m.city}: ${m.temp}°C `).join(' • ');
        }

        // Zmiana tła strony (Dzień/Noc)
        document.body.className = d.is_day ? (d.season || 'lato') : 'night';

    } catch (e) {
        console.error("Błąd aktualizacji pogody:", e);
    }
}

// URUCHOMIENIE
// 1. Zegar co 1 sekundę
setInterval(updateClock, 1000);
updateClock(); // Pierwsze wywołanie od razu

// 2. Pogoda co 5 minut
setInterval(updateWeather, 300000);
updateWeather(); // Pierwsze wywołanie od razu