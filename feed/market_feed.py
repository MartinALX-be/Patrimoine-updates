"""Données de marché publiées par l'éditeur de Patrimoine (fichier market_data.json).

Les applications installées ne lisent QUE ce fichier (sur GitHub, déjà utilisé pour les
mises à jour) : elles ne contactent ni CNN, ni Eurostat, ni la Réserve fédérale.

Sources (accès public, sans clé) :
- Réserve fédérale de St. Louis (FRED) : valeur de marché des actions des sociétés US
  (NCBEILQ027S), PIB (GDP), S&P 500 (SP500), VIX (VIXCLS), écart de crédit haut rendement
  (BAMLH0A0HYM2), taux à 10 ans (DGS10).
- Eurostat : inflation belge, IPCH variation annuelle (prc_hicp_manr) — licence CC BY 4.0.
- alternative.me : Fear & Greed crypto (attribution demandée).

Le « Baromètre Patrimoine » remplace le Fear & Greed de CNN (donnée propriétaire) : indice
0-100 calculé par nous, sur le modèle public de la méthode CNN, à partir de 5 composantes.

Usage :  python market_feed.py [--out market_data.json] [--previous ancien.json]
Utilisé tel quel par la console (Patrimoine-console) et par la tâche GitHub Actions.
"""
import argparse
import json
import math
import os
import sys
import time
from datetime import date, datetime, timedelta, timezone

import requests

SCHEMA = 1
UA = {"User-Agent": "Patrimoine-market-feed/1.0"}
FRED = "https://fred.stlouisfed.org/graph/fredgraph.csv"
FRED_API = "https://api.stlouisfed.org/fred/series/observations"


# ------------------------------------------------------------------ téléchargements
def fred(series, start=None):
    """[(date ISO, valeur)] d'une série FRED (valeurs manquantes « . » ignorées).

    Avec la variable d'environnement FRED_API_KEY (clé gratuite, secret GitHub) : API
    officielle api.stlouisfed.org — c'est la voie prévue pour les programmes et serveurs
    (le téléchargement CSV public ne répond pas depuis les serveurs de GitHub).
    Sans clé : téléchargement CSV public (fonctionne depuis un PC personnel)."""
    key = os.environ.get("FRED_API_KEY", "").strip()
    if not key and os.environ.get("GITHUB_ACTIONS"):
        # Le CSV public de FRED ne répond pas aux serveurs de GitHub : inutile d'attendre.
        raise RuntimeError("FRED inaccessible depuis GitHub sans le secret FRED_API_KEY")
    if key:
        url, params = FRED_API, {"series_id": series, "api_key": key, "file_type": "json"}
        if start:
            params["observation_start"] = start
    else:
        url, params = FRED, {"id": series}
        if start:
            params["cosd"] = start
    last = None
    for attempt in range(3):
        try:
            r = requests.get(url, params=params, headers=UA, timeout=(15, 60))
            r.raise_for_status()
            break
        except requests.RequestException as e:
            last = e
            time.sleep(5 * (attempt + 1))
    else:
        raise last
    out = []
    if key:
        for o in r.json().get("observations") or []:
            try:
                out.append((o["date"], float(o["value"])))
            except (KeyError, ValueError):
                continue
    else:
        for line in r.text.splitlines()[1:]:
            d, _, v = line.partition(",")
            try:
                out.append((d, float(v)))
            except ValueError:
                continue
    if not out:
        raise ValueError(f"Série FRED vide : {series}")
    return out


def _value_on(series, iso):
    """Dernière valeur ≤ date."""
    cand = [v for d, v in series if d <= iso]
    return cand[-1] if cand else None


