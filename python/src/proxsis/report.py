"""Markdown rendering of backtest results (docs/backtest/RAPPORT_BACKTEST.md)."""

from __future__ import annotations

from typing import Any

MODEL_LABELS = {
    "hasard": "Hasard",
    "plus_grosses": "Plus grosses entreprises",
    "activite_recente": "Activité récente (offres)",
    "M0_regles": "M0 — règles",
    "M1_boosting": "M1 — boosting d'arbres",
    "M2_survie": "M2 — survie (Cox)",
}
ORDER = ["hasard", "plus_grosses", "activite_recente", "M0_regles", "M1_boosting", "M2_survie"]


def _pct(x: float | None) -> str:
    return "—" if x is None else f"{100 * x:.1f} %"


def _ci(e: dict[str, Any]) -> str:
    lo, hi = e["ci95"]
    return f"{100 * e['mean']:.1f} % [{100 * lo:.1f} ; {100 * hi:.1f}]"


def _pts(e: dict[str, Any]) -> str:
    lo, hi = e["ci95"]
    return f"{100 * e['mean']:+.1f} pts [{100 * lo:+.1f} ; {100 * hi:+.1f}]"


def main_table(summary: dict[str, Any]) -> str:
    best = summary.get("_best_baseline")
    lines = [
        "| Méthode | P@10 liste agence (opérationnelle) | Écart vs meilleure naïve | P@20 liste globale | "
        "Rappel listes agence | Détection des besoins | Jours d'avance (médiane) |",
        "|---|---|---|---|---|---|---|",
    ]
    for m in ORDER:
        if m not in summary:
            continue
        e = summary[m]
        diff = e.get(f"diff_vs_{best}_p_at_k_agency_cd")
        lines.append(
            f"| {MODEL_LABELS[m]} | {_ci(e['p_at_k_agency_cd'])} | {_pts(diff) if diff else '(référence)'} | "
            f"{_ci(e['p_at_k_global'])} | {_ci(e['recall_agency_cd'])} | {_pct(e.get('detection_rate'))} | "
            f"{e.get('lead_days_median') or '—'} |"
        )
    return "\n".join(lines)


def ranking_table(summary: dict[str, Any]) -> str:
    lines = ["| Méthode | P@10 agence (classement pur, sans délai de relance) | Rappel |", "|---|---|---|"]
    for m in ORDER:
        if m in summary:
            e = summary[m]
            lines.append(f"| {MODEL_LABELS[m]} | {_ci(e['p_at_k_agency'])} | {_ci(e['recall_agency_lists'])} |")
    return "\n".join(lines)


def language_table(summary: dict[str, Any]) -> str:
    lines = [
        "| Méthode | P@10 agences FR | P@10 agences DE | Rappel FR | Rappel DE | Part des alertes DE |",
        "|---|---|---|---|---|---|",
    ]
    for m in ORDER:
        if m in summary:
            e = summary[m]
            lines.append(
                f"| {MODEL_LABELS[m]} | {_ci(e['p_at_k_agency_fr'])} | {_ci(e['p_at_k_agency_de'])} | "
                f"{_ci(e['recall_fr'])} | {_ci(e['recall_de'])} | {_ci(e['share_alerts_de'])} |"
            )
    return "\n".join(lines)


def calibration_table(cal: dict[str, Any]) -> str:
    lines = ["| Modèle | Brier | Brier du taux de base | ECE (10 classes) |", "|---|---|---|---|"]
    for m, c in cal.items():
        lines.append(f"| {MODEL_LABELS.get(m, m)} | {c['brier']:.4f} | {c['brier_base_rate']:.4f} | {c['ece']:.4f} |")
    return "\n".join(lines)


def variants_table(variants: dict[str, Any]) -> str:
    lines = [
        "| Variante | Meilleure naïve | P@10 opérationnelle naïve | M0 | M1 | M2 | Écart M1 vs naïve |",
        "|---|---|---|---|---|---|---|",
    ]
    for name, v in variants.items():
        s = v["summary"]
        best = s["_best_baseline"]

        def cell(m: str, s: dict[str, Any] = s) -> str:
            return _ci(s[m]["p_at_k_agency_cd"]) if m in s else "—"

        d = s.get("M1_boosting", {}).get(f"diff_vs_{best}_p_at_k_agency_cd")
        lines.append(
            f"| {name} | {MODEL_LABELS[best]} | {cell(best)} | {cell('M0_regles')} | {cell('M1_boosting')} | "
            f"{cell('M2_survie')} | {_pts(d) if d else '—'} |"
        )
    return "\n".join(lines)
