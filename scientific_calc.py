import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import math
import functools

# ------------------------------
# Colors / Theme
# ------------------------------
WINDOW_BG = "#F3FFF5"       # pale mint
ENTRY_BG = "#FFFFFF"        # calculator key background (white)
ENTRY_TEXT = "#000000"      # black text on keys
HOVER_COLOR = "#B3E5FC"     # light blue hover
BTN_PRESS = "#80DEEA"       # pressed shade
ACCENT = "#01579B"          # accent (for labels/toggles)

# ------------------------------
# Safe eval environment (with degree/radian mode)
# ------------------------------
class EvalEnv:
    def __init__(self):
        self.deg_mode = True

    def toggle_deg(self):
        self.deg_mode = not self.deg_mode

    # degree-aware wrappers
    def sin(self, x):
        return math.sin(math.radians(x)) if self.deg_mode else math.sin(x)
    def cos(self, x):
        return math.cos(math.radians(x)) if self.deg_mode else math.cos(x)
    def tan(self, x):
        return math.tan(math.radians(x)) if self.deg_mode else math.tan(x)
    def asin(self, x):
        r = math.asin(x)
        return math.degrees(r) if self.deg_mode else r
    def acos(self, x):
        r = math.acos(x)
        return math.degrees(r) if self.deg_mode else r
    def atan(self, x):
        r = math.atan(x)
        return math.degrees(r) if self.deg_mode else r

    def sqrt(self, x):
        return math.sqrt(x)
    def cbrt(self, x):
        return math.copysign(abs(x) ** (1.0/3.0), x)
    def root(self, x, n):
        # n-th root of x -> x ** (1/n)
        return math.copysign(abs(x) ** (1.0/float(n)), x)
    def ln(self, x):
        return math.log(x)
    def log10(self, x):
        return math.log10(x)
    def log(self, x, base=10):
        return math.log(x, base)
    def fact(self, n):
        n_int = int(n)
        if n_int < 0:
            raise ValueError("factorial not defined for negative")
        return math.factorial(n_int)
    def exp(self, x):
        return math.exp(x)
    def pow(self, x, y):
        return math.pow(x, y)
    def inv(self, x):
        return 1.0 / x
    def e(self):
        return math.e

    def namespace(self):
        ns = {
            'pi': math.pi,
            'e': math.e,
            'sin': self.sin,
            'cos': self.cos,
            'tan': self.tan,
            'asin': self.asin,
            'acos': self.acos,
            'atan': self.atan,
            'sqrt': self.sqrt,
            'cbrt': self.cbrt,
            'root': self.root,
            'ln': self.ln,
            'log10': self.log10,
            'log': self.log,
            'fact': self.fact,
            'exp': self.exp,
            'pow': self.pow,
            'inv': self.inv,
            # safe wrappers from math
            'abs': abs,
            'round': round,
        }
        # add a few math helpers
        for fn in ['sin','cos','tan','asin','acos','atan','sqrt','exp','log','log10','pow']:
            pass
        return ns

def safe_eval(expr, env: EvalEnv):
    # replace unicode pi if present
    expr = expr.replace('π', 'pi')
    expr = expr.replace('^', '**')
    if "__" in expr:
        raise ValueError("Invalid expression")
    ns = env.namespace()
    try:
        return eval(expr, {"__builtins__": None}, ns)
    except Exception as e:
        raise

