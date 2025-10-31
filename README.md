# Die Energie-Resonanz-Theorie (ERT)

Dieses Repository enthält das vollständige wissenschaftliche Manuskript  
**„Die Energie-Resonanz-Theorie – Eine neue Perspektive auf Raum, Resonanz und Struktur“**  
von **Steven Trümpert**.

---

##  Projektüberblick

Die Energie-Resonanz-Theorie (ERT) erweitert den klassischen mathematischen Rahmen der Physik  
um eine neue geometrische Beschreibung der Realität auf Basis der *Spiralis-Funktion* und des  
dimensionslosen Operators **Alpha\*** (α\*).  
Sie vereint experimentell bestätigte Theorien wie die Allgemeine Relativitätstheorie (ART)  
und die Quantenmechanik (QM) unter einem gemeinsamen, resonanzbasierten Ansatz.

---

##  Repository-Struktur

Energie-Resonanz-Theorie/
│
├── main.tex # Hauptdokument
├── preamble/
│ ├── packages.tex # Paketverwaltung (LaTeX)
│ ├── macros.tex # Eigene Befehle & Operatoren
│ ├── glossaries.tex # Glossar-Einträge (Spiralis, Alpha*)
│ └── theoremstyles.tex # Satz- & Definitionenumgebungen
│
├── content/ # Kapitelstruktur
│ ├── 01_einleitung.tex
│ ├── ...
│ └── anhang_daten.tex
│
├── bib/
│ ├── references.bib # Literaturdatenbank
│ └── local.bib # Lokale Quellen
│
├── codes/
│ ├── 03_numerischer_scan_fit/
│ │ ├── ert_operator_scan.py
│ │ ├── ert_dataset.py
│ │ ├── operator_fit.py
│ │ └── residuen.txt
│ └── 05_visualisierung/
│   └── Python/
│     └── generator_final.py
│   └── Paraview/
│     └── ERT_EM_Colormap.json
│
└── Grafiken/
└── Front.jpg
...

## Kompilieren des Whitepapers

**Abhängigkeiten:**
- TeX-Distribution mit `lualatex` oder `pdflatex`
- `biber` für Bibliographie
- `makeglossaries` für Glossar
- Python ≥ 3.10 (für experimentelle Generator-Skripte)

**Kompilierungsschritte:**
```bash
latexmk -pdf main.tex
biber main
makeglossaries main
latexmk -pdf main.tex

##  Lizenz

Dieses Werk ist unter einer Creative Commons BY-NC-SA 4.0 Lizenz
veröffentlicht.
Die Nutzung für wissenschaftliche und nicht-kommerzielle Zwecke ist ausdrücklich erwünscht.

##  Kontakt

Autor: Steven Trümpert
E-Mail: StevenTruempert@hotmail.de
Ort: Eisenach, Deutschland

##  reproduzierbare Experimente

Die Python-Skripte in /codes erzeugen numerische und visuelle Daten,
die im Whitepaper als empirischer Vergleich zur Theorie dienen.
Jede Datei ist vollständig dokumentiert und kann unabhängig ausgeführt werden.

##  Zitieren

Bitte zitiere diese Arbeit wie folgt:

Trümpert, S. (2025). Die Energie-Resonanz-Theorie (ERT):
Eine neue Perspektive auf Raum, Resonanz und Struktur.
Zenodo. DOI: [wird ergänzt]