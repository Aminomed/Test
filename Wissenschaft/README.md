# ⚛ Zoom ins Unbestimmte – Modelle & Erkenntnis in der Wissenschaft

Ein interaktives, visuelles Scrollytelling-Erlebnis über Wissenschaftstheorie, Modelle und Erkenntnisgrenzen, erzählt entlang der historischen Evolution des Atommodells.

---

## 📖 Über das Projekt

Warum ist Wissenschaft keine Ansammlung unveränderlicher Wahrheiten, sondern ein Prozess des Modellbaus?

Dieses Projekt visualisiert den Übergang vom anschaulichen Makrokosmos in die quantenmechanische Unschärfe und verbindet jede Stufe mit zentralen wissenschaftstheoretischen Konzepten:

1. **Prolog (Makrowelt / Wassertropfen):** *„Die Landkarte ist nicht das Territorium“* – Warum unser Verstand Modelle konstruiert.
2. **Demokrit & Dalton (Feste Kugeln, 1803):** Axiome, Abstraktion und der Geltungsbereich (Ideales Gasgesetz).
3. **Thomson & Rutherford (1911):** Die Anomalie im Experiment – Wie 1 von 8.000 reflektierten Alpha-Teilchen das alte Paradigma zerbrach.
4. **Niels Bohr (1913):** Das Quanten-Postulat – Warum quantisierte Bahnen und Spektrallinien die klassische Physik herausforderten.
5. **Schrödinger & Heisenberg (1925+):** Das Ende der Anschauung – Wahrscheinlichkeitsdichten ($|\psi|^2$) und 3D-Orbitale als mathematische Konstrukte.
6. **Epilog & Modell-Kompass:** Karl Popper (Falsifikation), Thomas Kuhn (Paradigmenwechsel) und George Box: *„Alle Modelle sind falsch, aber manche sind nützlich.“*

---

## 🚀 Schnellstart

### Option 1: Mit einem Klick starten
Doppelklicke einfach auf die Datei `start.bat` im Projektordner.

### Option 2: Über das Terminal
```bash
python -m http.server 8000
```
Öffne anschließend deinen Browser unter: **[http://localhost:8000](http://localhost:8000)**

---

## 🛠 Features & Interaktivität
* **Echtzeit 3D-WebGL Engine (Three.js):** Flüssiges Morphing und Partikel-Simulationen beim Scrollen.
* **Interaktive Labor-Stationen:**
  * 🧪 *Dalton-Gassimulator:* Gasdruck als Funktion der Teilchenbewegung & Temperatur.
  * 🎯 *Goldfolienversuch:* Alpha-Teilchen-Beschuss mit Live-Zähler.
  * 🌈 *Spektrallinien-Klicker:* Quantensprünge der Balmer-Serie im Wasserstoffatom.
  * 🌌 *3D-Orbital-Inspektor:* $1s, 2p_z, 2p_x, 3d_{z^2}, 3d_{xy}$ Aufenthaltswahrscheinlichkeiten im 3D-Raum drehen und erforschen.
  * 🧭 *Epistemologischer Modell-Kompass:* Ermittelt das optimale wissenschaftliche Modell für konkrete Anwendungsfälle.
* **Prozedurales Audio-Design (Web Audio API):** Abschaltbare Ambient-Soundkulisse und Klangfeedback bei Quantenübergängen.
