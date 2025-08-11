#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gráfico espectral simple desde metadata:
- Lee CenterWavelength (CWL) y FWHM/Bandwidth con exiftool.
- Dibuja solo la curva de respuesta idealizada (gaussiana), la línea del CWL
  y sombrea el FWHM.
Uso:
  python plot_wavelength_only.py --image /ruta/imagen.tif
  # Override si falta metadata:
  python plot_wavelength_only.py --image /ruta/imagen.tif --wl 440 --fwhm 10
  # Guardar figura:
  python plot_wavelength_only.py --image /ruta/imagen.tif --save out.png
Requisitos:
  - exiftool en PATH
  - pip install numpy matplotlib
"""

import argparse
import json
import re
import subprocess
from typing import Any, Dict, Optional, Tuple

import numpy as np
import matplotlib.pyplot as plt


def run_exiftool_json(path: str) -> Dict[str, Any]:
    cmd = ["exiftool", "-j", "-a", "-G", "-s", path]
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(out.stdout)
        return data[0] if isinstance(data, list) and data else {}
    except FileNotFoundError:
        raise RuntimeError("No se encontró 'exiftool'. Instálalo y añádelo al PATH.")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Error ejecutando exiftool: {e.stderr or e.stdout}")


def _to_float_nm(value: Any) -> Optional[float]:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    s = str(value)
    m = re.search(r'([-+]?\d+(?:\.\d+)?)\s*(?:nm|nanometer|nanometers)?', s, re.IGNORECASE)
    return float(m.group(1)) if m else None


def extract_cwl_fwhm(meta: Dict[str, Any]) -> Tuple[Optional[float], Optional[float]]:
    cwl_keys = ["CenterWavelength", "Wavelength", "CWL", "CentralWavelength",
                "SpectralBandCentralWavelength", "XMP:CenterWavelength", "XMP:Wavelength"]
    fwhm_keys = ["FWHM", "Bandwidth", "BandWidth", "FullWidthHalfMax",
                 "SpectralBandWidth", "XMP:FWHM", "XMP:Bandwidth"]

    cwl = None
    fwhm = None
    for k, v in meta.items():
        base = k.split(":")[-1]
        if base in cwl_keys or k in cwl_keys:
            cwl = cwl or _to_float_nm(v)
        if base in fwhm_keys or k in fwhm_keys:
            fwhm = fwhm or _to_float_nm(v)

    # Búsqueda laxa en textos si aún faltan
    if cwl is None or fwhm is None:
        blob = "\n".join([str(v) for v in meta.values() if isinstance(v, str) and v])
        if cwl is None:
            m1 = re.search(r'(center\s*wave(length)?|cwl)\s*[:=]?\s*([-+]?\d+(?:\.\d+)?)\s*nm', blob, re.IGNORECASE)
            if m1:
                cwl = float(m1.group(3))
        if fwhm is None:
            m2 = re.search(r'(fwhm|band\s*width|bandwidth)\s*[:=]?\s*([-+]?\d+(?:\.\d+)?)\s*nm', blob, re.IGNORECASE)
            if m2:
                fwhm = float(m2.group(2))
    return cwl, fwhm


def gaussian_from_fwhm(center_nm: float, fwhm_nm: Optional[float], wl_min=350, wl_max=1000, step=0.5):
    wl = np.arange(wl_min, wl_max + step, step)
    if not fwhm_nm or fwhm_nm <= 0:
        resp = np.zeros_like(wl, dtype=float)
        resp[(np.abs(wl - center_nm)).argmin()] = 1.0
        return wl, resp
    sigma = fwhm_nm / (2.0 * np.sqrt(2.0 * np.log(2.0)))
    resp = np.exp(-0.5 * ((wl - center_nm) / sigma) ** 2)
    resp /= resp.max() if resp.max() > 0 else 1.0
    return wl, resp


def main():
    ap = argparse.ArgumentParser(description="Gráfico de longitud de onda con CWL, FWHM y curva de respuesta.")
    ap.add_argument("--image", required=True, help="Ruta a la imagen.")
    ap.add_argument("--wl", type=float, default=None, help="CWL en nm (override si no hay metadata).")
    ap.add_argument("--fwhm", type=float, default=None, help="FWHM en nm (override si no hay metadata).")
    ap.add_argument("--wlmin", type=float, default=350, help="λ mínimo del eje X (nm).")
    ap.add_argument("--wlmax", type=float, default=1000, help="λ máximo del eje X (nm).")
    ap.add_argument("--save", type=str, default=None, help="Guardar figura en PNG.")
    args = ap.parse_args()

    meta = run_exiftool_json(args.image)
    cwl_meta, fwhm_meta = extract_cwl_fwhm(meta)

    cwl = args.wl if args.wl is not None else cwl_meta
    fwhm = args.fwhm if args.fwhm is not None else fwhm_meta
    if cwl is None:
        raise RuntimeError("No se encontró CWL en metadata y no se proporcionó --wl.")

    wl, resp = gaussian_from_fwhm(cwl, fwhm, wl_min=args.wlmin, wl_max=args.wlmax)

    plt.figure(figsize=(8, 5))
    plt.plot(wl, resp, label="Curva de respuesta (idealizada)")
    plt.axvline(cwl, linestyle="--", linewidth=1.2, label=f"CWL = {cwl:.1f} nm")

    half = 0.5
    plt.axhline(half, linestyle=":", linewidth=1.0, label="Mitad de altura (50%)")

    # sombrear FWHM si está disponible
    if fwhm and fwhm > 0:
        # puntos de cruce con 50%
        above = resp >= half
        idx = np.where(np.diff(above.astype(int)) != 0)[0]
        crossings = []
        for i in idx:
            x0, x1 = wl[i], wl[i+1]
            y0, y1 = resp[i], resp[i+1]
            if y1 != y0:
                xc = x0 + (half - y0) * (x1 - x0) / (y1 - y0)
                crossings.append(xc)
        if len(crossings) >= 2:
            left, right = crossings[0], crossings[-1]
            plt.fill_betweenx([0, 1], left, right, alpha=0.2,
                              label=f"FWHM ≈ {right - left:.1f} nm")

    plt.xlim(args.wlmin, args.wlmax)
    plt.ylim(0, 1.05)
    plt.xlabel("Longitud de onda (nm)")
    plt.ylabel("Respuesta relativa")
    plt.title("CWL, FWHM y curva de respuesta espectral")
    plt.grid(True, linestyle="--", linewidth=0.5)
    plt.legend(loc="upper right")
    plt.tight_layout()

    if args.save:
        plt.savefig(args.save, dpi=150)
    plt.show()


if __name__ == "__main__":
    main()
