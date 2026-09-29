#!/usr/bin/env python3
"""
betraege.py - rechnet die Beträge einer Rechnung nach und prüft Formate.

Eingabe als JSON (Datei oder stdin):
{
  "positionen": [{"netto": 100.00, "satz": 19}, {"netto": 20.00, "satz": 7}],
  "ausgewiesen": {"netto": 120.00, "ust": {"19": 19.00, "7": 1.40}, "brutto": 140.40},
  "ust_id_leistender": "DE123456789",
  "ust_id_empfaenger": "ATU12345678"
}
Alle Felder außer "positionen" sind optional.

Prüft: Summen je Steuersatz, Steuerbeträge (kaufmännisch gerundet je Satz),
Brutto = Netto + USt, gültige deutsche Steuersätze, Format von USt-IdNrn,
Kleinbetragsgrenze (250 EUR brutto, § 33 UStDV).

Usage: python3 betraege.py rechnung.json   |   cat r.json | python3 betraege.py
"""
import json, re, sys
from decimal import Decimal, ROUND_HALF_UP

SAETZE_DE = {Decimal("19"), Decimal("7"), Decimal("0")}
UST_ID = {
    "DE": r"DE\d{9}", "AT": r"ATU\d{8}", "CH": r"CHE\d{9}(MWST|TVA|IVA)?", "NL": r"NL\d{9}B\d{2}",
    "FR": r"FR[0-9A-Z]{2}\d{9}", "BE": r"BE[01]\d{9}", "IT": r"IT\d{11}", "ES": r"ES[0-9A-Z]\d{7}[0-9A-Z]",
    "PL": r"PL\d{10}", "CZ": r"CZ\d{8,10}", "DK": r"DK\d{8}", "LU": r"LU\d{8}", "IE": r"IE\d{7}[A-W][A-I]?|IE\d[A-Z+*]\d{5}[A-W]",
}
CENT = Decimal("0.01")


def d(x):
    return Decimal(str(x)).quantize(CENT, ROUND_HALF_UP)


def main():
    data = json.load(open(sys.argv[1], encoding="utf-8") if len(sys.argv) > 1 else sys.stdin)
    befunde, info = [], {}
    netto_je_satz = {}
    for i, p in enumerate(data.get("positionen", []), 1):
        satz = Decimal(str(p.get("satz", 19)))
        if satz not in SAETZE_DE:
            befunde.append(f"Position {i}: Steuersatz {satz} % ist kein deutscher Regelsatz (19/7/0) – Auslandsfall oder Fehler?")
        netto_je_satz[satz] = netto_je_satz.get(satz, Decimal(0)) + Decimal(str(p["netto"]))
    ust_je_satz = {s: d(n * s / 100) for s, n in netto_je_satz.items()}
    netto = d(sum(netto_je_satz.values(), Decimal(0)))
    ust = d(sum(ust_je_satz.values(), Decimal(0)))
    brutto = netto + ust
    info["berechnet"] = {"netto": str(netto), "ust_je_satz": {str(k): str(v) for k, v in ust_je_satz.items()},
                         "ust": str(ust), "brutto": str(brutto)}

    aus = data.get("ausgewiesen") or {}
    if "netto" in aus and d(aus["netto"]) != netto:
        befunde.append(f"Netto ausgewiesen {d(aus['netto'])}, berechnet {netto}")
    for s, v in (aus.get("ust") or {}).items():
        soll = ust_je_satz.get(Decimal(str(s)))
        if soll is None:
            befunde.append(f"USt zu {s} % ausgewiesen, aber keine Position mit diesem Satz")
        elif abs(d(v) - soll) > CENT:
            befunde.append(f"USt {s} %: ausgewiesen {d(v)}, berechnet {soll}")
        elif d(v) != soll:
            info.setdefault("hinweise", []).append(f"USt {s} %: 1 Cent Differenz (Rundung je Position statt je Satz) – unkritisch")
    if "brutto" in aus and abs(d(aus["brutto"]) - brutto) > CENT:
        befunde.append(f"Brutto ausgewiesen {d(aus['brutto'])}, berechnet {brutto}")
    if brutto <= 250:
        info.setdefault("hinweise", []).append("Brutto ≤ 250 EUR: Kleinbetragsrechnung nach § 33 UStDV möglich (reduzierte Pflichtangaben)")

    for feld in ("ust_id_leistender", "ust_id_empfaenger"):
        v = (data.get(feld) or "").replace(" ", "").upper()
        if not v:
            continue
        rx = UST_ID.get(v[:2])
        if rx is None:
            info.setdefault("hinweise", []).append(f"{feld}: Länderpräfix {v[:2]} nicht im Formatkatalog – nur per VIES prüfbar")
        elif not re.fullmatch(rx, v):
            befunde.append(f"{feld} {v}: Format passt nicht zu {v[:2]}")
    print(json.dumps({"befunde": befunde or ["keine Rechenfehler gefunden"], **info}, indent=2, ensure_ascii=False))
    sys.exit(1 if befunde else 0)


if __name__ == "__main__":
    main()
