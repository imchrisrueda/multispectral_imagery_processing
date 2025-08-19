#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Aplicación de escritorio para extraer altitud GPS de imágenes usando exiftool
-----------------------------------------------------------------------------

• SO compatibles: Linux, Windows, macOS (requiere exiftool instalado y en PATH, o especificar su ruta).
• Dependencias Python: PyQt6, pandas.
• Entrada: Directorio con imágenes .jpg/.tif/.tiff.
• Salida: Tabla con Archivo, Altitud (m), Estado; opción de exportar a CSV.
• Lógica base tomada del script CLI proporcionado por el usuario.

Novedad: selector de tipo de imágenes (RGB, Térmica, Multiespectral). En modo Multiespectral solo se analizan
archivos que representen la banda 1 con patrón "*_1.tif" (p. ej., "IMG_0000_1.tif") para optimizar la velocidad.

Instalación rápida:
    pip install PyQt6 pandas
    # Linux (Debian/Ubuntu): sudo apt install libimage-exiftool-perl
    # macOS: brew install exiftool
    # Windows: descargar exiftool.exe (Phil Harvey) y añadir a PATH o indicar su ruta en la app.

Ejecución:
    python app_altitud_exif.py

Autor: (tu nombre)
Fecha: 2025-08-13
Licencia: MIT
"""

from __future__ import annotations
import os
import sys
import json
import re
import subprocess
import fnmatch
from dataclasses import dataclass
from typing import List, Optional

import pandas as pd

from PyQt6.QtCore import (
    Qt,
    QThread,
    pyqtSignal,
)
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QFileDialog,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QProgressBar,
    QSpinBox,
    QCheckBox,
    QGroupBox,
    QMessageBox,
    QStatusBar,
    QToolBar,
    QComboBox,
)


# ---------------------------- Utilidades de extracción ----------------------------

def extraer_altitud_exiftool(ruta_imagen: str, exiftool_cmd: str = "exiftool") -> Optional[float]:
    """Extrae una altitud en metros desde GPSAltitude o AbsoluteAltitude.

    Acepta formatos como "549.7 m" o "549.7 Above Sea Level" y toma el primer
    número con signo y decimales que encuentre. Devuelve None si no hay dato.
    """
    try:
        comando = [exiftool_cmd, "-j", "-GPSAltitude", "-AbsoluteAltitude", ruta_imagen]
        resultado = subprocess.run(
            comando, capture_output=True, text=True, check=True
        )
        salida = resultado.stdout.strip()
        if not salida:
            return None
        metadata_list = json.loads(salida)
        if not metadata_list:
            return None
        metadata = metadata_list[0]
        alt = metadata.get("GPSAltitude") or metadata.get("AbsoluteAltitude")
        if isinstance(alt, str):
            match = re.search(r"[-+]?\d*\.\d+|[-+]?\d+", alt)
            if match:
                return float(match.group())
            return None
        elif isinstance(alt, (int, float)):
            return float(alt)
        return None
    except subprocess.CalledProcessError:
        return None
    except Exception:
        return None


# ---------------------------- Worker en hilo ----------------------------

@dataclass
class ResultadoFila:
    archivo: str
    altitud: Optional[float]
    estado: str


class ProcesadorThread(QThread):
    progreso = pyqtSignal(int)               # 0-100
    fila_lista = pyqtSignal(ResultadoFila)   # resultado por archivo
    terminado = pyqtSignal(list)             # lista completa de Resultados
    error = pyqtSignal(str)

    def __init__(self, directorio: str, extensiones: List[str], umbral: float, exiftool_cmd: str, tipo: str):
        super().__init__()
        self.directorio = directorio
        self.extensiones = tuple(extensiones)
        self.umbral = umbral
        self.exiftool_cmd = exiftool_cmd
        self.tipo = tipo  # "RGB" | "Térmica" | "Multiespectral"
        self._cancelado = False

    def cancelar(self):
        self._cancelado = True

    def _listar_archivos(self) -> List[str]:
        # Modo Multiespectral: solo banda 1 => patrón *_1.tif (insensible a mayúsculas)
        if self.tipo.lower().startswith("multi"):
            patron = "*_1.tif"
            archivos = [
                f for f in os.listdir(self.directorio)
                if fnmatch.fnmatch(f.lower(), patron)
            ]
            return sorted(archivos)
        # Otros modos: usa extensiones marcadas
        return sorted([
            f for f in os.listdir(self.directorio)
            if f.lower().endswith(self.extensiones)
        ])

    def run(self):
        try:
            archivos = self._listar_archivos()
            n = len(archivos)
            resultados: List[ResultadoFila] = []
            altitud_anterior: Optional[float] = None

            for i, archivo in enumerate(archivos, start=1):
                if self._cancelado:
                    break
                ruta = os.path.join(self.directorio, archivo)
                altitud = extraer_altitud_exiftool(ruta, self.exiftool_cmd)

                if altitud is not None and altitud_anterior is not None:
                    estado = (
                        f"Cambio >{int(self.umbral)} m" if abs(altitud - altitud_anterior) > self.umbral else "OK"
                    )
                else:
                    estado = "Sin comparación" if altitud_anterior is None else "Altitud no disponible"

                if altitud is not None:
                    altitud_anterior = altitud

                fila = ResultadoFila(
                    archivo=archivo,
                    altitud=round(altitud, 2) if altitud is not None else None,
                    estado=estado,
                )
                resultados.append(fila)
                self.fila_lista.emit(fila)

                progreso = int(i / n * 100) if n else 100
                self.progreso.emit(progreso)

            self.terminado.emit(resultados)
        except Exception as e:
            self.error.emit(str(e))


# ---------------------------- Interfaz principal ----------------------------

class VentanaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Altitud EXIF – Analizador")
        self.setMinimumSize(940, 660)
        if os.name == "nt":
            self.setWindowIcon(QIcon())

        self.worker: Optional[ProcesadorThread] = None
        self.resultados: List[ResultadoFila] = []

        self._crear_toolbar()
        self._crear_ui()
        self._aplicar_tema_fusion_moderno()

    # --------- UI ---------
    def _crear_toolbar(self):
        tb = QToolBar("Acciones")
        tb.setMovable(False)
        self.addToolBar(tb)

        act_abrir = QAction("Seleccionar carpeta", self)
        act_abrir.triggered.connect(self._seleccionar_directorio)
        tb.addAction(act_abrir)

        tb.addSeparator()

        act_exportar = QAction("Exportar CSV", self)
        act_exportar.triggered.connect(self._exportar_csv)
        tb.addAction(act_exportar)

        tb.addSeparator()

        act_acerca = QAction("Acerca de", self)
        act_acerca.triggered.connect(self._acerca_de)
        tb.addAction(act_acerca)

    def _crear_ui(self):
        cont = QWidget()
        lay = QVBoxLayout(cont)
        lay.setContentsMargins(16, 12, 16, 12)
        lay.setSpacing(12)

        # Grupo de entrada
        grp = QGroupBox("Parámetros de análisis")
        glay = QVBoxLayout(grp)

        # Fila: directorio
        fila_dir = QHBoxLayout()
        lbl_dir = QLabel("Directorio de imágenes")
        self.ed_dir = QLineEdit()
        self.ed_dir.setPlaceholderText("Selecciona un directorio con imágenes .jpg/.tif/.tiff")
        btn_dir = QPushButton("Buscar…")
        btn_dir.clicked.connect(self._seleccionar_directorio)
        fila_dir.addWidget(lbl_dir)
        fila_dir.addWidget(self.ed_dir, 1)
        fila_dir.addWidget(btn_dir)

        # Fila: exiftool
        fila_exif = QHBoxLayout()
        lbl_exif = QLabel("Comando/Ruta de exiftool")
        self.ed_exif = QLineEdit("exiftool")
        self.ed_exif.setPlaceholderText("p. ej., exiftool o C:/ruta/a/exiftool.exe")
        btn_exif = QPushButton("Buscar…")
        btn_exif.clicked.connect(self._seleccionar_exiftool)
        fila_exif.addWidget(lbl_exif)
        fila_exif.addWidget(self.ed_exif, 1)
        fila_exif.addWidget(btn_exif)

        # Fila: opciones
        fila_opts = QHBoxLayout()
        lbl_umbral = QLabel("Umbral de cambio (m)")
        self.sp_umbral = QSpinBox()
        self.sp_umbral.setRange(1, 10000)
        self.sp_umbral.setValue(10)

        # Nuevo: selector de tipo
        lbl_tipo = QLabel("Tipo de imágenes")
        self.cb_tipo = QComboBox()
        self.cb_tipo.addItems(["RGB", "Térmica", "Multiespectral"])
        self.cb_tipo.currentTextChanged.connect(self._tipo_cambiado)

        self.cb_jpg = QCheckBox(".jpg")
        self.cb_jpg.setChecked(True)
        self.cb_tif = QCheckBox(".tif")
        self.cb_tif.setChecked(True)
        self.cb_tiff = QCheckBox(".tiff")
        self.cb_tiff.setChecked(True)

        fila_opts.addWidget(lbl_umbral)
        fila_opts.addWidget(self.sp_umbral)
        fila_opts.addSpacing(16)
        fila_opts.addWidget(lbl_tipo)
        fila_opts.addWidget(self.cb_tipo)
        fila_opts.addSpacing(16)
        fila_opts.addWidget(QLabel("Extensiones:"))
        fila_opts.addWidget(self.cb_jpg)
        fila_opts.addWidget(self.cb_tif)
        fila_opts.addWidget(self.cb_tiff)
        fila_opts.addStretch(1)

        # Botones acción
        fila_btns = QHBoxLayout()
        self.btn_analizar = QPushButton("Analizar")
        self.btn_analizar.clicked.connect(self._iniciar_analisis)
        self.btn_cancelar = QPushButton("Cancelar")
        self.btn_cancelar.setEnabled(False)
        self.btn_cancelar.clicked.connect(self._cancelar)
        self.btn_limpiar = QPushButton("Limpiar tabla")
        self.btn_limpiar.clicked.connect(self._limpiar_tabla)
        fila_btns.addStretch(1)
        fila_btns.addWidget(self.btn_limpiar)
        fila_btns.addWidget(self.btn_cancelar)
        fila_btns.addWidget(self.btn_analizar)

        # Tabla
        self.tabla = QTableWidget(0, 3)
        self.tabla.setHorizontalHeaderLabels(["Archivo", "Altitud (m)", "Estado"])
        self.tabla.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.tabla.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.tabla.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.tabla.setAlternatingRowColors(True)
        self.tabla.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabla.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

        lay.addWidget(grp)
        glay.addLayout(fila_dir)
        glay.addLayout(fila_exif)
        glay.addLayout(fila_opts)
        glay.addLayout(fila_btns)
        lay.addWidget(self.tabla, 1)

        # Barra de estado
        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.progreso = QProgressBar()
        self.progreso.setRange(0, 100)
        self.progreso.setValue(0)
        self.status.addPermanentWidget(self.progreso, 1)

        self.setCentralWidget(cont)

    def _aplicar_tema_fusion_moderno(self):
        QApplication.setStyle("Fusion")

    # --------- Acciones ---------
    def _seleccionar_directorio(self):
        ruta = QFileDialog.getExistingDirectory(self, "Selecciona directorio de imágenes", os.path.expanduser("~"))
        if ruta:
            self.ed_dir.setText(ruta)

    def _seleccionar_exiftool(self):
        filtro = "Ejecutable (exiftool*);;Todos los archivos (*)"
        ruta, _ = QFileDialog.getOpenFileName(self, "Selecciona exiftool", os.path.expanduser("~"), filtro)
        if ruta:
            self.ed_exif.setText(ruta)

    def _tipo_cambiado(self, texto: str):
        # En Multiespectral, las extensiones se vuelven irrelevantes porque filtramos por *_1.tif.
        is_multi = texto.lower().startswith("multi")
        self.cb_jpg.setEnabled(not is_multi)
        self.cb_tif.setEnabled(not is_multi)
        self.cb_tiff.setEnabled(not is_multi)
        self.status.showMessage("Modo Multiespectral: solo se analizarán archivos *_1.tif (banda 1)", 5000) if is_multi else self.status.clearMessage()

    def _iniciar_analisis(self):
        if self.worker and self.worker.isRunning():
            QMessageBox.warning(self, "En ejecución", "Ya hay un análisis en curso.")
            return
        directorio = self.ed_dir.text().strip()
        if not directorio or not os.path.isdir(directorio):
            QMessageBox.warning(self, "Directorio no válido", "Selecciona un directorio válido con imágenes.")
            return
        exiftool_cmd = self.ed_exif.text().strip() or "exiftool"
        extensiones = []
        if self.cb_jpg.isChecked():
            extensiones.append(".jpg")
        if self.cb_tif.isChecked():
            extensiones.append(".tif")
        if self.cb_tiff.isChecked():
            extensiones.append(".tiff")
        if not extensiones and not self.cb_tipo.currentText().lower().startswith("multi"):
            QMessageBox.warning(self, "Sin extensiones", "Selecciona al menos una extensión o usa Multiespectral.")
            return

        self.resultados.clear()
        self.tabla.setRowCount(0)
        self.progreso.setValue(0)
        self.btn_analizar.setEnabled(False)
        self.btn_cancelar.setEnabled(True)
        self.status.showMessage("Analizando…")

        self.worker = ProcesadorThread(
            directorio=directorio,
            extensiones=extensiones,
            umbral=float(self.sp_umbral.value()),
            exiftool_cmd=exiftool_cmd,
            tipo=self.cb_tipo.currentText(),
        )
        self.worker.fila_lista.connect(self._insertar_fila)
        self.worker.progreso.connect(self.progreso.setValue)
        self.worker.error.connect(self._worker_error)
        self.worker.terminado.connect(self._worker_terminado)
        self.worker.start()

    def _cancelar(self):
        if self.worker and self.worker.isRunning():
            self.worker.cancelar()
            self.status.showMessage("Cancelando…")

    def _insertar_fila(self, fila: ResultadoFila):
        self.resultados.append(fila)
        r = self.tabla.rowCount()
        self.tabla.insertRow(r)
        self.tabla.setItem(r, 0, QTableWidgetItem(fila.archivo))
        self.tabla.setItem(
            r, 1,
            QTableWidgetItem("{:.2f}".format(fila.altitud) if fila.altitud is not None else "No disponible"),
        )
        item_estado = QTableWidgetItem(fila.estado)
        if fila.estado.startswith("Cambio"):
            item_estado.setForeground(Qt.GlobalColor.red)
        elif fila.estado == "OK":
            item_estado.setForeground(Qt.GlobalColor.darkGreen)
        self.tabla.setItem(r, 2, item_estado)

    def _worker_error(self, msg: str):
        QMessageBox.critical(self, "Error de procesamiento", msg)
        self.btn_analizar.setEnabled(True)
        self.btn_cancelar.setEnabled(False)
        self.status.clearMessage()

    def _worker_terminado(self, _res: list):
        self.btn_analizar.setEnabled(True)
        self.btn_cancelar.setEnabled(False)
        self.status.showMessage("Listo", 4000)
        self.progreso.setValue(100)

    def _limpiar_tabla(self):
        self.resultados.clear()
        self.tabla.setRowCount(0)
        self.progreso.setValue(0)
        self.status.clearMessage()

    def _exportar_csv(self):
        if not self.resultados:
            QMessageBox.information(self, "Sin datos", "No hay resultados para exportar.")
            return
        ruta, _ = QFileDialog.getSaveFileName(self, "Guardar CSV", os.path.join(os.path.expanduser("~"), "altitud_exif.csv"), "CSV (*.csv)")
        if not ruta:
            return
        df = pd.DataFrame([
            {
                "Archivo": f.archivo,
                "Altitud (m)": f.altitud if f.altitud is not None else "No disponible",
                "Estado": f.estado,
            }
            for f in self.resultados
        ])
        try:
            df.to_csv(ruta, index=False)
            self.status.showMessage(f"CSV guardado: {ruta}", 5000)
        except Exception as e:
            QMessageBox.critical(self, "Error al guardar", str(e))

    def _acerca_de(self):
        QMessageBox.information(
            self,
            "Acerca de",
            (
                "Altitud EXIF – Analizador\n\n"
                "Extrae altitudes GPS de imágenes mediante exiftool y destaca cambios\n"
                "superiores a un umbral configurable.\n\n"
                "Modos: RGB, Térmica y Multiespectral (solo *_1.tif)."
            ),
        )


def main():
    app = QApplication(sys.argv)
    win = VentanaPrincipal()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
