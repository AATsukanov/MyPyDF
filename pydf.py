"""
Модуль для объединения нескольких PDF-файлов в один с сохранением
оригинального содержимого страниц.

Требуется установка библиотеки pypdf:
    pip install pypdf

Использование как библиотека:
    from pydf import merge_pdfs
    merge_pdfs(["file1.pdf", "file2.pdf"], "output.pdf")

Использование из командной строки:
    python pydf.py file1.pdf file2.pdf -o merged.pdf
"""

import sys
from pathlib import Path
from typing import List
# from typing import Optional
# import pypdf
try:
    from pypdf import PdfReader, PdfWriter
except ImportError:
    print("Ошибка: требуется библиотека pypdf. Установите её: pip install pypdf")
    sys.exit(1)


def merge_pdfs(
    input_files: List[str],
    output_file: str,
    skip_errors: bool = True,
) -> bool:
    """
    Объединяет PDF-файлы из списка input_files в один выходной файл output_file.

    Аргументы:
        input_files: список путей к PDF-файлам.
        output_file: путь к результирующему PDF-файлу.
        skip_errors: если True, то при ошибке чтения файла он пропускается
                     и выводится предупреждение. При False ошибка вызывает исключение.

    Возвращает:
        True, если объединение прошло успешно (хотя бы одна страница добавлена),
        иначе False.
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
            # Проверяем, не зашифрован ли файл (если да, пытаемся расшифровать пустым паролем)
            if reader.is_encrypted:
                try:
                    reader.decrypt("")
                except Exception as e:
                    msg = f"Не удалось расшифровать файл {file_path}: {e}"
                    if skip_errors:
                        print(f"Предупреждение: {msg} Пропускаем.")
                        continue
                    raise RuntimeError(msg) from e

            num_pages = len(reader.pages)
            if num_pages == 0:
                print(f"Предупреждение: файл {file_path} не содержит страниц. Пропускаем.")
                continue

            for page in reader.pages:
                writer.add_page(page)
            pages_added += num_pages
            print(f"Добавлен файл: {file_path} ({num_pages} стр.)")

        except Exception as e:
            msg = f"Ошибка при обработке файла {file_path}: {e}"
            if skip_errors:
                print(f"Предупреждение: {msg} Пропускаем.")
                continue
            raise RuntimeError(msg) from e

    if pages_added == 0:
        print("Не удалось добавить ни одной страницы. Выходной файл не создан.")
        return False

    try:
        with open(output_file, "wb") as out_f:
            writer.write(out_f)
        print(f"Объединение завершено. Создан файл: {output_file} (всего страниц: {pages_added})")
        return True
    except Exception as e:
        print(f"Ошибка при записи выходного файла: {e}")
        return False


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Объединить несколько PDF-файлов в один, сохраняя содержимое страниц."
    )
    parser.add_argument(
        "files",
        nargs="+",
        help="Список PDF-файлов для объединения в нужном порядке.",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="merged.pdf",
        help="Имя выходного PDF-файла (по умолчанию: merged.pdf).",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Прерывать выполнение при первой ошибке чтения файла.",
    )

    args = parser.parse_args()

    success = merge_pdfs(
        input_files=args.files,
        output_file=args.output,
        skip_errors=not args.strict,
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
