# Skill: Backend SQLAlchemy

## Regole ORM

- naming coerente
- base model condiviso
- schema PostgreSQL esplicito quando richiesto
- modelli focalizzati sulla persistenza

## Regole architetturali

- l'ORM non sostituisce il layer servizi
- i repository incapsulano l'accesso dati
- le migrazioni passano da Alembic, non da modifiche manuali
