"""Resume las tiradas exportadas por EstudioResultados y genera el gráfico."""
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

import altair as alt

STUDY_DIR = Path(__file__).resolve().parents[1]
ROOT = STUDY_DIR.parent.parent
csv_path = Path(sys.argv[1]) if len(sys.argv) > 1 else STUDY_DIR / "resultados-1000.csv"
rows = [{k: int(v) for k, v in row.items()} for row in csv.DictReader(csv_path.open(encoding="utf-8"))]
assert rows and [r["tirada"] for r in rows] == list(range(1, len(rows) + 1))
n = len(rows)
balance = 10
for r in rows:
    a, b, c = [r[f"resultado_{i}"] for i in range(1, 4)]
    assert all(0 <= x <= 2 for x in (a, b, c))
    assert r["premio"] == (3 - a if a == b == c else 0)
    assert r["hay_premio"] == int(r["premio"] > 0)
    balance += r["premio"] - 1
    assert r["saldo_teorico"] == balance
prizes = Counter(r["premio"] for r in rows)
symbols = [Counter(r[f"resultado_{i}"] for r in rows) for i in range(1, 4)]
victories = sum(r["hay_premio"] for r in rows)
first_zero = next((r["tirada"] for r in rows if r["saldo_teorico"] <= 0), None)
circuit = ROOT / "tragamonedas.circ"
root = ET.parse(circuit).getroot()
generator = root.find("circuit[@name='generador_resultados']")
seeds = [int(next(a.get("val") for a in comp.findall("a") if a.get("name") == "seed"))
         for comp in sorted(generator.findall("comp"), key=lambda c: int(c.get("loc", "(0,0)").strip("()").split(",")[1]))
         if comp.get("name") == "Random"]
