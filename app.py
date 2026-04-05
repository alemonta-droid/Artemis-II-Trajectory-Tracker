from dash import Dash, html, dcc, Input, Output
import plotly.graph_objects as go
from datetime import datetime, timezone
import math
import numpy as np
from tracker import xs, ys, zs, t0, t_fine, posizione_a, velocita_a, posizione_luna, distanza_dalla_terra
from tracker import orbita_luna_reale

print("Calcolo orbita lunare...")
LUNA_OX, LUNA_OY, LUNA_OZ = orbita_luna_reale()
print("Fatto!")

app = Dash(__name__)

BG     = "#070714"
BG2    = "#0d0d2b"
ACCENT = "#00d4ff"
ORANGE = "#ff6b00"
TEXT   = "#e0e0ff"
GRAY   = "#2a2a4a"

app.layout = html.Div([

    html.Div([
        html.H1("🚀 ARTEMIS II — LIVE TRACKER",
                style={"color": ACCENT, "fontFamily": "monospace",
                       "letterSpacing": "4px", "margin": "0", "fontSize": "22px"}),
        html.P("Dati NASA/JSC • Aggiornamento in tempo reale",
               style={"color": "#666", "fontFamily": "monospace",
                      "margin": "4px 0 0 0", "fontSize": "11px"}),
    ], style={"padding": "20px 30px", "borderBottom": f"1px solid {GRAY}"}),

    html.Div([

        html.Div([
            dcc.Graph(id="grafico-3d",
                      style={"height": "580px"},
                      config={"displayModeBar": True, "scrollZoom": True})
        ], style={"width": "68%", "display": "inline-block", "verticalAlign": "top"}),

        html.Div([

            html.Div("TELEMETRIA", style={
                "color": ACCENT, "fontFamily": "monospace",
                "fontSize": "11px", "letterSpacing": "3px",
                "marginBottom": "20px", "paddingBottom": "8px",
                "borderBottom": f"1px solid {GRAY}"
            }),

            *[html.Div([
                html.P(label, style={"color": "#666", "fontSize": "10px",
                                     "fontFamily": "monospace", "margin": "0",
                                     "letterSpacing": "2px"}),
                html.P(id=pid, style={"color": TEXT, "fontSize": "18px",
                                      "fontFamily": "monospace", "margin": "4px 0 0 0",
                                      "fontWeight": "bold"}),
            ], style={"marginBottom": "20px", "paddingBottom": "16px",
                      "borderBottom": f"1px solid {GRAY}"})
            for label, pid in [
                ("ORA UTC",              "info-ora"),
                ("DISTANZA DALLA TERRA", "info-terra"),
                ("DISTANZA DALLA LUNA",  "info-luna"),
                ("VELOCITÀ",             "info-velocita"),
                ("PROGRESSO MISSIONE",   "info-missione"),
            ]],

            html.Div([
                html.Div(id="barra-progresso",
                         style={"height": "4px", "backgroundColor": ACCENT,
                                "borderRadius": "2px", "width": "0%",
                                "transition": "width 1s"})
            ], style={"backgroundColor": GRAY, "borderRadius": "2px",
                      "marginTop": "-10px"}),

        ], style={
            "width": "28%", "display": "inline-block",
            "verticalAlign": "top", "padding": "30px 20px",
            "backgroundColor": BG2, "height": "580px",
            "boxSizing": "border-box", "overflowY": "auto"
        }),

    ], style={"padding": "20px 30px"}),

    # Due timer separati
    dcc.Interval(id="timer",         interval=1000,  n_intervals=0),
    dcc.Interval(id="timer-grafico", interval=5000,  n_intervals=0),

], style={"backgroundColor": BG, "minHeight": "100vh", "color": TEXT})


def orbita_luna(lx, ly, lz):
    raggio = math.sqrt(lx**2 + ly**2 + lz**2)
    norm = raggio
    ux, uy, uz = lx/norm, ly/norm, lz/norm
    vx = -uy
    vy =  ux
    vz =  0.0
    vlen = math.sqrt(vx**2 + vy**2 + vz**2)
    vx, vy, vz = vx/vlen, vy/vlen, vz/vlen
    theta = np.linspace(0, 2 * np.pi, 300)
    ox = raggio * (np.cos(theta) * ux + np.sin(theta) * vx)
    oy = raggio * (np.cos(theta) * uy + np.sin(theta) * vy)
    oz = raggio * (np.cos(theta) * uz + np.sin(theta) * vz)
    return ox, oy, oz


