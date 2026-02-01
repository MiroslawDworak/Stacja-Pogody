// @ts-nocheck

function startRealTimeClock() {
    const clockEl = document.getElementById('clock');
    if (!clockEl) return;
    setInterval(() => {
        const teraz = new Date();
        clockEl.innerText = teraz.toLocaleTimeString('pl-PL', { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false });
    }, 1000);
}

function updateDayAndStyle(temp, description, isDay) {
    const dni = ["Niedziela", "Poniedziałek", "Wtorek", "Środa", "Czwartek", "Piątek", "Sobota"];
    const teraz = new Date();
    const dzienString = dni[teraz.getDay()];
    const dayEl = document.getElementById('day-of-week');
    if (dayEl) dayEl.innerText = dzienString;

    const card = document.getElementById('weather-card');
    if (!card) return;

    if (temp <= 0) {
        card.style.background = "linear-gradient(180deg, #1e3a8a 0%, #1e1e1e 100%)";
    } else if (description.includes("deszcz")) {
        card.style.background = "linear-gradient(180deg, #374151 0%, #1e1e1e 100%)";
    } else if (!isDay) {
        card.style.background = "linear-gradient(180deg, #0f172a 0%, #1e1e1e 100%)";
    } else {
        card.style.background = "#1e1e1e";
    }
}

async function updateWeather(miejscowosc = "Widełka") {
    try {
        const response = await fetch('wynik_pogoda.json?t=' + new Date().getTime());
        if (!response.ok) return;
        const data = await response.json();

        const setText = (id, text) => {
            const el = document.getElementById(id);
            if (el) el.innerText = text;
        };

        setText('location', miejscowosc);
        setText('temp', Math.round(data.main.temp) + "°C");
        setText('desc', data.weather[0].description);
        setText('wind', data.wind.speed);
        setText('hum', data.main.humidity);
        setText('press', data.main.pressure);
        setText('vis', (data.visibility / 1000).toFixed(1));
        
        if (data.moon) setText('moon', "🌙 " + data.moon);
        if (data.kalendarz) {
            setText('swieto', data.kalendarz.swieto);
            setText('imieniny', "Imieniny: " + data.kalendarz.imieniny);
        }

        const iconBox = document.getElementById('weather-icon');
        const terazUnix = Math.floor(Date.now() / 1000);
        const czy_dzien = data.sys ? (terazUnix > data.sys.sunrise && terazUnix < data.sys.sunset) : true;

        if (iconBox && data.weather[0]) {
            const desc = data.weather[0].description.toLowerCase();
            if (desc.includes("bezchmurnie") || desc.includes("czyste niebo")) {
                iconBox.innerText = czy_dzien ? "☀️" : "🌙";
            } else if (desc.includes("zachmurzenie") || desc.includes("chmury")) {
                iconBox.innerText = czy_dzien ? "⛅" : "☁️";
            } else if (desc.includes("deszcz")) {
                iconBox.innerText = "🌧️";
            } else if (desc.includes("śnieg")) {
                iconBox.innerText = "❄️";
            } else {
                iconBox.innerText = czy_dzien ? "☀️" : "🌙";
            }
        }

        updateDayAndStyle(Math.round(data.main.temp), data.weather[0].description.toLowerCase(), czy_dzien);

        const alertBox = document.getElementById('alert-box');
        const alertText = document.getElementById('alert-text');
        if (alertBox && alertText) {
            if (Math.round(data.main.temp) <= 2) {
                alertBox.style.display = 'block';
                alertText.innerText = "Ryzyko gołoledzi! Droga śliska.";
            } else {
                alertBox.style.display = 'none';
            }
        }

        if (data.prognoza) {
            setText('tomorrow-temp', data.prognoza.temp);
            setText('tomorrow-desc', data.prognoza.opis);
        }

    } catch (e) { console.log("Błąd wczytywania danych JSON."); }
}

startRealTimeClock();
updateWeather();
setInterval(() => updateWeather(), 300000);

const btn = document.getElementById('search-btn');
if (btn) {
    btn.addEventListener('click', () => {
        const city = document.getElementById('city-input').value;
        if (city) updateWeather(city);
    });
}