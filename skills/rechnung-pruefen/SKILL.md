---
name: rechnung-pruefen
description: Prüft deutsche Rechnungen (eingehend oder vor dem Versand) auf die Pflichtangaben nach § 14 Abs. 4 UStG, Sonderfälle (Kleinbetragsrechnung, Kleinunternehmer, Reverse Charge, innergemeinschaftliche Leistungen, Gutschrift), rechnet Beträge und Steuersätze nach und ordnet die E-Rechnungspflicht ein. Nutzen, wenn jemand eine Rechnung prüfen, eine Rechnung schreiben oder korrigieren, einen Vorsteuerabzug absichern oder wissen will, ob eine Rechnung als E-Rechnung kommen muss. Typische Auslöser sind „Rechnung prüfen", „ist die Rechnung korrekt", „Pflichtangaben Rechnung", „fehlt was auf der Rechnung", „Vorsteuer", „Kleinbetragsrechnung", „Reverse Charge", „E-Rechnung Pflicht", „check this German invoice". Keine Steuerberatung; bei Zweifeln an Steuerberater verweisen.
---

# Rechnung prüfen (Deutschland)

Ziel: Fehlt eine Pflichtangabe oder stimmt ein Betrag nicht, kann der Empfänger die Vorsteuer nicht abziehen und der Aussteller schuldet unter Umständen ausgewiesene Steuer trotzdem (§ 14c UStG). Diese Prüfung findet solche Fehler, bevor das Finanzamt es tut.

Das ist eine Checkliste, **keine Steuerberatung**. Rechtsstand beim Schreiben: 2026. Bei Grenzfällen (Bauleistungen, Reihengeschäfte, Differenzbesteuerung, Auslandssachverhalte außerhalb der EU) an Steuerberatung verweisen und die Norm nennen.

## 1. Pflichtangaben nach § 14 Abs. 4 UStG

Für jede Rechnung über 250 € brutto:

