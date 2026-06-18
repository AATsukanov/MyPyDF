import tkinter as tk
from tkinter import filedialog, messagebox
from datetime import datetime
# импорт из своего модуля:
from pydf import merge_pdfs
from pydfA4 import merge_pdfs_to_a4

MAXFILES: int = 10  # максимальное количество выбираемых файлов

class PDFCombinerApp:
    """Графический интерфейс для выбора PDF-файлов и вывода их списка."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title('Tsukanov Lab. "PyDF Combiner"')
        self.entries: list[tk.Entry] = []  # список полей ввода

        lbl = tk.Label(root, text="Выбор PDF файлов для слияния в один:", anchor="nw")
        lbl.pack(side=tk.TOP, pady=5)

        # Создаём MAXFILES строк с полем ввода и кнопкой "Выбрать"
        for i in range(MAXFILES):
            frame = tk.Frame(root)
            frame.pack(fill=tk.X, padx=5, pady=2)

            # Метка с номером файла
            lbl = tk.Label(frame, text=f"Файл {i+1}:", width=8, anchor="w")
            lbl.pack(side=tk.LEFT)

            # Длинное поле ввода
            entry = tk.Entry(frame, width=80)
            entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

            # Кнопка выбора файла (замыкание с фиксацией индекса)
            btn = tk.Button(frame, text="Выбрать",
                            command=lambda idx=i: self.select_file(idx))
            btn.pack(side=tk.LEFT, padx=(5, 0))

            self.entries.append(entry)

        # Фрейм для нижних кнопок
        bottom_frame = tk.Frame(root)
        bottom_frame.pack(pady=10)

        # Кнопка "Закрыть" слева
        btn_close = tk.Button(bottom_frame, text="Закрыть",
                              command=self.close, bg="lightcoral")
        btn_close.pack(side=tk.LEFT, padx=5)

        # Кнопки "Объединить..." справа от "Закрыть"
        btn_combine = tk.Button(bottom_frame, text="Объединить",
                                command=lambda: self.combine(fit_to_a4=False),
                                bg="lightblue")
        btn_combine.pack(side=tk.LEFT, padx=5)

        btn_combine_a4 = tk.Button(bottom_frame, text="Объединить в A4",
                                   command=lambda: self.combine(fit_to_a4=True))
        btn_combine_a4.pack(side=tk.LEFT, padx=5)


    def select_file(self, index: int) -> None:
        """Открывает диалог выбора PDF-файла и вставляет путь в поле с номером index."""
        filename = filedialog.askopenfilename(
            title=f"Выберите PDF-файл {index+1}",
            filetypes=[("PDF файлы", "*.pdf"), ("Все файлы", "*.*")]
        )
        if filename:
            self.entries[index].delete(0, tk.END)
            self.entries[index].insert(0, filename)

    def combine(self, fit_to_a4: bool, silence: bool = True) -> None:
        """Собирает непустые имена файлов в список и выводит его в консоль вместе с текущей датой/временем."""
        file_list = [e.get().strip() for e in self.entries if e.get().strip()]
        if not file_list:
            messagebox.showwarning("Предупреждение",
                                   "Не выбрано ни одного файла.")
            return

        # Количество исходных файлов:
        nf = len(file_list)

        # Имя выходного PDF-файла:
        datetime_str = datetime.now().strftime("%Y-%m-%d_%H-%M")
        fname = f'Combined_{nf}-in-1.{datetime_str}.pdf'

        fname = filedialog.asksaveasfilename(
            initialfile=fname,  # имя по умолчанию
            defaultextension=".pdf",  # автоматическое расширение, если не указано
            filetypes=[("PDF файлы", "*.pdf"), ("Все файлы", "*.*")],
            title="Сохранить PDF файл как"
        )

        if not fname:
            return

        # Вывод в консоль
        if not silence:
            print(f"Дата и время: {datetime_str}")
            print("Список выбранных файлов:")
            for f in file_list:
                print(f)
            print(f'Имя файла с результатом: {fname}')

        # Запускаем основную процедуру:
        if not fit_to_a4:
            merge_pdfs(file_list, fname)
        else:
            merge_pdfs_to_a4(file_list, fname)

        messagebox.showinfo("Готово", f"Проверьте результат в файле: {fname}.")

    def close(self) -> None:
        """Закрывает приложение."""
        self.root.destroy()


def main():
    root = tk.Tk()
    root.geometry("700x400")  # комфортный размер окна
    app = PDFCombinerApp(root)
    root.mainloop()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
