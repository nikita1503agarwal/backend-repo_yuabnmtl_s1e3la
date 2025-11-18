from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, JSONResponse
from typing import Literal

app = FastAPI(title="niomag API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "niomag backend is running"}


def color_palette(variant: str):
    variant = variant.lower()
    if variant == "black":
        return {
            "dock": "#1f2937",
            "dockHighlight": "#374151",
            "bank": "#111827",
            "bankHighlight": "#4b5563",
            "logo": "#9ca3af",
        }
    if variant == "blue":
        return {
            "dock": "#0f172a",
            "dockHighlight": "#1e3a8a",
            "bank": "#1d4ed8",
            "bankHighlight": "#60a5fa",
            "logo": "#93c5fd",
        }
    # default grey
    return {
        "dock": "#e5e7eb",
        "dockHighlight": "#9ca3af",
        "bank": "#d1d5db",
        "bankHighlight": "#9ca3af",
        "logo": "#6b7280",
    }


def generate_svg(banks: int = 3, color: str = "grey") -> str:
    colors = color_palette(color)

    slot_gap = 18
    bank_width = 82
    bank_height = 132
    dock_padding = 28

    total_width = dock_padding * 2 + banks * bank_width + (banks - 1) * slot_gap
    total_height = bank_height + dock_padding * 2 + 28

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{total_width}" height="{total_height}" viewBox="0 0 {total_width} {total_height}">',
        # background
        f'<rect width="100%" height="100%" fill="#ffffff"/>',
        # subtle shadow under dock
        f'<ellipse cx="{total_width/2}" cy="{total_height-10}" rx="{total_width*0.42}" ry="10" fill="rgba(0,0,0,0.08)"/>',
        # dock base
        f'<rect x="10" y="12" width="{total_width-20}" height="{total_height-28}" rx="22" fill="{colors["dock"]}"/>',
        f'<rect x="14" y="16" width="{total_width-28}" height="{total_height-36}" rx="20" fill="{colors["dockHighlight"]}" opacity="0.18"/>',
        # small "g" logo in corner
        f'<text x="{total_width-44}" y="{total_height-44}" font-family="Inter, Helvetica, Arial, sans-serif" font-size="20" fill="{colors["logo"]}" opacity="0.7">g</text>',
    ]

    # slots and banks
    start_x = dock_padding
    start_y = dock_padding + 4

    for i in range(banks):
        x = start_x + i * (bank_width + slot_gap)
        # slot recess
        svg.append(
            f'<rect x="{x-6}" y="{start_y-6}" width="{bank_width+12}" height="{bank_height+12}" rx="18" fill="#000000" opacity="0.06"/>'
        )
        # bank body
        svg.append(
            f'<rect x="{x}" y="{start_y}" width="{bank_width}" height="{bank_height}" rx="16" fill="{colors["bank"]}"/>'
        )
        # highlight gradient-ish overlay
        svg.append(
            f'<rect x="{x}" y="{start_y}" width="{bank_width}" height="{bank_height/2}" rx="16" fill="{colors["bankHighlight"]}" opacity="0.18"/>'
        )
        # camera clearance circle hint (aesthetic)
        svg.append(
            f'<circle cx="{x+bank_width/2}" cy="{start_y+18}" r="10" fill="#ffffff" opacity="0.06"/>'
        )
        # LED (white = charging, green = full). For variety, mark the first as green.
        led_color = "#a3ffa3" if i == 0 else "#ffffff"
        led_opacity = 0.95 if i == 0 else 0.7
        svg.append(
            f'<circle cx="{x+bank_width/2}" cy="{start_y+bank_height-16}" r="5" fill="{led_color}" opacity="{led_opacity}" stroke="#10b981" stroke-width="{1 if i==0 else 0}"/>'
        )
    
    svg.append("</svg>")
    return "".join(svg)


@app.get("/image/hub")
def image_hub(pack: Literal[3,4,6] = Query(3), color: Literal["grey", "black", "blue"] = Query("grey")):
    svg = generate_svg(banks=pack, color=color)
    return Response(content=svg, media_type="image/svg+xml")


@app.get("/image/mini")
def image_mini(color: Literal["grey", "black", "blue"] = Query("grey")):
    svg = generate_svg(banks=2, color=color)
    return Response(content=svg, media_type="image/svg+xml")


@app.get("/test")
def test():
    return JSONResponse({
        "backend": "ok",
        "database": "not-required",
        "connection_status": "ok",
    })
