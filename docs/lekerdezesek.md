# Hasznos lekérdezések

Operator endpoint nincs; a futások állapotát közvetlenül az adatbázisban nézzük.
A lekérdezések a fejlesztői Postgres ellen az alábbi paranccsal futtathatók a repo
gyökeréből (a lekérdezést a `psql` promptjába kell beírni):

```bash
docker compose -f docker-compose.dev.yml exec postgres psql -U swarmsense
```

Egyetlen lekérdezés közvetlenül is megadható: `... psql -U swarmsense -c "<lekérdezés>"`.

## Mai futások státusz szerint

Megmutatja, hány futás indult a mai napon, és hány van `queued`, `running`,
`completed`, `partial` vagy `failed` állapotban. A mintafutás nem számít bele.

```sql
select status, count(*) as futasok
from runs
where created_at >= date_trunc('day', now()) and not is_sample
group by status
order by futasok desc;
```

## Napi tokenösszeg az elmúlt 14 napra

Napi bontásban mutatja a bemeneti és kimeneti tokenek összegét, vagyis hogy mennyit
fogyasztott az LLM-keretből a demó.

```sql
select date_trunc('day', created_at)::date as nap,
       count(*) as futasok,
       sum(input_tokens) as bemeneti_tokenek,
       sum(output_tokens) as kimeneti_tokenek
from runs
where created_at >= now() - interval '14 days' and not is_sample
group by nap
order by nap desc;
```

## Leggyakoribb hibakódok az elmúlt 7 napra

A `run_events` táblából gyűjti ki a hibakóddal rögzített eseményeket (kiesett
persona, elbukott szintézis, elbukott futás), típus szerint bontva, hogy látszódjon,
mi okozza a legtöbb gondot.

```sql
select type, error_code, count(*) as darab
from run_events
where error_code is not null and created_at >= now() - interval '7 days'
group by type, error_code
order by darab desc;
```
