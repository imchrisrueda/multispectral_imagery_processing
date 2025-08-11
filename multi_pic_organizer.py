#!/usr/bin/env python3
"""
Organizador de Archivos Multiespectrales
========================================

Este script organiza archivos de imágenes multiespectrales desde las carpetas RED y BLUE
en una estructura más limpia y organizada.

Estructura objetivo:
- photos/: Todas las imágenes excepto las de calibración
- calibration/: Primeras 11 imágenes (IMG_0000_1 hasta IMG_0000_11)
- dat_files/: Todos los archivos .dat

Uso: python multi_pic_organizer.py /ruta/a/tu/directorio

Fecha: agosto 2025
"""

import os
import shutil
import glob
from pathlib import Path
import logging
from typing import List, Tuple
import re

# Configuración del logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('file_organizer.log'),
        logging.StreamHandler()
    ]
)

class MultispectralOrganizer:
    """Clase para organizar archivos multiespectrales."""
    
    def __init__(self, base_directory: str = "."):
        """
        Inicializa el organizador.

        Args:
            base_directory (str): Directorio base donde están las carpetas RED y BLUE
        """
        self.base_dir = Path(base_directory).resolve()
        self.red_dir = self.base_dir / "RED"
        self.blue_dir = self.base_dir / "BLUE"

        # Carpetas de destino
        self.photos_dir = self.base_dir / "photos"
        self.calibration_dir = self.base_dir / "calibration"
        self.dat_files_dir = self.base_dir / "dat_files"
        self.discard_images_dir = self.base_dir / "discard_images"

        # Patrón para archivos de calibración
        self.calibration_pattern = re.compile(r'IMG_0000_([1-9]|1[01])\..*')

        # Configuración de logging en el directorio base
        # Elimina handlers previos si ya existen
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)

        # Configura el nuevo archivo de log en el directorio base
        log_file = self.base_dir / "file_organizer.log"
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, mode='w', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )


        logging.info(f"Inicializando organizador en: {self.base_dir}")

    
    def validate_structure(self) -> bool:
        """
        Valida que existan las carpetas RED y BLUE.
        
        Returns:
            bool: True si la estructura es válida
        """
        if not self.red_dir.exists():
            logging.error(f"No se encontró la carpeta RED en: {self.red_dir}")
            return False
        
        if not self.blue_dir.exists():
            logging.error(f"No se encontró la carpeta BLUE en: {self.blue_dir}")
            return False
        
        logging.info("✓ Estructura de carpetas validada correctamente")
        return True
    
    def create_destination_folders(self) -> None:
        """Crea las carpetas de destino si no existen."""
        folders_to_create = [self.photos_dir, self.calibration_dir, self.dat_files_dir, self.discard_images_dir]
        
        for folder in folders_to_create:
            if folder.exists():
                logging.warning(f"La carpeta {folder.name} ya existe. Se mantendrá el contenido existente.")
            else:
                folder.mkdir(exist_ok=True)
                logging.info(f"✓ Carpeta creada: {folder.name}")
    
    def get_all_images(self, source_dir: Path) -> List[Path]:
        """
        Obtiene todas las imágenes de las subcarpetas numeradas.
        
        Args:
            source_dir (Path): Directorio fuente (RED o BLUE)
            
        Returns:
            List[Path]: Lista de rutas de imágenes
        """
        images = []
        
        # Buscar subcarpetas numeradas (000, 001, 002, etc.)
        subdirs = [d for d in source_dir.iterdir() if d.is_dir() and d.name.isdigit()]
        subdirs.sort()  # Ordenar numéricamente
        
        for subdir in subdirs:
            # Buscar archivos de imagen comunes
            image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.tiff', '*.tif', '*.bmp', '*.raw']
            
            for ext in image_extensions:
                images.extend(subdir.glob(ext))
                images.extend(subdir.glob(ext.upper()))  # También mayúsculas
        
        logging.info(f"Encontradas {len(images)} imágenes en {source_dir.name}")
        return images
    
    def is_calibration_image(self, image_path: Path) -> bool:
        """
        Determina si una imagen es de calibración.
        
        Args:
            image_path (Path): Ruta de la imagen
            
        Returns:
            bool: True si es imagen de calibración
        """
        return bool(self.calibration_pattern.match(image_path.name))
    
    def organize_images(self) -> Tuple[int, int]:
        """
        Organiza las imágenes en las carpetas correspondientes.
        
        Returns:
            Tuple[int, int]: (imágenes regulares procesadas, imágenes de calibración procesadas)
        """
        regular_count = 0
        calibration_count = 0
        
        # Procesar carpetas RED y BLUE
        for source_folder in [self.red_dir, self.blue_dir]:
            if not source_folder.exists():
                continue
                
            images = self.get_all_images(source_folder)
            
            for image_path in images:
                try:
                    if self.is_calibration_image(image_path):
                        # Es imagen de calibración
                        dest_path = self.calibration_dir / image_path.name
                        shutil.copy2(image_path, dest_path)
                        calibration_count += 1
                        logging.debug(f"Calibración: {image_path.name} → calibration/")
                    else:
                        # Es imagen regular
                        # Crear nombre único para evitar conflictos
                        new_name = f"{image_path.name}"
                        dest_path = self.photos_dir / new_name
                        shutil.copy2(image_path, dest_path)
                        regular_count += 1
                        logging.debug(f"Regular: {image_path.name} → photos/{new_name}")
                        
                except Exception as e:
                    logging.error(f"Error procesando {image_path}: {e}")
        
        return regular_count, calibration_count
    
    def organize_dat_files(self) -> int:
        """
        Organiza los archivos .dat en la carpeta dat_files.
        
        Returns:
            int: Número de archivos .dat procesados
        """
        dat_files = list(self.base_dir.rglob("*.dat"))
        dat_count = 0
        
        for dat_file in dat_files:
            try:
                dest_path = self.dat_files_dir / dat_file.name
                shutil.move(str(dat_file), str(dest_path))
                dat_count += 1
                logging.debug(f"DAT: {dat_file.name} → dat_files/")
            except Exception as e:
                logging.error(f"Error moviendo {dat_file}: {e}")
        
        return dat_count
    
    def cleanup_empty_folders(self) -> None:
        """Elimina las carpetas RED y BLUE si están vacías después de la organización."""
        folders_to_check = [self.red_dir, self.blue_dir]
        
        for folder in folders_to_check:
            if folder.exists():
                try:
                    # Verificar si la carpeta está vacía (incluyendo subcarpetas)
                    if not any(folder.rglob('*')):
                        shutil.rmtree(folder)
                        logging.info(f"✓ Carpeta vacía eliminada: {folder.name}")
                    else:
                        logging.info(f"La carpeta {folder.name} no está vacía, se mantiene")
                except Exception as e:
                    logging.warning(f"No se pudo eliminar {folder.name}: {e}")
    
    def generate_report(self, regular_images: int, calibration_images: int, dat_files: int) -> None:
        """
        Genera un reporte final de la organización.
        
        Args:
            regular_images (int): Número de imágenes regulares procesadas
            calibration_images (int): Número de imágenes de calibración procesadas
            dat_files (int): Número de archivos .dat procesados
        """
        print("\n" + "="*60)
        print("REPORTE FINAL DE ORGANIZACIÓN")
        print("="*60)
        print(f"📁 Imágenes regulares procesadas: {regular_images}")
        print(f"🔧 Imágenes de calibración procesadas: {calibration_images}")
        print(f"📄 Archivos .dat procesados: {dat_files}")
        print(f"📍 Directorio base: {self.base_dir}")
        print("\nEstructura final:")
        print(f"├── photos/ ({regular_images} archivos)")
        print(f"├── calibration/ ({calibration_images} archivos)")
        print(f"└── dat_files/ ({dat_files} archivos)")
        print(f"└── discard_images")
        print("="*60)
        
        # Verificar si se encontraron todas las imágenes de calibración esperadas
        if calibration_images < 11:
            print(f"⚠️  ADVERTENCIA: Se esperaban 11 imágenes de calibración, pero solo se encontraron {calibration_images}")
        elif calibration_images == 11:
            print("✅ Se encontraron todas las imágenes de calibración esperadas (11)")
    
    def run(self) -> bool:
        """
        Ejecuta el proceso completo de organización.
        
        Returns:
            bool: True si la organización fue exitosa
        """
        try:
            print("Iniciando organización de archivos multiespectrales...")
            
            # Validar estructura inicial
            if not self.validate_structure():
                return False
            
            # Crear carpetas de destino
            self.create_destination_folders()
            
            # Organizar imágenes
            print("Organizando imágenes...")
            regular_count, calibration_count = self.organize_images()
            
            # Organizar archivos .dat
            print("Organizando archivos .dat...")
            dat_count = self.organize_dat_files()
            
            # Limpiar carpetas vacías (opcional)
            print("Limpiando carpetas vacías...")
            self.cleanup_empty_folders()
            
            # Generar reporte
            self.generate_report(regular_count, calibration_count, dat_count)
            
            print("✅ ¡Organización completada exitosamente!")
            return True
            
        except Exception as e:
            logging.error(f"Error durante la organización: {e}")
            print(f"❌ Error: {e}")
            return False


def main():
    """Función principal."""
    # Permitir especificar directorio como argumento
    import sys
    
    if len(sys.argv) > 1:
        base_directory = sys.argv[1]
    else:
        base_directory = "."
    
    print("="*60)
    print("ORGANIZADOR DE IMÁGENES MULTIESPECTRALES - MICASENSE")
    print("="*60)
    
    # Crear instancia del organizador
    organizer = MultispectralOrganizer(base_directory)
    
    # Ejecutar organización
    success = organizer.run()
    
    if success:
        print("\n🎉 Proceso completado. Detalles del proceso en el archivo 'file_organizer.log'")
    else:
        print("\n❌ El proceso no se completó correctamente. Revise los errores en el log.")
    
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())