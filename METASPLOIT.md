Bezogen auf die Issues iss/mp-ids#132 und iss/mp-ids#121

#### Voraussetzung

* Metasploit installieren: Die kostenlose Basisversion reicht dazu aus.
  Bei Arch Linux gibt's die im AuR (`pacman -Syu metasploit`).
* Im Terminal `msfconsole` starten.

Hinweis: Ein Exploit wurde ausgeführt und somit Angriffsdaten von Dionaea gesammelt,
wenn in der Konsole `[*] Exploit completed` zu lesen ist.

### SMB

Um die in iss/mp-ids#132 beschriebene Sicherheitslücke zu testen, muss zunächst
sichergestellt werden, dass der Dionaea-Container den Port `445` nach außen hin
exposed, damit man da angreifen kann.

Mit `use windows/smb/ms10_061_spoolss` kann dann der Exploit geladen werden.
Danach die Optionen[^1] in der Konsole setzen:

````
set PNAME XPSPrinter
set RHOST 127.0.0.1
set RPORT 445
```

Hilfe zu den Optionen gibt der Befehlt `show options`.

Dann sollte alles bereit sein und man kann mit `exploit` den Angriff starten,
der nach ein paar Sekunden auch im CIM angezeigt werden sollte.

Hinweis: Der Exploit selbst schlägt fehl (soll er auch!), liefert aber bereits
Daten und Dateien. Im CIM sollten folgende Events ankommen:

````
dionaea_access (Als Notiz, dass ein Zugriff erfolgt ist)
3x dionaea_download_offer (mit Dateipfad)
2x dionaea_download_complete (mit md5-Hashwert, Source-URL und Dateipfad)
```

### MySQL

Ein weiterer Angriff, um MySQL zu testen, geht so: Man muss hier den Port `3306`
exposen, in der `msfconsole` folgende Befehle eingeben:
`use windows/mysql/mysql_payload`, `set RHOST 127.0.0.1`[^1]
und dann wieder `exploit`.

Da kann man auch überprüfen, ob unsere Fehlermeldung
mittlerweile angepasst wurde (im Moment kommt immer noch die Dionaea-typische
`ServerError LearnSQL!`-Meldung). Der Angriff wird auch hier von Dionaea an das
CIM gemeldet. Allerdings wird er durch genannte Fehlermeldung vorzeitig
abgebrochen, ohne, dass ein Payload eingespeist werden kann.

Im CIM sollte ein `dionaea_mysql_login`-Event ankommen, das den Username `root`
enthält und ein leeres Passwort (das liegt leider am Dionaea-Modul, dass es
nicht verlangt wird). Dann zwei `dionaea_mysql_command` Events:

````
SELECT @@version_compile_os
select * from mysql.func where name = 'sys_exec'
```

[^1]: Die IP ggf. anpassen (z.B. `0.0.0.0`). Im Zweifelsfall gibt `docker ps` Auskunft über die
      korrekte IP / Portwahl.