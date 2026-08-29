"""Kernlogik für den D-Flipflop Frequenzteiler.

Berechnet Zustandstabelle, boolesche Gleichungen (Quine-McCluskey-minimiert)
und alle Daten für die Visualisierung.
"""

import math

# ── Unicode-Hilfsfunktionen ──────────────────────────────────────────────────

SUBSCRIPTS = '₀₁₂₃₄₅₆₇₈₉'


def subscript(n):
    """Wandelt eine Zahl in Unicode-Subskript um. z.B. 12 → '₁₂'"""
    return ''.join(SUBSCRIPTS[int(d)] for d in str(n))


def var_name(idx, inverted=False):
    """Erzeugt Variablenname. var_name(2) → 'Q₂', var_name(1, True) → 'Q̄₁'"""
    sub = subscript(idx)
    if inverted:
        return f'\u0051\u0304{sub}'   # Q̄ + subscript
    return f'Q{sub}'


def d_name(idx):
    """Erzeugt D-Eingangsname. d_name(0) → 'D₀'"""
    return f'D{subscript(idx)}'


# ── Quine-McCluskey Minimierung ──────────────────────────────────────────────

def _to_binary_tuple(val, n):
    """Wandelt val in ein n-Bit Tupel um (MSB first)."""
    return tuple((val >> (n - 1 - i)) & 1 for i in range(n))


def _count_ones(term):
    """Zählt die '1'-Werte in einem Term (ignoriert Don't-Cares = 2)."""
    return sum(1 for v in term if v == 1)


def quine_mccluskey(minterms, dont_cares, num_vars):
    """Quine-McCluskey Minimierung.

    Args:
        minterms: Liste von Minterm-Indizes (Funktion = 1)
        dont_cares: Liste von Don't-Care-Indizes
        num_vars: Anzahl der Eingangsvariablen

    Returns:
        Liste von Prime-Implicant-Tupeln (ausgewählte Überdeckung)
    """
    if not minterms:
        return []

    all_terms = set(minterms) | set(dont_cares)

    # Initialisierung: Jeder Term als Binärtupel mit Abdeckungsmenge
    current = {}
    for t in all_terms:
        bt = _to_binary_tuple(t, num_vars)
        if bt in current:
            current[bt] = current[bt] | frozenset({t})
        else:
            current[bt] = frozenset({t})

    all_prime_implicants = []

    # ── Kombinations-Schleife ────────────────────────────────────────────
    while current:
        next_level = {}
        used = set()
        terms_list = list(current.keys())

        for i in range(len(terms_list)):
            for j in range(i + 1, len(terms_list)):
                t1, t2 = terms_list[i], terms_list[j]

                # Prüfe Kompatibilität: Don't-Care-Positionen müssen übereinstimmen
                diff = []
                compatible = True
                for pos in range(num_vars):
                    v1, v2 = t1[pos], t2[pos]
                    if v1 == 2 and v2 == 2:
                        continue
                    elif v1 == 2 or v2 == 2:
                        compatible = False
                        break
                    elif v1 != v2:
                        diff.append(pos)

                if not compatible or len(diff) != 1:
                    continue

                # Kombination möglich: Position wird zu Don't-Care
                pos = diff[0]
                new_term = tuple(2 if k == pos else t1[k] for k in range(num_vars))
                covered = current[t1] | current[t2]

                if new_term in next_level:
                    next_level[new_term] = next_level[new_term] | covered
                else:
                    next_level[new_term] = covered

                used.add(t1)
                used.add(t2)

        # Nicht-kombinierte Terme sind Prime Implicants
        for term in terms_list:
            if term not in used:
                all_prime_implicants.append((term, current[term]))

        current = next_level

    # ── Minimale Überdeckung (Essential + Greedy) ────────────────────────
    uncovered = set(minterms)
    selected = []

    # 1. Essentielle Prime Implicants finden
    for m in sorted(uncovered):
        covering = [(pi, cov) for pi, cov in all_prime_implicants if m in cov]
        if len(covering) == 1:
            pi, cov = covering[0]
            if (pi, cov) not in selected:
                selected.append((pi, cov))
                uncovered -= (cov & set(minterms))

    # 2. Greedy für restliche Minterme
    remaining = [(pi, cov) for pi, cov in all_prime_implicants
                 if (pi, cov) not in selected]
    while uncovered and remaining:
        best = max(remaining, key=lambda x: len(x[1] & uncovered))
        if not (best[1] & uncovered):
            break
        selected.append(best)
        uncovered -= (best[1] & set(minterms))
        remaining.remove(best)

    return selected


