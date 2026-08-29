"""Wahrheitstabellen-Fenster als Popup.

Zeigt die vollständige Zustandstabelle des Frequenzteilers
mit farbiger Hervorhebung und Export-Funktion.
"""

import tkinter as tk
from tkinter import ttk, filedialog
from theme import *
from circuit_logic import FrequencyDivider, subscript, var_name, d_name


class TruthTableWindow:
    """Popup-Fenster mit der Wahrheitstabelle."""

    def __init__(self, parent, divider: FrequencyDivider):
        self.divider = divider
        self.window = tk.Toplevel(parent)
        self.window.title(f"Wahrheitstabelle – Frequenzteiler ÷{divider.N}")
        self.window.configure(bg=BG_DARK)
        self.window.geometry("700x500")
        self.window.minsize(500, 300)
        self.window.transient(parent)

        self._create_ui()

    def _create_ui(self):
        n = self.divider.n

        # ── Header ───────────────────────────────────────────────────────
        header = tk.Frame(self.window, bg=BG_MEDIUM, pady=10, padx=15)
        header.pack(fill=tk.X)

        tk.Label(
            header,
            text=f"Wahrheitstabelle – ÷{self.divider.N}, "
                 f"Duty-Cycle {self.divider.k}/{self.divider.N}",
            font=FONT_HEADING, bg=BG_MEDIUM, fg=TEXT_PRIMARY,
        ).pack(side=tk.LEFT)

        export_btn = tk.Button(
            header, text="CSV Exportieren", font=FONT_SMALL,
            bg=BUTTON_BG, fg=BUTTON_FG, activebackground=SECONDARY,
            activeforeground=TEXT_BRIGHT, relief=tk.FLAT, padx=10, pady=4,
            command=self._export_csv, cursor='hand2',
        )
        export_btn.pack(side=tk.RIGHT)

        # ── Legende ──────────────────────────────────────────────────────
        legend = tk.Frame(self.window, bg=BG_DARK, pady=5, padx=15)
        legend.pack(fill=tk.X)

        for color, text in [(HIGH_COLOR, "Ausgang = 1"),
                            (LOW_COLOR, "Ausgang = 0"),
                            (TEXT_DIM, "Ungenutzt (→ Reset)")]:
            dot = tk.Label(legend, text="●", fg=color, bg=BG_DARK, font=('Segoe UI', 8))
            dot.pack(side=tk.LEFT, padx=(0, 2))
            lbl = tk.Label(legend, text=text, fg=TEXT_SECONDARY, bg=BG_DARK, font=FONT_SMALL)
            lbl.pack(side=tk.LEFT, padx=(0, 12))

        # ── Tabelle ──────────────────────────────────────────────────────
        table_frame = tk.Frame(self.window, bg=BG_DARK)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(5, 15))

        # Spalten definieren
        columns = ['state']
        headings = ['Zustand']

        # Aktuelle Bits Q
        for i in range(n - 1, -1, -1):
            columns.append(f'q{i}')
            headings.append(var_name(i))

        columns.append('sep1')
        headings.append('→')

        # Nächste Bits D
        for i in range(n - 1, -1, -1):
            columns.append(f'd{i}')
            headings.append(d_name(i))

        columns.append('sep2')
        headings.append('│')

        columns.append('output')
        headings.append('fout')

        # Treeview
        style = ttk.Style()
        style.configure(
            'TruthTable.Treeview',
            background=BG_DARK,
            foreground=TEXT_PRIMARY,
            fieldbackground=BG_DARK,
            rowheight=28,
            font=FONT_MONO,
        )
        style.configure(
            'TruthTable.Treeview.Heading',
            background=BG_MEDIUM,
            foreground=ACCENT,
            font=FONT_MONO_LARGE,
            relief=tk.FLAT,
        )
        style.map(
            'TruthTable.Treeview',
            background=[('selected', TERTIARY)],
            foreground=[('selected', TEXT_BRIGHT)],
        )
        style.map(
            'TruthTable.Treeview.Heading',
            background=[('active', BG_LIGHT)],
        )

        tree = ttk.Treeview(
            table_frame, columns=columns, show='headings',
            style='TruthTable.Treeview',
        )

        # Scrollbar
        vsb = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)

        for col, heading in zip(columns, headings):
            width = 70 if col not in ('sep1', 'sep2') else 30
            anchor = tk.CENTER
            tree.heading(col, text=heading, anchor=anchor)
            tree.column(col, width=width, minwidth=30, anchor=anchor, stretch=False)

        # Zeilen einfügen
        tree.tag_configure('high', background=ROW_HIGH, foreground=HIGH_COLOR)
        tree.tag_configure('low', background=ROW_LOW, foreground=LOW_COLOR)
        tree.tag_configure('unused', background=ROW_UNUSED, foreground=TEXT_DIM)

        for row in self.divider.state_table:
            values = [str(row['state'])]

            # Aktuelle Bits (MSB → LSB)
            for i in range(n - 1, -1, -1):
                bit_pos = n - 1 - i
                values.append(str(row['current_bits'][bit_pos]))

            values.append('→')

            # Nächste Bits (MSB → LSB)
            for i in range(n - 1, -1, -1):
                bit_pos = n - 1 - i
                values.append(str(row['next_bits'][bit_pos]))

            values.append('│')

            if row['used']:
                values.append(str(row['output']))
                tag = 'high' if row['output'] == 1 else 'low'
            else:
                values.append('X')
                tag = 'unused'

            tree.insert('', tk.END, values=values, tags=(tag,))

        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree = tree

    def _export_csv(self):
        """Exportiert die Wahrheitstabelle als CSV-Datei."""
        filepath = filedialog.asksaveasfilename(
            parent=self.window,
            defaultextension='.csv',
            filetypes=[("CSV-Dateien", "*.csv"), ("Alle Dateien", "*.*")],
            title="Wahrheitstabelle exportieren",
            initialfile=f"wahrheitstabelle_div{self.divider.N}.csv",
        )
        if not filepath:
            return

        n = self.divider.n
        headers = ['Zustand']
        for i in range(n - 1, -1, -1):
            headers.append(f'Q{i}')
        for i in range(n - 1, -1, -1):
            headers.append(f'D{i}')
        headers.append('Output')
        headers.append('Genutzt')

        lines = [';'.join(headers)]
        for row in self.divider.state_table:
            vals = [str(row['state'])]
            for i in range(n - 1, -1, -1):
                bit_pos = n - 1 - i
                vals.append(str(row['current_bits'][bit_pos]))
            for i in range(n - 1, -1, -1):
                bit_pos = n - 1 - i
                vals.append(str(row['next_bits'][bit_pos]))
            vals.append(str(row['output']) if row['used'] else 'X')
            vals.append('Ja' if row['used'] else 'Nein')
            lines.append(';'.join(vals))

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