# --- CALLBACK 1: grafico ogni 5 secondi ---
@app.callback(
    Output("grafico-3d", "figure"),
    Input("timer-grafico", "n_intervals")
)
def aggiorna_grafico(n):
    adesso = datetime.now(timezone.utc).replace(tzinfo=None)
    ox, oy, oz = posizione_a(adesso)
    lx, ly, lz = posizione_luna(adesso)

    olx, oly, olz = orbita_luna(lx, ly, lz)

    fig = go.Figure()

    fig.add_trace(go.Scatter3d(
    x=LUNA_OX, y=LUNA_OY, z=LUNA_OZ,
    mode="lines",
    line=dict(color="rgba(180,180,180,0.3)", width=1),
    name="Orbita Luna",
    hoverinfo="skip"
))

    fig.add_trace(go.Scatter3d(
        x=xs, y=ys, z=zs,
        mode="lines",
        line=dict(color=ORANGE, width=2),
        name="Traiettoria"
    ))

    fig.add_trace(go.Scatter3d(
        x=[0], y=[0], z=[0],
        mode="markers+text",
        marker=dict(size=12, color="#1a90ff"),
        text=["Terra"], textfont=dict(color=TEXT, size=11),
        textposition="top center", name="Terra"
    ))

    fig.add_trace(go.Scatter3d(
        x=[lx], y=[ly], z=[lz],
        mode="markers+text",
        marker=dict(size=9, color="#aaaaaa"),
        text=["Luna"], textfont=dict(color=TEXT, size=11),
        textposition="top center", name="Luna"
    ))

    fig.add_trace(go.Scatter3d(
        x=[ox], y=[oy], z=[oz],
        mode="markers+text",
        marker=dict(size=7, color="#ff4444", symbol="diamond"),
        text=["Orion"], textfont=dict(color=ACCENT, size=11),
        textposition="top center", name="Orion"
    ))

    fig.update_layout(
        uirevision=42,
        paper_bgcolor=BG,
        margin=dict(l=0, r=0, t=0, b=0),
        legend=dict(font=dict(color=TEXT, family="monospace"),
                    bgcolor="rgba(0,0,0,0)"),
        scene=dict(
            bgcolor=BG,
            xaxis=dict(gridcolor="#1a1a3a", color="#444", title="X (km)",
                       backgroundcolor=BG, showbackground=True),
            yaxis=dict(gridcolor="#1a1a3a", color="#444", title="Y (km)",
                       backgroundcolor=BG, showbackground=True),
            zaxis=dict(gridcolor="#1a1a3a", color="#444", title="Z (km)",
                       backgroundcolor=BG, showbackground=True),
            camera=dict(eye=dict(x=0.8, y=-1.8, z=0.5))
        )
    )

    return fig


# --- CALLBACK 2: telemetria ogni secondo ---
@app.callback(
    Output("info-ora",        "children"),
    Output("info-terra",      "children"),
    Output("info-luna",       "children"),
    Output("info-velocita",   "children"),
    Output("info-missione",   "children"),
    Output("barra-progresso", "style"),
    Input("timer", "n_intervals")
)
def aggiorna_telemetria(n):
    adesso = datetime.now(timezone.utc).replace(tzinfo=None)
    ox, oy, oz = posizione_a(adesso)
    lx, ly, lz = posizione_luna(adesso)
    vx, vy, vz = velocita_a(adesso)

    dist_terra = distanza_dalla_terra(ox, oy, oz)
    dist_luna  = distanza_dalla_terra(ox-lx, oy-ly, oz-lz)
    speed      = math.sqrt(vx**2 + vy**2 + vz**2)

    durata_totale = (t_fine - t0).total_seconds()
    trascorso     = (adesso - t0).total_seconds()
    percentuale   = min(100, max(0, (trascorso / durata_totale) * 100))

    barra_style = {
        "height": "4px",
        "backgroundColor": ACCENT,
        "borderRadius": "2px",
        "width": f"{percentuale:.1f}%",
        "transition": "width 1s"
    }

    return (
        adesso.strftime("%Y-%m-%d  %H:%M:%S"),
        f"{dist_terra:,.0f} km",
        f"{dist_luna:,.0f} km",
        f"{speed:.3f} km/s  ({speed*3600:,.0f} km/h)",
        f"{percentuale:.1f}%",
        barra_style
    )


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8050)
