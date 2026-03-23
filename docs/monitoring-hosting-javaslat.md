# Monitoring hosting javaslat (multi-site)

## Cel

Ez a dokumentum egy gyakorlati javaslatot ad arra, hogyan erdemes a SwarmSense monitoringjat hostolni ugy, hogy kesobb tobb weboldal/szolgaltatas monitorozasara is alkalmas legyen.

## Jelenlegi allapot roviden

- A projektben a Sentry backend es frontend oldalon is be van kotve.
- A Sentry alkalmas hibakovetesre es riasztasra, de nem teljes observability platform.
- Operatori endpointok mar adnak uzleti/operacios metrikakat (futasok, koltseg, email statok).

## Javasolt celarchitektura

Kulon monitoring szerver (vagy kesobb kis cluster), amely tobb projektet kiszolgal.

- `Grafana`: dashboardok es alerting felulet
- `Prometheus`: metrikak gyujtese
- `Alertmanager`: riasztasi routing szabalyok
- `Loki` (+ agent): log gyujtes/kereses
- `Uptime Kuma`: uptime es endpoint monitorozas
- `Sentry` (SaaS vagy self-hosted alternativa): hibakovetes

## Miert kulon szerver?

- Kisebb kockazat: app kieses eseten a monitoring rendszerek nagyobb esellyel elerhetok maradnak.
- Jobb elkulonites: tobb app kozponti megfigyelese egy helyen.
- Egyszerubb uzemeltetes: egyseges backup, frissites, riasztasi policy.

## Domain kerdes

Nem kotelezo, de erosen ajanlott.

- Domain nelkul: VPN-en keresztul IP/hostname alapjan is hasznalhato.
- Domainnel: kenyelmesebb URL-ek, egyszerubb TLS, atlathatobb kezeles.

Ajanlott subdomain minta:

- `grafana.<domain>`
- `uptime.<domain>`
- `logs.<domain>`
- `status.<domain>` (ha nyilvanos status page kell)

## Multi-site monitorozas bevett modja

Tobb oldal monitorozasakor minden metric/log/esemeny kapjon konzisztens cimekeket:

- `project`: pl. `swarmsense`, `site-b`, `site-c`
- `env`: `prod`, `staging`
- `service`: `frontend`, `backend`, `worker`

Ennek hatasa:

- projektenkent kulon dashboardok
- projektenkent kulon riasztasi csatornak
- gyorsabb hibakereses

## Biztonsagi alapelvek

- Monitoring feluletek ne legyenek nyitottak publikusan.
- Hozzaferes VPN mogul (pl. Tailscale/WireGuard), vagy eros auth/SSO mellett.
- HTTPS mindenhol (reverse proxy: Caddy/Traefik/Nginx).
- Titkok es API kulcsok csak szerver oldali secret tarban.

## Uzemeltetesi minimum

- Backup:
  - Grafana konfiguracio/adat
  - Prometheus adat snapshot
  - Loki tarolo
- Retention:
  - metrika: 30-90 nap
  - log: 7-30 nap (forgalomtol fuggoen)
- Riasztas:
  - kritikus: azonnali csatorna (pl. telefon/pager)
  - warning: Slack/email

## SwarmSense-re szabott gyakorlati setup

1. Hagyjatok meg a Sentry-t hibakovetesre (mar mukodik a projektben).
2. Inditsatok kulon monitoring hoston:
   - Grafana
   - Prometheus
   - Alertmanager
   - Uptime Kuma
3. Masodik korben adjatok hozza a Loki loggyujtest.
4. Vezessetek be egységes cimekezest minden szolgaltatasban (`project`, `env`, `service`).
5. Allitsatok be projektenkenti dashboardokat es alert routokat.

## Minimalis bevezetesi terv (2 fazis)

### Fazis 1 (gyors nyereseg)

- Sentry + Uptime Kuma + Grafana/Prometheus alap dashboard
- Legfontosabb riasztasok:
  - API nem elerheto
  - futasi hibaarany tul magas
  - koltsegkuszob/limit
  - email delivery rate romlas

### Fazis 2 (stabilizalas)

- Loki log centralizalas
- Alert deduplikacio es eszkalacios rend
- hosszabb retention, optimalizalt dashboardok

## Donto ajanlas

Igen, erdemes kulon monitoring szervert fenntartani, es igen, ezekkel az eszkozokkel tobb oldal egyideju monitorozasa standard, bevett gyakorlat. A legjobb kompromisszum jelenleg:

- hiba: Sentry
- uptime: Uptime Kuma
- metrika/riasztas: Prometheus + Grafana + Alertmanager
- log: Loki (masodik lepesben)
