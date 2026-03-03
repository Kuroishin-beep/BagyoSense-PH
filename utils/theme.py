# ── Base axis style ───────────────────────────────────────────────────────────
_AXIS = dict(
    gridcolor="#1e3a5f",
    linecolor="#1e3a5f",
    tickcolor="#94a3b8",
    zeroline=False,
)

# ── Base plot theme — NO xaxis/yaxis keys here ────────────────────────────────
PLOT_THEME = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(15,32,53,0.5)",
    font=dict(family="IBM Plex Mono", color="#94a3b8", size=11),
    colorway=["#00d4aa", "#3b82f6", "#a855f7", "#f59e0b", "#ef4444", "#10b981"],
    legend=dict(
        bgcolor="rgba(0,0,0,0)",
        bordercolor="#1e3a5f",
        font=dict(color="#94a3b8", size=10),
    ),
    margin=dict(l=10, r=10, t=30, b=10),
)


def apply_theme(fig, height=300, show_legend=False, xaxis=None, yaxis=None):
    """Apply dark theme safely — merges axes without duplicate key errors."""
    xa = {**_AXIS, **(xaxis or {})}
    ya = {**_AXIS, **(yaxis or {})}
    fig.update_layout(
        **PLOT_THEME,
        height=height,
        showlegend=show_legend,
        xaxis=xa,
        yaxis=ya,
    )
    return fig


# ── Colour palettes ───────────────────────────────────────────────────────────
COLORS = {
    "teal":   "#00d4aa",
    "blue":   "#3b82f6",
    "purple": "#a855f7",
    "amber":  "#f59e0b",
    "red":    "#ef4444",
    "slate":  "#94a3b8",
    "card":   "#0f2035",
    "border": "#1e3a5f",
    "bg":     "#0a1628",
}

ENSO_COLORS = {
    "El Nino": "#ef4444",
    "La Nina": "#3b82f6",
    "Neutral": "#00d4aa",
}

SEASON_COLORS = {
    "Peak (Jun-Nov)":       "#00d4aa",
    "Off-Season (Dec-May)": "#3b82f6",
}

MONTH_SHORT = ["J", "F", "M", "A", "M", "J", "J", "A", "S", "O", "N", "D"]