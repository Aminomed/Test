"""D-Flipflop Frequenzteiler – Visuelles Design-Tool.

Hauptanwendung mit tkinter-GUI. Ermöglicht die Eingabe beliebiger
Teilungsfaktoren und Duty-Cycles und zeigt Schaltplan, Timing-Diagramm,
boolesche Gleichungen und Wahrheitstabelle.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

from theme import *
from circuit_logic import FrequencyDivider
from circuit_drawer import CircuitDrawer
from truth_table_view import TruthTableWindow
from timing_diagram import TimingDiagramDrawer


class App:
    """Hauptanwendung."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("D-Flipflop Frequenzteiler")
        self.root.geometry("1150x780")
        self.root.minsize(900, 600)
        self.root.configure(bg=BG_DARK)

        # Icon setzen (optional)
        try:
            self.root.iconbitmap(default='')
        except Exception:
            pass

        self.divider = None  # type: FrequencyDivider | None

        self._setup_theme()
        self._create_ui()

        # Standardwerte einfügen
        self.entry_n.insert(0, '7')
        self.entry_k.insert(0, '4')

    # ── Theme-Setup ──────────────────────────────────────────────────────

    def _setup_theme(self):
        """Konfiguriert das dunkle ttk-Theme."""
        style = ttk.Style()
        style.theme_use('clam')

        # Notebook
        style.configure('TNotebook', background=BG_DARK, borderwidth=0)
        style.configure(
            'TNotebook.Tab',
            background=BG_MEDIUM, foreground=TEXT_SECONDARY,
            padding=(15, 8), font=FONT_NORMAL,
        )
        style.map(
            'TNotebook.Tab',
            background=[('selected', BG_LIGHT), ('active', BG_LIGHT)],
            foreground=[('selected', ACCENT), ('active', TEXT_PRIMARY)],
        )

        # Scrollbar
        style.configure(
            'Vertical.TScrollbar',
            background=SCROLLBAR_BG, troughcolor=BG_DARK,
            borderwidth=0, arrowsize=12,
        )
        style.map(
            'Vertical.TScrollbar',
            background=[('active', SCROLLBAR_FG), ('pressed', SCROLLBAR_FG)],
        )

        style.configure(
            'Horizontal.TScrollbar',
            background=SCROLLBAR_BG, troughcolor=BG_DARK,
            borderwidth=0, arrowsize=12,
        )
        style.map(
            'Horizontal.TScrollbar',
            background=[('active', SCROLLBAR_FG), ('pressed', SCROLLBAR_FG)],
        )

    # ── UI-Aufbau ────────────────────────────────────────────────────────

    def _create_ui(self):
        """Erstellt die gesamte Benutzeroberfläche."""
        # ── Header ───────────────────────────────────────────────────────
        header = tk.Frame(self.root, bg=BG_MEDIUM, pady=12, padx=20)
        header.pack(fill=tk.X)

        tk.Label(
            header, text="⚡ D-Flipflop Frequenzteiler",
            font=FONT_TITLE, bg=BG_MEDIUM, fg=TEXT_PRIMARY,
        ).pack(side=tk.LEFT)

        tk.Label(
            header,
            text="Beliebige Frequenzteilung visuell darstellen",
            font=FONT_SMALL, bg=BG_MEDIUM, fg=TEXT_SECONDARY,
        ).pack(side=tk.LEFT, padx=(15, 0))

        # ── Eingabebereich ───────────────────────────────────────────────
        input_frame = tk.Frame(self.root, bg=BG_DARK, pady=12, padx=20)
        input_frame.pack(fill=tk.X)

        # Linke Seite: Eingabefelder
        fields = tk.Frame(input_frame, bg=BG_DARK)
        fields.pack(side=tk.LEFT)

        # N-Eingabe
        tk.Label(
            fields, text="Teilungsfaktor N:", font=FONT_NORMAL,
            bg=BG_DARK, fg=TEXT_PRIMARY,
        ).grid(row=0, column=0, sticky=tk.W, padx=(0, 8))

        self.entry_n = tk.Entry(
            fields, font=FONT_MONO_LARGE, width=6,
            bg=INPUT_BG, fg=INPUT_FG, insertbackground=TEXT_PRIMARY,
            relief=tk.FLAT, highlightthickness=2,
            highlightbackground=BORDER_COLOR, highlightcolor=BORDER_FOCUS,
            justify=tk.CENTER,
        )
        self.entry_n.grid(row=0, column=1, padx=(0, 20))
        self.entry_n.bind('<Return>', lambda e: self._on_generate())

        # k-Eingabe
        tk.Label(
            fields, text="Duty-Cycle-Zähler k:", font=FONT_NORMAL,
            bg=BG_DARK, fg=TEXT_PRIMARY,
        ).grid(row=0, column=2, sticky=tk.W, padx=(0, 8))

        self.entry_k = tk.Entry(
            fields, font=FONT_MONO_LARGE, width=6,
            bg=INPUT_BG, fg=INPUT_FG, insertbackground=TEXT_PRIMARY,
            relief=tk.FLAT, highlightthickness=2,
            highlightbackground=BORDER_COLOR, highlightcolor=BORDER_FOCUS,
            justify=tk.CENTER,
        )
        self.entry_k.grid(row=0, column=3, padx=(0, 20))
        self.entry_k.bind('<Return>', lambda e: self._on_generate())

        # Info-Label
        self.info_label = tk.Label(
            fields, text="fout = fin / N,  Duty = k / N",
            font=FONT_SMALL, bg=BG_DARK, fg=TEXT_DIM,
        )
        self.info_label.grid(row=1, column=0, columnspan=4, sticky=tk.W, pady=(4, 0))

        # Rechte Seite: Buttons
        buttons = tk.Frame(input_frame, bg=BG_DARK)
        buttons.pack(side=tk.RIGHT)

        self.btn_truth = tk.Button(
            buttons, text="📋 Wahrheitstabelle",
            font=FONT_BUTTON, bg=SECONDARY, fg=TEXT_BRIGHT,
            activebackground=SECONDARY_HOVER, activeforeground=TEXT_BRIGHT,
            relief=tk.FLAT, padx=14, pady=6, cursor='hand2',
            command=self._show_truth_table, state=tk.DISABLED,
        )
        self.btn_truth.pack(side=tk.RIGHT, padx=(10, 0))

        self.btn_generate = tk.Button(
            buttons, text="⚙ Generieren",
            font=FONT_BUTTON, bg=ACCENT, fg=TEXT_BRIGHT,
            activebackground=ACCENT_HOVER, activeforeground=TEXT_BRIGHT,
            relief=tk.FLAT, padx=18, pady=6, cursor='hand2',
            command=self._on_generate,
        )
        self.btn_generate.pack(side=tk.RIGHT)

        # ── Trennlinie ──────────────────────────────────────────────────
        sep = tk.Frame(self.root, bg=BORDER_COLOR, height=1)
        sep.pack(fill=tk.X)

        # ── Notebook (Tabs) ─────────────────────────────────────────────
        self.notebook = ttk.Notebook(self.root, style='TNotebook')
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=8, pady=(8, 0))

        # Tab 1: Schaltplan
        self.tab_circuit = tk.Frame(self.notebook, bg=BG_DARK)
        self.notebook.add(self.tab_circuit, text='  📐 Schaltplan  ')

        self.circuit_canvas = tk.Canvas(
            self.tab_circuit, bg=BG_DARK, highlightthickness=0,
        )
        self.circuit_h_scroll = ttk.Scrollbar(
            self.tab_circuit, orient=tk.HORIZONTAL,
            command=self.circuit_canvas.xview,
        )
        self.circuit_v_scroll = ttk.Scrollbar(
            self.tab_circuit, orient=tk.VERTICAL,
            command=self.circuit_canvas.yview,
        )
        self.circuit_canvas.configure(
            xscrollcommand=self.circuit_h_scroll.set,
            yscrollcommand=self.circuit_v_scroll.set,
        )
        self.circuit_v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.circuit_h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.circuit_canvas.pack(fill=tk.BOTH, expand=True)

        # Tab 2: Timing-Diagramm
        self.tab_timing = tk.Frame(self.notebook, bg=BG_DARK)
        self.notebook.add(self.tab_timing, text='  📊 Timing-Diagramm  ')

        self.timing_canvas = tk.Canvas(
            self.tab_timing, bg=BG_DARK, highlightthickness=0,
        )
        self.timing_h_scroll = ttk.Scrollbar(
            self.tab_timing, orient=tk.HORIZONTAL,
            command=self.timing_canvas.xview,
        )
        self.timing_v_scroll = ttk.Scrollbar(
            self.tab_timing, orient=tk.VERTICAL,
            command=self.timing_canvas.yview,
        )
        self.timing_canvas.configure(
            xscrollcommand=self.timing_h_scroll.set,
            yscrollcommand=self.timing_v_scroll.set,
        )
        self.timing_v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.timing_h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.timing_canvas.pack(fill=tk.BOTH, expand=True)

        # Tab 3: Gleichungen
        self.tab_equations = tk.Frame(self.notebook, bg=BG_DARK)
        self.notebook.add(self.tab_equations, text='  📝 Gleichungen  ')

        self.eq_text = tk.Text(
            self.tab_equations, bg=BG_DARK, fg=TEXT_PRIMARY,
            font=FONT_EQUATION_LARGE, relief=tk.FLAT,
            highlightthickness=0, padx=30, pady=20,
            state=tk.DISABLED, cursor='arrow',
            spacing1=5, spacing3=5,
            wrap=tk.WORD,
        )
        self.eq_text.pack(fill=tk.BOTH, expand=True)

        # Text-Tags für farbige Darstellung
        self.eq_text.tag_configure('heading', font=FONT_HEADING, foreground=ACCENT)
        self.eq_text.tag_configure('equation', font=FONT_EQUATION_LARGE, foreground=TEXT_PRIMARY)
        self.eq_text.tag_configure('name', font=FONT_EQUATION_LARGE, foreground=DATA_COLOR)
        self.eq_text.tag_configure('output_name', font=FONT_EQUATION_LARGE, foreground=OUTPUT_COLOR)
        self.eq_text.tag_configure('info', font=FONT_NORMAL, foreground=TEXT_SECONDARY)
        self.eq_text.tag_configure('separator', font=FONT_SMALL, foreground=BORDER_COLOR)

        # ── Statusleiste ─────────────────────────────────────────────────
        self.status_bar = tk.Frame(self.root, bg=BG_MEDIUM, pady=6, padx=15)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)

        self.status_label = tk.Label(
            self.status_bar,
            text="Bitte Teilungsfaktor N und Duty-Cycle k eingeben und 'Generieren' klicken.",
            font=FONT_SMALL, bg=BG_MEDIUM, fg=TEXT_SECONDARY,
            anchor=tk.W,
        )
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Placeholder-Text
        self._draw_placeholder()

    def _draw_placeholder(self):
        """Zeichnet einen Platzhalter auf den leeren Canvas."""
        self.circuit_canvas.delete('all')
        self.circuit_canvas.update_idletasks()
        w = max(self.circuit_canvas.winfo_width(), 800)
        h = max(self.circuit_canvas.winfo_height(), 400)

        self.circuit_canvas.create_text(
            w / 2, h / 2 - 20,
            text="⚡",
            font=('Segoe UI', 48), fill=TEXT_DIM,
        )
        self.circuit_canvas.create_text(
            w / 2, h / 2 + 40,
            text="Parameter eingeben und 'Generieren' klicken",
            font=FONT_HEADING, fill=TEXT_DIM,
        )
        self.circuit_canvas.create_text(
            w / 2, h / 2 + 70,
            text="z.B. N=7, k=4 für fout = fin/7 mit Duty-Cycle 4/7",
            font=FONT_NORMAL, fill=TEXT_DIM,
        )

        self.timing_canvas.delete('all')
        self.timing_canvas.update_idletasks()
        self.timing_canvas.create_text(
            w / 2, h / 2,
            text="Timing-Diagramm erscheint nach dem Generieren",
            font=FONT_HEADING, fill=TEXT_DIM,
        )

    # ── Aktionen ─────────────────────────────────────────────────────────

    def _on_generate(self):
        """Generiert den Frequenzteiler aus den Eingaben."""
        # Eingaben validieren
        try:
            n_val = int(self.entry_n.get().strip())
        except ValueError:
            self._show_error("N muss eine ganze Zahl sein.")
            return

        try:
            k_val = int(self.entry_k.get().strip())
        except ValueError:
            self._show_error("k muss eine ganze Zahl sein.")
            return

        try:
            self.divider = FrequencyDivider(n_val, k_val)
        except ValueError as e:
            self._show_error(str(e))
            return

        # Info-Label aktualisieren
        self.info_label.configure(
            text=f"fout = fin / {n_val}  |  "
                 f"Duty = {k_val}/{n_val} ({k_val/n_val*100:.1f}%)  |  "
                 f"{self.divider.n} D-Flipflop{'s' if self.divider.n > 1 else ''}",
            fg=SUCCESS_COLOR,
        )

        # Schaltplan zeichnen
        self.root.update_idletasks()
        drawer = CircuitDrawer(self.circuit_canvas, self.divider)
        drawer.draw()

        # Timing-Diagramm zeichnen
        self.root.update_idletasks()
        timing = TimingDiagramDrawer(self.timing_canvas, self.divider)
        timing.draw(num_periods=2)

        # Gleichungen anzeigen
        self._update_equations()

        # Wahrheitstabelle-Button aktivieren
        self.btn_truth.configure(state=tk.NORMAL)

        # Status aktualisieren
        self.status_label.configure(
            text=self.divider.get_summary(),
            fg=SUCCESS_COLOR,
        )

        # Zum Schaltplan-Tab wechseln
        self.notebook.select(self.tab_circuit)

    def _update_equations(self):
        """Aktualisiert die Gleichungen-Ansicht."""
        self.eq_text.configure(state=tk.NORMAL)
        self.eq_text.delete('1.0', tk.END)

        div = self.divider
        n = div.n

        # Überschrift
        self.eq_text.insert(tk.END, "BOOLESCHE GLEICHUNGEN\n", 'heading')
        self.eq_text.insert(
            tk.END,
            f"Frequenzteiler ÷{div.N}, Duty-Cycle {div.k}/{div.N}\n",
            'info',
        )
        self.eq_text.insert(
            tk.END,
            f"{n} D-Flipflop{'s' if n > 1 else ''}, "
            f"{div.N} von {div.num_states} Zuständen genutzt\n\n",
            'info',
        )

        # Variablen
        self.eq_text.insert(tk.END, "─── Variablen ───\n", 'separator')
        ff_names = ', '.join(div.get_ff_names())
        self.eq_text.insert(tk.END, f"Flipflop-Ausgänge: {ff_names}\n", 'info')
        self.eq_text.insert(
            tk.END, f"Eingangstakt: fin (CLK)\n\n", 'info',
        )

        # D-Gleichungen
        self.eq_text.insert(tk.END, "─── Next-State-Logik ───\n\n", 'separator')
        for i in range(n - 1, -1, -1):
            from circuit_logic import subscript as sub
            name = f'D{sub(i)}'
            eq = div.equations.get(name, '?')
            self.eq_text.insert(tk.END, f"  {name}", 'name')
            self.eq_text.insert(tk.END, f"  =  {eq}\n\n", 'equation')

        # Ausgangsgleichung
        self.eq_text.insert(tk.END, "\n─── Ausgangslogik ───\n\n", 'separator')
        eq = div.equations.get('fout', '?')
        self.eq_text.insert(tk.END, f"  fout", 'output_name')
        self.eq_text.insert(tk.END, f"  =  {eq}\n\n", 'equation')

        # Erklärung
        self.eq_text.insert(tk.END, "\n─── Legende ───\n", 'separator')
        self.eq_text.insert(tk.END, "  · = UND (AND)\n", 'info')
        self.eq_text.insert(tk.END, "  + = ODER (OR)\n", 'info')
        self.eq_text.insert(tk.END, "  Q̄ = NICHT Q (invertiert)\n", 'info')

        self.eq_text.configure(state=tk.DISABLED)

    def _show_truth_table(self):
        """Öffnet das Wahrheitstabellen-Fenster."""
        if self.divider is None:
            self._show_error("Bitte zuerst einen Frequenzteiler generieren.")
            return
        TruthTableWindow(self.root, self.divider)

    def _show_error(self, msg):
        """Zeigt eine Fehlermeldung."""
        self.status_label.configure(text=f"⚠ {msg}", fg=ERROR_COLOR)
        messagebox.showerror("Fehler", msg, parent=self.root)


# ── Einstiegspunkt ───────────────────────────────────────────────────────────

def main():
    root = tk.Tk()

    # DPI-Awareness für scharfe Darstellung unter Windows
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass

    app = App(root)
    root.mainloop()


if __name__ == '__main__':
    main()
