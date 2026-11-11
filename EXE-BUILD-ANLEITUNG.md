# Windows EXE erstellen und auf GitHub veröffentlichen

## Automatisch auf GitHub

1. Alle Projektdateien **einschließlich** `.github/workflows/windows-exe.yml` in ein öffentliches GitHub-Repository hochladen.
2. Im Repository **Actions** öffnen und Workflow **Build Windows EXE** auswählen.
3. **Run workflow** klicken. Nach erfolgreichem Lauf erscheint unter **Artifacts** die Windows-EXE als ZIP.
4. Für ein Release einen Tag `v0.6.0-preview` erstellen und pushen; der Workflow hängt die EXE automatisch an ein GitHub-Release an. Falls GitHub Actions keine Releases schreiben darf: Settings → Actions → General → Workflow permissions → Read and write permissions prüfen.

## Lokal auf Windows

Python 3 installieren, danach `build-windows.bat` doppelklicken. Ergebnis: `dist/TB311FU-LineageOS-Installer.exe`.

## Wichtige Hinweise

- Das EXE-Paket enthält **keine** Lenovo-Firmware, kein LineageOS-Image und keine USB-Treiber. Die vorhandenen Downloadlinks im Installer bleiben erhalten.
- Die grafische Flash-Installation wurde **nicht vollständig auf einem zweiten TB311FU getestet**. Deshalb nur als **Preview** veröffentlichen und Nutzer ausdrücklich vor Datenverlust und Boot-Problemen warnen.
- Die EXE ist nicht digital signiert; Windows SmartScreen kann eine Warnung anzeigen. Nicht empfehlen, Schutzfunktionen pauschal zu deaktivieren.
- Der Build ist erst dann bestätigt, wenn GitHub Actions erfolgreich durchgelaufen ist. Der Installer muss anschließend unter Windows getestet werden.
