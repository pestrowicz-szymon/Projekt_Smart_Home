Projekt grupowy - System Smart Home

Wymagania funkcjonalne:
-Zdalne monitorowanie czujników (np. temperatury, ruchu).
-Zdalne sterowanie elementami wykonawczymi (np. włączanie światła, zamknięcie zamka).
-Zarządzanie domownikami (dodawanie/usuwanie użytkowników, przypisywanie ról).
-Powiadomienia o zdarzeniach krytycznych (np. wykrycie dymu).

Wymagania Bezpieczeństwa:
-Komunikacja z wykorzystaniem interfejsów REST wykorzystujących połączenie HTTPS
-Kolejka komunikatów zapewniających szyfrowanie przesyłanych danych w warstwie transportowej
-Komunikacja z interfejsami REST jest uwierzytelniana tokenami JWT
-Uwierzytelnianie aplikacji podłączających się do kolejek z wykorzystaniem certyfikatów
-Szyfrowanie danych wrażliwych w bazie danych
-Uwierzytelnianie dwuetapowe
-Zarządzanie uprawnieniami - nie każdy użytkownik będzie mógł usuwać i dodawać nowych użytkowników
-Izolacja komponentów

Architektura projektu:
-Backend : Django z dodatkiem Django Rest Framework
-Broker : Mosquitto
-Baza danych : PostgreSQL