import requests
import time
import os
import json
from datetime import datetime
from git import Repo

# --- KONFIGURACJA ---
PATH_OF_GIT_REPO = r'.' 
API_KEY = "4ab2a1fe5c04c6ef99fb38d06e42779d"

MIASTA = ["Białystok","Bydgoszcz","Gdańsk","Gorzów Wlkp.","Katowice","Kielce","Kraków","Lublin","Łódź","Olsztyn","Opole","Poznań","Rzeszów","Szczecin","Toruń","Warszawa","Wrocław","Zielona Góra"]

def get_moon_phase():
    diff = datetime.now() - datetime(2000, 1, 6, 18, 14)
    lunation = (diff.total_seconds() / 86400 % 29.53) / 29.53
    if lunation < 0.06 or lunation > 0.94: return "Nów"
    if lunation < 0.25: return "Przybywający sierpień"
    if lunation < 0.35: return "Pierwsza kwadra"
    if lunation < 0.50: return "Przybywający wypukły"
    if lunation < 0.56: return "Pełnia"
    return "Ubywający"

def get_season():
    m = datetime.now().month
    if m in [12, 1, 2]: return "zima"
    if m in [3, 4, 5]: return "wiosna"
    if m in [6, 7, 8]: return "lato"
    return "jesien"

while True:
    try:
        # Pogoda główna
        p = requests.get(f"http://api.openweathermap.org/data/2.5/weather?q=Widełka,PL&appid={API_KEY}&units=metric&lang=pl").json()
        
        # Miasta wojewódzkie (uproszczone dla szybkości)
        woj_dane = []
        for m in MIASTA:
            try:
                r = requests.get(f"http://api.openweathermap.org/data/2.5/weather?q={m},PL&appid={API_KEY}&units=metric").json()
                woj_dane.append({"city": m, "temp": round(r['main']['temp'])})
            except: continue

        wynik = {
            "main": p['main'],
            "weather": p['weather'],
            "wind": p['wind'],
            "sys": p['sys'],
            "is_day": p['sys']['sunrise'] < time.time() < p['sys']['sunset'],
            "moon": get_moon_phase(),
            "season": get_season(),
            "woj": woj_dane
        }
        
        with open('wynik_pogoda.json', 'w', encoding='utf-8') as f:
            json.dump(wynik, f, indent=2, ensure_ascii=False)
            
        # Git Push
        repo = Repo(PATH_OF_GIT_REPO)
        repo.index.add(['wynik_pogoda.json'])
        repo.index.commit("Aktualizacja stacji")
        repo.remote().push()
        print("✅ Dane wysłane")
    except Exception as e:
        print(f"❌ Błąd: {e}")
    time.sleep(600)