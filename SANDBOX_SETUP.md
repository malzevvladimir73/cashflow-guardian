# PayPal-Sandbox einrichten

1. Öffne https://developer.paypal.com/ und melde dich selbst an. Für Tests außerhalb
   der USA nennt PayPal ein Business-Konto als Voraussetzung.
2. Öffne Apps & Credentials und wähle Sandbox. Erstelle mit Create App eine App
   namens Cashflow Guardian und ordne sie deinem Sandbox-Business-Konto zu.
3. Unter Testing Tools > Sandbox Accounts findest du die Testkonten. Verwende nur
   erfundene Kunden und Rechnungen. Lege im Business-Testkonto Testrechnungen an,
   darunter offene, bezahlte und teilweise bezahlte Rechnungen.
4. Starte einmal SETUP_WINDOWS.bat, danach START_SANDBOX.bat.
5. Gib Client-ID und Secret ausschließlich im lokalen Eingabefenster ein. Beide
   Eingaben sind unsichtbar. Nicht hier im Chat, auf GitHub oder in HTML eintragen.
   Die Werte werden nicht in einer Datei gespeichert und gelten nur im Prozess.
6. Öffne die angezeigte lokale Adresse. Vergleiche Anzahl, Währung und Restbeträge
   mit dem Sandbox-Konto. Eine leere Sandbox ist kein erfolgreicher Rechnungstest.
7. Beende den Server nach dem Test. Bei Fehlern nur die allgemeine Fehlermeldung
   weitergeben, niemals Schlüssel oder private Rechnungsdaten.

Der Start prüft die Verbindung. Die Anwendung liest Rechnungen, erstellt keine
Zahlungen und verschickt keine Nachrichten. Die Einrichtung muss vom Kontoinhaber
abgeschlossen werden; derzeit ist noch keine echte Verbindung nachgewiesen.

Offizielle Anleitung: https://developer.paypal.com/api/rest/
