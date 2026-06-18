# Zavrsni_backend
Backend repo

## Environment varijable

Sve env varijable postavljaju se na serveru (docker-compose, docker run -e, ili .env fajl).

### Obavezne (baza)
```
DB_HOST=
DB_NAME=
DB_USER=
DB_PASSWORD=
```

### Sigurnost
```
JWT_SECRET=          # postavi na neki dugi random string, ne ostavljaj defaultni
```

### Email notifikacije (opcionalno)
Bez ovih varijabli aplikacija radi normalno, samo emailovi se ne šalju.
Za Gmail koristi App Password (Google Account → Security → 2-Step Verification → App passwords).

```
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=matecunimi@gmail.com
SMTP_PASS=<16-znakna app password bez razmaka na whapp poslana>
SMTP_FROM=matecunimi@gmail.com
```

### Admin korisnik
Nakon što se netko registrira, ručno postavi admin rolu u bazi:
```sql
UPDATE users SET role = 'admin' WHERE email = 'tvoj@email.com';
```

### Pokretanje migracije (jednom, nakon novog deploya)
```
python migrate.py
```
