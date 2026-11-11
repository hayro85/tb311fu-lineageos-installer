#!/usr/bin/env python3
"""TB311FU LineageOS Installer — guided Windows utility, no bundled firmware."""
import hashlib
import locale
import sys
import os
import re
import shutil
import subprocess
import threading
import webbrowser
import queue
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

APP = 'TB311FU LineageOS Installer v0.6'
URLS = {'Platform-Tools': 'https://developer.android.com/tools/releases/platform-tools', 'Google USB-Treiber': 'https://developer.android.com/studio/run/win-usb', 'LineageOS GSI': 'https://github.com/MisterZtr/LineageOS_gsi/releases', 'Lenovo Software Fix': 'https://pcsupport.lenovo.com/'}
MAGIC = b'1a2blenovo3c4d5e' + bytes.fromhex('0000000001000000000000000000000001000000')


# UI language follows Windows system UI language, not a persisted user preference.
# Unsupported system languages fall back to English. Language can be changed
# at any time through the menu, without restarting or modifying the device.
LANGUAGES = {'en': 'English', 'de': 'Deutsch', 'tr': 'Türkçe', 'es': 'Español', 'fr': 'Français'}
TRANSLATIONS = {
 'en': {
  'Community-Werkzeug • nur Lenovo TB311FU • auf eigenes Risiko': 'Community tool • Lenovo TB311FU only • use at your own risk',
  '1. Vorbereitung': '1. Preparation', '2. Prüfen': '2. Check', '3. Entsperren': '3. Unlock', '4. Flashen': '4. Flash', '5. Abschluss': '5. Finish',
  'Sprache': 'Language', 'Bereit': 'Ready', 'Prüfung / Vorgang läuft …': 'Checking / operation in progress …',
  'Bitte erst die Vorbereitung lesen. Der Installer lädt keine Firmware herunter und installiert keine Treiber automatisch.': 'Read the preparation instructions first. The installer does not download firmware or install drivers automatically.',
  'Auswählen': 'Browse', 'Ordner': 'Folder', 'Platform-Tools-Ordner': 'Platform-tools folder', 'Originale vbmeta.img': 'Original vbmeta.img',
  'Automatisch erkennen (Tools, Dateien, USB)': 'Auto-detect tools, files and USB', 'Windows-Treiberdiagnose': 'Windows driver diagnostics', 'Dateien prüfen': 'Validate files',
  'ADB-Gerät und Modell prüfen': 'Check ADB device and model', 'In Bootloader neu starten (ADB)': 'Reboot to bootloader (ADB)', 'Fastboot-Status prüfen': 'Check fastboot status', 'In Fastbootd wechseln': 'Enter fastbootd',
  'Token aus Gerätekennungen lokal erzeugen': 'Generate token locally from device IDs', 'Token an Bootloader übertragen (RISIKO)': 'Send token to bootloader (RISK)', 'Bootloader entsperren (DATENVERLUST)': 'Unlock bootloader (DATA LOSS)',
  'Voraussetzungen erneut prüfen': 'Run preflight checks', 'Verified Boot auf Slot A deaktivieren (RISIKO)': 'Disable verified boot on slot A (RISK)', 'LineageOS auf system_a flashen (RISIKO)': 'Flash LineageOS to system_a (RISK)',
  'Benutzerdaten löschen (UNWIDERRUFLICH)': 'Erase user data (IRREVERSIBLE)', 'Tablet neu starten': 'Reboot tablet',
  'Abgebrochen': 'Stopped', 'FEHLER: ': 'ERROR: ', 'Download: ': 'Download: ',
 },
 'tr': {
  'Community-Werkzeug • nur Lenovo TB311FU • auf eigenes Risiko': 'Topluluk aracı • yalnızca Lenovo TB311FU • sorumluluk size aittir',
  '1. Vorbereitung':'1. Hazırlık','2. Prüfen':'2. Kontrol','3. Entsperren':'3. Kilit açma','4. Flashen':'4. Yükleme','5. Abschluss':'5. Tamamlama',
  'Sprache':'Dil','Bereit':'Hazır','Prüfung / Vorgang läuft …':'Kontrol / işlem sürüyor …',
  'Bitte erst die Vorbereitung lesen. Der Installer lädt keine Firmware herunter und installiert keine Treiber automatisch.':'Önce hazırlık yönergelerini okuyun. Program ürün yazılımını indirmez ve sürücüleri otomatik yüklemez.',
  'Auswählen':'Seç','Ordner':'Klasör','Platform-Tools-Ordner':'Platform-tools klasörü','Originale vbmeta.img':'Orijinal vbmeta.img',
  'Automatisch erkennen (Tools, Dateien, USB)':'Araçları, dosyaları ve USB’yi otomatik algıla','Windows-Treiberdiagnose':'Windows sürücü tanılama','Dateien prüfen':'Dosyaları doğrula',
  'ADB-Gerät und Modell prüfen':'ADB cihazını ve modelini kontrol et','In Bootloader neu starten (ADB)':'Bootloader moduna yeniden başlat (ADB)','Fastboot-Status prüfen':'Fastboot durumunu kontrol et','In Fastbootd wechseln':'Fastbootd moduna geç',
  'Token aus Gerätekennungen lokal erzeugen':'Cihaz kimliklerinden yerel token oluştur','Token an Bootloader übertragen (RISIKO)':'Tokenı bootloader’a gönder (RİSK)','Bootloader entsperren (DATENVERLUST)':'Bootloader kilidini aç (VERİ KAYBI)',
  'Voraussetzungen erneut prüfen':'Ön koşulları tekrar kontrol et','Verified Boot auf Slot A deaktivieren (RISIKO)':'A yuvasında doğrulanmış önyüklemeyi kapat (RİSK)','LineageOS auf system_a flashen (RISIKO)':'LineageOS’u system_a üzerine yaz (RİSK)',
  'Benutzerdaten löschen (UNWIDERRUFLICH)':'Kullanıcı verilerini sil (GERİ ALINAMAZ)','Tablet neu starten':'Tableti yeniden başlat',
  'Abgebrochen':'Durduruldu','FEHLER: ':'HATA: ','Download: ':'İndir: ',
 },
 'es': {
  'Community-Werkzeug • nur Lenovo TB311FU • auf eigenes Risiko':'Herramienta comunitaria • solo Lenovo TB311FU • bajo tu responsabilidad',
  '1. Vorbereitung':'1. Preparación','2. Prüfen':'2. Comprobar','3. Entsperren':'3. Desbloquear','4. Flashen':'4. Instalar','5. Abschluss':'5. Finalizar',
  'Sprache':'Idioma','Bereit':'Listo','Prüfung / Vorgang läuft …':'Comprobación / operación en curso …',
  'Bitte erst die Vorbereitung lesen. Der Installer lädt keine Firmware herunter und installiert keine Treiber automatisch.':'Lee primero las instrucciones. El instalador no descarga firmware ni instala controladores automáticamente.',
  'Auswählen':'Elegir','Ordner':'Carpeta','Platform-Tools-Ordner':'Carpeta de platform-tools','Originale vbmeta.img':'vbmeta.img original',
  'Automatisch erkennen (Tools, Dateien, USB)':'Detectar herramientas, archivos y USB','Windows-Treiberdiagnose':'Diagnóstico de controladores','Dateien prüfen':'Validar archivos',
  'ADB-Gerät und Modell prüfen':'Comprobar dispositivo y modelo ADB','In Bootloader neu starten (ADB)':'Reiniciar al bootloader (ADB)','Fastboot-Status prüfen':'Comprobar fastboot','In Fastbootd wechseln':'Entrar en fastbootd',
  'Token aus Gerätekennungen lokal erzeugen':'Generar token localmente','Token an Bootloader übertragen (RISIKO)':'Enviar token al bootloader (RIESGO)','Bootloader entsperren (DATENVERLUST)':'Desbloquear bootloader (BORRA DATOS)',
  'Voraussetzungen erneut prüfen':'Comprobar requisitos','Verified Boot auf Slot A deaktivieren (RISIKO)':'Desactivar arranque verificado en A (RIESGO)','LineageOS auf system_a flashen (RISIKO)':'Instalar LineageOS en system_a (RIESGO)',
  'Benutzerdaten löschen (UNWIDERRUFLICH)':'Borrar datos (IRREVERSIBLE)','Tablet neu starten':'Reiniciar tableta',
  'Abgebrochen':'Detenido','FEHLER: ':'ERROR: ','Download: ':'Descargar: ',
 },
 'fr': {
  'Community-Werkzeug • nur Lenovo TB311FU • auf eigenes Risiko':'Outil communautaire • Lenovo TB311FU uniquement • à vos risques',
  '1. Vorbereitung':'1. Préparation','2. Prüfen':'2. Vérifier','3. Entsperren':'3. Déverrouiller','4. Flashen':'4. Flasher','5. Abschluss':'5. Terminer',
  'Sprache':'Langue','Bereit':'Prêt','Prüfung / Vorgang läuft …':'Vérification / opération en cours …',
  'Bitte erst die Vorbereitung lesen. Der Installer lädt keine Firmware herunter und installiert keine Treiber automatisch.':'Lisez d’abord les instructions. Le programme ne télécharge pas de firmware et n’installe pas automatiquement les pilotes.',
  'Auswählen':'Parcourir','Ordner':'Dossier','Platform-Tools-Ordner':'Dossier platform-tools','Originale vbmeta.img':'vbmeta.img original',
  'Automatisch erkennen (Tools, Dateien, USB)':'Détecter outils, fichiers et USB','Windows-Treiberdiagnose':'Diagnostic des pilotes Windows','Dateien prüfen':'Vérifier les fichiers',
  'ADB-Gerät und Modell prüfen':'Vérifier appareil et modèle ADB','In Bootloader neu starten (ADB)':'Redémarrer vers bootloader (ADB)','Fastboot-Status prüfen':'Vérifier fastboot','In Fastbootd wechseln':'Passer en fastbootd',
  'Token aus Gerätekennungen lokal erzeugen':'Créer un jeton localement','Token an Bootloader übertragen (RISIKO)':'Envoyer le jeton au bootloader (RISQUE)','Bootloader entsperren (DATENVERLUST)':'Déverrouiller bootloader (PERTE DE DONNÉES)',
  'Voraussetzungen erneut prüfen':'Vérifier les prérequis','Verified Boot auf Slot A deaktivieren (RISIKO)':'Désactiver Verified Boot sur A (RISQUE)','LineageOS auf system_a flashen (RISIKO)':'Flasher LineageOS sur system_a (RISQUE)',
  'Benutzerdaten löschen (UNWIDERRUFLICH)':'Effacer les données (IRRÉVERSIBLE)','Tablet neu starten':'Redémarrer la tablette',
  'Abgebrochen':'Arrêté','FEHLER: ':'ERREUR : ','Download: ':'Télécharger : ',
 }
}
# Log entries are stored in their original form and re-rendered on language changes.
# Technical output from adb/fastboot/Windows remains verbatim to preserve diagnostics.
LOG_I18N = {
'en': {
 '=== Automatische Erkennung (nur lesend) ===':'=== Automatic detection (read-only) ===',
 'Platform-Tools gefunden: ':'Platform-Tools found: ',
 'adb und fastboot über PATH gefunden.':'adb and fastboot found in PATH.',
 'Platform-Tools nicht gefunden: Download-Link in Vorbereitung nutzen.':'Platform-Tools not found: use the download link in Preparation.',
 'vbmeta-Datei gefunden (Herkunft MANUELL prüfen): ':'vbmeta file found (verify origin MANUALLY): ',
 'GSI-Datei gefunden (Release/Hash MANUELL prüfen): ':'GSI file found (verify release/hash MANUALLY): ',
 'Kein Fastboot-Gerät. Wenn Tablet im Bootloader ist: Treiberdiagnose nutzen.':'No Fastboot device. If tablet is in bootloader mode, use driver diagnostics.',
 'USB-Debugging am Tablet autorisieren.':'Authorize USB debugging on the tablet.',
 'Erkennung abgeschlossen. Kein Treiber installiert und keine Partition verändert.':'Detection complete. No drivers installed or partitions modified.',
 '=== Windows USB-/Treiberdiagnose (nur lesend) ===':'=== Windows USB/driver diagnostics (read-only) ===',
 'Keine passenden Geräte gefunden. Tablet anschließen und erneut prüfen.':'No matching devices found. Connect the tablet and check again.',
 'Treiberdiagnose ist nur unter Windows verfügbar.':'Driver diagnostics are only available on Windows.',
 'Windows-Diagnose fehlgeschlagen: ':'Windows diagnostics failed: ',
 'PowerShell-Diagnose nicht verfügbar: ':'PowerShell diagnostics unavailable: ',
 'Bei gelbem Warnsymbol im Geräte-Manager: Google USB Driver herunterladen, Treiber manuell für das richtige Gerät auswählen. Keine automatische Treiberänderung.':'If Device Manager shows a yellow warning icon: download Google USB Driver and manually select it for the correct device. No automatic driver changes.',
 'EXT4 erkannt. Image: ':'EXT4 detected. Image: ',
 'Hashes mit dem vertrauenswürdigen Release vergleichen, sofern Checksummen veröffentlicht wurden.':'Compare hashes with the trusted release, if checksums are published.',
 'TB311FU / ARM64 / Treble / A-B bestätigt.':'TB311FU / ARM64 / Treble / A/B confirmed.',
 'Bootloader entsperrt: ':'Bootloader unlocked: ',
 'Fastbootd gestartet. Bitte danach erneut Fastboot-Status prüfen.':'Fastbootd started. Check Fastboot status again.',
 'Bootloader bereits entsperrt. Kein Token nötig.':'Bootloader already unlocked. No token needed.',
 'Token lokal erzeugt: ':'Token generated locally: ',
 'Bestätigung ggf. am Tablet durchführen. Danach fastboot getvar unlocked erneut prüfen.':'Confirm on tablet if prompted. Then check fastboot getvar unlocked again.',
 'Preflight bestanden. Keine Schreiboperation ausgeführt.':'Preflight passed. No write operation performed.',
 'vbmeta_a geschrieben. Jetzt Fastbootd-Status erneut prüfen.':'vbmeta_a written. Check Fastbootd status again.',
 'system_a geschrieben. Jetzt Werksreset im Abschluss-Tab.':'system_a written. Perform a factory reset in the Finish tab.',
 'Falls „raw not supported“ erscheint und Recovery einen Reset anbietet: Recovery-Factory-Reset verwenden.':'If “raw not supported” appears and Recovery offers a reset, use Recovery factory reset.',
 'Language / Sprache: ':'Language: ',
 ' nicht gefunden. Platform-Tools-Ordner prüfen.':' not found. Check the Platform-Tools folder.',
 ' fehlgeschlagen (Exit ':' failed (exit ',
 ' Bytes; vbmeta: ':' bytes; vbmeta: ',
 ' (356 Bytes). Nicht öffentlich teilen.':' (356 bytes). Do not share publicly.',
 'Kein autorisiertes ADB-Gerät gefunden.':'No authorized ADB device found.',
 'Falsches Gerät: ':'Wrong device: ',
 'Architektur/Treble/A-B-Prüfung fehlgeschlagen.':'Architecture/Treble/A/B check failed.',
 'Kein Fastboot-Gerät gefunden.':'No Fastboot device found.',
 'Bootloader ist gesperrt.':'Bootloader is locked.',
 'Bitte System-Image und originale vbmeta.img auswählen.':'Select a system image and the original vbmeta.img.',
 },
 'tr': {
 '=== Automatische Erkennung (nur lesend) ===':'=== Otomatik algılama (salt okunur) ===',
 'Platform-Tools gefunden: ':'Platform-Tools bulundu: ',
 'adb und fastboot über PATH gefunden.':'adb ve fastboot PATH içinde bulundu.',
 'Platform-Tools nicht gefunden: Download-Link in Vorbereitung nutzen.':'Platform-Tools bulunamadı: Hazırlık bölümündeki indirme bağlantısını kullanın.',
 'vbmeta-Datei gefunden (Herkunft MANUELL prüfen): ':'vbmeta dosyası bulundu (kaynağını ELLE doğrulayın): ',
 'GSI-Datei gefunden (Release/Hash MANUELL prüfen): ':'GSI dosyası bulundu (sürümü/hash değerini ELLE doğrulayın): ',
 'Kein Fastboot-Gerät. Wenn Tablet im Bootloader ist: Treiberdiagnose nutzen.':'Fastboot cihazı yok. Tablet bootloader modundaysa sürücü tanılamasını kullanın.',
 'USB-Debugging am Tablet autorisieren.':'Tablette USB hata ayıklama izni verin.',
 'Erkennung abgeschlossen. Kein Treiber installiert und keine Partition verändert.':'Algılama tamamlandı. Sürücü yüklenmedi, bölümler değiştirilmedi.',
 '=== Windows USB-/Treiberdiagnose (nur lesend) ===':'=== Windows USB/sürücü tanılama (salt okunur) ===',
 'Keine passenden Geräte gefunden. Tablet anschließen und erneut prüfen.':'Uygun cihaz bulunamadı. Tableti bağlayıp yeniden deneyin.',
 'Treiberdiagnose ist nur unter Windows verfügbar.':'Sürücü tanılama yalnızca Windows üzerinde kullanılabilir.',
 'Windows-Diagnose fehlgeschlagen: ':'Windows tanılama başarısız: ',
 'PowerShell-Diagnose nicht verfügbar: ':'PowerShell tanılama kullanılamıyor: ',
 'Bei gelbem Warnsymbol im Geräte-Manager: Google USB Driver herunterladen, Treiber manuell für das richtige Gerät auswählen. Keine automatische Treiberänderung.':'Aygıt Yöneticisi’nde sarı uyarı varsa Google USB sürücüsünü indirip doğru cihaz için elle seçin. Otomatik sürücü değişikliği yapılmaz.',
 'EXT4 erkannt. Image: ':'EXT4 algılandı. İmaj: ',
 'Hashes mit dem vertrauenswürdigen Release vergleichen, sofern Checksummen veröffentlicht wurden.':'Yayımlanmışsa hash değerlerini güvenilir sürümle karşılaştırın.',
 'TB311FU / ARM64 / Treble / A-B bestätigt.':'TB311FU / ARM64 / Treble / A/B doğrulandı.',
 'Bootloader entsperrt: ':'Bootloader kilidi açık: ',
 'Fastbootd gestartet. Bitte danach erneut Fastboot-Status prüfen.':'Fastbootd başlatıldı. Fastboot durumunu tekrar kontrol edin.',
 'Bootloader bereits entsperrt. Kein Token nötig.':'Bootloader kilidi zaten açık. Token gerekmiyor.',
 'Token lokal erzeugt: ':'Token yerel olarak oluşturuldu: ',
 'Bestätigung ggf. am Tablet durchführen. Danach fastboot getvar unlocked erneut prüfen.':'Gerekirse tablette onaylayın. Ardından fastboot getvar unlocked komutunu tekrar kontrol edin.',
 'Preflight bestanden. Keine Schreiboperation ausgeführt.':'Ön kontroller başarılı. Yazma işlemi yapılmadı.',
 'vbmeta_a geschrieben. Jetzt Fastbootd-Status erneut prüfen.':'vbmeta_a yazıldı. Fastbootd durumunu tekrar kontrol edin.',
 'system_a geschrieben. Jetzt Werksreset im Abschluss-Tab.':'system_a yazıldı. Tamamlama sekmesinden fabrika ayarlarına sıfırlayın.',
 'Falls „raw not supported“ erscheint und Recovery einen Reset anbietet: Recovery-Factory-Reset verwenden.':'“raw not supported” görünürse ve Recovery sıfırlama sunarsa Recovery üzerinden fabrika ayarlarına sıfırlayın.',
 'Language / Sprache: ':'Dil: ',
 ' nicht gefunden. Platform-Tools-Ordner prüfen.':' bulunamadı. Platform-Tools klasörünü kontrol edin.',
 ' fehlgeschlagen (Exit ':' başarısız (çıkış kodu ',
 ' Bytes; vbmeta: ':' bayt; vbmeta: ',
 ' (356 Bytes). Nicht öffentlich teilen.':' (356 bayt). Herkese açık paylaşmayın.',
 'Kein autorisiertes ADB-Gerät gefunden.':'Yetkilendirilmiş ADB cihazı bulunamadı.',
 'Falsches Gerät: ':'Yanlış cihaz: ',
 'Architektur/Treble/A-B-Prüfung fehlgeschlagen.':'Mimari/Treble/A-B kontrolü başarısız.',
 'Kein Fastboot-Gerät gefunden.':'Fastboot cihazı bulunamadı.',
 'Bootloader ist gesperrt.':'Bootloader kilitli.',
 'Bitte System-Image und originale vbmeta.img auswählen.':'Sistem imajını ve orijinal vbmeta.img dosyasını seçin.',
 },
 'es': {
 '=== Automatische Erkennung (nur lesend) ===':'=== Detección automática (solo lectura) ===',
 'Platform-Tools gefunden: ':'Platform-Tools encontrados: ',
 'adb und fastboot über PATH gefunden.':'adb y fastboot encontrados en PATH.',
 'Platform-Tools nicht gefunden: Download-Link in Vorbereitung nutzen.':'No se encontraron Platform-Tools. Usa el enlace de descarga en Preparación.',
 'vbmeta-Datei gefunden (Herkunft MANUELL prüfen): ':'Archivo vbmeta encontrado (verifica su origen MANUALMENTE): ',
 'GSI-Datei gefunden (Release/Hash MANUELL prüfen): ':'Archivo GSI encontrado (verifica versión/hash MANUALMENTE): ',
 'Kein Fastboot-Gerät. Wenn Tablet im Bootloader ist: Treiberdiagnose nutzen.':'No hay dispositivo Fastboot. Usa el diagnóstico de controladores.',
 'USB-Debugging am Tablet autorisieren.':'Autoriza la depuración USB en la tableta.',
 'Erkennung abgeschlossen. Kein Treiber installiert und keine Partition verändert.':'Detección terminada. No se instalaron controladores ni se modificaron particiones.',
 '=== Windows USB-/Treiberdiagnose (nur lesend) ===':'=== Diagnóstico USB/controladores de Windows (solo lectura) ===',
 'Keine passenden Geräte gefunden. Tablet anschließen und erneut prüfen.':'No se encontraron dispositivos. Conecta la tableta e inténtalo de nuevo.',
 'Treiberdiagnose ist nur unter Windows verfügbar.':'El diagnóstico de controladores solo funciona en Windows.',
 'Windows-Diagnose fehlgeschlagen: ':'Falló el diagnóstico de Windows: ',
 'PowerShell-Diagnose nicht verfügbar: ':'Diagnóstico de PowerShell no disponible: ',
 'Bei gelbem Warnsymbol im Geräte-Manager: Google USB Driver herunterladen, Treiber manuell für das richtige Gerät auswählen. Keine automatische Treiberänderung.':'Si hay un aviso amarillo en el Administrador de dispositivos, instala manualmente el controlador USB de Google. No se cambian controladores automáticamente.',
 'EXT4 erkannt. Image: ':'EXT4 detectado. Imagen: ',
 'Hashes mit dem vertrauenswürdigen Release vergleichen, sofern Checksummen veröffentlicht wurden.':'Compara los hashes con la versión oficial si hay sumas publicadas.',
 'TB311FU / ARM64 / Treble / A-B bestätigt.':'TB311FU / ARM64 / Treble / A/B confirmado.',
 'Bootloader entsperrt: ':'Bootloader desbloqueado: ',
 'Fastbootd gestartet. Bitte danach erneut Fastboot-Status prüfen.':'Fastbootd iniciado. Comprueba el estado otra vez.',
 'Bootloader bereits entsperrt. Kein Token nötig.':'Bootloader ya desbloqueado. No se necesita token.',
 'Token lokal erzeugt: ':'Token creado localmente: ',
 'Bestätigung ggf. am Tablet durchführen. Danach fastboot getvar unlocked erneut prüfen.':'Confirma en la tableta si se solicita y comprueba fastboot getvar unlocked.',
 'Preflight bestanden. Keine Schreiboperation ausgeführt.':'Comprobaciones previas correctas. No se ha escrito nada.',
 'vbmeta_a geschrieben. Jetzt Fastbootd-Status erneut prüfen.':'vbmeta_a escrito. Comprueba fastbootd.',
 'system_a geschrieben. Jetzt Werksreset im Abschluss-Tab.':'system_a escrito. Restablece datos en Finalizar.',
 'Falls „raw not supported“ erscheint und Recovery einen Reset anbietet: Recovery-Factory-Reset verwenden.':'Si aparece “raw not supported” y Recovery ofrece reinicio de fábrica, úsalo.',
 'Language / Sprache: ':'Idioma: ',
 ' nicht gefunden. Platform-Tools-Ordner prüfen.':' no encontrado. Comprueba Platform-Tools.',
 ' fehlgeschlagen (Exit ':' falló (código ',
 ' Bytes; vbmeta: ':' bytes; vbmeta: ',
 ' (356 Bytes). Nicht öffentlich teilen.':' (356 bytes). No lo compartas públicamente.',
 'Kein autorisiertes ADB-Gerät gefunden.':'No se encontró un dispositivo ADB autorizado.',
 'Falsches Gerät: ':'Dispositivo incorrecto: ',
 'Architektur/Treble/A-B-Prüfung fehlgeschlagen.':'Falló la comprobación de arquitectura/Treble/A-B.',
 'Kein Fastboot-Gerät gefunden.':'No se encontró un dispositivo Fastboot.',
 'Bootloader ist gesperrt.':'El bootloader está bloqueado.',
 'Bitte System-Image und originale vbmeta.img auswählen.':'Selecciona una imagen del sistema y el vbmeta.img original.',
 },
 'fr': {
 '=== Automatische Erkennung (nur lesend) ===':'=== Détection automatique (lecture seule) ===',
 'Platform-Tools gefunden: ':'Platform-Tools trouvés : ',
 'adb und fastboot über PATH gefunden.':'adb et fastboot trouvés dans PATH.',
 'Platform-Tools nicht gefunden: Download-Link in Vorbereitung nutzen.':'Platform-Tools introuvables. Utilisez le lien dans Préparation.',
 'vbmeta-Datei gefunden (Herkunft MANUELL prüfen): ':'Fichier vbmeta trouvé (vérifiez MANUELLEMENT la provenance) : ',
 'GSI-Datei gefunden (Release/Hash MANUELL prüfen): ':'Fichier GSI trouvé (vérifiez MANUELLEMENT la version/le hash) : ',
 'Kein Fastboot-Gerät. Wenn Tablet im Bootloader ist: Treiberdiagnose nutzen.':'Aucun appareil Fastboot. Utilisez le diagnostic des pilotes.',
 'USB-Debugging am Tablet autorisieren.':'Autorisez le débogage USB sur la tablette.',
 'Erkennung abgeschlossen. Kein Treiber installiert und keine Partition verändert.':'Détection terminée. Aucun pilote installé, aucune partition modifiée.',
 '=== Windows USB-/Treiberdiagnose (nur lesend) ===':'=== Diagnostic USB/pilotes Windows (lecture seule) ===',
 'Keine passenden Geräte gefunden. Tablet anschließen und erneut prüfen.':'Aucun appareil correspondant. Branchez la tablette et réessayez.',
 'Treiberdiagnose ist nur unter Windows verfügbar.':'Diagnostic des pilotes disponible uniquement sous Windows.',
 'Windows-Diagnose fehlgeschlagen: ':'Échec du diagnostic Windows : ',
 'PowerShell-Diagnose nicht verfügbar: ':'Diagnostic PowerShell indisponible : ',
 'Bei gelbem Warnsymbol im Geräte-Manager: Google USB Driver herunterladen, Treiber manuell für das richtige Gerät auswählen. Keine automatische Treiberänderung.':'En cas d’alerte jaune dans le Gestionnaire de périphériques, installez manuellement le pilote USB Google. Aucun changement automatique.',
 'EXT4 erkannt. Image: ':'EXT4 détecté. Image : ',
 'Hashes mit dem vertrauenswürdigen Release vergleichen, sofern Checksummen veröffentlicht wurden.':'Comparez les empreintes avec la version fiable si disponibles.',
 'TB311FU / ARM64 / Treble / A-B bestätigt.':'TB311FU / ARM64 / Treble / A/B confirmé.',
 'Bootloader entsperrt: ':'Bootloader déverrouillé : ',
 'Fastbootd gestartet. Bitte danach erneut Fastboot-Status prüfen.':'Fastbootd démarré. Vérifiez à nouveau son état.',
 'Bootloader bereits entsperrt. Kein Token nötig.':'Bootloader déjà déverrouillé. Aucun jeton nécessaire.',
 'Token lokal erzeugt: ':'Jeton créé localement : ',
 'Bestätigung ggf. am Tablet durchführen. Danach fastboot getvar unlocked erneut prüfen.':'Confirmez sur la tablette si demandé, puis vérifiez fastboot getvar unlocked.',
 'Preflight bestanden. Keine Schreiboperation ausgeführt.':'Vérifications préalables réussies. Aucune écriture effectuée.',
 'vbmeta_a geschrieben. Jetzt Fastbootd-Status erneut prüfen.':'vbmeta_a écrit. Vérifiez fastbootd.',
 'system_a geschrieben. Jetzt Werksreset im Abschluss-Tab.':'system_a écrit. Réinitialisez dans Terminer.',
 'Falls „raw not supported“ erscheint und Recovery einen Reset anbietet: Recovery-Factory-Reset verwenden.':'Si “raw not supported” apparaît et Recovery propose une réinitialisation, utilisez-la.',
 'Language / Sprache: ':'Langue : ',
 ' nicht gefunden. Platform-Tools-Ordner prüfen.':' introuvable. Vérifiez le dossier Platform-Tools.',
 ' fehlgeschlagen (Exit ':' a échoué (code ',
 ' Bytes; vbmeta: ':' octets ; vbmeta : ',
 ' (356 Bytes). Nicht öffentlich teilen.':' (356 octets). Ne partagez pas publiquement.',
 'Kein autorisiertes ADB-Gerät gefunden.':'Aucun appareil ADB autorisé.',
 'Falsches Gerät: ':'Mauvais appareil : ',
 'Architektur/Treble/A-B-Prüfung fehlgeschlagen.':'Échec de la vérification architecture/Treble/A-B.',
 'Kein Fastboot-Gerät gefunden.':'Aucun appareil Fastboot trouvé.',
 'Bootloader ist gesperrt.':'Bootloader verrouillé.',
 'Bitte System-Image und originale vbmeta.img auswählen.':'Sélectionnez l’image système et le vbmeta.img original.',
 }
}

