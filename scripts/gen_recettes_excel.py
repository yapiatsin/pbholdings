"""Génère un fichier Excel d'exemple pour l'import de recettes.

Usage :
    python scripts/gen_recettes_excel.py

Produit : ./media/imports/recettes_exemple.xlsx (10 lignes)

Colonnes dans l'ordre attendu par AddRecetteExcelView :
    Immatriculation | Marque | Catégorie | Chauffeur |
    Compte comptable | N° facture | N° pièce | Montant | Date saisie
"""

from datetime import date, timedelta
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter


HEADERS = [
    "Immatriculation",
    "Marque",
    "Catégorie",
    "Chauffeur",
    "Compte comptable",
    "N° facture",
    "N° pièce",
    "Montant",
    "Date saisie",
]


def build_rows():
    """10 enregistrements basés sur les immatriculations TX-1003-CI / -CZ et variantes."""
    today = date.today()
    return [
        # Immat,         Marque,    Catégorie, Chauffeur,         Cpte,        N°Fact,    N°Pièce,   Montant, Date
        ("TX-1003-CI",  "Toyota",  "TX",      "Kouassi Adama",   "411-CHF-01", "FAC-2026-001", "PC-001", 35000, today),
        ("TX-1003-CZ",  "Toyota",  "TX",      "Yao Konan",       "411-CHF-02", "FAC-2026-002", "PC-002", 32000, today - timedelta(days=1)),
        ("TX-1004-CI",  "Hyundai", "TX",      "Diabaté Sékou",   "411-CHF-03", "FAC-2026-003", "PC-003", 41000, today - timedelta(days=2)),
        ("TX-1004-CZ",  "Hyundai", "TX",      "Touré Aboubacar", "411-CHF-04", "FAC-2026-004", "PC-004", 28000, today - timedelta(days=3)),
        ("TX-1005-CI",  "Kia",     "TX",      "Coulibaly Issouf", "411-CHF-05", "FAC-2026-005", "PC-005", 39500, today - timedelta(days=4)),
        ("TX-1005-CZ",  "Kia",     "TX",      "Bamba Lassina",   "411-CHF-06", "FAC-2026-006", "PC-006", 36000, today - timedelta(days=5)),
        ("TX-1006-CI",  "Suzuki",  "TX",      "Soro Drissa",     "411-CHF-07", "FAC-2026-007", "PC-007", 30000, today - timedelta(days=6)),
        ("TX-1006-CZ",  "Suzuki",  "TX",      "N'Guessan Yves",  "411-CHF-08", "FAC-2026-008", "PC-008", 27500, today - timedelta(days=7)),
        ("TX-1007-CI",  "Nissan",  "TX",      "Ouattara Moussa", "411-CHF-09", "FAC-2026-009", "PC-009", 42000, today - timedelta(days=8)),
        ("TX-1007-CZ",  "Nissan",  "TX",      "Koffi Eric",      "411-CHF-10", "FAC-2026-010", "PC-010", 33500, today - timedelta(days=9)),
    ]


def main():
    out_dir = Path(__file__).resolve().parent.parent / "media" / "imports"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "recettes_exemple.xlsx"

    wb = Workbook()
    ws = wb.active
    ws.title = "Recettes"

    # ---- Style en-tête ----
    header_font = Font(bold=True, color="FFFFFF")
    header_fill = PatternFill("solid", fgColor="EC281C")
    header_align = Alignment(horizontal="center", vertical="center")

    for col_idx, label in enumerate(HEADERS, start=1):
        cell = ws.cell(row=1, column=col_idx, value=label)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = header_align

    # ---- Données ----
    for r_idx, row in enumerate(build_rows(), start=2):
        for c_idx, value in enumerate(row, start=1):
            cell = ws.cell(row=r_idx, column=c_idx, value=value)
            # Date au bon format
            if HEADERS[c_idx - 1] == "Date saisie":
                cell.number_format = "DD/MM/YYYY"
            # Montant aligné à droite
            if HEADERS[c_idx - 1] == "Montant":
                cell.number_format = "#,##0"
                cell.alignment = Alignment(horizontal="right")

    # ---- Largeur auto des colonnes ----
    widths = {
        "Immatriculation": 16,
        "Marque": 12,
        "Catégorie": 11,
        "Chauffeur": 22,
        "Compte comptable": 18,
        "N° facture": 16,
        "N° pièce": 12,
        "Montant": 12,
        "Date saisie": 14,
    }
    for col_idx, label in enumerate(HEADERS, start=1):
        ws.column_dimensions[get_column_letter(col_idx)].width = widths.get(label, 14)

    ws.freeze_panes = "A2"

    wb.save(out_path)
    print(f"OK -> {out_path}")
    print(f"   {len(build_rows())} lignes ecrites.")


if __name__ == "__main__":
    main()
