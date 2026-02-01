import requests
import time
import os
import json
from datetime import datetime
import math
from git import Repo

# --- KONFIGURACJA ---
PATH_OF_GIT_REPO = r'.' 
API_KEY = "4ab2a1fe5c04c6ef99fb38d06e42779d"

MIASTA_WOJ = [
    "Białystok", "Bydgoszcz", "Gdańsk", "Gorzów Wielkopolski", "Katowice", "Kielce", 
    "Kraków", "Lublin", "Łódź", "Olsztyn", "Opole", "Poznań", "Rzeszów", 
    "Szczecin", "Toruń", "Warszawa", "Wrocław", "Zielona Góra"
]

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
    m, d = datetime.now().month, datetime.now().day
    if (m == 12 and d >= 21) or m in [1, 2]: return "zima"
    if m in [3, 4, 5]: return "wiosna"
    if m in [6, 7, 8]: return "lato"
    return "jesien"

def pobierz_dane():
    try:
        # Główna pogoda (Widełka)
        p = requests.get(f"http://api.openweathermap.org/data/2.5/weather?q=Widełka,PL&appid={API_KEY}&units=metric&lang=pl").json()
        f = requests.get(f"http://api.openweathermap.org/data/2.5/forecast?q=Widełka,PL&appid={API_KEY}&units=metric&lang=pl").json()
        
        # Miasta wojewódzkie
        woj_pogoda = []
        for m in MIASTA_WOJ:
            res = requests.get(f"http://api.openweathermap.org/data/2.5/weather?q={m},PL&appid={API_KEY}&units=metric").json()
            woj_pogoda.append({"city": m, "temp": round(res['main']['temp'])})
            
        return p, f, woj_pogoda
    except: return None, None, None

def push_to_github():
    try:
        repo = Repo(PATH_OF_GIT_REPO)
        repo.index.add(['wynik_pogoda.json'])
        repo.index.commit(f"Meteo Update: {datetime.now().strftime('%H:%M')}")
        repo.remote().push()
        return "✅ Dane wysłane na stronę"
    except Exception as e: return f"❌ Git: {e}"

while True:
    p, f, woj = pobierz_dane()
    if p:
        wynik = {
            "main": p['main'], "weather": p['weather'], "wind": p['wind'],
            "sys": p['sys'], "is_day": p['sys']['sunrise'] < time.time() < p['sys']['sunset'],
            "moon": get_moon_phase(), "season": get_season(),
            "forecast": [{"temp": round(i['main']['temp']), "desc": i['weather'][0]['description']} for i in f['list'][::8][:3]],
            "wojewodztwa": woj
        }
        with open('wynik_pogoda.json', 'w', encoding='utf-8') as file:
            json.dump(wynik, file, indent=2, ensure_ascii=False)
        print(push_to_github())
    time.sleep(600)