def _implicants_to_expression(implicants, num_vars):
    """Wandelt eine Liste von Prime Implicants in einen SOP-Ausdruck um."""
    if not implicants:
        return '0'

    terms = []
    for pi, _ in implicants:
        literals = []
        for i, val in enumerate(pi):
            ff_idx = num_vars - 1 - i  # MSB-first → FF-Index
            if val == 1:
                literals.append(var_name(ff_idx, inverted=False))
            elif val == 0:
                literals.append(var_name(ff_idx, inverted=True))
            # val == 2: Variable kommt nicht vor (Don't-Care-Position)

        if not literals:
            return '1'
        terms.append('·'.join(literals))

    return ' + '.join(terms)


# ── Frequenzteiler-Klasse ────────────────────────────────────────────────────

class FrequencyDivider:
    """Berechnet die vollständige Logik eines synchronen Frequenzteilers.

    Attributes:
        N: Teilungsfaktor (fout = fin / N)
        k: Duty-Cycle-Zähler (Ausgang HIGH für k Takte)
        n: Anzahl benötigter D-Flipflops
        num_states: Gesamtzahl möglicher Zustände (2^n)
        state_table: Liste der Zustandszeilen
        equations: Dict mit booleschen Gleichungen {Name: Ausdruck}
        raw_equations: Dict mit Prime-Implicant-Daten für Zeichnung
    """

    def __init__(self, N, k):
        """Erstellt einen Frequenzteiler.

        Args:
            N: Teilungsfaktor (≥ 2)
            k: Duty-Cycle-Zähler (1 ≤ k < N)

        Raises:
            ValueError: Bei ungültigen Parametern
        """
        if N < 2:
            raise ValueError("Teilungsfaktor N muss ≥ 2 sein.")
        if k < 1 or k >= N:
            raise ValueError(f"Duty-Cycle-Zähler k muss zwischen 1 und {N-1} liegen.")

        self.N = N
        self.k = k
        self.n = max(1, math.ceil(math.log2(N))) if N > 1 else 1
        # Sonderfall: N ist eine Zweierpotenz
        if 2 ** self.n < N:
            self.n += 1
        self.num_states = 2 ** self.n

        self.state_table = self._generate_state_table()
        self.equations, self.raw_equations = self._derive_all_equations()

    def _generate_state_table(self):
        """Erzeugt die vollständige Zustandstabelle."""
        table = []
        for state in range(self.num_states):
            if state < self.N:
                next_state = (state + 1) % self.N
                output = 1 if state < self.k else 0
                used = True
            else:
                next_state = 0   # Ungültige Zustände → Reset
                output = 0
                used = False

            table.append({
                'state': state,
                'current_bits': self._to_bits(state),
                'next_bits': self._to_bits(next_state),
                'output': output,
                'used': used,
            })
        return table

    def _to_bits(self, val):
        """Wandelt val in eine n-Bit-Liste um (MSB first)."""
        return [(val >> (self.n - 1 - i)) & 1 for i in range(self.n)]

    def _derive_all_equations(self):
        """Leitet alle booleschen Gleichungen ab und minimiert sie."""
        equations = {}
        raw = {}

        # ── D-Eingänge ───────────────────────────────────────────────────
        for bit_pos in range(self.n):
            ff_idx = self.n - 1 - bit_pos  # FF-Index (0 = LSB)
            name = f'D{subscript(ff_idx)}'

            minterms = []
            dont_cares = []
            for row in self.state_table:
                if not row['used']:
                    dont_cares.append(row['state'])
                elif row['next_bits'][bit_pos] == 1:
                    minterms.append(row['state'])

            pis = quine_mccluskey(minterms, dont_cares, self.n)
            expr = _implicants_to_expression(pis, self.n)

            # Prüfe ob Funktion immer 1 ist
            all_used = [r['state'] for r in self.state_table if r['used']]
            if set(minterms) == set(all_used):
                expr = '1'
            if not minterms:
                expr = '0'
            # Prüfe ob alle Zustände (inkl. DC) abgedeckt
            if set(minterms) | set(dont_cares) == set(range(self.num_states)):
                expr = '1'

            equations[name] = expr
            raw[name] = {'minterms': minterms, 'dont_cares': dont_cares, 'pis': pis}

        # ── Ausgang ──────────────────────────────────────────────────────
        out_minterms = []
        out_dont_cares = []
        for row in self.state_table:
            if not row['used']:
                out_dont_cares.append(row['state'])
            elif row['output'] == 1:
                out_minterms.append(row['state'])

        pis = quine_mccluskey(out_minterms, out_dont_cares, self.n)
        expr = _implicants_to_expression(pis, self.n)

        all_used = [r['state'] for r in self.state_table if r['used']]
        if set(out_minterms) == set(all_used):
            expr = '1'
        if not out_minterms:
            expr = '0'
        if set(out_minterms) | set(out_dont_cares) == set(range(self.num_states)):
            expr = '1'

        equations['fout'] = expr
        raw['fout'] = {'minterms': out_minterms, 'dont_cares': out_dont_cares, 'pis': pis}

        return equations, raw

    # ── Hilfsmethoden für UI ─────────────────────────────────────────────

    def get_ff_names(self):
        """Gibt die FF-Namen als Liste zurück: ['Q₀', 'Q₁', ...]"""
        return [var_name(i) for i in range(self.n)]

    def get_d_names(self):
        """Gibt die D-Eingangsnamen zurück: ['D₀', 'D₁', ...]"""
        return [d_name(i) for i in range(self.n)]

    def get_equations_text(self):
        """Gibt einen formatierten Text aller Gleichungen zurück."""
        lines = []
        # D-Gleichungen (höchstes Bit zuerst)
        for i in range(self.n - 1, -1, -1):
            name = f'D{subscript(i)}'
            lines.append(f'{name} = {self.equations[name]}')
        lines.append('')
        lines.append(f'fout = {self.equations["fout"]}')
        return '\n'.join(lines)

    def get_timing_sequence(self, num_periods=3):
        """Erzeugt die Signalverläufe für das Timing-Diagramm.

        Returns:
            Dict mit Signalnamen → Liste von (Wert, Dauer)-Tupeln
        """
        total_clocks = self.N * num_periods
        signals = {}

        # CLK-Signal
        clk = []
        for _ in range(total_clocks):
            clk.append((1, 0.5))
            clk.append((0, 0.5))
        signals['CLK (fin)'] = clk

        # Zustandsfolge berechnen
        state_sequence = []
        state = 0
        for _ in range(total_clocks):
            state_sequence.append(state)
            state = (state + 1) % self.N

        # Q-Signale
        for bit_idx in range(self.n):
            ff_idx = self.n - 1 - bit_idx  # MSB first in display
            signal = []
            for s in state_sequence:
                bit_val = (s >> ff_idx) & 1
                signal.append((bit_val, 1.0))
            signals[var_name(ff_idx)] = signal

        # fout-Signal
        fout = []
        for s in state_sequence:
            out_val = 1 if s < self.k else 0
            fout.append((out_val, 1.0))
        signals['fout'] = fout

        return signals, state_sequence

    def get_summary(self):
        """Gibt eine Zusammenfassung als Text zurück."""
        return (
            f"Frequenzteiler ÷{self.N}  |  "
            f"Duty-Cycle: {self.k}/{self.N} "
            f"({self.k/self.N*100:.1f}%)  |  "
            f"{self.n} D-Flipflop{'s' if self.n > 1 else ''} benötigt  |  "
            f"{self.N} von {self.num_states} Zuständen genutzt"
        )