def translate_log_line(line, lang):
    if lang == 'de' or line.startswith('> '):
        return line
    translations = LOG_I18N.get(lang, LOG_I18N['en'])
    if line in translations:
        return translations[line]
    for original, translated in translations.items():
        if line.startswith(original):
            return translated + line[len(original):]
    return line

# Longer instructional texts are translated separately and displayed in each tab.
INSTRUCTIONS = {
'en': [
 '1. Have Windows 10/11, a USB data cable and recent Android SDK Platform-Tools ready. If necessary, install the official Google USB driver manually in Device Manager. Avoid unknown unsigned drivers.',
 '2. Lenovo Software Fix may offer stock firmware for recovery. One TB311FU owner could download it using only the serial number. Never publish serial numbers in GitHub issues.',
 '3. Download the ARM64 / A/B / Vanilla / EXT4 LineageOS GSI from its original release. This project does not redistribute the GSI.',
 '4. Use only vbmeta.img from stock firmware matching your own TB311FU. Never use an unrelated vbmeta image.',
 'With Android running, authorize USB debugging and check the device. Bootloader and fastbootd checks require their respective modes.',
 'Note: the active slot and system_a are checked again before flashing. This installer only supports the tested slot A.',
 'Only for locked devices. This community MediaTek LK method is not verified for every firmware. Unlocking may erase data or render the device unusable.',
 'The token is generated locally. No serial numbers are sent to a server. You may need to confirm unlocking on the tablet.',
 'Warning: these actions change system partitions and may cause boot loops. Back up data, obtain recovery firmware, and verify that the device is a TB311FU.',
 'If a partition is missing or flashing fails, do not automatically retry. Check fastbootd and partition layout first. Never erase super or product automatically.',
 'After flashing, a factory reset deletes all user data. First boot may take several minutes. Recovery may offer “Try Again” or “Factory data Reset”.',
 'Do NOT relock the bootloader. Test Wi-Fi, camera, audio, standby, Bluetooth and battery use. Compatibility and updates are not guaranteed.'
],
'de': [
 '1. Windows 10/11, USB-Datenkabel und aktuelle Android SDK Platform-Tools bereithalten. Google USB-Treiber ggf. über den Windows-Geräte-Manager manuell installieren. Keine unsignierten Treiber aus unbekannten Quellen verwenden.',
 '2. Lenovo Software Fix kann die passende Original-Firmware als Rückfalloption anbieten. Bei einem getesteten TB311FU war der Download allein mit der Seriennummer möglich. Die Seriennummer niemals im GitHub-Issue veröffentlichen.',
 '3. LineageOS-GSI als ARM64 / A/B / Vanilla / EXT4 vom Original-Release herunterladen. Das GSI wird nicht mit diesem Projekt verteilt.',
 '4. Die vbmeta.img muss aus der zum eigenen TB311FU passenden Original-Firmware stammen. Keine fremde vbmeta verwenden.',
 'Android normal gestartet: USB-Debugging erlauben. Dann Gerät prüfen. Für Bootloader-/Fastbootd-Prüfungen muss das Tablet im jeweiligen Modus sein.',
 'Hinweis: Der aktive Slot und das Vorhandensein von system_a werden vor dem Flashen erneut geprüft. Der Installer unterstützt ausschließlich den getesteten Slot A.',
 'Nur für noch gesperrte Geräte. Die Methode basiert auf einer Community-Anleitung für den MediaTek-LK-Bootloader. Sie ist nicht für jede Firmware verifiziert. Der Vorgang kann Daten löschen und das Gerät unbrauchbar machen.',
 'Der Token wird ausschließlich lokal erstellt. Es werden keine Seriennummern an einen Server gesendet. Der Benutzer muss den Entsperrvorgang auf dem Tablet ggf. bestätigen.',
 'Achtung: Diese Aktionen verändern Systempartitionen und können Bootloops verursachen. Nur ausführen, wenn Original-Firmware als Wiederherstellungsoption vorhanden ist, alle Daten gesichert sind und das Gerät als TB311FU identifiziert wurde.',
 'Bei „partition doesn’t exist“ oder anderen Fehlern NICHT automatisch wiederholen. Zuerst Fastbootd/Partitionen erneut prüfen. Kein automatisches Löschen von super, product oder anderen Partitionen.',
 'Nach erfolgreichem Flashen: Werksreset löscht alle Benutzerdaten. Der erste Start kann mehrere Minuten dauern. Wenn Recovery „Try Again“ / „Factory data Reset“ zeigt, kann ein Recovery-Reset nötig sein.',
 'Bootloader NICHT wieder sperren. WLAN, Kamera, Ton, Standby, Bluetooth und Akkuverbrauch testen. Keine automatische Garantie für Updates oder Hardwarekompatibilität.'
],
'tr': [
 '1. Windows 10/11, USB veri kablosu ve güncel Android SDK Platform-Tools hazırlayın. Gerekirse resmi Google USB sürücüsünü Aygıt Yöneticisi üzerinden elle kurun. Bilinmeyen imzasız sürücülerden kaçının.',
 '2. Lenovo Software Fix, kurtarma için orijinal yazılımı sağlayabilir. Bir TB311FU cihazında yalnızca seri numarasıyla indirilebildi. Seri numaranızı GitHub üzerinde paylaşmayın.',
 '3. ARM64 / A/B / Vanilla / EXT4 LineageOS GSI dosyasını orijinal sürüm sayfasından indirin. Bu proje GSI dosyasını dağıtmaz.',
 '4. Yalnızca kendi TB311FU cihazınıza uygun orijinal yazılımdan alınmış vbmeta.img kullanın.',
 'Android açıkken USB hata ayıklamaya izin verin ve cihazı kontrol edin. Bootloader ve fastbootd kontrolleri ilgili modda yapılmalıdır.',
 'Not: Yükleme öncesinde etkin yuva ve system_a yeniden kontrol edilir. Yalnızca test edilen A yuvası desteklenir.',
 'Yalnızca kilitli cihazlar için. Bu topluluk yöntemi her sürümde doğrulanmamıştır. Veriler silinebilir veya cihaz kullanılamaz hale gelebilir.',
 'Token yalnızca yerel olarak oluşturulur. Seri numaraları sunucuya gönderilmez. Kilit açma işlemini tablette onaylamanız gerekebilir.',
 'Uyarı: Bu işlemler sistem bölümlerini değiştirir ve açılış döngüsüne yol açabilir. Verilerinizi yedekleyin, kurtarma yazılımını edinin ve cihaz modelini doğrulayın.',
 'Bölüm bulunamazsa veya yükleme başarısız olursa otomatik tekrar denemeyin. Önce fastbootd ve bölüm düzenini kontrol edin. super/product bölümlerini silmeyin.',
 'Yüklemeden sonra fabrika ayarlarına sıfırlama tüm kullanıcı verilerini siler. İlk açılış birkaç dakika sürebilir. Kurtarma ekranında sıfırlama gerekebilir.',
 'Bootloader kilidini tekrar KAPATMAYIN. Wi-Fi, kamera, ses, bekleme, Bluetooth ve pili test edin. Uyumluluk garanti değildir.'
],
'es': [
 '1. Prepara Windows 10/11, un cable USB de datos y Android SDK Platform-Tools reciente. Instala manualmente el controlador USB oficial si hace falta.',
 '2. Lenovo Software Fix puede ofrecer firmware original de recuperación. En un TB311FU bastó el número de serie. No publiques números de serie.',
 '3. Descarga LineageOS GSI ARM64 / A/B / Vanilla / EXT4 desde la publicación original. Este proyecto no lo redistribuye.',
 '4. Usa solo vbmeta.img del firmware original correspondiente a tu TB311FU.',
 'Con Android iniciado, autoriza la depuración USB y comprueba el dispositivo. Para otras comprobaciones entra en el modo correspondiente.',
 'Nota: se revisan la ranura activa y system_a antes de instalar. Solo se admite la ranura A probada.',
 'Solo para dispositivos bloqueados. El método comunitario no está verificado en todos los firmwares. Puede borrar datos o inutilizar el dispositivo.',
 'El token se crea localmente. No se envían números de serie a servidores. Puede requerirse confirmación en la tableta.',
 'Aviso: estas operaciones modifican particiones y pueden impedir el arranque. Haz una copia de seguridad y verifica el modelo.',
 'Si falta una partición o falla la instalación, no repitas automáticamente. Comprueba fastbootd y el diseño de particiones.',
 'Tras instalar, el restablecimiento borra todos los datos. El primer inicio puede tardar varios minutos; puede requerirse un restablecimiento desde Recovery.',
 'NO vuelvas a bloquear el bootloader. Prueba Wi-Fi, cámara, audio, suspensión, Bluetooth y batería. No se garantiza la compatibilidad.'
],
'fr': [
 '1. Préparez Windows 10/11, un câble USB de données et Android SDK Platform-Tools récent. Installez manuellement le pilote USB officiel si nécessaire.',
 '2. Lenovo Software Fix peut fournir le firmware d’origine. Sur un TB311FU, le numéro de série a suffi. Ne publiez jamais votre numéro de série.',
 '3. Téléchargez le GSI LineageOS ARM64 / A/B / Vanilla / EXT4 depuis sa publication d’origine. Ce projet ne le redistribue pas.',
 '4. Utilisez uniquement vbmeta.img provenant du firmware d’origine correspondant à votre TB311FU.',
 'Avec Android démarré, autorisez le débogage USB et vérifiez l’appareil. Les autres contrôles nécessitent les modes correspondants.',
 'Remarque : le slot actif et system_a sont vérifiés avant le flash. Seul le slot A testé est pris en charge.',
 'Réservé aux appareils verrouillés. Cette méthode communautaire n’est pas validée pour tous les firmwares. Elle peut effacer les données ou bloquer l’appareil.',
 'Le jeton est créé localement. Aucun numéro de série n’est envoyé à un serveur. Une confirmation sur la tablette peut être nécessaire.',
 'Attention : ces actions modifient les partitions et peuvent empêcher le démarrage. Sauvegardez vos données et vérifiez le modèle.',
 'Si une partition est absente ou si le flash échoue, ne réessayez pas automatiquement. Vérifiez fastbootd et les partitions.',
 'Après le flash, la réinitialisation efface toutes les données. Le premier démarrage peut être long. Recovery peut demander une réinitialisation.',
 'Ne reverrouillez PAS le bootloader. Testez Wi-Fi, caméra, son, veille, Bluetooth et batterie. Compatibilité non garantie.'
]}

