"""Timing-Diagramm für den D-Flipflop Frequenzteiler.

Zeichnet die digitalen Signalverläufe (CLK, Q₀…Qₙ₋₁, fout)
über mehrere Perioden auf einem tkinter Canvas.
"""

import tkinter as tk
from theme import *
from circuit_logic import FrequencyDivider, var_name


# Farbpalette für die Signale (rotiert bei vielen FFs)
SIGNAL_COLORS = [
    CLK_COLOR,       # CLK
    '#bb86fc',       # Q-Signale: Lila
    '#03dac6',       # Türkis
    '#cf6679',       # Rosa
    '#ffab40',       # Orange
    '#69f0ae',       # Mintgrün
    '#82b1ff',       # Hellblau
    '#ea80fc',       # Magenta
]


class TimingDiagramDrawer:
    """Zeichnet das Timing-Diagramm auf einen Canvas."""

    MARGIN_LEFT = 90       # Platz für Signalnamen
    MARGIN_RIGHT = 30
    MARGIN_TOP = 50
    MARGIN_BOTTOM = 30
    SIGNAL_HEIGHT = 40     # Höhe eines Signals (Amplitude)
    SIGNAL_SPACING = 20    # Abstand zwischen Signalen
    TRANSITION_WIDTH = 3   # Breite der Flanken (Pixel)

    def __init__(self, canvas: tk.Canvas, divider: FrequencyDivider):
        self.canvas = canvas
        self.divider = divider

    def draw(self, num_periods=2):
        """Zeichnet das komplette Timing-Diagramm."""
        self.canvas.delete('all')

        signals, state_seq = self.divider.get_timing_sequence(num_periods)
        signal_names = list(signals.keys())
        num_signals = len(signal_names)

        total_clocks = self.divider.N * num_periods

        # ── Canvas-Größe berechnen ───────────────────────────────────────
        content_height = (
            self.MARGIN_TOP
            + num_signals * (self.SIGNAL_HEIGHT + self.SIGNAL_SPACING)
            + self.MARGIN_BOTTOM + 40
        )

        canvas_width = self.canvas.winfo_width()
        if canvas_width < 100:
            canvas_width = 900

        content_width = max(canvas_width, total_clocks * 40 + self.MARGIN_LEFT + self.MARGIN_RIGHT)

        self.canvas.configure(scrollregion=(0, 0, content_width, content_height))

        avail_width = content_width - self.MARGIN_LEFT - self.MARGIN_RIGHT
        # Für CLK: jede Halbperiode braucht Platz
        clk_step_width = avail_width / (total_clocks * 2)  # CLK hat 2x so viele Schritte
        data_step_width = avail_width / total_clocks

        # ── Hintergrund ──────────────────────────────────────────────────
        self.canvas.create_rectangle(
            0, 0, content_width, content_height,
            fill=BG_DARK, outline='',
        )

        # ── Titel ────────────────────────────────────────────────────────
        self.canvas.create_text(
            content_width / 2, 20,
            text=f"Timing-Diagramm – ÷{self.divider.N}, "
                 f"Duty-Cycle {self.divider.k}/{self.divider.N}",
            font=FONT_HEADING, fill=TEXT_PRIMARY, anchor=tk.CENTER,
        )

        # ── Vertikale Taktflanken-Linien ─────────────────────────────────
        for clk_idx in range(total_clocks + 1):
            x = self.MARGIN_LEFT + clk_idx * data_step_width
            self.canvas.create_line(
                x, self.MARGIN_TOP - 5,
                x, content_height - self.MARGIN_BOTTOM,
                fill=TIMING_GRID, dash=(2, 4), width=1,
            )

        # ── Zustandsnummern oben ─────────────────────────────────────────
        for idx, state in enumerate(state_seq):
            x_center = self.MARGIN_LEFT + (idx + 0.5) * data_step_width
            self.canvas.create_text(
                x_center, self.MARGIN_TOP - 12,
                text=str(state), font=FONT_MONO_SMALL,
                fill=TEXT_DIM, anchor=tk.CENTER,
            )

        # Zustandslabel
        self.canvas.create_text(
            self.MARGIN_LEFT - 10, self.MARGIN_TOP - 12,
            text="Zustand:", font=FONT_SMALL, fill=TEXT_DIM, anchor=tk.E,
        )

        # ── Signale zeichnen ─────────────────────────────────────────────
        color_idx = 0
        for sig_idx, name in enumerate(signal_names):
            y_base = (
                self.MARGIN_TOP
                + sig_idx * (self.SIGNAL_HEIGHT + self.SIGNAL_SPACING)
                + self.SIGNAL_SPACING
            )
            y_high = y_base
            y_low = y_base + self.SIGNAL_HEIGHT

            # Farbe wählen
            if name.startswith('CLK'):
                color = SIGNAL_COLORS[0]
            elif name == 'fout':
                color = OUTPUT_COLOR
            else:
                color_idx += 1
                color = SIGNAL_COLORS[min(color_idx, len(SIGNAL_COLORS) - 1)]

            # Signalname
            self.canvas.create_text(
                self.MARGIN_LEFT - 10, (y_high + y_low) / 2,
                text=name, font=FONT_CIRCUIT_LABEL, fill=color,
                anchor=tk.E,
            )

            # HIGH/LOW Marker
            self.canvas.create_text(
                self.MARGIN_LEFT - 5, y_high + 2,
                text='1', font=('Consolas', 7), fill=TEXT_DIM, anchor=tk.W,
            )
            self.canvas.create_text(
                self.MARGIN_LEFT - 5, y_low - 2,
                text='0', font=('Consolas', 7), fill=TEXT_DIM, anchor=tk.W,
            )

            # Signal zeichnen
            data = signals[name]
            is_clk = name.startswith('CLK')

            points = []
            x = self.MARGIN_LEFT

            if is_clk:
                step_w = clk_step_width
            else:
                step_w = data_step_width

            prev_val = None
            for val, dur in data:
                y_val = y_high if val == 1 else y_low

                if prev_val is not None and prev_val != val:
                    # Flanke zeichnen (vertikale Transition)
                    y_prev = y_high if prev_val == 1 else y_low
                    points.append((x, y_prev))
                    points.append((x, y_val))
                elif prev_val is None:
                    points.append((x, y_val))

                x_end = x + step_w * dur
                points.append((x_end, y_val))

                prev_val = val
                x = x_end

            # Linie zeichnen
            if len(points) >= 2:
                flat = []
                for px, py in points:
                    flat.extend([px, py])
                self.canvas.create_line(
                    *flat, fill=color, width=2, capstyle=tk.ROUND,
                )

            # Hintergrund-Füllung für fout
            if name == 'fout':
                x = self.MARGIN_LEFT
                for val, dur in data:
                    x_end = x + step_w * dur
                    if val == 1:
                        self.canvas.create_rectangle(
                            x, y_high, x_end, y_low,
                            fill='#3fb95015', outline='',
                        )
                    x = x_end

            # Horizontale Basislinie (LOW-Referenz)
            self.canvas.create_line(
                self.MARGIN_LEFT, y_low,
                self.MARGIN_LEFT + avail_width, y_low,
                fill=TIMING_GRID, width=1, dash=(1, 3),
            )

        # ── Periodenmarkierungen ─────────────────────────────────────────
        y_bottom = content_height - self.MARGIN_BOTTOM
        for p in range(num_periods):
            x_start = self.MARGIN_LEFT + p * self.divider.N * data_step_width
            x_end = self.MARGIN_LEFT + (p + 1) * self.divider.N * data_step_width

            # Klammer
            self.canvas.create_line(
                x_start, y_bottom - 5, x_start, y_bottom,
                fill=TEXT_DIM, width=1,
            )
            self.canvas.create_line(
                x_start, y_bottom, x_end, y_bottom,
                fill=TEXT_DIM, width=1,
            )
            self.canvas.create_line(
                x_end, y_bottom - 5, x_end, y_bottom,
                fill=TEXT_DIM, width=1,
            )

            # Label
            mid_x = (x_start + x_end) / 2
            self.canvas.create_text(
                mid_x, y_bottom + 12,
                text=f"Periode {p+1}", font=FONT_SMALL,
                fill=TEXT_DIM, anchor=tk.CENTER,
            )