summary = {
    "tiradas": n, "semillas_resultados_1_2_3": seeds,
    "circuito_sha256": hashlib.sha256(circuit.read_bytes()).hexdigest(),
    "csv_sha256": hashlib.sha256(csv_path.read_bytes()).hexdigest(),
    "victorias": victories, "derrotas": n - victories,
    "frecuencia_victoria": victories / n,
    "premios_por_valor": dict(sorted(prizes.items())),
    "simbolos_por_display": [dict(sorted(c.items())) for c in symbols],
    "combinaciones_observadas": len({tuple(r[f"resultado_{i}"] for i in range(1, 4)) for r in rows}),
    "creditos_iniciales": 10, "premios_totales": sum(r["premio"] for r in rows),
    "primera_tirada_sin_creditos": first_zero,
    "saldo_teorico_final_sin_bloqueo": rows[-1]["saldo_teorico"],
    "alcance": "Generador y evaluador reales aislados. Saldo matemático sin bloqueo en cero ni límite de 8 bits.",
    "referencia_teorica": "Tres símbolos equiprobables e independientes; no es una prueba de independencia de las semillas."
}
(csv_path.parent / "resumen-1000.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
# Composición estática en Altair/Vega-Lite, exportable sin navegador.
ink = "#16321A"
muted = "#526655"
logisim_green = "#00FF00"
background = "#FAFCF9"
def percent(value):
    return f"{value:.1f}".replace(".", ",") + " %"

outcomes = [
    {"tipo": "Victoria", "cantidad": victories, "orden": 0},
    {"tipo": "Sin premio", "cantidad": n - victories, "orden": 1},
]
strip = alt.Chart(alt.Data(values=outcomes)).mark_bar(size=24, cornerRadius=2).encode(
    x=alt.X("cantidad:Q", stack="zero", axis=None, scale=alt.Scale(domain=[0, n])),
    color=alt.Color("tipo:N", scale=alt.Scale(domain=["Victoria", "Sin premio"], range=[logisim_green, "#E1E8DF"]), legend=None),
    order=alt.Order("orden:Q", sort="ascending")
).properties(width=860, height=30, title=alt.TitleParams(
    text=f"{victories} victorias · {percent(100 * victories / n)}",
    subtitle=f"{n-victories} tiradas sin premio · {percent(100 * (n-victories) / n)}",
    anchor="start", fontSize=20, color=ink, subtitleColor=muted, subtitleFontSize=13, offset=13
))

win_names = ["Tres sietes", "Tres campanas", "Tres rayos"]
win_data = [{"resultado": name, "cantidad": prizes[prize],
             "etiqueta": f"{prizes[prize]}  ·  {percent(100 * prizes[prize] / n)}"}
            for name, prize in zip(win_names, [3, 2, 1])]
base = alt.Chart(alt.Data(values=win_data)).encode(
    y=alt.Y("resultado:N", sort=win_names, axis=alt.Axis(title=None, labelPadding=12)),
    x=alt.X("cantidad:Q", scale=alt.Scale(domain=[0, n*.055]),
            axis=alt.Axis(title="Cantidad de tiradas", values=[0, n*.01, n*.02, n*.03, n*.04, n*.05], format=".0f", grid=True))
)
bars = base.mark_bar(color=logisim_green, size=28, cornerRadiusEnd=3)
labels = base.mark_text(align="left", dx=8, color=ink, fontSize=13).encode(text="etiqueta:N")
reference = alt.Chart(alt.Data(values=[{"cantidad": n/27}])).mark_rule(
    color="#47734B", strokeDash=[4,4], strokeWidth=1.5
).encode(x="cantidad:Q")
wins = (bars + reference + labels).properties(width=370, height=210,
    title=alt.TitleParams(text="Cómo se repartieron las victorias",
        subtitle=f"Línea punteada: referencia ideal ≈ {n/27:.0f} por combinación",
        anchor="start", fontSize=15, subtitleFontSize=11, color=ink, subtitleColor=muted, offset=20))

heat_values = []
for i, counts in enumerate(symbols):
    for j, symbol in enumerate(["Siete", "Campana", "Rayo"]):
        count = counts[j]
        heat_values.append({"display": f"Display {i+1}", "simbolo": symbol,
                            "cantidad": count, "porcentaje": 100*count/n,
                            "porcentaje_texto": percent(100*count/n)})
heat_base = alt.Chart(alt.Data(values=heat_values)).encode(
    x=alt.X("simbolo:N", sort=["Siete", "Campana", "Rayo"],
            axis=alt.Axis(title=None, orient="top", labelAngle=0, labelPadding=12)),
    y=alt.Y("display:N", sort=["Display 1", "Display 2", "Display 3"],
            axis=alt.Axis(title=None, labelPadding=10))
)
tiles = heat_base.mark_rect(stroke=background, strokeWidth=6, cornerRadius=7).encode(
    color=alt.Color("porcentaje:Q", scale=alt.Scale(domain=[25,40], range=["#F0FFED", "#8FFF80"]), legend=None))
counts_text = heat_base.mark_text(color=ink, fontSize=21, fontWeight="bold", dy=-6).encode(text="cantidad:Q")
percent_text = heat_base.mark_text(color="#365438", fontSize=11, dy=16).encode(text="porcentaje_texto:N")
heat = (tiles + counts_text + percent_text).properties(width=340, height=210,
    title=alt.TitleParams(text="Qué mostró cada display",
        subtitle="Apariciones y porcentaje · referencia ideal: 33,33 %",
        anchor="start", fontSize=15, subtitleFontSize=11, color=ink, subtitleColor=muted, offset=20))

panels = alt.hconcat(wins, heat, spacing=44)
chart = alt.vconcat(strip, panels, spacing=38).properties(
    title=alt.TitleParams(text="Mil tiradas, tres formas de ganar",
        subtitle=f"Semillas {', '.join(map(str, seeds))} · aparecieron las 27 combinaciones posibles",
        anchor="start", fontSize=27, fontWeight="bold", color=ink,
        subtitleFontSize=13, subtitleColor=muted, offset=28),
    background=background, padding=28
).configure(font="Segoe UI").configure_view(stroke=None).configure_axis(
    labelFontSize=12, titleFontSize=11, titleFontWeight="normal", titlePadding=12,
    labelColor=muted, titleColor=muted, domain=False, ticks=False, gridColor="#E3EBE0"
)
output = ROOT / "img/estudio-resultados-1000.png"
chart.save(str(output), scale_factor=2)
print(f"Gráfico actualizado: {output}")
