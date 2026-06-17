# Projekt grupowy - System Smart Home

## Wymagania 

### Funkcjonalność:

- [x] Zdalne monitorowanie czujników (np. temperatury, ruchu).
- [x] Zdalne sterowanie elementami wykonawczymi (np. włączanie światła, zamknięcie zamka).
- [x] Zarządzanie domownikami (dodawanie/usuwanie użytkowników, przypisywanie ról).
- [x] Powiadomienia o zdarzeniach krytycznych (np. wykrycie dymu).

### Bezpieczeństwo:

- [x] Komunikacja z wykorzystaniem interfejsów REST wykorzystujących połączenie HTTPS
- [x] Kolejka komunikatów zapewniających szyfrowanie przesyłanych danych w warstwie transportowej
- [x] Komunikacja z interfejsami REST jest uwierzytelniana tokenami JWT
- [x] Uwierzytelnianie aplikacji podłączających się do kolejek z wykorzystaniem certyfikatów
- [x] Szyfrowanie danych wrażliwych w bazie danych
- [x] MFA
- [x] Zarządzanie uprawnieniami - nie każdy użytkownik będzie mógł usuwać i dodawać nowych użytkowników
- [x] Izolacja komponentów

### Architektura projektu:

- Backend : Django z dodatkiem Django Rest Framework
- Symulator urządzeń: Python
- Frontend: SvelteKit
- Broker : Mosquitto
- Baza danych : PostgreSQL

## Rozwój aplikacji

### Wymagania

- uv/python
- bun/node/deno
- docker compose


### Opis

Dla poprawnego działania serwisów wymagane jest wytworzenie cerytfikatów dla:
- backendu (*backend*)
- symulatora (*gateway*)
- mosquitto (*server*)
- certyfikat *ca* wspólny dla wszystkich serwisów

Certyfikaty muszą znajdować się w folderze certs. Można je wygenerować za pomocą skryptu `generate_certs.sh`

Aby dodwać urządzenia do domu należy najpierw przypisać *gateway* do domu.
Pin do gateway'a otrzymujemy z logów serwisu lub kontenera `docker log [hash kontenera z symulacjami]`.

Urządzenia definiujemy za pomocą pliku 'config.py' w serwisie symulacji.
```py
# simulations/src/config.py

from models import Light, Lock, SmokeDetector, Thermometer


def get_devices(gateway):
    """
    Returns a dictionary of initialized devices for the given gateway.
    """
    return {
        "temp-01": Thermometer(gateway, [UUID], [Nazwa urządzenia]),
        ...
    }


```





