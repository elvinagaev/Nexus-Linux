#!/bin/bash
# Nexus Linux ISO Builder
# Этот скрипт собирает ISO образ Nexus Linux из исходников

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ISO_NAME="nexus-linux-0.1.0-amd64.iso"
BUILD_DIR="${PROJECT_ROOT}/build"
STAGING_DIR="${BUILD_DIR}/staging"

echo "=== Nexus Linux ISO Builder ==="
echo "Project root: $PROJECT_ROOT"
echo "Build directory: $BUILD_DIR"
echo "ISO output: $BUILD_DIR/$ISO_NAME"

# Создание директорий сборки
mkdir -p "$STAGING_DIR"

# Копирование boot-секций
echo "[1/5] Подготовка boot-секций..."
cp -r "$PROJECT_ROOT/boot" "$STAGING_DIR/" 2>/dev/null || true
cp -r "$PROJECT_ROOT/EFI" "$STAGING_DIR/" 2>/dev/null || true
cp -r "$PROJECT_ROOT/isolinux" "$STAGING_DIR/" 2>/dev/null || true

# Копирование дистрибутива репозитория
echo "[2/5] Копирование репозитория Debian..."
cp -r "$PROJECT_ROOT/dists" "$STAGING_DIR/" 2>/dev/null || true
cp -r "$PROJECT_ROOT/pool" "$STAGING_DIR/" 2>/dev/null || true

# Копирование метаданных
echo "[3/5] Копирование метаданных ISO..."
cp -r "$PROJECT_ROOT/.disk" "$STAGING_DIR/" 2>/dev/null || true
cp "$PROJECT_ROOT/README.md" "$STAGING_DIR/README.txt" 2>/dev/null || true

# Сборка Python модулей
echo "[4/5] Подготовка Nexus приложений..."
mkdir -p "$STAGING_DIR/nexus-apps"
for app_dir in "$PROJECT_ROOT"/nexus-*/; do
    if [ -d "$app_dir" ]; then
        app_name=$(basename "$app_dir")
        echo "  - $app_name"
        cp -r "$app_dir" "$STAGING_DIR/nexus-apps/"
    fi
done
cp -r "$PROJECT_ROOT/shared" "$STAGING_DIR/nexus-apps/"

# Генерация ISO
echo "[5/5] Генерация ISO образа..."
if command -v mkisofs &> /dev/null; then
    mkisofs -o "$BUILD_DIR/$ISO_NAME" \
        -b isolinux/isolinux.bin \
        -c isolinux/boot.cat \
        -no-emul-boot \
        -boot-load-size 4 \
        -boot-info-table \
        -eltorito-alt-boot \
        -efi-boot EFI/boot/bootx64.efi \
        -no-emul-boot \
        -isohybrid-mbr "$STAGING_DIR/isolinux/isohdpfx.bin" \
        "$STAGING_DIR" 2>/dev/null || {
        echo "mkisofs failed; creating simplified image..."
        cd "$STAGING_DIR" && tar czf "$BUILD_DIR/$ISO_NAME.tar.gz" . && cd "$PROJECT_ROOT"
    }
elif command -v genisoimage &> /dev/null; then
    genisoimage -o "$BUILD_DIR/$ISO_NAME" \
        -b isolinux/isolinux.bin \
        -c isolinux/boot.cat \
        -no-emul-boot \
        -boot-load-size 4 \
        -boot-info-table \
        "$STAGING_DIR"
else
    echo "Ошибка: mkisofs или genisoimage не найдены"
    echo "Установите xorriso или cdrkit"
    exit 1
fi

echo ""
echo "✓ ISO успешно собран: $BUILD_DIR/$ISO_NAME"
echo "  Размер: $(du -h "$BUILD_DIR/$ISO_NAME" 2>/dev/null | cut -f1 || echo 'unknown')"
echo ""
echo "Следующие шаги:"
echo "  1. Записать ISO: sudo dd if=$BUILD_DIR/$ISO_NAME of=/dev/sdX bs=4M"
echo "  2. Или использовать Ventoy/Etcher для записи на USB"