def system_language():
    if sys.platform == 'win32':
        try:
            import ctypes
            # Windows UI language, e.g. 0x0407 de-DE, 0x041F tr-TR.
            lid = ctypes.windll.kernel32.GetUserDefaultUILanguage()
            mapping = {0x07:'de', 0x09:'en', 0x1f:'tr', 0x0a:'es', 0x0c:'fr'}
            return mapping.get(lid & 0x3ff, 'en')
        except (OSError, AttributeError):
            return 'en'
    loc = locale.getlocale()[0] or ''
    code = loc.split('_')[0].lower()
    return code if code in LANGUAGES else 'en'

class Wizard(tk.Tk):
    def __init__(self):
        super().__init__()
        self.lang = system_language()
        self.title(APP)
        # Keep the status log visible on typical laptop/desktop displays.
        screen_height = self.winfo_screenheight()
        window_height = min(900, max(620, screen_height - 90))
        self.geometry(f'900x{window_height}')
        self.minsize(740, min(700, window_height))
        self.tools = tk.StringVar(value=str(Path.cwd()))
        self.image = tk.StringVar()
        self.vbmeta = tk.StringVar()
        self.model_ok = False
        self.unlocked = False
        self.fastbootd = False
        self.slot = None
        self.busy = False
        self.log_history = []
        self.progress = tk.StringVar(value=self.t("Bereit"))
        self.lang_choice = tk.StringVar(value=self.lang)
        self.build_ui()
        self.after(250, lambda: self.run(self.detect_environment))

    def t(self, msg):
        if self.lang == 'de':
            return msg
        return TRANSLATIONS.get(self.lang, TRANSLATIONS['en']).get(msg, TRANSLATIONS['en'].get(msg, msg))

    def change_language(self, language):
        if language not in LANGUAGES or language == self.lang or self.busy:
            return
        self.lang = language
        self.lang_choice.set(language)
        selected = self.tabs.index(self.tabs.select())
        # Rebuild the widgets. Device state, selected paths and log are retained.
        for widget in self.winfo_children():
            if widget is not self.log:
                widget.destroy()
        # Rebuild whole UI, preserving log text and active tab.
        self.log.destroy()
        self.build_ui(initial_note=False)
        self.render_log()
        self.tabs.select(selected)
        self.progress.set(self.t('Bereit'))
        self.note(f'Language / Sprache: {LANGUAGES[language]}')

    def build_ui(self, initial_note=True):
        menu = tk.Menu(self)
        lang_menu = tk.Menu(menu, tearoff=False)
        for code, name in LANGUAGES.items():
            lang_menu.add_radiobutton(label=name, value=code, variable=self.lang_choice,
                                      command=lambda c=code: self.change_language(c))
        menu.add_cascade(label=self.t('Sprache'), menu=lang_menu)
        self.configure(menu=menu)
        top = ttk.Frame(self, padding=12)
        top.pack(fill='x')
        ttk.Label(top, text=APP, font=('Segoe UI', 17, 'bold')).pack(anchor='w')
        ttk.Label(top, text=self.t('Community-Werkzeug • nur Lenovo TB311FU • auf eigenes Risiko')).pack(anchor='w')
        self.tabs = ttk.Notebook(self)
        self.tabs.pack(fill='both', expand=True, padx=12, pady=5)
        for title, fn in [('1. Vorbereitung', self.prepare), ('2. Prüfen', self.inspect), ('3. Entsperren', self.unlock_tab), ('4. Flashen', self.flash_tab), ('5. Abschluss', self.finish_tab)]:
            frame = ttk.Frame(self.tabs, padding=14)
            self.tabs.add(frame, text=self.t(title))
            fn(frame)
        ttk.Label(self, textvariable=self.progress).pack(anchor='w', padx=12)
        self.bar = ttk.Progressbar(self, mode='indeterminate')
        self.bar.pack(fill='x', padx=12, pady=3)
        self.log = tk.Text(self, height=10, wrap='word', state='disabled', font=('Consolas', 9))
        self.log.pack(fill='both', expand=True, padx=12, pady=(4, 10))
        if initial_note:
            self.note(self.t('Bitte erst die Vorbereitung lesen. Der Installer lädt keine Firmware herunter und installiert keine Treiber automatisch.'))

    def render_log(self):
        """Redraw translated status messages while keeping tool output unchanged."""
        self.log.configure(state='normal')
        self.log.delete('1.0', 'end')
        for message, technical in self.log_history:
            rendered = message if technical else '\n'.join(
                translate_log_line(line, self.lang) for line in message.split('\n')
            )
            self.log.insert('end', rendered + '\n')
        self.log.see('end')
        self.log.configure(state='disabled')

    def note(self, msg, technical=False):
        if threading.current_thread() is not threading.main_thread():
            self.after(0, self.note, msg, technical)
            return
        message = str(msg).rstrip()
        self.log_history.append((message, technical))
        self.log.configure(state='normal')
        rendered = message if technical else '\n'.join(
            translate_log_line(line, self.lang) for line in message.split('\n')
        )
        self.log.insert('end', rendered + '\n')
        self.log.see('end')
        self.log.configure(state='disabled')

    def label(self, parent, text):
        ttk.Label(parent, text=self.t(text), wraplength=770, justify='left').pack(anchor='w', pady=(0, 10))

    def pick(self, parent, title, variable, filetypes):
        line = ttk.Frame(parent)
        line.pack(fill='x', pady=5)
        ttk.Label(line, text=self.t(title), width=24).pack(side='left')
        ttk.Entry(line, textvariable=variable).pack(side='left', fill='x', expand=True, padx=6)
        ttk.Button(line, text=self.t('Auswählen'), command=lambda: variable.set(filedialog.askopenfilename(filetypes=filetypes) or variable.get())).pack(side='left')

    def prepare(self, f):
        self.label(f, INSTRUCTIONS[self.lang][0])
        self.label(f, INSTRUCTIONS[self.lang][1])
        self.label(f, INSTRUCTIONS[self.lang][2])
        self.label(f, INSTRUCTIONS[self.lang][3])
        row = ttk.Frame(f)
        row.pack(fill='x', pady=10)
        ttk.Label(row, text=self.t('Platform-Tools-Ordner'), width=24).pack(side='left')
        ttk.Entry(row, textvariable=self.tools).pack(side='left', fill='x', expand=True, padx=6)
        ttk.Button(row, text=self.t('Ordner'), command=lambda: self.tools.set(filedialog.askdirectory() or self.tools.get())).pack(side='left')
        self.pick(f, 'LineageOS system.img', self.image, [('Android Image', '*.img'), ('Alle Dateien', '*.*')])
        self.pick(f, 'Originale vbmeta.img', self.vbmeta, [('Android Image', '*.img'), ('Alle Dateien', '*.*')])
        ttk.Button(f, text=self.t('Automatisch erkennen (Tools, Dateien, USB)'), command=lambda: self.run(self.detect_environment)).pack(anchor='w', pady=5)
        ttk.Button(f, text=self.t('Windows-Treiberdiagnose'), command=lambda: self.run(self.driver_diagnostics)).pack(anchor='w', pady=5)
        links = ttk.Frame(f)
        links.pack(fill='x', pady=6)
        for label, url in URLS.items():
            ttk.Button(links, text=self.t('Download: ') + label, command=lambda u=url: webbrowser.open(u)).pack(anchor='w', pady=2)
        ttk.Button(f, text=self.t('Dateien prüfen'), command=lambda: self.run(self.validate_files)).pack(anchor='w', pady=10)

    def inspect(self, f):
        self.label(f, INSTRUCTIONS[self.lang][4])
        ttk.Button(f, text=self.t('ADB-Gerät und Modell prüfen'), command=lambda: self.run(self.adb_check)).pack(anchor='w', pady=4)
        ttk.Button(f, text=self.t('In Bootloader neu starten (ADB)'), command=lambda: self.run(lambda: self.command('adb', 'reboot', 'bootloader'))).pack(anchor='w', pady=4)
        ttk.Button(f, text=self.t('Fastboot-Status prüfen'), command=lambda: self.run(self.fastboot_check)).pack(anchor='w', pady=4)
        ttk.Button(f, text=self.t('In Fastbootd wechseln'), command=lambda: self.run(self.enter_fastbootd)).pack(anchor='w', pady=4)
        self.label(f, INSTRUCTIONS[self.lang][5])

    def unlock_tab(self, f):
        self.label(f, INSTRUCTIONS[self.lang][6])
        ttk.Button(f, text=self.t('Token aus Gerätekennungen lokal erzeugen'), command=lambda: self.run(self.make_token)).pack(anchor='w', pady=5)
        ttk.Button(f, text=self.t('Token an Bootloader übertragen (RISIKO)'), command=lambda: self.run(self.flash_token)).pack(anchor='w', pady=5)
        ttk.Button(f, text=self.t('Bootloader entsperren (DATENVERLUST)'), command=lambda: self.run(self.oem_unlock)).pack(anchor='w', pady=5)
        self.label(f, INSTRUCTIONS[self.lang][7])

    def flash_tab(self, f):
        self.label(f, INSTRUCTIONS[self.lang][8])
        ttk.Button(f, text=self.t('Voraussetzungen erneut prüfen'), command=lambda: self.run(self.preflight)).pack(anchor='w', pady=5)
        ttk.Button(f, text=self.t('Verified Boot auf Slot A deaktivieren (RISIKO)'), command=lambda: self.run(self.flash_vbmeta)).pack(anchor='w', pady=5)
        ttk.Button(f, text=self.t('LineageOS auf system_a flashen (RISIKO)'), command=lambda: self.run(self.flash_system)).pack(anchor='w', pady=5)
        self.label(f, INSTRUCTIONS[self.lang][9])

    def finish_tab(self, f):
        self.label(f, INSTRUCTIONS[self.lang][10])
        ttk.Button(f, text=self.t('Benutzerdaten löschen (UNWIDERRUFLICH)'), command=lambda: self.run(self.wipe)).pack(anchor='w', pady=5)
        ttk.Button(f, text=self.t('Tablet neu starten'), command=lambda: self.run(self.reboot)).pack(anchor='w', pady=5)
        self.label(f, INSTRUCTIONS[self.lang][11])

    def binary(self, name):
        exe = Path(self.tools.get()) / (name + '.exe' if os.name == 'nt' else name)
        if exe.is_file():
            return str(exe)
        result = shutil.which(name)
        if result:
            return result
        raise RuntimeError(f'{name} nicht gefunden. Platform-Tools-Ordner prüfen.')

    def command(self, tool, *args):
        cmd = [self.binary(tool), *args]
        self.note('> ' + tool + ' ' + ' '.join(str(a) for a in args if 'token' not in str(a).lower()))
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=1800 if 'flash' in args else 240, errors='replace')
        result = (p.stdout + '\n' + p.stderr).strip()
        self.note(result, technical=True)
        if p.returncode:
            raise RuntimeError(f'{tool} fehlgeschlagen (Exit {p.returncode}).')
        return result

    def run(self, fn):
        if self.busy:
            return
        self.busy = True
        self.after(0, lambda: (self.progress.set(self.t('Prüfung / Vorgang läuft …')), self.bar.start(12)))
        def worker():
            try:
                fn()
            except Exception as e:
                self.after(0, lambda err=str(e): messagebox.showerror(self.t('Abgebrochen'), err))
                self.note(self.t('FEHLER: ') + str(e))
            finally:
                self.busy = False
                self.after(0, lambda: (self.bar.stop(), self.progress.set(self.t('Bereit'))))
        threading.Thread(target=worker, daemon=True).start()

    def confirm(self, title, msg):
        # Modal dialogs must execute on Tk main thread.
        import queue
        q = queue.Queue(maxsize=1)
        self.after(0, lambda: q.put(messagebox.askyesno(title, msg)))
        return q.get()

    @staticmethod
    def candidate_tool_dirs():
        home = Path.home()
        roots = [Path.cwd(), Path('C:/platform-tools'), home / 'platform-tools', home / 'Downloads' / 'platform-tools', home / 'Desktop' / 'platform-tools', home / 'AppData/Local/Android/Sdk/platform-tools']
        sdk = os.environ.get('ANDROID_HOME') or os.environ.get('ANDROID_SDK_ROOT')
        if sdk:
            roots.insert(0, Path(sdk) / 'platform-tools')
        return roots

    def detect_environment(self):
        """Read-only discovery; never downloads, installs drivers or flashes."""
        self.note('=== Automatische Erkennung (nur lesend) ===')
        selected = Path(self.tools.get())
        dirs = [selected] + self.candidate_tool_dirs()
        found = None
        for directory in dirs:
            adb = directory / ('adb.exe' if os.name == 'nt' else 'adb')
            fastboot = directory / ('fastboot.exe' if os.name == 'nt' else 'fastboot')
            if adb.is_file() and fastboot.is_file():
                found = directory
                break
        if found:
            self.after(0, self.tools.set, str(found))
            self.note('Platform-Tools gefunden: ' + str(found))
        elif shutil.which('adb') and shutil.which('fastboot'):
            self.note('adb und fastboot über PATH gefunden.')
        else:
            self.note('Platform-Tools nicht gefunden: Download-Link in Vorbereitung nutzen.')
        folders = [Path.cwd(), Path('C:/platform-tools'), Path.home() / 'Downloads']
        for folder in folders:
            if not folder.is_dir():
                continue
            for path in folder.glob('*.img'):
                name = path.name.lower()
                if name == 'vbmeta.img' and not self.vbmeta.get():
                    self.after(0, self.vbmeta.set, str(path))
                    self.note('vbmeta-Datei gefunden (Herkunft MANUELL prüfen): ' + str(path))
                elif 'lineageos' in name and 'gsi' in name and not self.image.get():
                    self.after(0, self.image.set, str(path))
                    self.note('GSI-Datei gefunden (Release/Hash MANUELL prüfen): ' + str(path))
        for tool in ('adb', 'fastboot'):
            try:
                binary = str((found / (tool + '.exe' if os.name == 'nt' else tool))) if found else (shutil.which(tool) or '')
                if not binary:
                    continue
                cmd = [binary, 'devices']
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=12, errors='replace')
                lines = (result.stdout + '\n' + result.stderr).strip()
                self.note(tool + ' devices: ' + (lines or '(kein Gerät)'), technical=True)
                if tool == 'adb' and '\tunauthorized' in lines:
                    self.note('USB-Debugging am Tablet autorisieren.')
                if tool == 'fastboot' and not re.search(r'\S+\s+fastboot', lines):
                    self.note('Kein Fastboot-Gerät. Wenn Tablet im Bootloader ist: Treiberdiagnose nutzen.')
            except (OSError, subprocess.TimeoutExpired) as e:
                self.note(f'{tool}: Diagnose nicht möglich: {e}')
        self.note('Erkennung abgeschlossen. Kein Treiber installiert und keine Partition verändert.')

    def driver_diagnostics(self):
        if os.name != 'nt':
            self.note('Treiberdiagnose ist nur unter Windows verfügbar.')
            return
        self.note('=== Windows USB-/Treiberdiagnose (nur lesend) ===')
        ps = r"Get-PnpDevice -PresentOnly | Where-Object { $_.InstanceId -match 'VID_0E8D|VID_18D1|ADB|FASTBOOT' -or $_.FriendlyName -match 'Android|Bootloader|MediaTek|ADB' } | Select-Object Status,Class,FriendlyName,InstanceId | Format-Table -AutoSize | Out-String -Width 180"
        try:
            result = subprocess.run(['powershell.exe', '-NoProfile', '-Command', ps], capture_output=True, text=True, errors='replace', timeout=20)
            self.note(result.stdout.strip(), technical=True) if result.stdout.strip() else self.note('Keine passenden Geräte gefunden. Tablet anschließen und erneut prüfen.')
            if result.returncode:
                self.note('PowerShell-Diagnose nicht verfügbar: ' + result.stderr.strip())
        except (OSError, subprocess.TimeoutExpired) as e:
            self.note('Windows-Diagnose fehlgeschlagen: ' + str(e))
        self.note('Bei gelbem Warnsymbol im Geräte-Manager: Google USB Driver herunterladen, Treiber manuell für das richtige Gerät auswählen. Keine automatische Treiberänderung.')

    def validate_files(self):
        img = Path(self.image.get())
        vb = Path(self.vbmeta.get())
        if not img.is_file() or not vb.is_file():
            raise RuntimeError('Bitte System-Image und originale vbmeta.img auswählen.')
        if img.stat().st_size < 500_000_000:
            raise RuntimeError('System-Image ungewöhnlich klein.')
        with img.open('rb') as h:
            h.seek(1080)
            ext4 = h.read(2)
        if ext4 != bytes.fromhex('53ef'):
            raise RuntimeError('Kein direktes EXT4-Image erkannt. Sparse-Images werden nicht unterstützt.')
        if vb.read_bytes()[:4] != b'AVB0':
            raise RuntimeError('vbmeta hat keinen AVB0-Header.')
        self.note(f'EXT4 erkannt. Image: {img.stat().st_size} Bytes; vbmeta: {vb.stat().st_size} Bytes.')
        self.note('SHA-256 Image: ' + self.sha256(img))
        self.note('SHA-256 vbmeta: ' + self.sha256(vb))
        self.note('Hashes mit dem vertrauenswürdigen Release vergleichen, sofern Checksummen veröffentlicht wurden.')

    @staticmethod
    def sha256(path):
        h = hashlib.sha256()
        with path.open('rb') as f:
            for block in iter(lambda: f.read(1024 * 1024), b''):
                h.update(block)
        return h.hexdigest()

    def adb_check(self):
        devices = self.command('adb', 'devices')
        if '\tdevice' not in devices:
            raise RuntimeError('Kein autorisiertes ADB-Gerät gefunden.')
        model = self.command('adb', 'shell', 'getprop', 'ro.product.device').strip()
        if model.upper() != 'TB311FU':
            raise RuntimeError(f'Falsches Gerät: {model!r}. Nur TB311FU erlaubt.')
        arch = self.command('adb', 'shell', 'getprop', 'ro.product.cpu.abi').strip()
        treble = self.command('adb', 'shell', 'getprop', 'ro.treble.enabled').strip()
        ab = self.command('adb', 'shell', 'getprop', 'ro.build.ab_update').strip()
        if (arch, treble, ab) != ('arm64-v8a', 'true', 'true'):
            raise RuntimeError('Architektur/Treble/A-B-Prüfung fehlgeschlagen.')
        self.model_ok = True
        self.note('TB311FU / ARM64 / Treble / A-B bestätigt.')

    def fastboot_check(self):
        devices = self.command('fastboot', 'devices')
        if not re.search(r'\S+\s+fastboot', devices):
            raise RuntimeError('Kein Fastboot-Gerät gefunden.')
        unlocked = self.command('fastboot', 'getvar', 'unlocked')
        self.unlocked = bool(re.search(r'\bunlocked:\s*yes\b', unlocked))
        slot = self.command('fastboot', 'getvar', 'current-slot')
        m = re.search(r'current-slot:\s*([ab])\b', slot)
        self.slot = m.group(1) if m else None
        userspace = self.command('fastboot', 'getvar', 'is-userspace')
        self.fastbootd = bool(re.search(r'is-userspace:\s*yes\b', userspace))
        self.note(f'Bootloader entsperrt: {self.unlocked}; Slot: {self.slot}; Fastbootd: {self.fastbootd}')

    def enter_fastbootd(self):
        self.fastboot_check()
        if not self.unlocked:
            raise RuntimeError('Bootloader ist gesperrt.')
        self.command('fastboot', 'reboot', 'fastboot')
        self.note('Fastbootd gestartet. Bitte danach erneut Fastboot-Status prüfen.')
        self.fastbootd = False

    def make_token(self):
        self.fastboot_check()
        if self.unlocked:
            self.note('Bootloader bereits entsperrt. Kein Token nötig.')
            return
        if self.fastbootd:
            raise RuntimeError('Token nur im Bootloader-Fastboot erstellen, nicht in Fastbootd.')
        # These vendor-specific getvars are community documented and may be unsupported.
        a = self.command('fastboot', 'getvar', 'Bootloader_SN_Part1')
        b = self.command('fastboot', 'getvar', 'Bootloader_SN_Part2')
        def part(s, key):
            m = re.search(rf'(?i){key}:\s*([0-9a-f]{{32}})', s)
            if not m:
                raise RuntimeError(f'{key} nicht lesbar. Nicht mit geratenen Werten fortfahren.')
            return m.group(1)
        sn1, sn2 = part(a, 'Bootloader_SN_Part1'), part(b, 'Bootloader_SN_Part2')
        data = MAGIC + (sn1 + sn2).encode('ascii') + bytes(256)
        assert len(data) == 356
        output = Path(self.tools.get()) / 'sn.img'
        output.write_bytes(data)
        self.note(f'Token lokal erzeugt: {output} (356 Bytes). Nicht öffentlich teilen.')

    def flash_token(self):
        self.fastboot_check()
        if self.unlocked:
            raise RuntimeError('Bereits entsperrt.')
        if self.fastbootd:
            raise RuntimeError('Bitte Bootloader-Fastboot verwenden.')
        token = Path(self.tools.get()) / 'sn.img'
        if not token.is_file() or token.stat().st_size != 356:
            raise RuntimeError('Lokales 356-Byte-Token fehlt.')
        if not self.confirm('RISIKO: Token übertragen', 'Community-Methode ohne Garantie. Token jetzt an die virtuelle unlock-Partition übertragen?'):
            return
        self.command('fastboot', 'flash', 'unlock', str(token))

    def oem_unlock(self):
        self.fastboot_check()
        if self.unlocked:
            self.note('Bootloader bereits entsperrt.')
            return
        if self.fastbootd:
            raise RuntimeError('Bitte Bootloader-Fastboot verwenden.')
        if not self.confirm('DATENVERLUST', 'Bootloader-Entsperrung kann ALLE Daten löschen und das Gerät beschädigen. Fortfahren?'):
            return
        self.command('fastboot', 'oem', 'unlock')
        self.note('Bestätigung ggf. am Tablet durchführen. Danach fastboot getvar unlocked erneut prüfen.')

    def preflight(self):
        if not self.model_ok:
            raise RuntimeError('Bitte zuerst im Android-Modus das TB311FU per ADB prüfen (Register „2. Prüfen“).')
        self.validate_files()
        self.fastboot_check()
        if not self.unlocked or self.slot != 'a' or not self.fastbootd:
            raise RuntimeError('Erforderlich: entsperrt, aktiver Slot A, Fastbootd.')
        logical = self.command('fastboot', 'getvar', 'is-logical:system_a')
        if not re.search(r'is-logical:system_a:\s*yes\b', logical):
            raise RuntimeError('system_a ist keine bestätigte logische Partition.')
        size = self.command('fastboot', 'getvar', 'partition-size:system_a')
        m = re.search(r'partition-size:system_a:\s*0x([0-9a-f]+)', size, re.I)
        if not m:
            raise RuntimeError('system_a-Größe nicht lesbar.')
        if Path(self.image.get()).stat().st_size > int(m.group(1), 16):
            raise RuntimeError('Image größer als system_a; kein automatisches Partition-Resize.')
        self.note('Preflight bestanden. Keine Schreiboperation ausgeführt.')

    def flash_vbmeta(self):
        self.preflight()
        if not self.confirm('RISIKO: vbmeta_a', 'Die Verified-Boot-Prüfung auf Slot A deaktivieren? Original-vbmeta muss zum TB311FU passen.'):
            return
        self.command('fastboot', '--disable-verity', '--disable-verification', 'flash', 'vbmeta_a', str(Path(self.vbmeta.get()).resolve()))
        self.note('vbmeta_a geschrieben. Jetzt Fastbootd-Status erneut prüfen.')

    def flash_system(self):
        self.preflight()
        if not self.confirm('SYSTEM WIRD ÜBERSCHRIEBEN', 'Das bestehende Android-System auf system_a wird überschrieben. Gerät kann danach nicht mehr starten. Fortfahren?'):
            return
        self.command('fastboot', 'flash', 'system_a', str(Path(self.image.get()).resolve()))
        self.note('system_a geschrieben. Jetzt Werksreset im Abschluss-Tab.')

    def wipe(self):
        self.fastboot_check()
        if not self.unlocked:
            raise RuntimeError('Bootloader nicht entsperrt.')
        if not self.confirm('UNWIDERRUFLICH: DATEN LÖSCHEN', 'ALLE Nutzerdaten löschen? Das kann nicht rückgängig gemacht werden.'):
            return
        self.command('fastboot', '-w')
        self.note('Falls „raw not supported“ erscheint und Recovery einen Reset anbietet: Recovery-Factory-Reset verwenden.')

    def reboot(self):
        if not self.confirm('Neustart', 'Tablet jetzt neu starten?'):
            return
        self.command('fastboot', 'reboot')

if __name__ == '__main__':
    Wizard().mainloop()