# ------------------------------
# Rounded Button using Canvas
# ------------------------------
class RoundedButton(tk.Canvas):
    def __init__(self, master, text, command=None, width=80, height=48,
                 radius=16, bg=ENTRY_BG, fg=ENTRY_TEXT, hover=HOVER_COLOR, pressed=BTN_PRESS,
                 font=("Segoe UI", 11, "bold")):
        tk.Canvas.__init__(self, master, width=width, height=height, highlightthickness=0, bg=master['bg'])
        self.command = command
        self.radius = radius
        self.bg = bg
        self.fg = fg
        self.hover_col = hover
        self.pressed_col = pressed
        self.font = font
        self._text = text
        self._width = width
        self._height = height
        self._is_pressed = False
        self._draw(bg)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<ButtonPress-1>", self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)

    def _draw(self, color):
        self.delete("all")
        w = self._width
        h = self._height
        r = self.radius
        # rounded rectangle (two arcs + rects)
        self.create_arc((0, 0, r*2, r*2), start=90, extent=90, fill=color, outline=color)
        self.create_arc((w-2*r, 0, w, r*2), start=0, extent=90, fill=color, outline=color)
        self.create_arc((0, h-2*r, r*2, h), start=180, extent=90, fill=color, outline=color)
        self.create_arc((w-2*r, h-2*r, w, h), start=270, extent=90, fill=color, outline=color)
        self.create_rectangle((r, 0, w-r, h), fill=color, outline=color)
        self.create_rectangle((0, r, w, h-r), fill=color, outline=color)
        # text
        self.create_text(w/2, h/2, text=self._text, fill=self.fg, font=self.font, tags="btn_text")

    def _on_enter(self, event):
        if not self._is_pressed:
            self._draw(self.hover_col)

    def _on_leave(self, event):
        if not self._is_pressed:
            self._draw(self.bg)

    def _on_press(self, event):
        self._is_pressed = True
        self._draw(self.pressed_col)

    def _on_release(self, event):
        if self._is_pressed:
            self._is_pressed = False
            self._draw(self.hover_col)
            if self.command:
                self.command()

# allow changing text
    def set_text(self, t):
        self._text = t
        self._draw(self.bg)

