import requests
import time
import os
import json
from datetime import datetime
from git import Repo

# --- KONFIGURACJA GITHUB ---
PATH_OF_GIT_REPO = r'.' 

def push_to_github():
    """Wysyła plik wynik_pogoda.json do repozytorium GitHub"""
    try:
        repo = Repo(PATH_OF_GIT_REPO)
        repo.index.add(['wynik_pogoda.json'])
        now = datetime.now().strftime("%H:%M:%S")
        repo.index.commit(f"Aktualizacja pogody: {now}")
        origin = repo.remote(name='origin')
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
    
    # Wyciągamy dane na jutro (zazwyczaj indeks [8] w prognozie 3-godzinnej to +24h)
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
        "weather": [{"description": dane_z_api['weather'][0]['description']}],
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
    """NOWA FUNKCJA: Pobiera prognozę 5-dniową"""
    url = "http://api.openweathermap.org/data/2.5/forecast"
    params = {'q': miasto, 'appid': api_key, 'units': 'metric', 'lang': 'pl'}
    try:
        r = requests.get(url, params=params, timeout=10)
        return r.json() if r.status_code == 200 else None
    except:
        return None

def uruchom_stacje():
    miasto = "Widełka, PL"
    api_key = "WPISZ_KLUCZ_API"
    
    baza_imienin = wczytaj_json('dane.json')
    baza_swiat = wczytaj_json('holidays.json')
    
    ostatnia_aktualizacja_pogody = 0
    ostatnia_aktualizacja_sieci = 0
    dane_p = None
    dane_f = None
    status_sieci = "Oczekiwanie..."

    os.system('clear')

    while True:
        teraz_ts = time.time()
        teraz_dt = datetime.now()
        
        # Pobieranie pogody i PROGNOZY co 5 minut
        if teraz_ts - ostatnia_aktualizacja_pogody > 300:
            dane_p = pobierz_pogode_dane(miasto, api_key)
            dane_f = pobierz_prognoze_dane(miasto, api_key)
            ostatnia_aktualizacja_pogody = teraz_ts

        klucz_imienin = teraz_dt.strftime('%m-%d')
        klucz_swiat = teraz_dt.strftime('%Y-%m-%d')
        imieniny = baza_imienin.get(klucz_imienin, "Brak danych")
        swieto = baza_swiat.get(klucz_swiat, None)

        if dane_p:
            zapisz_wynik_pogody(dane_p, dane_f, imieniny, swieto)
            
            if teraz_ts - ostatnia_aktualizacja_sieci > 600:
                status_sieci = push_to_github()
                ostatnia_aktualizacja_sieci = teraz_ts

        print("\033[H", end="") 

        # PANEL INFORMACYJNY
        print("█" + "▀"*55 + "█")
        print(f"  🕒 {teraz_dt.strftime('%H:%M:%S')}  📅 {teraz_dt.strftime('%d.%m.%Y')}  (Widełka)")
        line_swieto = f"  🚩 DZISIAJ: {swieto}" if swieto else "  🚩 DZISIAJ: Dzień powszedni"
        print(line_swieto.ljust(56))
        print(f"  🎂 IMIENINY: {imieniny}".ljust(56))
        print(f"  🌙 KSIĘŻYC: {get_moon_phase()}".ljust(56))
        
        # Wyświetlanie prognozy w konsoli (pod księżycem)
        if dane_f and 'list' in dane_f:
            t_j = round(dane_f['list'][8]['main']['temp'])
            o_j = dane_f['list'][8]['weather'][0]['description']
            print(f"  🔮 JUTRO: {t_j}°C, {o_j}".ljust(56))
            
        print("█" + "▄"*55 + "█")

        if dane_p:
            temp = dane_p['main']['temp']
            odcuwalna = dane_p['main']['feels_like']
            wilgotnosc = dane_p['main']['humidity']
            cisnienie = dane_p['main']['pressure']
            wiatr = dane_p['wind']['speed']
            opis = dane_p['weather'][0]['description']
            widok = dane_p.get('visibility', 0) / 1000
            
            print(f"\n🌡️  POGODA: {temp}°C (Odczuwalna: {odcuwalna}°C)".ljust(57))
            print(f"☁️  STAN: {opis.capitalize()} | 💦 Wilgotność: {wilgotnosc}%".ljust(57))
            print(f"⏲️  CIŚNIENIE: {cisnienie} hPa | 💨 WIATR: {wiatr} m/s".ljust(57))
            print(f"👁️  WIDOCZNOŚĆ: {widok} km".ljust(57))
            
            print("-" * 57)
            alert_drogowy = "✅ WARUNKI DROGOWE: Stabilne"
            if temp <= 2: alert_drogowy = "⚠️  ALERT: Ryzyko gołoledzi! Droga może być śliska."
            if widok < 1: alert_drogowy = "🌫️  ALERT: Gęsta mgła! Zachowaj ostrożność."
            if wiatr > 10: alert_drogowy = "🌬️  ALERT: Silny wiatr! Możliwe utrudnienia."
            print(alert_drogowy.ljust(57))
        
        print("\n" + "." * 57)
        print(f"Status: {status_sieci}".ljust(57))
        
        time.sleep(1)

if __name__ == "__main__":
    uruchom_stacje()
