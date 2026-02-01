function createWeatherParticles(type) {
    const existing = document.querySelectorAll('.particle');
    existing.forEach(p => p.remove());
    
    const count = type === 'stars' ? 40 : 60;
    for (let i = 0; i < count; i++) {
        let p = document.createElement('div');
        p.className = 'particle ' + type;
        p.style.left = Math.random() * 100 + 'vw';
        if (type === 'stars') {
            p.style.top = Math.random() * 100 + 'vh';
            p.style.animationDelay = Math.random() * 2 + 's';
        } else {
            p.style.animationDuration = (Math.random() * 2 + 1) + 's';
            p.style.animationDelay = Math.random() * 2 + 's';
        }
        document.body.appendChild(p);
    }
}

async function updateWeather() {
    try {
        const response = await fetch('wynik_pogoda.json?t=' + new Date().getTime());
        const data = await response.json();
        
        const desc = data.weather[0].description.toLowerCase();
        const isDay = data.is_day;

        // Tła i Animacje
        document.body.className = isDay ? data.season + '-bg' : 'night-bg';
        if (!isDay) createWeatherParticles('stars');
        else if (desc.includes('śnieg')) createWeatherParticles('snow');
        else if (desc.includes('deszcz')) createWeatherParticles('rain');

        // Dane główne
        document.getElementById('temp-akt').innerText = Math.round(data.main.temp);
        document.getElementById('pogoda-opis').innerText = desc;
        document.getElementById('wind-speed').innerText = data.wind.speed + " m/s";
        document.getElementById('sun-times').innerText = `🌅 ${new Date(data.sys.sunrise*1000).toLocaleTimeString([], {hour:'2-digit', minute:'2-digit'})} | 🌇 ${new Date(data.sys.sunset*1000).toLocaleTimeString([], {hour:'2-digit', minute:'2-digit'})}`;
        document.getElementById('moon-phase').innerText = data.moon;

        // Miasta wojewódzkie
        const list = document.getElementById('woj-list');
        list.innerHTML = data.wojewodztwa.map(m => `<span>${m.city}: <b>${m.temp}°C</b></span>`).join(' • ');

        // Prognoza
        const forecast = document.getElementById('forecast-box');
        forecast.innerHTML = data.forecast.map(f => `<div>${f.dt.split(' ')[0].slice(5)} | ${f.temp}°C | ${f.desc}</div>`).join('');

    } catch (e) { console.log("Ładowanie..."); }
}

setInterval(updateWeather, 300000);
updateWeather();