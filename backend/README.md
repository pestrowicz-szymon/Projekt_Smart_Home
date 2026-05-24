Dokumentacja Swagger:
`http://localhost:8000/api/docs/`

Ważne! Żeby działał postgresql trzeba go pobrać i przy pobieraniu zapamiętać hasło które sie ustawi, następnie w folderze backend utworzyć plik .env o takiej treści:
POSTGRES_DB=smarthome_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD={HASŁO Z POSTGRESQL}
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

Testowanie:

Logowanie:
POST http://127.0.0.1:8000/api/users/login/ - w body username i password - z tego potrzebny jest access token, żeby móc wykonać inne akcje

Zapraszanie do domu:
POST http://127.0.0.1:8000/api/invites/homes/{HOME_ID}/invites/ - tylko owner domu, zwraca jednorazowy kod ważny 30 minut
POST http://127.0.0.1:8000/api/invites/invites/redeem/ - zalogowany użytkownik podaje code i zostaje dodany do domu

Inne akcje:
XXXX http://127.0.0.1:8000/api/{AKCJA DO WYKONANIA} - tutaj trzeba podążać zgodnie z dokumentacją swagger, w headers dodać Authorization: Bearer {ACCESS_TOKEN}