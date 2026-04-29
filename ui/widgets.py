import customtkinter as ctk
import calendar
import tkinter as tk
from datetime import datetime
from typing import Any, Callable


def create_frame(parent, **kwargs) -> ctk.CTkFrame:
    """Cria um frame com estilo padrão"""
    return ctk.CTkFrame(parent, **kwargs)


def create_label(parent, text: str, **kwargs) -> ctk.CTkLabel:
    """Cria um label com estilo padrão"""
    return ctk.CTkLabel(parent, text=text, **kwargs)


def create_entry(parent, **kwargs) -> ctk.CTkEntry:
    """Cria um entry com estilo padrão"""
    return ctk.CTkEntry(parent, **kwargs)


def create_button(parent, text: str, command=None, **kwargs) -> ctk.CTkButton:
    """Cria um button com estilo padrão"""
    return ctk.CTkButton(parent, text=text, command=command, **kwargs)


class DatePickerFrame(ctk.CTkFrame):
    """Widget customizado para seleção de data com calendário suspenso"""

    def __init__(self, parent, on_date_selected: Callable = None, **kwargs):
        super().__init__(parent, **kwargs)

        self.on_date_selected = on_date_selected
        self.selected_date = None
        self.calendar_window = None

        # Frame para o entrada e botão
        self.container = ctk.CTkFrame(self)
        self.container.pack(fill="x", expand=True)

        # Entry para exibir data
        self.date_entry = ctk.CTkEntry(
            self.container,
            width=200,
            placeholder_text="dd/mm/aaaa"
        )
        self.date_entry.pack(side="left", padx=(0, 5), fill="x", expand=True)

        # Botão para abrir calendário
        self.calendar_btn = ctk.CTkButton(
            self.container,
            text="📅",
            width=40,
            command=self.open_calendar
        )
        self.calendar_btn.pack(side="left")

    def open_calendar(self):
        """Abre uma janela com calendário para seleção de data"""
        if self.calendar_window is not None and self.calendar_window.winfo_exists():
            self.calendar_window.lift()
            return

        self.calendar_window = tk.Toplevel(self.master)
        self.calendar_window.title("Selecionar Data")
        self.calendar_window.geometry("400x400")
        self.calendar_window.resizable(False, False)
        self.calendar_window.protocol("WM_DELETE_WINDOW", self.close_calendar)

        # Obtém data atual ou data selecionada
        try:
            if self.date_entry.get():
                parts = self.date_entry.get().split('/')
                current_date = datetime(
                    int(parts[2]), int(parts[1]), int(parts[0]))
            else:
                current_date = datetime.now()
        except:
            current_date = datetime.now()

        # Frame para navegação de mês/ano
        nav_frame = tk.Frame(self.calendar_window, bg="#212121")
        nav_frame.pack(fill="x", padx=5, pady=5)

        # Variáveis para mês e ano
        self.current_month = tk.IntVar(value=current_date.month)
        self.current_year = tk.IntVar(value=current_date.year)

        # Botão voltar mês
        tk.Button(
            nav_frame,
            text="◀",
            command=lambda: self.change_month(-1),
            width=3
        ).pack(side="left")

        # Label mês/ano
        self.month_label = tk.Label(
            nav_frame, text="", width=15, bg="#212121", fg="white")
        self.month_label.pack(side="left", expand=True, padx=5)

        # Botão próximo mês
        tk.Button(
            nav_frame,
            text="▶",
            command=lambda: self.change_month(1),
            width=3
        ).pack(side="left")

        # Frame para o calendário
        calendar_frame = tk.Frame(self.calendar_window, bg="#212121")
        calendar_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Dias da semana
        days = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sab", "Dom"]
        for i, day in enumerate(days):
            tk.Label(
                calendar_frame,
                text=day,
                bg="#212121",
                fg="white",
                font=("Arial", 10, "bold"),
                width=5,
                height=2
            ).grid(row=0, column=i)

        self.calendar_frame = calendar_frame
        self.update_calendar()

        # Frame botões
        button_frame = tk.Frame(self.calendar_window, bg="#212121")
        button_frame.pack(fill="x", padx=5, pady=5)

        tk.Button(
            button_frame,
            text="Cancelar",
            command=self.close_calendar,
            width=15
        ).pack(side="left", padx=2)

        tk.Button(
            button_frame,
            text="OK",
            command=self.confirm_date,
            width=15
        ).pack(side="left", padx=2)

    def change_month(self, delta):
        """Muda o mês exibido"""
        month = self.current_month.get() + delta
        year = self.current_year.get()

        if month > 12:
            month = 1
            year += 1
        elif month < 1:
            month = 12
            year -= 1

        self.current_month.set(month)
        self.current_year.set(year)
        self.update_calendar()

    def update_calendar(self):
        """Atualiza o calendário exibido"""
        import calendar as cal

        # Limpar calendário anterior
        for widget in self.calendar_frame.grid_slaves():
            if widget.grid_info()['row'] > 0:
                widget.destroy()

        month = self.current_month.get()
        year = self.current_year.get()

        # Atualizar label
        months_pt = ["", "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
                     "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
        self.month_label.config(text=f"{months_pt[month]} {year}")

        # Obter dias do mês
        month_calendar = cal.monthcalendar(year, month)

        # Exibir dias
        row = 1
        for week in month_calendar:
            for col, day in enumerate(week):
                if day == 0:
                    bg = "#212121"
                    text = ""
                else:
                    bg = "#2a2a2a"
                    text = str(day)

                btn = tk.Button(
                    self.calendar_frame,
                    text=text,
                    bg=bg,
                    fg="white",
                    font=("Arial", 10),
                    width=5,
                    height=2,
                    command=lambda d=day: self.select_day(
                        d) if d != 0 else None
                )
                btn.grid(row=row, column=col, padx=1, pady=1)
            row += 1

    def select_day(self, day):
        """Seleciona um dia do calendário"""
        self.selected_date = datetime(
            self.current_year.get(),
            self.current_month.get(),
            day
        )
        self.date_entry.delete(0, "end")
        self.date_entry.insert(0, self.selected_date.strftime("%d/%m/%Y"))
        self.close_calendar()

        if self.on_date_selected:
            self.on_date_selected(self.selected_date.strftime("%d/%m/%Y"))

    def close_calendar(self):
        """Fecha a janela do calendário e limpa a referência"""
        if self.calendar_window:
            self.calendar_window.destroy()
            self.calendar_window = None

    def confirm_date(self):
        """Confirma a data selecionada"""
        if self.selected_date:
            self.date_entry.delete(0, "end")
            self.date_entry.insert(0, self.selected_date.strftime("%d/%m/%Y"))
        self.close_calendar()

    def get(self):
        """Retorna a data selecionada no formato dd/mm/aaaa"""
        return self.date_entry.get()

    def delete(self, start, end):
        """Limpa o conteúdo da entrada"""
        self.date_entry.delete(start, end)

    def insert(self, index, text):
        """Insere texto na entrada"""
        self.date_entry.insert(index, text)


class MultiDatePickerFrame(ctk.CTkFrame):
    """Widget customizado para seleção de múltiplas datas com geração automática de descrição"""

    def __init__(self, parent, on_dates_changed: Callable = None, **kwargs):
        super().__init__(parent, **kwargs)

        self.on_dates_changed = on_dates_changed
        self.selected_dates = []
        self.calendar_window = None

        # Frame para o botão e descrição
        self.container = ctk.CTkFrame(self)
        self.container.pack(fill="both", expand=True)

        # Botão para abrir calendário
        button_frame = ctk.CTkFrame(self.container)
        button_frame.pack(fill="x", padx=0, pady=(0, 5))

        self.calendar_btn = ctk.CTkButton(
            button_frame,
            text="📅 Selecionar Datas das Sessões",
            command=self.open_calendar,
            height=30
        )
        self.calendar_btn.pack(fill="x")

        # Entry para exibir descrição gerada
        self.description_entry = ctk.CTkEntry(
            self.container,
            width=280,
            placeholder_text="Descrição será gerada automaticamente..."
        )
        self.description_entry.pack(fill="x")

    def open_calendar(self):
        """Abre uma janela com calendário para seleção de múltiplas datas"""
        if self.calendar_window is not None and self.calendar_window.winfo_exists():
            self.calendar_window.lift()
            return

        self.calendar_window = tk.Toplevel(self.master)
        self.calendar_window.title("Selecionar Datas das Sessões")
        self.calendar_window.geometry("400x400")
        self.calendar_window.resizable(False, False)
        self.calendar_window.protocol("WM_DELETE_WINDOW", self.close_calendar)

        current_date = datetime.now()

        # Frame para navegação de mês/ano
        nav_frame = tk.Frame(self.calendar_window, bg="#212121")
        nav_frame.pack(fill="x", padx=5, pady=5)

        self.current_month = tk.IntVar(value=current_date.month)
        self.current_year = tk.IntVar(value=current_date.year)

        tk.Button(
            nav_frame,
            text="◀",
            command=lambda: self.change_month(-1),
            width=3
        ).pack(side="left")

        self.month_label = tk.Label(
            nav_frame, text="", width=15, bg="#212121", fg="white")
        self.month_label.pack(side="left", expand=True, padx=5)

        tk.Button(
            nav_frame,
            text="▶",
            command=lambda: self.change_month(1),
            width=3
        ).pack(side="left")

        # Frame para o calendário
        calendar_frame = tk.Frame(self.calendar_window, bg="#212121")
        calendar_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Dias da semana
        days = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sab", "Dom"]
        for i, day in enumerate(days):
            tk.Label(
                calendar_frame,
                text=day,
                bg="#212121",
                fg="white",
                font=("Arial", 10, "bold"),
                width=5,
                height=2
            ).grid(row=0, column=i)

        self.calendar_frame = calendar_frame

        # Frame para datas selecionadas
        info_frame = tk.Frame(self.calendar_window, bg="#212121")
        info_frame.pack(fill="x", padx=5, pady=5)

        tk.Label(
            info_frame,
            text=f"Datas selecionadas: {len(self.selected_dates)}",
            bg="#212121",
            fg="white"
        ).pack(side="left")

        self.info_label = tk.Label(
            info_frame,
            text="",
            bg="#212121",
            fg="yellow",
            wraplength=400,
            justify="left"
        )
        self.info_label.pack(side="left", padx=10)

        # Frame botões
        button_frame = tk.Frame(self.calendar_window, bg="#212121")
        button_frame.pack(fill="x", padx=5, pady=5)

        tk.Button(
            button_frame,
            text="Limpar Seleção",
            command=self.clear_selection,
            width=15
        ).pack(side="left", padx=2)

        tk.Button(
            button_frame,
            text="Cancelar",
            command=self.close_calendar,
            width=15
        ).pack(side="left", padx=2)

        tk.Button(
            button_frame,
            text="OK",
            command=self.confirm_dates,
            width=15
        ).pack(side="left", padx=2)

        self.update_calendar()

    def change_month(self, delta):
        """Muda o mês exibido"""
        month = self.current_month.get() + delta
        year = self.current_year.get()

        if month > 12:
            month = 1
            year += 1
        elif month < 1:
            month = 12
            year -= 1

        self.current_month.set(month)
        self.current_year.set(year)
        self.update_calendar()

    def update_calendar(self):
        """Atualiza o calendário exibido"""
        import calendar as cal

        # Limpar calendário anterior
        for widget in self.calendar_frame.grid_slaves():
            if widget.grid_info()['row'] > 0:
                widget.destroy()

        month = self.current_month.get()
        year = self.current_year.get()

        months_pt = ["", "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
                     "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
        self.month_label.config(text=f"{months_pt[month]} {year}")

        month_calendar = cal.monthcalendar(year, month)

        row = 1
        for week in month_calendar:
            for col, day in enumerate(week):
                if day == 0:
                    bg = "#212121"
                    text = ""
                    cmd = None
                else:
                    date_str = f"{day:02d}/{month:02d}/{year}"
                    is_selected = date_str in self.selected_dates
                    bg = "#4a4a4a" if is_selected else "#2a2a2a"
                    text = str(day)
                    def cmd(d=day): return self.select_day(d)

                btn = tk.Button(
                    self.calendar_frame,
                    text=text,
                    bg=bg,
                    fg="white",
                    font=("Arial", 10),
                    width=5,
                    height=2,
                    command=cmd
                )
                btn.grid(row=row, column=col, padx=1, pady=1)
            row += 1

        # Atualizar info
        if hasattr(self, 'info_label'):
            dates_str = ", ".join(
                self.selected_dates) if self.selected_dates else "Nenhuma"
            self.info_label.config(text=dates_str)

    def select_day(self, day):
        """Seleciona/deseleciona um dia do calendário"""
        month = self.current_month.get()
        year = self.current_year.get()
        date_str = f"{day:02d}/{month:02d}/{year}"

        if date_str in self.selected_dates:
            self.selected_dates.remove(date_str)
        else:
            self.selected_dates.append(date_str)

        # Ordenar datas
        self.selected_dates.sort(
            key=lambda x: datetime.strptime(x, "%d/%m/%Y"))

        self.update_calendar()

    def clear_selection(self):
        """Limpa toda a seleção de datas"""
        self.selected_dates = []
        self.update_calendar()

    def close_calendar(self):
        """Fecha a janela do calendário e limpa a referência"""
        if self.calendar_window:
            self.calendar_window.destroy()
            self.calendar_window = None

    def confirm_dates(self):
        """Confirma as datas selecionadas e gera descrição"""
        self.generate_description()
        self.close_calendar()

    def generate_description(self):
        """Gera automaticamente a descrição baseada nas datas selecionadas"""
        if not self.selected_dates:
            self.description_entry.delete(0, "end")
            self.description_entry.insert(0, "")
            return

        num_sessoes = len(self.selected_dates)
        num_sessoes_str = f"{num_sessoes:02d}"

        if num_sessoes == 1:
            descricao = f"Referente a {num_sessoes_str} sessão de psicoterapia realizada no dia {self.selected_dates[0]}."
        else:
            datas_formatted = ", ".join(self.selected_dates[:-1])
            datas_formatted += f" e {self.selected_dates[-1]}"
            descricao = f"Referente a {num_sessoes_str} sessões de psicoterapia realizadas nos dias {datas_formatted}."

        self.description_entry.delete(0, "end")
        self.description_entry.insert(0, descricao)

        if self.on_dates_changed:
            self.on_dates_changed(descricao)

    def get(self):
        """Retorna a descrição gerada"""
        return self.description_entry.get()

    def delete(self, start, end):
        """Limpa o conteúdo"""
        self.description_entry.delete(start, end)
        self.selected_dates = []

    def insert(self, index, text):
        """Insere texto"""
        self.description_entry.insert(index, text)


class MonthYearPickerFrame(ctk.CTkFrame):
    """Widget para seleção de Mês e Ano (Competência) usando Comboboxes"""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        # Configurar grid interno
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        current_date = datetime.now()

        # Combobox Mês
        self.months = [f"{i:02d}" for i in range(1, 13)]
        self.month_cb = ctk.CTkComboBox(
            self,
            values=self.months,
            width=70
        )
        self.month_cb.set(f"{current_date.month:02d}")
        self.month_cb.grid(row=0, column=0, padx=(0, 5), sticky="ew")

        # Combobox Ano
        start_year = 2020
        end_year = current_date.year + 5
        self.years = [str(i) for i in range(start_year, end_year + 1)]
        self.year_cb = ctk.CTkComboBox(
            self,
            values=self.years,
            width=80
        )
        self.year_cb.set(str(current_date.year))
        self.year_cb.grid(row=0, column=1, padx=(5, 0), sticky="ew")

    def get(self):
        """Retorna a competência no formato mm/aaaa"""
        return f"{self.month_cb.get()}/{self.year_cb.get()}"

    def set(self, value):
        """Define o valor (formato mm/aaaa)"""
        try:
            if "/" in value:
                m, y = value.split("/")
                if m in self.months:
                    self.month_cb.set(m)
                if y in self.years:
                    self.year_cb.set(y)
        except:
             pass

    def delete(self, start, end):
         """Método dummy para compatibilidade com delete(0, 'end')"""
         pass # Comboboxes não precisam ser limpos da mesma forma, ou podemos resetar para data atual

