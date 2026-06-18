"""
Модуль для объединения PDF-файлов в один с приведением всех страниц
к формату A4 (книжная ориентация). Содержимое страниц масштабируется
с сохранением пропорций и центрируется.

Требуется библиотека pypdf:
    pip install pypdf

Использование как библиотека:
    from pydfA4 import merge_pdfs_to_a4
    merge_pdfs_to_a4(["file1.pdf", "file2.pdf"], "output.pdf")

Использование из командной строки:
    python pydfA4.py file1.pdf file2.pdf -o merged.pdf
"""

import sys
from pathlib import Path
from typing import List

try:
    from pypdf import PdfReader, PdfWriter, Transformation, PageObject
except ImportError:
    print("Ошибка: требуется библиотека pypdf. Установите её: pip install pypdf")
    sys.exit(1)

# Размер A4 в пунктах (portrait)
A4_WIDTH = 595.28
A4_HEIGHT = 841.89


def _scale_page_to_a4(page: PageObject) -> PageObject:
    """
    Возвращает новую страницу формата A4, на которую наложено
    содержимое исходной страницы с масштабированием до вписывания
    и центрированием.
    """
    # Получаем размеры исходного медиабокса (без учёта поворота)
    w = float(page.mediabox.width)
    h = float(page.mediabox.height)

    # Учитываем поворот страницы для определения логической ширины/высоты
    rotation = page.get('/Rotate', 0)
    if rotation in (90, 270):
        w, h = h, w

    # Если уже точно A4, можно вернуть без изменений (опционально)
    if abs(w - A4_WIDTH) < 0.1 and abs(h - A4_HEIGHT) < 0.1:
        return page

    # Коэффициент масштабирования, чтобы вписать в A4 с сохранением пропорций
    scale = min(A4_WIDTH / w, A4_HEIGHT / h) if w > 0 and h > 0 else 1.0

    # Размеры после масштабирования
    new_w = w * scale
    new_h = h * scale

    # Смещение для центрирования
    tx = (A4_WIDTH - new_w) / 2
    ty = (A4_HEIGHT - new_h) / 2

    # Создаём чистую A4-страницу и накладываем на неё исходную с трансформацией
    new_page = PageObject.create_blank_page(width=A4_WIDTH, height=A4_HEIGHT)
    transform = Transformation().scale(scale).translate(tx, ty)
    new_page.merge_transformed_page(page, transform)

    return new_page


def merge_pdfs_to_a4(
    input_files: List[str],
    output_file: str,
    skip_errors: bool = True,
) -> bool:
    """
    Объединяет PDF-файлы в один, приводя все страницы к формату A4 (книжный).

    Аргументы:
        input_files: список путей к PDF-файлам.
        output_file: путь к результирующему PDF-файлу.
        skip_errors: если True, повреждённые или защищённые файлы пропускаются
                     с предупреждением. При False ошибка прерывает работу.

    Возвращает:
        True в случае успеха (добавлена хотя бы одна страница), иначе False.
    """
    if not input_files:
        print("Список входных файлов пуст.")
        return False

    writer = PdfWriter()
    pages_added = 0

    for file_path in input_files:
        path = Path(file_path)
        if not path.is_file():
            msg = f"Файл не найден: {file_path}"
            if skip_errors:
                print(f"Предупреждение: {msg} Пропускаем.")
                continue
            raise FileNotFoundError(msg)

        try:
            reader = PdfReader(str(path))
            if reader.is_encrypted:
                try:
                    reader.decrypt("")
                except Exception as e:
                    msg = f"Не удалось расшифровать {file_path}: {e}"
                    if skip_errors:
                        print(f"Предупреждение: {msg} Пропускаем.")
                        continue
                    raise RuntimeError(msg) from e

            num_pages = len(reader.pages)
            if num_pages == 0:
                print(f"Предупреждение: файл {file_path} не содержит страниц. Пропускаем.")
                continue

            for page in reader.pages:
                scaled_page = _scale_page_to_a4(page)
                writer.add_page(scaled_page)
                pages_added += 1

            print(f"Добавлен файл: {file_path} ({num_pages} стр.)")

        except Exception as e:
            msg = f"Ошибка при обработке {file_path}: {e}"
            if skip_errors:
                print(f"Предупреждение: {msg} Пропускаем.")
                continue
            raise RuntimeError(msg) from e

    if pages_added == 0:
        print("Не удалось добавить ни одной страницы. Выходной файл не создан.")
        return False

    try:
        with open(output_file, "wb") as f:
            writer.write(f)
        print(f"Объединение завершено. Сохранён файл: {output_file} (всего страниц: {pages_added})")
        return True
    except Exception as e:
        print(f"Ошибка при записи выходного файла: {e}")
        return False


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Объединить PDF-файлы в один, приводя страницы к A4 (книжный)."
    )
    parser.add_argument(
        "files",
        nargs="+",
        help="Список PDF-файлов для объединения в нужном порядке.",
    )
    parser.add_argument(
        "-o", "--output",
        default="merged_a4.pdf",
        help="Имя выходного PDF-файла (по умолчанию: merged_a4.pdf).",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Прерывать выполнение при первой ошибке чтения файла.",
    )

    args = parser.parse_args()

    success = merge_pdfs_to_a4(
        input_files=args.files,
        output_file=args.output,
        skip_errors=not args.strict,
    )
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
