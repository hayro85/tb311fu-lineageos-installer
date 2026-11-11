> ⚠️ **PREVIEW / NICHT FÜR UNBEAUFSICHTIGTES FLASHEN:** Der vollständige GUI-Flashablauf wurde noch nicht auf einem zweiten Gerät getestet. Insbesondere die Moduswechsel zwischen Bootloader-Fastboot (vbmeta) und Fastbootd (system) müssen vor einer öffentlichen Installationsfreigabe validiert werden. Aktuell nur Diagnose und Dokumentation empfehlen.

# TB311FU LineageOS Installer v0.6 (Windows)

**Inoffizielles Community-Projekt – kein Lenovo- oder LineageOS-Produkt.**

Ein deutschsprachiger grafischer Windows-Assistent für die manuelle Installation eines **LineageOS-GSI** auf dem **Lenovo TB311FU**. Er führt durch Geräteprüfung, optionale Bootloader-Entsperrung, Auswahl lokaler Dateien, Flashen und Werksreset. Kritische Aktionen benötigen jeweils eine ausdrückliche Bestätigung.

> **Erfahrungsbericht (11. November 2026):** Ein Lenovo TB311FU mit ZUI 17 / Android 16, MediaTek MT8786 und Produkt `POPLAR_ROW_WIFI` startete erfolgreich mit `LineageOS-23.2-20260524-VANILLA-EXT4-GSI.img`. WLAN, Kamera und alltägliche Nutzung funktionierten nach Aussage des Testers; er beobachtete flüssige Bedienung und niedrigeren Akkuverbrauch. **Ein Einzeltest ist keine Kompatibilitätsgarantie.**

## Automatische Erkennung

- Beim Start werden **ADB und Fastboot** in typischen Windows-Ordnern sowie über `PATH` gesucht.
- Der Assistent prüft **angeschlossene ADB-/Fastboot-Geräte** ohne Schreiboperationen und meldet nicht autorisiertes USB-Debugging.
- **Windows-Treiberdiagnose** liest per PowerShell den Plug-and-Play-Gerätestatus (u. a. MediaTek `VID_0E8D`); sie installiert **keine** Treiber und verändert keine Geräteeinstellungen.
- Bereits vorhandene LineageOS-GSI- und `vbmeta.img`-Dateien in üblichen Ordnern werden vorgeschlagen. Herkunft und Prüfsummen müssen weiterhin manuell bestätigt werden.
- Download-Schaltflächen für offizielle Platform-Tools, Google USB Driver, Community-GSI und Lenovo Support.
- Aktivitätsanzeige und längerer Timeout für Flashvorgänge.

**Einschränkungen:** Keine automatische Treiberinstallation, keine automatische Firmware-Downloads, keine überprüfte Wiederherstellung und keine prozentgenaue Flash-Fortschrittsanzeige. Die Erkennung wurde nicht auf einem Windows-Gerät mit angeschlossenem TB311FU getestet. Kritische Aktionen bleiben manuell und bestätigungspflichtig.

## Downloads

