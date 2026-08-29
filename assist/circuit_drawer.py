"""Schaltplan-Zeichnung für den D-Flipflop Frequenzteiler.

Zeichnet D-Flipflops, die Next-State-Logik-Box, die Ausgangslogik-Box
und alle Verbindungen auf einem tkinter Canvas.
"""

import tkinter as tk
import math
from theme import *
from circuit_logic import FrequencyDivider, var_name, d_name, subscript


class CircuitDrawer:
    """Zeichnet den Schaltplan des Frequenzteilers auf einen Canvas."""

    # ── Dimensionen ──────────────────────────────────────────────────────
    FF_W = 110
    FF_H = 140
    FF_GAP = 60          # Abstand zwischen FFs

    LOGIC_BOX_PAD = 20   # Innenabstand der Logik-Boxen
    MIN_LOGIC_W = 200
    MIN_LOGIC_H = 120

    WIRE_RADIUS = 4      # Radius der Verbindungspunkte
    ARROW_SIZE = 8

    MARGIN = 50

    def __init__(self, canvas: tk.Canvas, divider: FrequencyDivider):
        self.canvas = canvas
        self.divider = divider
        self.n = divider.n

    def draw(self):
        """Zeichnet den kompletten Schaltplan."""
        self.canvas.delete('all')
        n = self.n

        # ── Layout berechnen ─────────────────────────────────────────────
        total_ff_w = n * self.FF_W + (n - 1) * self.FF_GAP
        logic_text_lines = self._get_logic_lines()
        output_text_lines = self._get_output_lines()

        # Logik-Box Breite basierend auf längstem Text
        max_logic_text = max(
            (len(line) for line in logic_text_lines),
            default=10
        )
        logic_w = max(self.MIN_LOGIC_W, max_logic_text * 9 + 2 * self.LOGIC_BOX_PAD)
        logic_h = max(self.MIN_LOGIC_H, len(logic_text_lines) * 22 + 2 * self.LOGIC_BOX_PAD + 30)

        max_out_text = max((len(line) for line in output_text_lines), default=10)
        output_w = max(140, max_out_text * 9 + 2 * self.LOGIC_BOX_PAD)
        output_h = max(90, len(output_text_lines) * 22 + 2 * self.LOGIC_BOX_PAD + 30)

        # Positionen
        center_x_ffs = max(logic_w / 2 + self.MARGIN + 40, 350)
        ff_start_x = center_x_ffs - total_ff_w / 2

        # Vertikal: Logic → Gap → FFs → Gap → CLK → Gap → Feedback
        logic_y = self.MARGIN + 10
        ff_y = logic_y + logic_h + 70
        clk_y = ff_y + self.FF_H + 35
        feedback_y = clk_y + 35

        # Output-Box rechts neben FFs
        output_x = ff_start_x + total_ff_w + 60
        output_y = ff_y + (self.FF_H - output_h) / 2

        # Canvas-Größe
        canvas_w = max(900, output_x + output_w + self.MARGIN + 20)
        canvas_h = feedback_y + 60

        self.canvas.configure(scrollregion=(0, 0, canvas_w, canvas_h))

        # ── Hintergrund ──────────────────────────────────────────────────
        self.canvas.create_rectangle(
            0, 0, canvas_w, canvas_h, fill=BG_DARK, outline='',
        )

        # ── Titel ────────────────────────────────────────────────────────
        self.canvas.create_text(
            canvas_w / 2, 20,
            text=f"Schaltplan – Frequenzteiler ÷{self.divider.N}",
            font=FONT_HEADING, fill=TEXT_PRIMARY, anchor=tk.CENTER,
        )

        # ── Next-State-Logik-Box ─────────────────────────────────────────
        logic_x = center_x_ffs - logic_w / 2
        self._draw_box(
            logic_x, logic_y, logic_w, logic_h,
            title="Next-State-Logik",
            lines=logic_text_lines,
            fill=GATE_FILL, border=GATE_BORDER,
            title_color=SECONDARY_HOVER,
        )

        # ── D-Flipflops ─────────────────────────────────────────────────
        ff_positions = []
        for i in range(n):
            x = ff_start_x + i * (self.FF_W + self.FF_GAP)
            ff_positions.append((x, ff_y))
            self._draw_flipflop(x, ff_y, n - 1 - i)  # MSB first

        # ── Ausgangslogik-Box ────────────────────────────────────────────
        self._draw_box(
            output_x, output_y, output_w, output_h,
            title="Ausgangslogik",
            lines=output_text_lines,
            fill='#1a2e1a', border=OUTPUT_COLOR,
            title_color=OUTPUT_COLOR,
        )

        # ── fout Ausgang ─────────────────────────────────────────────────
        fout_x = output_x + output_w
        fout_y = output_y + output_h / 2
        self.canvas.create_line(
            fout_x, fout_y,
            fout_x + 50, fout_y,
            fill=OUTPUT_COLOR, width=2.5, arrow=tk.LAST, arrowshape=(10, 12, 5),
        )
        self.canvas.create_text(
            fout_x + 55, fout_y,
            text="fout", font=FONT_CIRCUIT_LABEL, fill=OUTPUT_COLOR, anchor=tk.W,
        )

        # ── Verbindungen: Logic → D-Eingänge ────────────────────────────
        logic_bottom = logic_y + logic_h
        for i, (fx, fy) in enumerate(ff_positions):
            ff_idx = n - 1 - i  # MSB first
            d_x = fx + 20  # D-Pin ist links oben am FF
            d_y = fy

            # Vertikale Linie von Logik-Box nach unten zum D-Eingang
            line_x = d_x + 5
            self.canvas.create_line(
                line_x, logic_bottom,
                line_x, d_y,
                fill=DATA_COLOR, width=2, arrow=tk.LAST, arrowshape=(8, 10, 4),
            )

            # Label
            self.canvas.create_text(
                line_x + 8, (logic_bottom + d_y) / 2,
                text=d_name(ff_idx), font=FONT_CIRCUIT,
                fill=DATA_COLOR, anchor=tk.W,
            )

        # ── Verbindungen: Q-Ausgänge → Ausgangslogik ────────────────────
        for i, (fx, fy) in enumerate(ff_positions):
            ff_idx = n - 1 - i
            q_x = fx + self.FF_W - 20  # Q-Pin rechts oben
            q_y = fy + 35

            # Horizontale Linie nach rechts zum Output-Block
            if i == n - 1:
                # Letzer FF → direkte Verbindung zur Ausgangslogik
                self.canvas.create_line(
                    q_x, q_y,
                    output_x, output_y + output_h / 2,
                    fill=WIRE_COLOR, width=1.5, smooth=True,
                )
            else:
                # Linie nach unten, dann nach rechts (Routing)
                route_y = ff_y + self.FF_H + 12 + i * 6
                self.canvas.create_line(
                    q_x, q_y,
                    q_x, route_y,
                    fill=WIRE_COLOR, width=1, dash=(4, 2),
                )

        # ── CLK-Verteilung ───────────────────────────────────────────────
        clk_start_x = ff_start_x - 40
        clk_end_x = ff_start_x + total_ff_w + 10

        # CLK-Bus (horizontale Linie)
        self.canvas.create_line(
            clk_start_x, clk_y,
            clk_end_x, clk_y,
            fill=CLK_COLOR, width=2.5,
        )

        # CLK-Label links
        self.canvas.create_text(
            clk_start_x - 5, clk_y,
            text="fin (CLK)", font=FONT_CIRCUIT_LABEL, fill=CLK_COLOR, anchor=tk.E,
        )

        # CLK-Pfeil links
        self.canvas.create_line(
            clk_start_x - 40, clk_y,
            clk_start_x, clk_y,
            fill=CLK_COLOR, width=2.5, arrow=tk.LAST, arrowshape=(10, 12, 5),
        )

        # Vertikale Leitungen zu jedem FF CLK-Pin
        for i, (fx, fy) in enumerate(ff_positions):
            clk_pin_x = fx + 20
            clk_pin_y = fy + self.FF_H  # CLK unten am FF

            self.canvas.create_line(
                clk_pin_x, clk_y,
                clk_pin_x, clk_pin_y,
                fill=CLK_COLOR, width=1.5,
            )
            # Verbindungspunkt
            self.canvas.create_oval(
                clk_pin_x - 3, clk_y - 3,
                clk_pin_x + 3, clk_y + 3,
                fill=CLK_COLOR, outline='',
            )

        # ── Rückkopplung: Q → Next-State-Logik ──────────────────────────
        fb_y = feedback_y
        fb_left_x = logic_x - 15
        fb_right_x = ff_start_x + total_ff_w + 15

        # Sammelpunkt unten
        for i, (fx, fy) in enumerate(ff_positions):
            ff_idx = n - 1 - i
            q_x = fx + self.FF_W / 2
            q_bottom_y = fy + self.FF_H

            # Q nach unten
            self.canvas.create_line(
                q_x, q_bottom_y,
                q_x, fb_y,
                fill=FEEDBACK_COLOR, width=1.5,
            )

            # Label am Q-Ausgang
            self.canvas.create_text(
                q_x + 10, q_bottom_y + 10,
                text=var_name(ff_idx), font=FONT_CIRCUIT,
                fill=FEEDBACK_COLOR, anchor=tk.W,
            )

        # Horizontaler Feedback-Bus unten
        self.canvas.create_line(
            ff_positions[0][0] + self.FF_W / 2, fb_y,
            ff_positions[-1][0] + self.FF_W / 2, fb_y,
            fill=FEEDBACK_COLOR, width=2,
        )

        # Feedback links hoch zur Logic-Box
        fb_bus_left = ff_positions[0][0] + self.FF_W / 2
        self.canvas.create_line(
            fb_bus_left, fb_y,
            fb_left_x, fb_y,
            fill=FEEDBACK_COLOR, width=2,
        )
        self.canvas.create_line(
            fb_left_x, fb_y,
            fb_left_x, logic_y + logic_h / 2,
            fill=FEEDBACK_COLOR, width=2,
        )
        self.canvas.create_line(
            fb_left_x, logic_y + logic_h / 2,
            logic_x, logic_y + logic_h / 2,
            fill=FEEDBACK_COLOR, width=2,
            arrow=tk.LAST, arrowshape=(10, 12, 5),
        )

        # Rückkopplungs-Label
        self.canvas.create_text(
            fb_left_x - 5, (fb_y + logic_y + logic_h / 2) / 2,
            text="Rück-\nkopplung",
            font=FONT_SMALL, fill=FEEDBACK_COLOR, anchor=tk.E,
            justify=tk.CENTER,
        )

        # Feedback rechts zur Ausgangslogik
        fb_bus_right = ff_positions[-1][0] + self.FF_W / 2
        out_connect_y = output_y + output_h * 0.7
        self.canvas.create_line(
            fb_bus_right, fb_y,
            fb_right_x, fb_y,
            fill=WIRE_COLOR, width=1.5,
        )
        self.canvas.create_line(
            fb_right_x, fb_y,
            fb_right_x, out_connect_y,
            fill=WIRE_COLOR, width=1.5,
        )
        self.canvas.create_line(
            fb_right_x, out_connect_y,
            output_x, out_connect_y,
            fill=WIRE_COLOR, width=1.5,
            arrow=tk.LAST, arrowshape=(8, 10, 4),
        )

    # ── Hilfs-Zeichenmethoden ────────────────────────────────────────────

    def _draw_flipflop(self, x, y, ff_idx):
        """Zeichnet ein D-Flipflop-Symbol."""
        w, h = self.FF_W, self.FF_H

        # Schatten
        self.canvas.create_rectangle(
            x + 3, y + 3, x + w + 3, y + h + 3,
            fill='#000000', outline='', stipple='gray25',
        )

        # Hauptrechteck
        self.canvas.create_rectangle(
            x, y, x + w, y + h,
            fill=FF_FILL, outline=FF_BORDER, width=2,
        )

        # Header-Bereich
        header_h = 28
        self.canvas.create_rectangle(
            x + 1, y + 1, x + w - 1, y + header_h,
            fill=FF_HEADER, outline='',
        )

        # FF-Name
        self.canvas.create_text(
            x + w / 2, y + header_h / 2,
            text=f"FF{subscript(ff_idx)}", font=FONT_CIRCUIT_LABEL,
            fill=TEXT_BRIGHT, anchor=tk.CENTER,
        )

        # Pin-Labels
        pin_font = FONT_CIRCUIT
        pin_pad = 15

        # D-Eingang (links oben)
        self.canvas.create_text(
            x + pin_pad, y + header_h + 18,
            text="D", font=FONT_CIRCUIT_LABEL, fill=DATA_COLOR, anchor=tk.W,
        )

        # Q-Ausgang (rechts oben)
        self.canvas.create_text(
            x + w - pin_pad, y + header_h + 18,
            text="Q", font=FONT_CIRCUIT_LABEL, fill=OUTPUT_COLOR, anchor=tk.E,
        )

        # Q̄-Ausgang (rechts unten)
        self.canvas.create_text(
            x + w - pin_pad, y + h - 35,
            text="Q\u0304", font=FONT_CIRCUIT_LABEL, fill=TEXT_DIM, anchor=tk.E,
        )

        # CLK (links unten) mit Dreieck-Symbol
        clk_tri_x = x + pin_pad
        clk_tri_y = y + h - 20
        tri_size = 8
        self.canvas.create_polygon(
            clk_tri_x, clk_tri_y - tri_size,
            clk_tri_x + tri_size, clk_tri_y,
            clk_tri_x, clk_tri_y + tri_size,
            fill='', outline=CLK_COLOR, width=1.5,
        )
        self.canvas.create_text(
            clk_tri_x + tri_size + 4, clk_tri_y,
            text="CLK", font=pin_font, fill=CLK_COLOR, anchor=tk.W,
        )

        # Trennlinie
        self.canvas.create_line(
            x + 10, y + h / 2 + 5,
            x + w - 10, y + h / 2 + 5,
            fill=BORDER_COLOR, dash=(3, 3), width=1,
        )

    def _draw_box(self, x, y, w, h, title, lines, fill, border,
                  title_color=TEXT_BRIGHT):
        """Zeichnet eine beschriftete Box (Logik-Block)."""
        # Schatten
        self.canvas.create_rectangle(
            x + 3, y + 3, x + w + 3, y + h + 3,
            fill='#000000', outline='', stipple='gray25',
        )

        # Hauptrechteck (abgerundete Ecken simuliert)
        self.canvas.create_rectangle(
            x, y, x + w, y + h,
            fill=fill, outline=border, width=2,
        )

        # Titel-Bereich
        title_h = 28
        self.canvas.create_rectangle(
            x + 1, y + 1, x + w - 1, y + title_h,
            fill=border, outline='',
        )
        self.canvas.create_text(
            x + w / 2, y + title_h / 2,
            text=title, font=FONT_CIRCUIT_LABEL,
            fill=TEXT_BRIGHT, anchor=tk.CENTER,
        )

        # Gleichungen
        text_y = y + title_h + self.LOGIC_BOX_PAD
        for line in lines:
            self.canvas.create_text(
                x + self.LOGIC_BOX_PAD, text_y,
                text=line, font=FONT_CIRCUIT,
                fill=title_color, anchor=tk.W,
            )
            text_y += 20

    def _get_logic_lines(self):
        """Erzeugt die Textzeilen für die Next-State-Logik-Box."""
        lines = []
        for i in range(self.n - 1, -1, -1):
            name = f'D{subscript(i)}'
            eq = self.divider.equations.get(name, '?')
            lines.append(f'{name} = {eq}')
        return lines

    def _get_output_lines(self):
        """Erzeugt die Textzeilen für die Ausgangslogik-Box."""
        eq = self.divider.equations.get('fout', '?')
        return [f'fout = {eq}']