def _quarter_end(iso_start):
    """FRED date un trimestre par son 1er jour (2026-04-01 = T2) → dernier jour du trimestre."""
    d = date.fromisoformat(iso_start)
    m = d.month + 2
    nxt = date(d.year + (m // 12), m % 12 + 1, 1)
    return (nxt - timedelta(days=1)).isoformat()


# ------------------------------------------------------------------ indicateur Buffett
def buffett():
    eq = fred("NCBEILQ027S")            # millions de $
    gdp = fred("GDP")                    # milliards de $, rythme annualisé
    gdp_by = dict(gdp)
    # dernier trimestre disponible dans LES DEUX séries
    common = [d for d, _ in eq if d in gdp_by]
    q = common[-1]
    eq_bn = dict(eq)[q] / 1000.0
    ratio = eq_bn / gdp_by[q] * 100.0
    q_end = _quarter_end(q)
    spx = fred("SP500", (date.fromisoformat(q_end) - timedelta(days=15)).isoformat())
    spx_ref = _value_on(spx, q_end)
    gdps = [v for d, v in gdp]
    growth = (gdps[-1] / gdps[-5] - 1.0) * 100.0 if len(gdps) >= 5 else 4.0
    d = date.fromisoformat(q)
    return {
        "ratio": round(ratio, 1), "as_of": q_end, "quarter": f"{d.year}-T{(d.month - 1) // 3 + 1}",
        "equities_bn": round(eq_bn, 0), "gdp_bn": round(gdp_by[q], 0),
        "spx_ref": spx_ref, "gdp_growth_annual": round(growth, 2),
        "source": "Réserve fédérale (FRED : NCBEILQ027S ÷ GDP), extrapolé avec le S&P 500",
    }


# ------------------------------------------------------------------ inflation belge
def inflation_be():
    url = ("https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/"
           "prc_hicp_manr?format=JSON&lang=EN&geo=BE&coicop=CP00")
    r = requests.get(url, headers=UA, timeout=40)
    r.raise_for_status()
    d = r.json()
    cat = d["dimension"]["time"]["category"]["index"]
    idx = {int(i): p for p, i in cat.items()}
    pts = sorted(((int(k), float(v)) for k, v in (d.get("value") or {}).items()), key=lambda x: x[0])
    if not pts:
        raise ValueError("Eurostat : aucune donnée")
    hist = [{"period": idx.get(i, str(i)), "value": round(v, 2)} for i, v in pts][-13:]
    return {"value": hist[-1]["value"], "period": hist[-1]["period"],
            "prev": hist[-2]["value"] if len(hist) > 1 else None, "history": hist,
            "source": "Eurostat — IPCH (HICP) Belgique, variation sur un an (CC BY 4.0)"}


# ------------------------------------------------------------------ sentiment crypto
def crypto_sentiment():
    r = requests.get("https://api.alternative.me/fng/", params={"limit": 1}, headers=UA, timeout=30)
    r.raise_for_status()
    x = r.json()["data"][0]
    v = int(x["value"])
    return {"value": v, "label": sentiment_label(v),
            "as_of": datetime.fromtimestamp(int(x["timestamp"]), timezone.utc).date().isoformat(),
            "source": "alternative.me — Crypto Fear & Greed Index"}


# ------------------------------------------------------------------ Baromètre Patrimoine
def sentiment_label(v):
    return ("Peur extrême" if v < 25 else "Peur" if v < 45 else "Neutre" if v <= 55
            else "Avidité" if v <= 75 else "Avidité extrême")


def _pct_rank(values, x):
    """Rang centile (0-100) de x parmi values."""
    if not values:
        return 50.0
    below = sum(1 for v in values if v < x)
    equal = sum(1 for v in values if v == x)
    return (below + 0.5 * equal) / len(values) * 100.0


def _align(*series):
    """Dates communes à toutes les séries, triées → listes de valeurs alignées."""
    maps = [dict(s) for s in series]
    dates = sorted(set.intersection(*(set(m) for m in maps)))
    return dates, [[m[d] for d in dates] for m in maps]


def barometer():
    start = (date.today() - timedelta(days=760)).isoformat()
    spx, vix, hy, t10 = fred("SP500", start), fred("VIXCLS", start), fred("BAMLH0A0HYM2", start), fred("DGS10", start)
    dates, (S, V, H, T) = _align(spx, vix, hy, t10)
    n = len(dates)
    if n < 300:
        raise ValueError("Historique FRED insuffisant pour le baromètre")

    def comp(i):
        """Valeurs brutes des 5 composantes au jour i (orientées : plus haut = plus d'avidité)."""
        ma125 = sum(S[i - 124:i + 1]) / 125
        hi252 = max(S[i - 251:i + 1])
        ma50v = sum(V[i - 49:i + 1]) / 50
        spx20 = S[i] / S[i - 20] - 1.0
        bond20 = -7.5 * (T[i] - T[i - 20]) / 100.0           # rendement approx. d'une oblig. 10 ans
        return {
            "momentum": S[i] / ma125 - 1.0,                     # élan : au-dessus de la moyenne 125 j
            "strength": S[i] / hi252 - 1.0,                     # proximité du plus haut annuel
            "volatility": -(V[i] / ma50v - 1.0),                 # VIX sous sa moyenne 50 j = calme
            "credit": -H[i],                                     # écart de crédit faible = appétit
            "safe_haven": spx20 - bond20,                        # actions > obligations sur 20 j
        }

    first = 251
    hist = [comp(i) for i in range(first, n)]
    window = hist[-252:]
    today = hist[-1]
    labels = {"momentum": "Élan du S&P 500 (vs moyenne 125 j)", "strength": "Proximité du plus haut annuel",
              "volatility": "Volatilité VIX (vs moyenne 50 j)", "credit": "Écart de crédit haut rendement",
              "safe_haven": "Actions vs obligations (20 j)"}
    comps = []
    for k, lab in labels.items():
        score = _pct_rank([h[k] for h in window], today[k])
        comps.append({"key": k, "label": lab, "raw": round(today[k], 5), "score": round(score)})
    value = round(sum(c["score"] for c in comps) / len(comps))
    return {"value": value, "label": sentiment_label(value), "as_of": dates[-1], "components": comps,
            "source": "Baromètre Patrimoine — calculé par l'éditeur (FRED : S&P 500, VIX, écart de crédit, taux 10 ans)"}


# ------------------------------------------------------------------ assemblage
BLOCKS = {"buffett": buffett, "sentiment": barometer, "crypto_sentiment": crypto_sentiment,
          "inflation_be": inflation_be}


def build(previous=None, only=None):
    """Recalcule les blocs (tous ou `only`). Un bloc en échec garde sa valeur précédente
    (sans marque : c'est l'app qui juge l'ancienneté d'après `as_of` / `period` et le
    rythme normal de chaque donnée) : une source indisponible ne vide jamais le fichier."""
    prev = previous or {}
    out = {"schema": SCHEMA, "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
           "errors": {}}
    for key, fn in BLOCKS.items():
        if only and key not in only:
            if key in prev:
                out[key] = prev[key]
            continue
        try:
            out[key] = fn()
        except Exception as e:                     # noqa: BLE001 — on garde l'ancienne valeur
            out["errors"][key] = f"{type(e).__name__}: {e}"[:300]
            if key in prev:
                out[key] = {k: v for k, v in prev[key].items() if k != "stale"}
    return out


def anomalies(old, new):
    """Écarts suspects entre deux publications (à vérifier avant de publier)."""
    warn = []
    def num(b, k):
        try:
            return float((b or {}).get(k))
        except (TypeError, ValueError):
            return None
    checks = [("buffett", "ratio", 25, "pts"), ("sentiment", "value", 40, "pts"),
              ("crypto_sentiment", "value", 40, "pts"), ("inflation_be", "value", 1.5, "pt")]
    for blk, k, lim, unit in checks:
        a, b = num(old.get(blk), k), num(new.get(blk), k)
        if a is not None and b is not None and abs(b - a) > lim:
            warn.append(f"{blk} : {a} → {b} (écart > {lim} {unit})")
        if b is None and a is not None:
            warn.append(f"{blk} : valeur absente dans la nouvelle version")
    for blk, err in (new.get("errors") or {}).items():
        warn.append(f"{blk} : source en échec ({err}) — ancienne valeur conservée")
    return warn


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default="market_data.json")
    ap.add_argument("--previous", help="fichier précédent (par défaut : --out s'il existe)")
    ap.add_argument("--strict", action="store_true",
                    help="publication automatique : en cas d'écart suspect, ne rien écrire et échouer (code 3)")
    a = ap.parse_args()
    prev = {}
    try:
        with open(a.previous or a.out, encoding="utf-8") as f:
            prev = json.load(f)
    except (OSError, ValueError):
        pass
    data = build(prev)
    if not any(k in data for k in BLOCKS):
        sys.exit("Aucune donnée récupérée : fichier non modifié.")
    warns = [w for w in anomalies(prev, data) if "source en échec" not in w]
    if a.strict and warns:
        for w in warns:
            print("⚠", w)
        print("Écart suspect : publication automatique annulée, à vérifier dans la console.")
        sys.exit(3)
    with open(a.out, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    for w in anomalies(prev, data):
        print("⚠", w)
    print(json.dumps({k: (data.get(k) or {}).get("value", (data.get(k) or {}).get("ratio")) for k in BLOCKS},
                     ensure_ascii=False))


if __name__ == "__main__":
    main()