# ------------------------------
# Main Application
# ------------------------------
class ScientificAppbySundram(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Scientific Calculator + Unit Converter by Sundram")
        self.configure(bg=WINDOW_BG)
        self.geometry("520x760")
        self.resizable(False, False)

        self.env = EvalEnv()
        self.history = []  # list of strings

        # Notebook
        style = ttk.Style(self)
        style.theme_use("default")
        style.configure("TNotebook", background=WINDOW_BG)
        style.configure("TNotebook.Tab", padding=[12,8], font=("Segoe UI", 12, "bold"))

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(expand=True, fill="both", padx=10, pady=10)

        # Tabs
        self.tab_calc = tk.Frame(self.notebook, bg=WINDOW_BG)
        self.tab_conv = tk.Frame(self.notebook, bg=WINDOW_BG)
        self.tab_history = tk.Frame(self.notebook, bg=WINDOW_BG)

        self.notebook.add(self.tab_calc, text="Calculator")
        self.notebook.add(self.tab_conv, text="Converter")
        self.notebook.add(self.tab_history, text="History")

        self._build_calculator_tab()
        self._build_converter_tab()
        self._build_history_tab()

    # ------------------------------
    # Calculator Tab
    # ------------------------------
    def _build_calculator_tab(self):
        top = tk.Frame(self.tab_calc, bg=WINDOW_BG)
        top.pack(fill="x", padx=10, pady=(8,6))

        # mode & controls
        left_ctrl = tk.Frame(top, bg=WINDOW_BG)
        left_ctrl.pack(side="left", anchor="nw")

        self.mode_label = tk.Label(left_ctrl, text="Mode: DEG", fg=ACCENT, bg=WINDOW_BG, font=("Segoe UI", 10, "bold"))
        self.mode_label.pack(anchor="w", pady=2)

        def toggle_deg():
            self.env.toggle_deg()
            self.mode_label.config(text="Mode: " + ("DEG" if self.env.deg_mode else "RAD"))
        RoundedButton(left_ctrl, text="Toggle\nDeg/Rad", command=toggle_deg, width=96, height=44).pack(padx=4, pady=4)

        # entry area
        entry_frame = tk.Frame(self.tab_calc, bg=WINDOW_BG)
        entry_frame.pack(fill="x", padx=14, pady=4)

        # calculator entry (disable direct keyboard typing)
        self.calc_entry = tk.Entry(entry_frame, font=("Segoe UI", 22), bd=0, relief="flat",
                                   justify="right", bg="#F9F9F9", fg="#111")
        self.calc_entry.pack(fill="x", padx=6, pady=6, ipady=8)
        # block keyboard typing in calculator entry (buttons-only)
        self.calc_entry.bind("<Key>", lambda e: "break")

        # small label for expression/result
        self.result_var = tk.StringVar()
        tk.Label(entry_frame, textvariable=self.result_var, bg=WINDOW_BG, fg=ACCENT, anchor="e",
                 font=("Segoe UI", 10)).pack(fill="x", padx=6)

        # keypad layout (rounded buttons)
        keypad = tk.Frame(self.tab_calc, bg=WINDOW_BG)
        keypad.pack(padx=10, pady=6)

        # top row: brackets, backspace, clear, factorial
        row0 = tk.Frame(keypad, bg=WINDOW_BG)
        row0.pack(fill="x", pady=4)
        RoundedButton(row0, text="(", command=lambda: self._insert("("), width=72, height=44).pack(side="left", padx=6)
        RoundedButton(row0, text=")", command=lambda: self._insert(")"), width=72, height=44).pack(side="left", padx=6)
        RoundedButton(row0, text="⌫", command=self._backspace, width=72, height=44).pack(side="left", padx=6)
        RoundedButton(row0, text="C", command=self._clear, width=72, height=44).pack(side="left", padx=6)
        RoundedButton(row0, text="n!", command=lambda: self._insert("fact("), width=72, height=44).pack(side="left", padx=6)

        # second row: trig dropdown, log dropdown, inverse, sqrt
        row1 = tk.Frame(keypad, bg=WINDOW_BG)
        row1.pack(fill="x", pady=4)

        # Trig dropdown (as OptionMenu)
        trig_var = tk.StringVar(value="sin")
        trig_menu = ttk.OptionMenu(row1, trig_var, "sin", "sin", "cos", "tan", "asin", "acos", "atan")
        trig_menu.config(width=8)
        trig_menu.pack(side="left", padx=6)
        RoundedButton(row1, text="Apply", command=lambda: self._apply_trig(trig_var.get()), width=72, height=44).pack(side="left", padx=6)

        # Log dropdown
        log_var = tk.StringVar(value="log10")
        log_menu = ttk.OptionMenu(row1, log_var, "log10", "log10", "ln", "log")
        log_menu.config(width=8)
        log_menu.pack(side="left", padx=6)
        # Log apply button: for 'log' for base
        def apply_log():
            fn = log_var.get()
            if fn == "log":
                base = simpledialog.askfloat("Log base", "Enter base:", parent=self)
                if base is None:
                    return
                self._insert(f"log(")
                # user will need to input "x,base)" so we prefill base? Instead we call eval directly:
                try:
                    x = float(self.calc_entry.get())
                    res = self.env.log(x, base)
                    self._set_result(str(res))
                    self._add_history(f"log({x},{base}) = {res}")
                except Exception as e:
                    self._set_result("Error")
            else:
                RoundedButton(row1, text="Apply", command=lambda: self._apply_log(fn), width=72, height=44).pack_forget() # noop
        RoundedButton(row1, text="Apply", command=lambda: self._apply_log(log_var.get()), width=72, height=44).pack(side="left", padx=6)

        RoundedButton(row1, text="1/x", command=self._inverse, width=72, height=44).pack(side="left", padx=6)
        RoundedButton(row1, text="√", command=lambda: self._insert("sqrt("), width=72, height=44).pack(side="left", padx=6)

        # third row: numbers and operators (4x)
        nums = [
            ("7","8","9","/"),
            ("4","5","6","*"),
            ("1","2","3","-"),
            ("0",".","π","+")
        ]
        for r in nums:
            row = tk.Frame(keypad, bg=WINDOW_BG)
            row.pack(fill="x", pady=4)
            for val in r:
                RoundedButton(row, text=val, command=lambda v=val: self._insert(v), width=88, height=54).pack(side="left", padx=6)

        # fourth row: power, y-root, cbrt, exp, x^y
        row3 = tk.Frame(keypad, bg=WINDOW_BG)
        row3.pack(fill="x", pady=6)
        RoundedButton(row3, text="x²", command=lambda: self._insert("**2"), width=84, height=52).pack(side="left", padx=6)
        RoundedButton(row3, text="xʸ", command=lambda: self._insert("**"), width=84, height=52).pack(side="left", padx=6)
        RoundedButton(row3, text="³√", command=lambda: self._insert("cbrt("), width=84, height=52).pack(side="left", padx=6)
        RoundedButton(row3, text="y√x", command=lambda: self._insert("root("), width=84, height=52).pack(side="left", padx=6)
        RoundedButton(row3, text="eˣ", command=lambda: self._insert("exp("), width=84, height=52).pack(side="left", padx=6)

        # equals & history quick-add
        bottom_row = tk.Frame(self.tab_calc, bg=WINDOW_BG)
        bottom_row.pack(fill="x", pady=8)
        RoundedButton(bottom_row, text="=", command=self._evaluate_and_store, width=420, height=56).pack(side="left", padx=8)

    # insert text into calc entry
    def _insert(self, s):
        self.calc_entry.insert(tk.END, s)

    def _backspace(self):
        cur = self.calc_entry.get()
        if cur:
            self.calc_entry.delete(len(cur)-1, tk.END)

    def _clear(self):
        self.calc_entry.delete(0, tk.END)
        self.result_var.set("")

    def _inverse(self):
        try:
            val = float(self.calc_entry.get())
            res = 1.0 / val
            self.calc_entry.delete(0, tk.END)
            self.calc_entry.insert(0, str(res))
            self._add_history(f"1/({val}) = {res}")
        except:
            self._set_result("Error")

    def _apply_trig(self, fn_name):
        try:
            val = float(self.calc_entry.get())
            fn = getattr(self.env, fn_name)
            res = fn(val)
            self.calc_entry.delete(0, tk.END)
            self.calc_entry.insert(0, str(res))
            self._add_history(f"{fn_name}({val}) = {res}")
        except Exception as e:
            self._set_result("Error")

    def _apply_log(self, fn_name):
        try:
            val = float(self.calc_entry.get())
            if fn_name == "log10":
                res = self.env.log10(val)
            elif fn_name == "ln":
                res = self.env.ln(val)
            else:
                res = self.env.log(val)
            self.calc_entry.delete(0, tk.END)
            self.calc_entry.insert(0, str(res))
            self._add_history(f"{fn_name}({val}) = {res}")
        except:
            self._set_result("Error")

    def _set_result(self, text):
        self.result_var.set(text)

    def _evaluate_and_store(self):
        expr = self.calc_entry.get().strip()
        if not expr:
            return
        try:
            val = safe_eval(expr, self.env)
            # format
            if isinstance(val, float):
                out = "{:.12g}".format(val)
            else:
                out = str(val)
            self.calc_entry.delete(0, tk.END)
            self.calc_entry.insert(0, out)
            self._set_result(out)
            self._add_history(f"{expr} = {out}")
        except Exception as e:
            self._set_result("Error")
            messagebox.showerror("Error", f"Could not evaluate expression:\n{e}")

    def _add_history(self, text):
        self.history.append(text)
        # update history tab listbox if exists
        if hasattr(self, 'history_listbox'):
            self.history_listbox.insert(tk.END, text)

    # ------------------------------
    # Converter Tab
    # ------------------------------
    def _build_converter_tab(self):
        frame = tk.Frame(self.tab_conv, bg=WINDOW_BG)
        frame.pack(fill="both", expand=True, padx=12, pady=12)

        # category selection
        tk.Label(frame, text="Category:", bg=WINDOW_BG, fg=ACCENT, font=("Segoe UI", 11, "bold")).grid(row=0, column=0, sticky="w")
        categories = ["Length","Mass","Volume","Speed","Temperature","Area","Power"]
        self.cat_var = tk.StringVar(value="Length")
        cat_menu = ttk.OptionMenu(frame, self.cat_var, categories[0], *categories, command=self._on_cat_change)
        cat_menu.grid(row=0, column=1, sticky="w", padx=8, pady=6)

        # from/to unit
        tk.Label(frame, text="From:", bg=WINDOW_BG).grid(row=1, column=0, sticky="w")
        self.from_var = tk.StringVar()
        self.from_menu = ttk.OptionMenu(frame, self.from_var, "")
        self.from_menu.grid(row=1, column=1, sticky="w", padx=8, pady=6)

        tk.Label(frame, text="To:", bg=WINDOW_BG).grid(row=2, column=0, sticky="w")
        self.to_var = tk.StringVar()
        self.to_menu = ttk.OptionMenu(frame, self.to_var, "")
        self.to_menu.grid(row=2, column=1, sticky="w", padx=8, pady=6)

        # value entry
        tk.Label(frame, text="Value:", bg=WINDOW_BG).grid(row=3, column=0, sticky="w")
        self.conv_entry = tk.Entry(frame, bg="#FFFFFF", fg="#111", font=("Segoe UI", 12), bd=1, relief="solid")
        self.conv_entry.grid(row=3, column=1, sticky="we", padx=8, pady=6)

        # convert button and result
        RoundedButton(frame, text="Convert", command=self._do_convert, width=120, height=44).grid(row=4, column=0, pady=10, padx=6)
        self.conv_result_var = tk.StringVar()
        tk.Label(frame, textvariable=self.conv_result_var, bg=WINDOW_BG, fg=ACCENT, font=("Segoe UI", 12, "bold")).grid(row=4, column=1, sticky="w")

        # fill initial
        self._on_cat_change("Length")

    def _on_cat_change(self, cat):
        menu_from = self.from_menu["menu"]
        menu_to = self.to_menu["menu"]
        menu_from.delete(0, "end")
        menu_to.delete(0, "end")

        if cat == "Length":
            units = ["km","m","cm","mm","inch","foot","yard","mile"]
            conv_to_m = {
                "km":1000.0, "m":1.0, "cm":0.01, "mm":0.001,
                "inch":0.0254, "foot":0.3048, "yard":0.9144, "mile":1609.344
            }
            self._conv_to_base = lambda v,u: v * conv_to_m[u]
            self._conv_from_base = lambda v,u: v / conv_to_m[u]
        elif cat == "Mass":
            units = ["t","q","kg","g","mg","ct","lb","oz"]  # t: tonne, q: quintal, ct: carat
            conv_to_kg = {"t":1000.0, "q":100.0, "kg":1.0, "g":0.001, "mg":0.000001, "ct":0.0002, "lb":0.45359237, "oz":0.028349523125}
            self._conv_to_base = lambda v,u: v * conv_to_kg[u]
            self._conv_from_base = lambda v,u: v / conv_to_kg[u]
        elif cat == "Volume":
            units = ["mL","L","cup","pint","quart","gallon","m³"]
            conv_to_L = {"mL":0.001,"L":1.0,"cup":0.24,"pint":0.473176,"quart":0.946353,"gallon":3.78541,"m³":1000.0}
            self._conv_to_base = lambda v,u: v * conv_to_L[u]
            self._conv_from_base = lambda v,u: v / conv_to_L[u]
        elif cat == "Speed":
            units = ["m/s","km/h","mph"]
            conv_to_ms = {"m/s":1.0,"km/h":1/3.6,"mph":0.44704}
            self._conv_to_base = lambda v,u: v * conv_to_ms[u]
            self._conv_from_base = lambda v,u: v / conv_to_ms[u]
        elif cat == "Temperature":
            units = ["C","F","K"]
            def to_c(v,u):
                if u=="C": return v
                if u=="F": return (v-32)*5.0/9.0
                if u=="K": return v-273.15
            def from_c(v,u):
                if u=="C": return v
                if u=="F": return v*9.0/5.0+32
                if u=="K": return v+273.15
            self._conv_to_base = to_c
            self._conv_from_base = from_c
            units = ["C","F","K"]
        elif cat == "Area":
            units = ["m²","cm²","km²","ft²","acre","hectare"]
            conv_to_m2 = {"m²":1.0,"cm²":0.0001,"km²":1e6,"ft²":0.092903,"acre":4046.8564224,"hectare":10000.0}
            self._conv_to_base = lambda v,u: v * conv_to_m2[u]
            self._conv_from_base = lambda v,u: v / conv_to_m2[u]
        elif cat == "Power":
            units = ["W","kW","hp"]
            conv_to_w = {"W":1.0,"kW":1000.0,"hp":745.699872}
            self._conv_to_base = lambda v,u: v * conv_to_w[u]
            self._conv_from_base = lambda v,u: v / conv_to_w[u]
        else:
            units = []
            self._conv_to_base = lambda v,u: v
            self._conv_from_base = lambda v,u: v

        # populate menus
        if units:
            self.from_var.set(units[0])
            self.to_var.set(units[1] if len(units)>1 else units[0])
        else:
            self.from_var.set("")
            self.to_var.set("")

        for u in units:
            menu_from.add_command(label=u, command=lambda v=u: self.from_var.set(v))
            menu_to.add_command(label=u, command=lambda v=u: self.to_var.set(v))

    def _do_convert(self):
        cat = self.cat_var.get()
        from_u = self.from_var.get()
        to_u = self.to_var.get()
        try:
            v = float(self.conv_entry.get())
        except:
            messagebox.showerror("Input error", "Please enter a numeric value")
            return
        try:
            base = self._conv_to_base(v, from_u)
            res = self._conv_from_base(base, to_u)
            # format nicely
            if isinstance(res, float):
                out = "{:.12g}".format(res)
            else:
                out = str(res)
            self.conv_result_var.set(out)
            self._add_history(f"Convert ({cat}): {v} {from_u} -> {out} {to_u}")
        except Exception as e:
            messagebox.showerror("Conversion error", str(e))

    # ------------------------------
    # History Tab
    # ------------------------------
    def _build_history_tab(self):
        frame = tk.Frame(self.tab_history, bg=WINDOW_BG)
        frame.pack(fill="both", expand=True, padx=12, pady=12)

        tk.Label(frame, text="History (click to re-use)", bg=WINDOW_BG, fg=ACCENT, font=("Segoe UI", 11, "bold")).pack(anchor="w")

        listbox_frame = tk.Frame(frame, bg=WINDOW_BG)
        listbox_frame.pack(fill="both", expand=True, pady=8)

        self.history_listbox = tk.Listbox(listbox_frame, font=("Segoe UI", 11))
        self.history_listbox.pack(side="left", fill="both", expand=True)
        self.history_listbox.bind("<Double-Button-1>", self._on_history_double)

        scrollbar = tk.Scrollbar(listbox_frame, orient="vertical", command=self.history_listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.history_listbox.config(yscrollcommand=scrollbar.set)

        btns = tk.Frame(frame, bg=WINDOW_BG)
        btns.pack(fill="x")
        RoundedButton(btns, text="Clear History", command=self._clear_history, width=160, height=44).pack(side="left", padx=6)
        RoundedButton(btns, text="Copy Selected", command=self._copy_selected_history, width=160, height=44).pack(side="left", padx=6)

    def _on_history_double(self, event):
        sel = self.history_listbox.curselection()
        if not sel:
            return
        text = self.history_listbox.get(sel[0])
        # if it is an "expr = result" style, extract left side
        if "=" in text:
            expr = text.split("=",1)[0].strip()
            self.notebook.select(self.tab_calc)
            self.calc_entry.delete(0, tk.END)
            self.calc_entry.insert(0, expr)
        else:
            self.calc_entry.delete(0, tk.END)
            self.calc_entry.insert(0, text)

    def _clear_history(self):
        if messagebox.askyesno("Clear", "Clear all history?"):
            self.history_listbox.delete(0, tk.END)
            self.history.clear()

    def _copy_selected_history(self):
        sel = self.history_listbox.curselection()
        if not sel:
            return
        text = self.history_listbox.get(sel[0])
        self.clipboard_clear()
        self.clipboard_append(text)
        messagebox.showinfo("Copied", "History item copied to clipboard")

# ------------------------------
# Run app
# ------------------------------
if __name__ == "__main__":
    app = ScientificAppbySundram()
    app.mainloop()
