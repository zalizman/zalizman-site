# zalizman-site - drift & deploy

Uppdaterad 2026-11-20: NY MARITIMA DESIGN v2 live pa kedjor.

## Struktur

| Sökväg | Innehåll |
|---|---|
| `site/` | Själva sajten - 5 HTML-sidor + images/ (design v2, maritim) |
| `site_backup_2026-11-20/` | Backup av gamla designen (reversibel) |
| `tools/ftp_upload.py` | FTPS-uppladdning till Loopia (list/upload/move) |
| `tools/compress_images.py` | Komprimerar bilder i site/images/ |
| `_research/` | Nedladdat underlag från gamla sajten (skräp, kan raderas) |
| `ftp_credentials.txt.txt` | FTP-inlogg - **ALDRIG i git!** |

## DESIGN v2 (2026-11-20)

- Maritim designsystem: rep-ornament (CSS-gradient), Georgia-serif display,
  mässing/brass-accent, tupp-kaptenen som hero-badge.
- EN huvudspråk: index.html, cbots.html, matrix.html, pics.html, flow.html (NY sida).
- Svenska varianter finns som index-sv.html + cbots-sv.html (orefererade, mall för framtiden).
- Inga emoji som UI-ikoner, accent-disciplin, responsivt (900/600 breakpoints).

## FTP (Loopia)

- Värd: `ftpcluster.loopia.se` (FTPS explicit port 21)
- Kontostruktur:
  - `zalizman.se/public_html/` - **huvuddomänen = NYA DESIGNEN v2 LIVE** (WP flyttad till wp-backup 2026-11-20)
  - `zalizman.se/wp-backup/` - gamla filerna (reversibel backup)
  - `cbots.zalizman.se/public_html/` - samma design (speglas)
  - `autoconfig.zalizman.se/` - e-post-autokonfiguration, rör ej

## Kommandon

```bash
# lista servern
python -I tools/ftp_upload.py list

# uppladdning till huvuddomänen
python -I -u tools/ftp_upload.py upload real /zalizman.se/public_html

# uppladdning till cbots-subdomänen
python -I -u tools/ftp_upload.py upload real /cbots.zalizman.se/public_html

# flytta poster (t.ex. wp-backup)
python -I -u tools/ftp_upload.py move /fran /till
```

> `MSYS_NO_PATHCONV=1` behövs i Git Bash.

## DNS-läge (2026-11-20)

- `zalizman.se` + `www` pekar på **webbhotellet** (93.188.2.56) — v2 designen är LIVE.
- Förhandsgranskning: https://cbots.zalizman.se (samma innehåll).
- Om site-builder åter visas: kontrollera DNS-poster i Loopia-portalen (A 93.188.2.56 + AAAA 2a02:250:0:8::53).

## Bra att veta

- Allt innehåll härstammar från gamla sajten + nya maritima designen.
- Bilder komprimerade: 12,5 MB → 2,5 MB.
- Footer-disclaimer bevarad (hobby project, demo account).
- Payhip-länk: https://payhip.com/ZalizmanTrading · Kontakt: zalizman@pm.me
