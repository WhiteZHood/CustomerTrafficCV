import os
import re
from pathlib import Path
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from utils.paths import project_path


class ImageRenamerApp:
    def __init__(self, folder):
        self.folder = Path(folder)
        self.pattern = re.compile(r"(\d{4}_\d{2}_\d{2}_[A-Za-z]+)")
        self.files = sorted([
            f for f in self.folder.iterdir()
            if f.is_file() and f.suffix.lower() in ['.jpg', '.jpeg', '.png']
            and self.pattern.search(f.stem)
        ])
        self.index = 0

        self.root = tk.Tk()
        self.root.title("Ручное переименование изображений")

        self.image_label = tk.Label(self.root)
        self.image_label.pack()

        # Поля времени
        time_frame = tk.Frame(self.root)
        time_frame.pack(pady=10)

        self.hh_entry = tk.Entry(time_frame, width=3, font=('Arial', 16), justify='center')
        self.mm_entry = tk.Entry(time_frame, width=3, font=('Arial', 16), justify='center')
        self.ss_entry = tk.Entry(time_frame, width=3, font=('Arial', 16), justify='center')

        self.hh_entry.grid(row=0, column=0, padx=5)
        self.mm_entry.grid(row=0, column=1, padx=5)
        self.ss_entry.grid(row=0, column=2, padx=5)

        self.entries = [self.hh_entry, self.mm_entry, self.ss_entry]
        placeholders = ["чч", "мм", "cc"]

        for i, entry in enumerate(self.entries):
            entry.insert(0, placeholders[i])
            entry.bind("<FocusIn>", lambda e, ent=entry, ph=placeholders[i]: self.clear_placeholder(ent, ph))
            entry.bind("<Return>", lambda e: self.rename_current())
            entry.bind("<KeyRelease>", lambda e, idx=i: self.auto_advance(idx))
            entry.bind("<Left>", lambda e, idx=i: self.handle_left_arrow(e, idx))
            entry.bind("<Right>", lambda e, idx=i: self.handle_right_arrow(e, idx))

        self.rename_button = tk.Button(self.root, text="Переименовать", command=self.rename_current)
        self.rename_button.pack()

        self.status_label = tk.Label(self.root, text="")
        self.status_label.pack(pady=5)

        self.show_image()
        self.root.mainloop()
    
    def restrict_to_digits(self, event):
        if event.char.isdigit():
            widget = event.widget
            if len(widget.get()) >= 2:   # Блокируем ввод после 2 цифр
                return "break"
            widget.insert(tk.END, event.char)
            self.advance_if_full(widget)
            return "break"
        elif event.keysym in ["BackSpace", "Left", "Right", "Tab"]:
            return
        return "break"


    def clear_placeholder(self, entry, placeholder):
        if entry.get() == placeholder:
            entry.delete(0, tk.END)

    def auto_advance(self, index):
        entry = self.entries[index]
        if len(entry.get()) >= 2:
            if index + 1 < len(self.entries):
                self.entries[index + 1].focus()

    def handle_left_arrow(self, event, index):
        entry = self.entries[index]
        if entry.index(tk.INSERT) == 0 and index > 0:
            self.entries[index - 1].focus()

    def handle_right_arrow(self, event, index):
        entry = self.entries[index]
        if entry.index(tk.INSERT) == len(entry.get()) and index + 1 < len(self.entries):
            self.entries[index + 1].focus()

    def show_image(self):
        if self.index >= len(self.files):
            self.image_label.config(image='')
            self.status_label.config(text="Готово! Все изображения обработаны.")
            self.rename_button.config(state="disabled")
            return

        self.current_file = self.files[self.index]
        img = Image.open(self.current_file)
        img.thumbnail((800, 600))
        self.tk_image = ImageTk.PhotoImage(img)
        self.image_label.config(image=self.tk_image)
        self.status_label.config(text=f"Файл: {self.current_file.name}")

        # Сброс полей
        for entry, placeholder in zip(self.entries, ["чч", "мм", "cc"]):
            entry.delete(0, tk.END)
            entry.insert(0, placeholder)
        self.hh_entry.focus()

    def rename_current(self):
        values = [entry.get().strip() for entry in self.entries]
        if not all(val.isdigit() and len(val) == 2 for val in values):
            messagebox.showerror("Ошибка", "Введите корректное время: по 2 цифры в каждом поле (чч мм cc)")
            return

        manual_time = "_".join(values)
        match = self.pattern.search(self.current_file.stem)
        if not match:
            messagebox.showerror("Ошибка", f"Неверный формат имени файла: {self.current_file.name}")
            return

        date_part = match.group(1)
        base_name = f"{date_part}_{manual_time}"
        ext = self.current_file.suffix.lower()

        new_path = self.current_file.with_name(base_name + ext)
        
        if new_path.exists():
            count = 1
            while True:
                repeated_name = f"{base_name}_repeated{count if count > 1 else ''}{ext}"
                repeated_path = self.current_file.with_name(repeated_name)
                if not repeated_path.exists():
                    new_path = repeated_path
                    break
                count += 1
            messagebox.showwarning("Повтор имени", f"Файл с таким именем существует, переименование с суффиксом:\n{new_path.name}")

        os.rename(self.current_file, new_path)
        self.index += 1
        self.show_image()


if __name__ == "__main__":
    ImageRenamerApp(str(project_path("data/images/March_week_img/2025_03_26_Wed")))
