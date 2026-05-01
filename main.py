import tkinter as tk
from tkinter import ttk, messagebox
import random
import json
import os
from datetime import datetime

class RandomTaskGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Random Task Generator")
        self.root.geometry("650x550")
        self.root.resizable(True, True)

        # Предопределённые задачи с типами
        self.default_tasks = [
            {"text": "Прочитать статью по Python", "type": "учёба"},
            {"text": "Сделать зарядку 15 минут", "type": "спорт"},
            {"text": "Написать отчёт по работе", "type": "работа"},
            {"text": "Посмотреть лекцию по машинному обучению", "type": "учёба"},
            {"text": "Пробежка 3 км", "type": "спорт"},
            {"text": "Созвониться с клиентом", "type": "работа"},
            {"text": "Прочитать главу из книги", "type": "учёба"},
            {"text": "Йога или растяжка", "type": "спорт"},
            {"text": "Запланировать задачи на неделю", "type": "работа"},
            {"text": "Решить 5 задач на LeetCode", "type": "учёба"},
            {"text": "Отжимания 30 раз", "type": "спорт"},
            {"text": "Подготовить презентацию", "type": "работа"}
        ]

        # Загрузка задач и истории из файлов
        self.tasks_list = self.load_tasks()
        self.history = self.load_history()

        # Создание интерфейса
        self.create_widgets()

        # Обновление отображения
        self.update_task_display()
        self.update_history_display()

    def create_widgets(self):
        # === Верхняя панель с генерацией ===
        top_frame = tk.Frame(self.root, bg="#2c3e50", height=120)
        top_frame.pack(fill="x", padx=10, pady=5)
        top_frame.pack_propagate(False)

        self.btn_generate = tk.Button(top_frame, text="🎲 СГЕНЕРИРОВАТЬ ЗАДАЧУ", 
                                       command=self.generate_random_task,
                                       font=("Arial", 14, "bold"),
                                       bg="#3498db", fg="white",
                                       cursor="hand2", height=2)
        self.btn_generate.pack(pady=10)

        self.lbl_current_task = tk.Label(top_frame, text="Нажмите на кнопку выше", 
                                         font=("Arial", 12, "italic"),
                                         fg="#ecf0f1", bg="#2c3e50",
                                         wraplength=600)
        self.lbl_current_task.pack(pady=5)

        # === Панель фильтрации ===
        filter_frame = tk.LabelFrame(self.root, text="🔍 Фильтр по типу задач", 
                                      font=("Arial", 10, "bold"),
                                      padx=10, pady=5)
        filter_frame.pack(fill="x", padx=10, pady=5)

        self.filter_var = tk.StringVar(value="все")
        
        filter_buttons_frame = tk.Frame(filter_frame)
        filter_buttons_frame.pack()
        
        filters = [("📋 Все задачи", "все"), 
                   ("📚 Учёба", "учёба"), 
                   ("🏃 Спорт", "спорт"), 
                   ("💼 Работа", "работа")]
        
        for text, value in filters:
            rb = tk.Radiobutton(filter_buttons_frame, text=text, 
                                 variable=self.filter_var, 
                                 value=value,
                                 command=self.update_task_display,
                                 font=("Arial", 10))
            rb.pack(side="left", padx=10, pady=5)

        # === Список доступных задач ===
        tasks_frame = tk.LabelFrame(self.root, text="📝 Мои задачи", 
                                     font=("Arial", 10, "bold"),
                                     padx=5, pady=5)
        tasks_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Listbox с прокруткой
        scrollbar_tasks = tk.Scrollbar(tasks_frame)
        scrollbar_tasks.pack(side="right", fill="y")

        self.tasks_listbox = tk.Listbox(tasks_frame, 
                                         yscrollcommand=scrollbar_tasks.set,
                                         font=("Arial", 10),
                                         height=6,
                                         selectmode=tk.SINGLE)
        self.tasks_listbox.pack(fill="both", expand=True)
        scrollbar_tasks.config(command=self.tasks_listbox.yview)

        # Кнопки управления задачами
        task_buttons_frame = tk.Frame(tasks_frame)
        task_buttons_frame.pack(fill="x", pady=5)

        tk.Button(task_buttons_frame, text="➕ Добавить задачу", 
                  command=self.add_task,
                  bg="#27ae60", fg="white",
                  cursor="hand2").pack(side="left", padx=5)
        
        tk.Button(task_buttons_frame, text="✖️ Удалить задачу", 
                  command=self.delete_task,
                  bg="#e74c3c", fg="white",
                  cursor="hand2").pack(side="left", padx=5)
        
        tk.Button(task_buttons_frame, text="💾 Сохранить все задачи", 
                  command=self.save_tasks_to_file,
                  bg="#f39c12", fg="white",
                  cursor="hand2").pack(side="left", padx=5)

        # === История задач ===
        history_frame = tk.LabelFrame(self.root, text="📜 История сгенерированных задач", 
                                       font=("Arial", 10, "bold"),
                                       padx=5, pady=5)
        history_frame.pack(fill="both", expand=True, padx=10, pady=5)

        scrollbar_history = tk.Scrollbar(history_frame)
        scrollbar_history.pack(side="right", fill="y")

        self.history_listbox = tk.Listbox(history_frame,
                                           yscrollcommand=scrollbar_history.set,
                                           font=("Arial", 9),
                                           height=6,
                                           fg="#2c3e50")
        self.history_listbox.pack(fill="both", expand=True)
        scrollbar_history.config(command=self.history_listbox.yview)

        # Кнопки управления историей
        history_buttons_frame = tk.Frame(history_frame)
        history_buttons_frame.pack(fill="x", pady=5)

        tk.Button(history_buttons_frame, text="🗑 Очистить историю", 
                  command=self.clear_history,
                  bg="#95a5a6", fg="white",
                  cursor="hand2").pack(side="right", padx=5)

        # Статусная строка
        self.status_bar = tk.Label(self.root, text="Готов к работе", 
                                    bd=1, relief=tk.SUNKEN, 
                                    anchor=tk.W,
                                    font=("Arial", 8))
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def load_tasks(self):
        """Загрузка задач из JSON или создание с дефолтными"""
        if os.path.exists("tasks.json"):
            try:
                with open("tasks.json", "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return self.default_tasks.copy()
        else:
            return self.default_tasks.copy()

    def save_tasks_to_file(self):
        """Сохранение задач в JSON"""
        try:
            with open("tasks.json", "w", encoding="utf-8") as f:
                json.dump(self.tasks_list, f, ensure_ascii=False, indent=2)
            self.status_bar.config(text=f"✅ Задачи сохранены в tasks.json ({len(self.tasks_list)} задач)")
            messagebox.showinfo("Успех", f"Сохранено {len(self.tasks_list)} задач в файл tasks.json")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить задачи: {str(e)}")

    def load_history(self):
        """Загрузка истории из JSON"""
        if os.path.exists("history.json"):
            try:
                with open("history.json", "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return []
        return []

    def save_history(self):
        """Сохранение истории в JSON"""
        try:
            with open("history.json", "w", encoding="utf-8") as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить историю: {str(e)}")

    def update_task_display(self):
        """Обновление списка задач с учётом фильтра"""
        self.tasks_listbox.delete(0, tk.END)
        filter_type = self.filter_var.get()
        
        filtered_count = 0
        for task in self.tasks_list:
            if filter_type == "все" or task["type"] == filter_type:
                # Эмодзи для типов
                type_emoji = {"учёба": "📚", "спорт": "🏃", "работа": "💼"}
                emoji = type_emoji.get(task["type"], "📌")
                display_text = f"{emoji} [{task['type']}] {task['text']}"
                self.tasks_listbox.insert(tk.END, display_text)
                filtered_count += 1
        
        self.status_bar.config(text=f"Показано задач: {filtered_count} из {len(self.tasks_list)} (фильтр: {filter_type})")

    def update_history_display(self):
        """Обновление отображения истории"""
        self.history_listbox.delete(0, tk.END)
        for entry in reversed(self.history):  # Новые сверху
            self.history_listbox.insert(tk.END, entry)
        
        self.status_bar.config(text=f"История содержит {len(self.history)} записей")

    def generate_random_task(self):
        """Генерация случайной задачи и добавление в историю"""
        if not self.tasks_list:
            messagebox.showwarning("Нет задач", 
                                  "Список задач пуст!\nДобавьте хотя бы одну задачу через кнопку 'Добавить задачу'")
            return

        filter_type = self.filter_var.get()
        
        if filter_type != "все":
            filtered_tasks = [t for t in self.tasks_list if t["type"] == filter_type]
            if not filtered_tasks:
                messagebox.showwarning("Нет задач", 
                                      f"Нет задач типа '{filter_type}'\nИзмените фильтр или добавьте новые задачи")
                return
            selected_task = random.choice(filtered_tasks)
        else:
            selected_task = random.choice(self.tasks_list)

        task_text = selected_task["text"]
        task_type = selected_task["type"]
        
        # Эмодзи для типа
        type_emoji = {"учёба": "📚", "спорт": "🏃", "работа": "💼"}
        emoji = type_emoji.get(task_type, "✅")
        
        # Формирование строки истории с временем
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        history_entry = f"{timestamp}  {emoji}  [{task_type}]  {task_text}"
        
        self.history.append(history_entry)
        self.save_history()
        self.update_history_display()
        
        # Отображение текущей задачи
        self.lbl_current_task.config(text=f"{emoji}  {task_text}  [{task_type}]", 
                                     fg="#f1c40f")
        
        self.status_bar.config(text=f"✅ Сгенерирована задача: {task_text}")
        
        # Визуальный эффект на кнопке
        self.btn_generate.config(bg="#2ecc71")
        self.root.after(200, lambda: self.btn_generate.config(bg="#3498db"))

    def add_task(self):
        """Диалог добавления новой задачи с проверкой ввода"""
        dialog = tk.Toplevel(self.root)
        dialog.title("➕ Добавление новой задачи")
        dialog.geometry("450x250")
        dialog.resizable(False, False)
        
        # Центрирование окна
        dialog.transient(self.root)
        dialog.grab_set()
        
        tk.Label(dialog, text="Введите текст задачи:", 
                font=("Arial", 10, "bold")).pack(pady=(20, 5))
        
        entry_text = tk.Entry(dialog, width=50, font=("Arial", 10))
        entry_text.pack(pady=5, padx=20)
        entry_text.focus()
        
        tk.Label(dialog, text="Выберите тип задачи:", 
                font=("Arial", 10, "bold")).pack(pady=(15, 5))
        
        type_var = tk.StringVar(value="учёба")
        types_frame = tk.Frame(dialog)
        types_frame.pack(pady=5)
        
        # Типы с эмодзи
        types = [("📚 Учёба", "учёба"), ("🏃 Спорт", "спорт"), ("💼 Работа", "работа")]
        for text, value in types:
            rb = tk.Radiobutton(types_frame, text=text, 
                                variable=type_var, value=value,
                                font=("Arial", 10))
            rb.pack(side="left", padx=15)
        
        def on_add():
            task_text = entry_text.get().strip()
            if not task_text:
                messagebox.showerror("Ошибка", "Текст задачи не может быть пустым!")
                return
            
            if len(task_text) < 3:
                messagebox.showerror("Ошибка", "Текст задачи слишком короткий (минимум 3 символа)")
                return
            
            self.tasks_list.append({"text": task_text, "type": type_var.get()})
            self.save_tasks_to_file()
            self.update_task_display()
            dialog.destroy()
            self.status_bar.config(text=f"✅ Добавлена задача: {task_text}")
            messagebox.showinfo("Успех", f"Задача '{task_text}' успешно добавлена!")
        
        button_frame = tk.Frame(dialog)
        button_frame.pack(pady=20)
        
        tk.Button(button_frame, text="✅ Добавить", command=on_add,
                 bg="#27ae60", fg="white", font=("Arial", 10, "bold"),
                 cursor="hand2", padx=20).pack(side="left", padx=10)
        
        tk.Button(button_frame, text="❌ Отмена", command=dialog.destroy,
                 bg="#95a5a6", fg="white", font=("Arial", 10),
                 cursor="hand2", padx=20).pack(side="left", padx=10)

    def delete_task(self):
        """Удаление выбранной задачи из списка"""
        selection = self.tasks_listbox.curselection()
        if not selection:
            messagebox.showwarning("Внимание", "Сначала выберите задачу для удаления")
            return
        
        # Получаем отображаемую строку
        display_text = self.tasks_listbox.get(selection[0])
        
        # Парсим "[тип] текст" (с эмодзи)
        # Убираем эмодзи в начале
        if " " in display_text:
            parts = display_text.split(" ", 1)
            if len(parts) > 1:
                rest = parts[1]
                if rest.startswith("[") and "] " in rest:
                    bracket_end = rest.find("] ")
                    task_type = rest[1:bracket_end]
                    task_text = rest[bracket_end + 2:]
                else:
                    return
            else:
                return
        else:
            return
        
        # Подтверждение удаления
        if not messagebox.askyesno("Подтверждение", 
                                   f"Удалить задачу?\n\n'{task_text}'\nТип: {task_type}"):
            return
        
        # Ищем и удаляем задачу в списке
        for i, task in enumerate(self.tasks_list):
            if task["text"] == task_text and task["type"] == task_type:
                del self.tasks_list[i]
                break
        
        self.save_tasks_to_file()
        self.update_task_display()
        self.status_bar.config(text=f"🗑 Удалена задача: {task_text}")
        messagebox.showinfo("Успех", "Задача удалена!")

    def clear_history(self):
        """Очистка истории"""
        if not self.history:
            messagebox.showinfo("Информация", "История и так пуста")
            return
        
        if messagebox.askyesno("Подтверждение очистки", 
                              f"Вы уверены, что хотите очистить всю историю?\n\nВсего записей: {len(self.history)}"):
            self.history = []
            self.save_history()
            self.update_history_display()
            self.lbl_current_task.config(text="История очищена", fg="#ecf0f1")
            self.status_bar.config(text="🗑 История полностью очищена")
            messagebox.showinfo("Успех", "История очищена!")

if __name__ == "__main__":
    root = tk.Tk()
    
    # Установка иконки окна (если есть файл, иначе стандартная)
    try:
        root.iconbitmap("icon.ico")
    except:
        pass
    
    app = RandomTaskGenerator(root)
    
    # Центрирование окна на экране
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    root.mainloop()