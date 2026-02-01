import requests
import time
import os
import json
from datetime import datetime
from git import Repo

# --- KONFIGURACJA ---
PATH_OF_GIT_REPO = r'.' 

# Pobieranie klucza z GitHub Secrets (jeśli skrypt działa na serwerze)
# lub użycie Twojego klucza (jeśli skrypt działa u Ciebie w Widełce)
api_key_env = os.getenv('OPENWEATHER_API_KEY')
if api_key_env:
    API_KEY = api_key_env
else:
    # Wpisz tutaj swój klucz do testów lokalnych
    API_KEY = "4ab2a1fe5c04c6ef99fb38d06e42779d"

def push_to_github():
    """Wysyła plik wynik_pogoda.json do repozytorium GitHub"""
    try:
        repo = Repo(PATH_OF_GIT_REPO)
        # Dodajemy zabezpieczenie rebase, aby uniknąć błędów synchronizacji
        origin = repo.remote(name='origin')
        origin.pull(rebase=True)
        
        repo.index.add(['wynik_pogoda.json'])
        now = datetime.now().strftime("%H:%M:%S")
        repo.index.commit(f"Aktualizacja pogody: {now}")
        origin.push()
        return f"[{now}] ✅ Wysłano do sieci"
    except Exception as e:
        return f"❌ Błąd synchronizacji: {e}"

def get_moon_phase():
    """Oblicza fazę księżyca na podstawie daty"""
    diff = datetime.now() - datetime(2000, 1, 6, 18, 14)
    days = diff.total_seconds() / 86400
    lunation = (days % 29.530588853) / 29.530588853

    if lunation < 0.02 or lunation > 0.98: return "Nów"
    if lunation < 0.24: return "Przybywający sierp"
    if lunation < 0.26: return "Pierwsza kwadra"
    if lunation < 0.48: return "Przybywający wypukły"
    if lunation < 0.52: return "Pełnia"
    if lunation < 0.74: return "Ubywający wypukły"
    if lunation < 0.76: return "Ostatnia kwadra"
    return "Ubywający sierp"

def wczytaj_json(nazwa_pliku):
    try:
        with open(nazwa_pliku, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

def zapisz_wynik_pogody(dane_z_api, dane_prognozy, imieniny, swieto):
    """Zapisuje bieżące dane ORAZ prognozę do pliku wynik_pogoda.json"""
    temp_jutro = "brak"
    opis_jutro = "brak"
    if dane_prognozy and 'list' in dane_prognozy:
        temp_jutro = round(dane_prognozy['list'][8]['main']['temp'])
        opis_jutro = dane_prognozy['list'][8]['weather'][0]['description']

    wynik = {
        "name": dane_z_api['name'],
        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "main": {
            "temp": dane_z_api['main']['temp'],
            "feels_like": dane_z_api['main']['feels_like'],
            "humidity": dane_z_api['main']['humidity'],
            "pressure": dane_z_api['main']['pressure']
        },
        "weather": [{"description": dane_z_api['weather'][0]['description'], "icon": dane_z_api['weather'][0]['icon']}],
        "wind": {
            "speed": dane_z_api['wind']['speed'],
            "gust": dane_z_api['wind'].get('gust', 0)
        },
        "sys": {
            "sunrise": dane_z_api['sys']['sunrise'],
            "sunset": dane_z_api['sys']['sunset']
        },
        "visibility": dane_z_api.get('visibility', 0),
        "moon": get_moon_phase(),
        "kalendarz": {
            "imieniny": imieniny,
            "swieto": swieto if swieto else "Dzień powszedni"
        },
        "prognoza": {
            "temp": temp_jutro,
            "opis": opis_jutro
        }
    }
    try:
        with open('wynik_pogoda.json', 'w', encoding='utf-8') as f:
            json.dump(wynik, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Błąd zapisu JSON: {e}")

def pobierz_pogode_dane(miasto, api_key):
    url = "http://api.openweathermap.org/data/2.5/weather"
    params = {'q': miasto, 'appid': api_key, 'units': 'metric', 'lang': 'pl'}
    try:
        r = requests.get(url, params=params, timeout=10)
        return r.json() if r.status_code == 200 else None
    except:
        return None

def pobierz_prognoze_dane(miasto, api_key):
    url = "http://api.openweathermap.org/data/2.5/forecast"
    params = {'q': miasto, 'appid': api_key, 'units': 'metric', 'lang': 'pl'}
    try:
        r = requests.get(url, params=params, timeout=10)
        return r.json() if r.status_code == 200 else None
    except:
        return None

def uruchom_stacje():
    miasto = "Widełka, PL"
    
    baza_imienin = wczytaj_json('dane.json')
    baza_swiat = wczytaj_json('holidays.json')
    
    # Ustawiamy na 0, żeby pobrało od razu po starcie
    ostatnia_aktualizacja_pogody = 0
    ostatnia_aktualizacja_sieci = 0
    dane_p = None
    dane_f = None
    status_sieci = "Oczekiwanie..."

    while True:
        teraz_ts = time.time()
        teraz_dt = datetime.now()
        
        if teraz_ts - ostatnia_aktualizacja_pogody > 300:
            dane_p = pobierz_pogode_dane(miasto, API_KEY)
            dane_f = pobierz_prognoze_dane(miasto, API_KEY)
            ostatnia_aktualizacja_pogody = teraz_ts

        klucz_imienin = teraz_dt.strftime('%m-%d')
        klucz_swiat = teraz_dt.strftime('%Y-%m-%d')
        imieniny = baza_imienin.get(klucz_imienin, "Brak danych")
        swieto = baza_swiat.get(klucz_swiat, None)

        if dane_p:
            zapisz_wynik_pogody(dane_p, dane_f, imieniny, swieto)
            
            # WYSYŁKA CO 10 MINUT (600 sekund)
            if teraz_ts - ostatnia_aktualizacja_sieci > 600:
                status_sieci = push_to_github()
                ostatnia_aktualizacja_sieci = teraz_ts

        # Czyszczenie ekranu (dla Linux/Windows)
        os.system('cls' if os.name == 'nt' else 'clear')

        # PANEL INFORMACYJNY
        print("█" + "▀"*55 + "█")
        print(f"  🕒 {teraz_dt.strftime('%H:%M:%S')}  📅 {teraz_dt.strftime('%d.%m.%Y')}  (Widełka)")
        line_swieto = f"  🚩 DZISIAJ: {swieto}" if swieto else "  🚩 DZISIAJ: Dzień powszedni"
        print(line_swieto.ljust(56))
        print(f"  🎂 IMIENINY: {imieniny}".ljust(56))
        print(f"  🌙 KSIĘŻYC: {get_moon_phase()}".ljust(56))
        
        if dane_f and 'list' in dane_f:
            t_j = round(dane_f['list'][8]['main']['temp'])
            o_j = dane_f['list'][8]['weather'][0]['description']
            print(f"  🔮 JUTRO: {t_j}°C, {o_j}".ljust(56))
            
        print("█" + "▄"*55 + "█")

        if dane_p:
            temp = dane_p['main']['temp']
            opis = dane_p['weather'][0]['description']
            print(f"\n🌡️  POGODA: {temp}°C | {opis.capitalize()}")
            print(f"Status: {status_sieci}")
        
        time.sleep(1)

if __name__ == "__main__":
    uruchom_stacje()