- [Android SDK Platform-Tools (Google)](https://developer.android.com/tools/releases/platform-tools)
- [Google USB Driver (Windows)](https://developer.android.com/studio/run/win-usb)
- [LineageOS-GSI-Releases (MisterZtr)](https://github.com/MisterZtr/LineageOS_gsi/releases) – passende **ARM64 / A/B / VANILLA / EXT4**-Variante auswählen. Dateinamen, Checksummen und Release-Hinweise prüfen.
- [Lenovo Software Fix / Support](https://pcsupport.lenovo.com/) – Original-Firmware für das **eigene** TB311FU bereithalten.

**Keine Firmware, ROMs, Treiber, Seriennummern oder Token sind in diesem Repository enthalten.**

## Start unter Windows

1. Python 3.10 oder neuer installieren (Tkinter muss enthalten sein).
2. Android SDK Platform-Tools herunterladen und entpacken.
3. Bei fehlendem Fastboot-Treiber den Google USB Driver über den Geräte-Manager installieren. Die Treiberauswahl ist geräteabhängig; nicht blind fremde Treiber installieren.
4. `installer.py` mit `python installer.py` starten.
5. Den Platform-Tools-Ordner, das heruntergeladene GSI-`*.img` und die **originale `vbmeta.img` aus der passenden TB311FU-Firmware** auswählen.
6. Die Registerkarten der Reihe nach durcharbeiten. Nach jedem Schritt die Log-Ausgabe prüfen.

## Ablauf und Sicherheit

1. Android mit USB-Debugging starten; Modell `TB311FU`, ARM64, Treble und A/B über ADB bestätigen.
2. Falls erforderlich, Bootloader im regulären Fastboot-Modus entsperren. Die angebotene **MediaTek-LK-Token-Methode ist community-basiert** und kann bei anderer Firmware fehlschlagen. Token wird nur lokal aus zwei Bootloader-Kennungen erzeugt. **Entsperrung löscht Daten.**
3. Fastbootd verwenden und aktiven Slot A sowie logische Partition `system_a` prüfen.
4. Mit originaler, zum eigenen Gerät gehörender `vbmeta.img` die AVB-Verifikation auf `vbmeta_a` deaktivieren.
5. Das ausgewählte EXT4-GSI auf `system_a` schreiben.
6. Nutzerdaten zurücksetzen; bei Bedarf zusätzlich den Factory Reset aus der Android Recovery durchführen.
7. Starten und Funktionen (WLAN, Kamera, Ton, Bluetooth, Standby) testen.

**Kein automatisches Partition-Löschen, kein Flashen von Preloader, kein automatischer Firmware-Download, kein Bootloader-Re-Lock.** Bei jeder Fastboot-Fehlermeldung anhalten. Der Installer unterstützt zunächst nur den **aktiven Slot A** und das beobachtete TB311FU-Layout; bei Slot B nicht fortfahren.

## Bekannte Stolpersteine

- `fastboot flash system_a ...` kann mit `This partition doesn't exist` fehlschlagen, wenn nicht wirklich Fastbootd aktiv ist. **Nicht** wahllos Partitionen löschen. Status prüfen und gegebenenfalls neu in Fastbootd wechseln.
- `Invalid sparse file format at header magic` kann beim Flashen eines rohen EXT4-Images erscheinen; entscheidend ist der finale Status jedes Schreibabschnitts.
- `fastboot -w` kann `File system type raw not supported` melden. Ein Factory Reset über Recovery kann dann erforderlich sein.
- `system_b` muss im dynamischen Partitionslayout nicht als logische Partition vorhanden sein.
- Der Bootloader **darf nach Installation des GSIs nicht wieder gesperrt werden**.
- Die Wiederherstellung über Lenovo Software Fix / SP Flash Tool wurde **nicht** als vollständiger Disaster-Recovery-Ablauf validiert.

## Original-Firmware / Seriennummer

Bei einem Test ließ sich die Original-Firmware in Lenovo Software Fix **allein durch Eingabe der Seriennummer** herunterladen, ohne das Tablet über USB anzuschließen. Ob das bei anderen Geräten oder Programmversionen genauso funktioniert, ist nicht garantiert. Seriennummern niemals in öffentlichen Issues posten.

## Status

**Experimentell / Community Preview.** Noch keine automatisierten Hardwaretests. Bitte vor einer öffentlichen Empfehlung zunächst zusätzliche TB311FU-Tester, Firmwarestände und Checksummen dokumentieren.

## Lizenz

MIT, siehe `LICENSE`. Fremde Downloads unterliegen den Lizenzen ihrer jeweiligen Anbieter.

## Auf GitHub veröffentlichen

1. Auf GitHub ein **öffentliches** Repository `tb311fu-lineageos-installer` anlegen.
2. Den Inhalt dieses Projektordners hochladen (`installer.py`, `README.md`, `LICENSE`, `.gitignore`). **Keine** `*.img`, `sn.img`, Firmwarepakete, Geräte-Logs oder Seriennummern hochladen.
3. Als erste Version `v0.6.0-preview` veröffentlichen und deutlich als **experimentell / ungetesteter Installer** kennzeichnen.
4. Den Assistenten vor einer breiteren Empfehlung zuerst auf einem Testgerät oder mit kontrollierten Fake-ADB-/Fastboot-Antworten prüfen.
5. Rückmeldungen mit Modell, Firmwareversion und Fehlermeldung sammeln, aber Nutzer auffordern, Gerätekennungen und Seriennummern zu schwärzen.


## Languages (v0.6)

The **Language / Sprache** menu offers English, Deutsch, Türkçe, Español and Français. On startup the app uses the Windows UI language when supported, otherwise English. Switching languages keeps selected files, device state and existing log. Hardware diagnostic output and some low-level confirmation/error messages remain in German/English; translations are a first pass. No internet is required for language selection.


## Version 0.6: übersetzte Statusanzeige
Die Statusmeldungen werden in Deutsch, Englisch, Türkisch, Spanisch und Französisch angezeigt. Beim Sprachwechsel werden bereits angezeigte Statusmeldungen neu übersetzt. Originalausgaben von ADB, Fastboot und Windows bleiben zur Fehlersuche unverändert.