1. Vollständiger Name und Anschrift von **leistendem Unternehmer und Leistungsempfänger** (Postfach genügt nicht als Anschrift des Leistenden; c/o-Adressen sind zulässig, wenn dort erreichbar).
2. **Steuernummer oder USt-IdNr.** des leistenden Unternehmers.
3. **Ausstellungsdatum**.
4. **Fortlaufende Rechnungsnummer**, einmalig vergeben (Präfixe und mehrere Nummernkreise sind erlaubt).
5. **Menge und handelsübliche Bezeichnung** der Gegenstände bzw. **Art und Umfang** der Leistung. Pauschal „Beratung" ohne Zeitraum oder Umfang ist riskant.
6. **Zeitpunkt der Lieferung/Leistung** (auch als Monat, z. B. „Leistungszeitraum September 2026"); ein Hinweis „Leistungsdatum = Rechnungsdatum" genügt, wenn er stimmt.
7. **Entgelt nach Steuersätzen und Befreiungen aufgeschlüsselt**, sowie im Voraus vereinbarte Minderungen (Skonto, Rabatte), soweit nicht im Entgelt berücksichtigt.
8. **Steuersatz und Steuerbetrag** – oder bei Steuerbefreiung ein **Hinweis auf den Grund** (z. B. „steuerfreie innergemeinschaftliche Lieferung").
9. Bei Leistungen im Zusammenhang mit einem Grundstück an Privatpersonen: Hinweis auf die **zweijährige Aufbewahrungspflicht** des Empfängers.
10. Bei Abrechnung durch den Empfänger: das Wort **„Gutschrift"**.

## 2. Sonderfälle

- **Kleinbetragsrechnung (≤ 250 € brutto, § 33 UStDV)**: Name und Anschrift des Leistenden, Ausstellungsdatum, Menge/Art der Leistung, Bruttobetrag und Steuersatz (bzw. Hinweis auf Befreiung) reichen.
- **Kleinunternehmer (§ 19 UStG)**: keine Umsatzsteuer ausweisen, Hinweis auf die Steuerbefreiung nach § 19 UStG. Wird trotzdem Steuer ausgewiesen, wird sie nach § 14c UStG geschuldet.
- **Reverse Charge (§ 13b UStG)**, z. B. Leistungen an Unternehmer im EU-Ausland oder bestimmte Inlandsfälle: keine USt ausweisen, Hinweis „Steuerschuldnerschaft des Leistungsempfängers", bei EU-Sachverhalten die **USt-IdNr. beider Parteien**.
- **Innergemeinschaftliche Lieferung**: steuerfrei mit Hinweis, USt-IdNr. von Leistendem und Empfänger; USt-IdNr. des Empfängers über [VIES](https://ec.europa.eu/taxation_customs/vies/) prüfen (öffentlich, kein Key).
- **Anzahlungs- und Schlussrechnungen**: in der Schlussrechnung die bereits vereinnahmten Anzahlungen und die darauf entfallende Steuer abziehen, sonst doppelte Steuerschuld.
- **Steuersätze**: 19 % Regelsatz, 7 % ermäßigt (Anlage 2 UStG, u. a. bestimmte Lebensmittel, Bücher, Eintritt Kultur); falscher Satz ist ein inhaltlicher Fehler, nicht nur ein Rechenfehler.

## 3. E-Rechnung (B2B im Inland)

- Seit **1.1.2025** müssen alle inländischen Unternehmen **E-Rechnungen empfangen** können (strukturiertes Format nach EN 16931, z. B. XRechnung oder ZUGFeRD ab Profil EN 16931; ein PDF per Mail ist keine E-Rechnung).
- Übergang beim **Versand**: Papier/PDF bleibt bis **31.12.2026** zulässig; bis **31.12.2027** für Unternehmen mit höchstens 800.000 € Vorjahresumsatz. Ab **2028** ist die E-Rechnung bei inländischen B2B-Umsätzen die Regel.
- Ausnahmen u. a.: Kleinbetragsrechnungen, Fahrausweise, Rechnungen von Kleinunternehmern, Rechnungen an Privatpersonen.
- Bei einer E-Rechnung ist die **XML-Datei** das Original, nicht die Sichtdarstellung; bei ZUGFeRD-Hybrid-PDFs müssen Bild und XML übereinstimmen.

## 4. Beträge nachrechnen

```bash
python3 scripts/betraege.py rechnung.json
```
Eingabe: Positionen mit Netto und Satz, optional die ausgewiesenen Summen und USt-IdNrn (Format siehe Skriptkopf). Das Skript rechnet Netto, Steuer je Satz, Brutto, erkennt 1-Cent-Rundungsdifferenzen, prüft Formate von USt-IdNrn und meldet, ob eine Kleinbetragsrechnung vorliegt. Rechnungen aus PDF oder Foto erst in dieses JSON übertragen.

## 5. Ergebnis

Tabelle mit allen Pflichtangaben: vorhanden / fehlt / fehlerhaft, jeweils mit Fundstelle auf der Rechnung. Danach:
- **Kritisch** (gefährdet den Vorsteuerabzug oder erzeugt Steuerschuld): fehlende Pflichtangaben, falscher Steuersatz, Steuer ausgewiesen trotz § 19 oder § 13b.
- **Formal** (sollte korrigiert werden): unklare Leistungsbeschreibung, fehlender Leistungszeitraum.
- **Hinweise**: Rundung, E-Rechnungs-Übergang.

Korrektur: Eine fehlerhafte Rechnung wird durch eine **Rechnungsberichtigung** mit Bezug auf die ursprüngliche Rechnungsnummer korrigiert oder storniert und neu ausgestellt. Nicht einfach eine neue Nummer ohne Bezug vergeben.

Personenbezogene und Bankdaten aus Rechnungen nur für die Prüfung verwenden, nicht speichern.
