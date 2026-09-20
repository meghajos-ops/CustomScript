import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox
import re
import random


class ModernLanguageIDE:
    def __init__(self, root):
        self.root = root
        self.root.title("CustomScript Developer Studio")
        self.root.geometry("1250x780")
        self.root.minsize(950, 620)

        self.bg = "#0B0E13"
        self.chrome = "#10141B"
        self.sidebar_bg = "#0D1117"
        self.editor_bg = "#0B0F14"
        self.terminal_bg = "#080B10"
        self.line_bg = "#0D1219"
        self.border = "#202733"
        self.text = "#DCE3EA"
        self.muted = "#687586"
        self.accent = "#22D3EE"
        self.success = "#4ADE80"
        self.error = "#F87171"

        self.current_file = None
        self.panel_visible = True
        self.sidebar_visible = True
        self.active_panel = "output"
        self.active_tab = None
        self.documents = {}
        self.tab_buttons = {}
        self.problems = []
        self.search_visible = False
        self._loading_document = False
        self._folds = {}
        self._diagnostic_count = 0
        self._diagnostic_lines = {}
        self._autocomplete_popup = None
        self._autocomplete_list = None

        self.root.configure(bg=self.bg)
        self._build_menu()
        self._build_ui()
        self._load_starter()
        self._ensure_documents()
        self.reset_memory()
        self._update_line_numbers()
        self._schedule_highlight(delay=1)
        self._set_status("Ready")
        self._run_live_diagnostics()

    # ========================= UI =========================
    def _build_menu(self):
        menubar = tk.Menu(self.root, bg=self.chrome, fg=self.text,
                          activebackground="#1B2732", activeforeground=self.accent,
                          tearoff=False, bd=0)

        file_menu = tk.Menu(menubar, tearoff=False, bg=self.chrome, fg=self.text,
                            activebackground="#1B2732", activeforeground=self.accent)
        file_menu.add_command(label="New", accelerator="Ctrl+N", command=self.new_file)
        file_menu.add_command(label="Open...", accelerator="Ctrl+O", command=self.open_file)
        file_menu.add_command(label="Save", accelerator="Ctrl+S", command=self.save_file)
        file_menu.add_command(label="Save As...", command=self.save_as)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.destroy)
        menubar.add_cascade(label="File", menu=file_menu)

        edit_menu = tk.Menu(menubar, tearoff=False, bg=self.chrome, fg=self.text,
                            activebackground="#1B2732", activeforeground=self.accent)
        edit_menu.add_command(label="Undo", accelerator="Ctrl+Z", command=lambda: self.editor.event_generate("<<Undo>>"))
        edit_menu.add_command(label="Redo", accelerator="Ctrl+Y", command=lambda: self.editor.event_generate("<<Redo>>"))
        edit_menu.add_separator()
        edit_menu.add_command(label="Select All", accelerator="Ctrl+A", command=self.select_all)
        menubar.add_cascade(label="Edit", menu=edit_menu)

        view_menu = tk.Menu(menubar, tearoff=False, bg=self.chrome, fg=self.text,
                            activebackground="#1B2732", activeforeground=self.accent)
        view_menu.add_command(label="Toggle Explorer", command=self.toggle_sidebar)
        view_menu.add_command(label="Toggle Bottom Panel", command=self.toggle_panel)
        view_menu.add_command(label="Show Output", command=lambda: self.show_panel("output"))
        view_menu.add_command(label="Show Terminal", command=lambda: self.show_panel("terminal"))
        menubar.add_cascade(label="View", menu=view_menu)

        run_menu = tk.Menu(menubar, tearoff=False, bg=self.chrome, fg=self.text,
                           activebackground="#1B2732", activeforeground=self.accent)
        run_menu.add_command(label="Run CustomScript", accelerator="Ctrl+R", command=self.execute_code)
        run_menu.add_command(label="Clear Output", accelerator="Ctrl+L", command=self.clear_output)
        menubar.add_cascade(label="Run", menu=run_menu)

        help_menu = tk.Menu(menubar, tearoff=False, bg=self.chrome, fg=self.text,
                            activebackground="#1B2732", activeforeground=self.accent)
        help_menu.add_command(label="About CustomScript", command=self.show_about)
        menubar.add_cascade(label="Help", menu=help_menu)

        self.root.config(menu=menubar)

        self.root.bind_all("<Control-r>", lambda e: self.execute_code() or "break")
        self.root.bind_all("<Control-l>", lambda e: self.clear_output() or "break")
        self.root.bind_all("<Control-s>", lambda e: self.save_file() or "break")
        self.root.bind_all("<Control-o>", lambda e: self.open_file() or "break")
        self.root.bind_all("<Control-n>", lambda e: self.new_file() or "break")
        self.root.bind_all("<Control-f>", lambda e: self.focus_search() or "break")
        self.root.bind_all("<Control-Shift-f>", lambda e: self.focus_search() or "break")
        self.root.bind_all("<Control-Shift-Up>", lambda e: self.toggle_fold_at_cursor() or "break")
        self.root.bind_all("<Control-Shift-Down>", lambda e: self.unfold_all() or "break")

    def _build_ui(self):
        top = tk.Frame(self.root, bg=self.chrome, height=38)
        top.pack(fill=tk.X, side=tk.TOP)
        top.pack_propagate(False)

        tk.Label(top, text="CS", bg=self.chrome, fg=self.accent,
                 font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT, padx=(14, 8))
        tk.Label(top, text="CUSTOMSCRIPT", bg=self.chrome, fg="#E7ECF2",
                 font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT)
        tk.Label(top, text="  Developer Studio", bg=self.chrome, fg=self.muted,
                 font=("Segoe UI", 9)).pack(side=tk.LEFT)

        self.run_btn = tk.Button(top, text="▶  RUN", bg="#18232B", fg=self.accent,
                                 activebackground="#20323B", activeforeground="#67E8F9",
                                 font=("Segoe UI", 8, "bold"), relief="flat", bd=0,
                                 padx=12, cursor="hand2", command=self.execute_code)
        self.run_btn.pack(side=tk.RIGHT, padx=(4, 10), pady=6)
        self.status_dot = tk.Label(top, text="●", bg=self.chrome, fg=self.success,
                                   font=("Segoe UI", 8))
        self.status_dot.pack(side=tk.RIGHT, padx=(8, 2))

        main = tk.Frame(self.root, bg=self.bg)
        main.pack(fill=tk.BOTH, expand=True)

        self.rail = tk.Frame(main, bg="#0A0D12", width=44)
        self.rail.pack(side=tk.LEFT, fill=tk.Y)
        self.rail.pack_propagate(False)
        self.explorer_btn = self._rail_button(self.rail, "▣", True, self.toggle_sidebar)
        self.search_btn = self._rail_button(self.rail, "⌕", False, self.focus_search)

        self.sidebar = tk.Frame(main, bg=self.sidebar_bg, width=190)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar.pack_propagate(False)
        tk.Label(self.sidebar, text="EXPLORER", bg=self.sidebar_bg, fg="#718096",
                 font=("Segoe UI", 8, "bold"), anchor="w").pack(fill=tk.X, padx=15, pady=(16, 12))
        tk.Label(self.sidebar, text="⌄  CUSTOMSCRIPT PROJECT", bg=self.sidebar_bg,
                 fg="#AEB8C5", font=("Segoe UI", 8, "bold"), anchor="w").pack(fill=tk.X, padx=12, pady=3)
        self.file_row = tk.Button(self.sidebar, text="●  main.cs", bg="#151B24", fg="#D5DCE5",
                                  activebackground="#1B2732", activeforeground="#FFFFFF",
                                  font=("Consolas", 9), anchor="w", relief="flat", bd=0,
                                  cursor="hand2", command=lambda: self.editor.focus_set())
        self.file_row.pack(fill=tk.X, padx=8, pady=2)
        tk.Frame(self.sidebar, bg=self.sidebar_bg).pack(expand=True, fill=tk.BOTH)
        tk.Label(self.sidebar, text="CUSTOMSCRIPT", bg=self.sidebar_bg, fg="#4D5968",
                 font=("Consolas", 7, "bold"), anchor="w").pack(fill=tk.X, padx=14)
        self.side_status = tk.Label(self.sidebar, text="Runtime  •  Ready", bg=self.sidebar_bg,
                                    fg="#657283", font=("Consolas", 8), anchor="w")
        self.side_status.pack(fill=tk.X, padx=14, pady=(2, 12))

        self.workspace = tk.Frame(main, bg=self.editor_bg)
        self.workspace.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        tabbar = tk.Frame(self.workspace, bg="#0C1016", height=34)
        tabbar.pack(fill=tk.X)
        tabbar.pack_propagate(False)
        self.tabbar = tabbar
        self.tabs_frame = tk.Frame(tabbar, bg="#0C1016")
        self.tabs_frame.pack(side=tk.LEFT, fill=tk.Y)
        self.new_tab_btn = tk.Button(tabbar, text="+", bg="#0C1016", fg="#657283",
                                     activebackground="#151B24", activeforeground=self.accent,
                                     relief="flat", bd=0, font=("Consolas", 11),
                                     cursor="hand2", command=self.new_file)
        self.new_tab_btn.pack(side=tk.LEFT, padx=4)
        self.tab_name = None

        crumb = tk.Frame(self.workspace, bg=self.editor_bg, height=25)
        crumb.pack(fill=tk.X)
        crumb.pack_propagate(False)
        self.crumb_label = tk.Label(crumb, text="main.cs  ›  CustomScript  ›  source",
                                    bg=self.editor_bg, fg="#586575", font=("Consolas", 8), anchor="w")
        self.crumb_label.pack(fill=tk.X, padx=12, pady=5)

        self.editor_area = tk.Frame(self.workspace, bg=self.editor_bg)
        self.editor_area.pack(fill=tk.BOTH, expand=True)
        editor_area = self.editor_area

        self.line_numbers = tk.Text(editor_area, width=5, bg=self.line_bg, fg="#465363",
                                    font=("Consolas", 11), relief="flat", bd=0, padx=8, pady=9,
                                    state=tk.DISABLED, takefocus=0, cursor="arrow", wrap=tk.NONE)
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)

        self.editor = scrolledtext.ScrolledText(
            editor_area, bg=self.editor_bg, fg=self.text, insertbackground="#F8FAFC",
            font=("Consolas", 11), relief="flat", bd=0, padx=12, pady=9,
            selectbackground="#183247", selectforeground="#FFFFFF", undo=True, wrap=tk.NONE)
        self.editor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.editor.bind("<KeyRelease>", self._editor_changed)
        self.editor.bind("<ButtonRelease-1>", self._editor_changed)
        self.editor.bind("<MouseWheel>", self._sync_line_scroll)
        self.editor.bind("<Tab>", self._autocomplete_accept)
        self.editor.bind("<Escape>", self._hide_autocomplete)
        self.editor.bind("<Up>", self._autocomplete_key)
        self.editor.bind("<Down>", self._autocomplete_key)
        self.editor.bind("<Return>", self._autocomplete_key)
        self._configure_syntax_highlighting()

        self.panel = tk.Frame(self.workspace, bg=self.terminal_bg, height=190)
        self.panel.pack(fill=tk.X)
        self.panel.pack_propagate(False)

        panel_head = tk.Frame(self.panel, bg="#0C1016", height=31)
        panel_head.pack(fill=tk.X)
        panel_head.pack_propagate(False)

        self.output_tab_btn = self._panel_button(panel_head, "OUTPUT", "output")
        self.terminal_tab_btn = self._panel_button(panel_head, "TERMINAL", "terminal")
        self.problems_tab_btn = self._panel_button(panel_head, "PROBLEMS", "problems")
        self.clear_btn = tk.Button(panel_head, text="Clear", bg="#0C1016", fg="#657283",
                                   activebackground="#151B24", activeforeground="#FFFFFF",
                                   relief="flat", bd=0, font=("Consolas", 8), cursor="hand2",
                                   command=self.clear_output)
        self.clear_btn.pack(side=tk.RIGHT, padx=8)

        body = tk.Frame(self.panel, bg=self.terminal_bg)
        body.pack(fill=tk.BOTH, expand=True)
        self.output_console = scrolledtext.ScrolledText(
            body, bg=self.terminal_bg, fg="#C7D0DB", insertbackground="white",
            font=("Consolas", 9), relief="flat", bd=0, padx=12, pady=8,
            state=tk.DISABLED, wrap=tk.NONE)
        self.terminal_console = scrolledtext.ScrolledText(
            body, bg=self.terminal_bg, fg="#8D99A8", insertbackground="white",
            font=("Consolas", 9), relief="flat", bd=0, padx=12, pady=8,
            state=tk.DISABLED, wrap=tk.NONE)
        self.problems_console = scrolledtext.ScrolledText(
            body, bg=self.terminal_bg, fg="#D8E0E8", insertbackground="white",
            font=("Consolas", 9), relief="flat", bd=0, padx=12, pady=8,
            state=tk.DISABLED, wrap=tk.NONE)
        self.output_console.pack(fill=tk.BOTH, expand=True)

        status = tk.Frame(self.root, bg="#0E131A", height=22)
        status.pack(fill=tk.X, side=tk.BOTTOM)
        status.pack_propagate(False)
        tk.Label(status, text="  CustomScript", bg="#0E131A", fg=self.accent,
                 font=("Consolas", 8, "bold")).pack(side=tk.LEFT)
        self.status_text = tk.Label(status, text="Ready", bg="#0E131A", fg="#667486",
                                    font=("Consolas", 8))
        self.status_text.pack(side=tk.LEFT, padx=12)
        self.cursor_text = tk.Label(status, text="Ln 1, Col 1", bg="#0E131A", fg="#7B8797",
                                    font=("Consolas", 8))
        self.cursor_text.pack(side=tk.RIGHT, padx=12)

    def _rail_button(self, parent, symbol, active, command):
        b = tk.Button(parent, text=symbol, bg="#0A0D12", fg=self.accent if active else "#46515F",
                      activebackground="#151B24", activeforeground=self.accent,
                      font=("Segoe UI Symbol", 15), relief="flat", bd=0,
                      cursor="hand2", command=command)
        b.pack(fill=tk.X, pady=(10, 4))
        return b

    def _panel_button(self, parent, text, name):
        b = tk.Button(parent, text=text, bg="#111720" if name == self.active_panel else "#0C1016",
                      fg=self.accent if name == self.active_panel else "#667486",
                      activebackground="#151B24", activeforeground="#FFFFFF",
                      relief="flat", bd=0, font=("Consolas", 8, "bold"),
                      padx=10, cursor="hand2", command=lambda: self.show_panel(name))
        b.pack(side=tk.LEFT, fill=tk.Y)
        return b

    def show_panel(self, name):
        self.active_panel = name
        for widget in (self.output_console, self.terminal_console, self.problems_console):
            widget.pack_forget()
        target = {"output": self.output_console, "terminal": self.terminal_console, "problems": self.problems_console}.get(name, self.output_console)
        target.pack(fill=tk.BOTH, expand=True)
        for btn, key in ((self.output_tab_btn, "output"), (self.terminal_tab_btn, "terminal"), (self.problems_tab_btn, "problems")):
            btn.config(bg="#111720" if name == key else "#0C1016", fg=self.accent if name == key else "#667486")
        if name == "problems":
            self._render_problems()

    def toggle_panel(self):
        if self.panel_visible:
            self.panel.pack_forget()
            self.panel_visible = False
        else:
            self.panel.pack(fill=tk.X)
            self.panel_visible = True
            self.show_panel(self.active_panel)

    def toggle_sidebar(self):
        if self.sidebar_visible:
            self.sidebar.pack_forget()
            self.sidebar_visible = False
        else:
            self.sidebar.pack(side=tk.LEFT, fill=tk.Y, before=self.workspace)
            self.sidebar_visible = True

    def _load_starter(self):
        self.editor.delete("1.0", tk.END)
        self.editor.insert(tk.END, self.get_starter_code())

    def _editor_changed(self, event=None):
        self._update_line_numbers()
        try:
            line, col = self.editor.index(tk.INSERT).split(".")
            self.cursor_text.config(text=f"Ln {line}, Col {int(col) + 1}")
        except Exception:
            pass
        if self._loading_document:
            return
        self._set_status("Modified")
        if self.active_tab and self.active_tab in self.documents:
            self.documents[self.active_tab]["dirty"] = True
            self.documents[self.active_tab]["code"] = self.editor.get("1.0", "end-1c")
            self._rebuild_tabs()
        self._schedule_highlight()
        self._schedule_live_diagnostics()
        self._schedule_autocomplete()

    def _sync_line_scroll(self, event=None):
        self.root.after_idle(self._update_line_numbers)
        self.root.after_idle(self._highlight_visible)

    # ========================= Syntax Highlighting =========================
    def _configure_syntax_highlighting(self):
        # CustomScript syntax colors.  These affect the editor only; the
        # interpreter/runtime is completely separate.
        styles = {
            "cs_keyword": "#60A5FA",      # let, maybe, suppose, otherwise...
            "cs_command": "#22D3EE",      # reveal, rewind, fast_ram
            "cs_subcommand": "#A78BFA",   # byte, write, read
            "cs_variable": "#E5E7EB",     # declared variable names
            "cs_number": "#B5CEA8",      # numbers / numeric literals
            "cs_string": "#CE9178",      # reveal text
            "cs_comment": "#5E6A78",      # comments
            "cs_operator": "#F59E0B",     # + - * / comparisons / =
            "cs_unit": "#4EC9B0",         # meters, seconds, etc.
            "cs_scope": "#C084FC",        # |>
            "cs_identifier": "#DCE3EA",   # normal identifiers
            "cs_delimiter": "#6B7280",    # slash/brackets/parentheses
        }
        for tag, color in styles.items():
            self.editor.tag_configure(tag, foreground=color)

        # NOVA diagnostics: CustomScript-native error visuals.
        self.editor.tag_configure("nova_error_line", background="#24151A")
        self.editor.tag_configure("nova_error_token", foreground="#FF8A9A", underline=True)
        self.line_numbers.tag_configure("nova_error_number", foreground="#F87171", background="#24151A")

        self._highlight_after_id = None
        self._highlighting = False
        self._schedule_highlight(delay=1)

    def _schedule_highlight(self, delay=35):
        if not hasattr(self, "editor"):
            return
        if self._highlight_after_id is not None:
            try:
                self.root.after_cancel(self._highlight_after_id)
            except Exception:
                pass
        self._highlight_after_id = self.root.after(delay, self._highlight_visible)

    def _highlight_visible(self):
        self._highlight_after_id = None
        if self._highlighting:
            return
        self._highlighting = True
        try:
            self._highlight_syntax()
        finally:
            self._highlighting = False

    def _highlight_syntax(self):
        """Lex CustomScript for editor coloring without changing program text."""
        text = self.editor.get("1.0", "end-1c")

        tags = ("cs_keyword", "cs_command", "cs_subcommand", "cs_variable",
                "cs_number", "cs_string", "cs_comment", "cs_operator",
                "cs_unit", "cs_scope", "cs_identifier", "cs_delimiter")
        for tag in tags:
            self.editor.tag_remove(tag, "1.0", tk.END)

        keyword_set = {"let", "maybe", "suppose", "otherwise", "attempt", "rescue", "ask"}
        command_set = {"reveal", "rewind", "fast_ram"}
        subcommand_set = {"byte", "write", "read"}

        # Process line-by-line so comment and reveal-string boundaries stay
        # simple and predictable.
        for line_no, line in enumerate(text.split("\n"), 1):
            base = f"{line_no}.0"
            i = 0
            n = len(line)
            expect_declared_name = False

            while i < n:
                # Comment: // outside a reveal//variable// construct.
                if line.startswith("//", i):
                    self.editor.tag_add("cs_comment", f"{base}+{i}c", f"{base}+{n}c")
                    break

                # Scope operator.
                if line.startswith("|>", i):
                    self.editor.tag_add("cs_scope", f"{base}+{i}c", f"{base}+{i+2}c")
                    i += 2
                    continue

                # reveal/text/ — highlight command + everything between slashes
                # as a string. This is checked before generic slash handling.
                if line.startswith("reveal/", i) and (i == 0 or line[i-1].isspace()):
                    self.editor.tag_add("cs_command", f"{base}+{i}c", f"{base}+{i+6}c")
                    start = i + 7
                    end = line.find("/", start)
                    if end >= 0:
                        self.editor.tag_add("cs_delimiter", f"{base}+{i+6}c", f"{base}+{i+7}c")
                        if end > start:
                            self.editor.tag_add("cs_string", f"{base}+{start}c", f"{base}+{end}c")
                        self.editor.tag_add("cs_delimiter", f"{base}+{end}c", f"{base}+{end+1}c")
                        i = end + 1
                        continue

                # reveal//name// — command, delimiters, then identifier.
                if line.startswith("reveal//", i) and (i == 0 or line[i-1].isspace()):
                    self.editor.tag_add("cs_command", f"{base}+{i}c", f"{base}+{i+6}c")
                    self.editor.tag_add("cs_delimiter", f"{base}+{i+6}c", f"{base}+{i+8}c")
                    start = i + 8
                    end = line.find("//", start)
                    if end >= 0:
                        if end > start:
                            self.editor.tag_add("cs_identifier", f"{base}+{start}c", f"{base}+{end}c")
                        self.editor.tag_add("cs_delimiter", f"{base}+{end}c", f"{base}+{end+2}c")
                        i = end + 2
                        continue

                ch = line[i]

                # Identifiers / keywords / units.
                if ch.isalpha() or ch == "_":
                    j = i + 1
                    while j < n and (line[j].isalnum() or line[j] == "_"):
                        j += 1
                    word = line[i:j]

                    if word in keyword_set:
                        self.editor.tag_add("cs_keyword", f"{base}+{i}c", f"{base}+{j}c")
                        expect_declared_name = word in {"let", "maybe"}
                    elif word in command_set:
                        self.editor.tag_add("cs_command", f"{base}+{i}c", f"{base}+{j}c")
                    elif word in subcommand_set:
                        self.editor.tag_add("cs_subcommand", f"{base}+{i}c", f"{base}+{j}c")
                    elif expect_declared_name:
                        self.editor.tag_add("cs_variable", f"{base}+{i}c", f"{base}+{j}c")
                        expect_declared_name = False
                    elif i > 0 and line[i-1] not in "." and re.match(r"\s*$", line[:i]):
                        self.editor.tag_add("cs_identifier", f"{base}+{i}c", f"{base}+{j}c")
                    else:
                        self.editor.tag_add("cs_identifier", f"{base}+{i}c", f"{base}+{j}c")
                    i = j
                    continue

                # Numeric literal, including a unit immediately after it.
                if ch.isdigit() or (ch == "-" and i + 1 < n and line[i+1].isdigit()):
                    j = i + 1
                    while j < n and (line[j].isdigit() or line[j] == "."):
                        j += 1
                    self.editor.tag_add("cs_number", f"{base}+{i}c", f"{base}+{j}c")
                    u = j
                    while u < n and line[u].isalpha():
                        u += 1
                    if u > j:
                        self.editor.tag_add("cs_unit", f"{base}+{j}c", f"{base}+{u}c")
                    i = u
                    continue

                # Operators. Long operators first.
                if line[i:i+2] in {"==", "!=", "<=", ">="}:
                    self.editor.tag_add("cs_operator", f"{base}+{i}c", f"{base}+{i+2}c")
                    i += 2
                    continue
                if ch in "+-*/=<>~":
                    self.editor.tag_add("cs_operator", f"{base}+{i}c", f"{base}+{i+1}c")
                    i += 1
                    continue
                if ch in "[]()":
                    self.editor.tag_add("cs_delimiter", f"{base}+{i}c", f"{base}+{i+1}c")
                    i += 1
                    continue

                i += 1

    # ========================= end Syntax Highlighting =========================


    def _update_line_numbers(self):
        try:
            count = int(self.editor.index("end-1c").split(".")[0])
            numbers = "\n".join(str(i) for i in range(1, count + 1))
            self.line_numbers.config(state=tk.NORMAL)
            self.line_numbers.delete("1.0", tk.END)
            self.line_numbers.insert("1.0", numbers)
            self.line_numbers.config(state=tk.DISABLED)
        except Exception:
            pass

    def _set_status(self, text):
        self.status_text.config(text=text)
        self.side_status.config(text=f"Runtime  •  {text}")

    def show_message(self, text):
        messagebox.showinfo("CustomScript Developer Studio", text)

    def focus_search(self):
        if not self.search_visible:
            self.search_visible = True
            if not hasattr(self, "search_bar"):
                self._build_search_bar()
            self.search_bar.pack(fill=tk.X, before=self.editor_area)
        self.search_entry.focus_set()
        self.search_entry.select_range(0, tk.END)

    def _build_search_bar(self):
        self.search_bar = tk.Frame(self.workspace, bg="#111720", height=34)
        self.search_bar.pack_propagate(False)
        tk.Label(self.search_bar, text="SEARCH", bg="#111720", fg=self.accent, font=("Consolas", 8, "bold")).pack(side=tk.LEFT, padx=(10, 6))
        self.search_entry = tk.Entry(self.search_bar, bg="#0B0F14", fg=self.text, insertbackground="white", relief="flat", font=("Consolas", 9))
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4, pady=6)
        self.search_entry.bind("<Return>", lambda e: self.find_next())
        self.search_entry.bind("<Shift-Return>", lambda e: self.find_previous())
        for label, cmd in (("↑", self.find_previous), ("↓", self.find_next), ("×", self.close_search)):
            tk.Button(self.search_bar, text=label, bg="#111720", fg="#8290A1", activebackground="#18232B", activeforeground=self.accent, relief="flat", bd=0, command=cmd, cursor="hand2", font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=2)

    def close_search(self):
        if hasattr(self, "search_bar"):
            self.search_bar.pack_forget()
        self.search_visible = False
        self.editor.tag_remove("search_hit", "1.0", tk.END)
        self.editor.focus_set()

    def find_next(self):
        query = self.search_entry.get() if hasattr(self, "search_entry") else ""
        if not query:
            return
        start = self.editor.index(tk.INSERT)
        pos = self.editor.search(query, start, stopindex=tk.END, nocase=False)
        if not pos:
            pos = self.editor.search(query, "1.0", stopindex=tk.END, nocase=False)
        self._select_search_hit(pos, query)

    def find_previous(self):
        query = self.search_entry.get() if hasattr(self, "search_entry") else ""
        if not query:
            return
        start = self.editor.index(tk.INSERT)
        pos = self.editor.search(query, start, stopindex="1.0", backwards=True, nocase=False)
        if not pos:
            pos = self.editor.search(query, tk.END, stopindex="1.0", backwards=True, nocase=False)
        self._select_search_hit(pos, query)

    def _select_search_hit(self, pos, query):
        self.editor.tag_remove("search_hit", "1.0", tk.END)
        if pos:
            end = f"{pos}+{len(query)}c"
            self.editor.tag_configure("search_hit", background="#3A3215", foreground="#FDE68A")
            self.editor.tag_add("search_hit", pos, end)
            self.editor.mark_set(tk.INSERT, end)
            self.editor.see(pos)

    # ========================= File/UI actions =========================
    def _make_doc(self, name, code=""):
        return {"name": name, "path": None, "code": code, "dirty": False}

    def _ensure_documents(self):
        if not self.documents:
            doc = self._make_doc("main.cs", self.editor.get("1.0", "end-1c"))
            self.documents["main.cs"] = doc
            self.active_tab = "main.cs"
            self._rebuild_tabs()

    def _save_current_doc_state(self):
        if self.active_tab and self.active_tab in self.documents:
            self.documents[self.active_tab]["code"] = self.editor.get("1.0", "end-1c")

    def _switch_tab(self, name):
        self._save_current_doc_state()
        self.active_tab = name
        doc = self.documents[name]
        self._loading_document = True
        self.editor.delete("1.0", tk.END)
        self.editor.insert("1.0", doc["code"])
        self._loading_document = False
        self.current_file = doc["path"]
        self._update_file_labels(doc["name"])
        self._editor_changed()
        self._rebuild_tabs()

    def _rebuild_tabs(self):
        if not hasattr(self, "tabs_frame"):
            return
        for child in self.tabs_frame.winfo_children():
            child.destroy()
        self.tab_buttons.clear()
        for name, doc in self.documents.items():
            active = name == self.active_tab
            label = ("● " if doc["dirty"] else "") + name
            b = tk.Button(self.tabs_frame, text=label, bg=self.editor_bg if active else "#0C1016", fg="#D8E0E8" if active else "#687586", activebackground="#151B24", activeforeground="#FFFFFF", relief="flat", bd=0, font=("Consolas", 9), cursor="hand2", padx=10, command=lambda n=name: self._switch_tab(n))
            b.pack(side=tk.LEFT, fill=tk.Y)
            self.tab_buttons[name] = b

    def new_file(self):
        self._ensure_documents()
        base = "untitled.cs"
        i = 1
        name = base
        while name in self.documents:
            name = f"untitled{i}.cs"; i += 1
        self._save_current_doc_state()
        self.documents[name] = self._make_doc(name, "// New CustomScript file\nreveal/Hello, CustomScript!/\n")
        self._switch_tab(name)
        self._set_status("New file")

    def open_file(self):
        path = filedialog.askopenfilename(filetypes=[("CustomScript", "*.cs"), ("Text", "*.txt"), ("All files", "*.*")])
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                code = f.read()
            name = path.split("/")[-1].split("\\")[-1]
            self._ensure_documents()
            self._save_current_doc_state()
            self.documents[name] = {"name": name, "path": path, "code": code, "dirty": False}
            self._switch_tab(name)
            self.terminal_log(f"Opened: {path}")
        except Exception as e:
            messagebox.showerror("Open failed", str(e))

    def save_file(self):
        self._ensure_documents()
        self._save_current_doc_state()
        doc = self.documents[self.active_tab]
        if not doc["path"]:
            return self.save_as()
        try:
            with open(doc["path"], "w", encoding="utf-8") as f:
                f.write(doc["code"])
            doc["dirty"] = False
            self.current_file = doc["path"]
            self._rebuild_tabs()
            self._set_status("Saved")
            self.terminal_log(f"Saved: {doc['path']}")
        except Exception as e:
            messagebox.showerror("Save failed", str(e))

    def save_as(self):
        self._ensure_documents()
        path = filedialog.asksaveasfilename(defaultextension=".cs", filetypes=[("CustomScript", "*.cs"), ("All files", "*.*")])
        if not path:
            return
        name = path.split("/")[-1].split("\\")[-1]
        self._save_current_doc_state()
        old_key = self.active_tab
        doc = self.documents.pop(old_key)
        doc.update({"name": name, "path": path, "dirty": False})
        self.documents[name] = doc
        self.active_tab = name
        self.current_file = path
        self._rebuild_tabs()
        self._update_file_labels(name)
        self.save_file()

    def _update_file_labels(self, name):
        self.crumb_label.config(text=f"{name}  ›  CustomScript  ›  source")
        self.file_row.config(text=f"●  {name}")

    def select_all(self):
        self.editor.tag_add(tk.SEL, "1.0", tk.END)
        self.editor.mark_set(tk.INSERT, "1.0")
        self.editor.see(tk.INSERT)

    def show_about(self):
        messagebox.showinfo("About CustomScript", "CustomScript Developer Studio NOVA v2\n\nA CustomScript-native development environment.")

    # ========================= NOVA v2 Smart Editor =========================
    def _schedule_live_diagnostics(self):
        if hasattr(self, "_live_diag_after") and self._live_diag_after is not None:
            try: self.root.after_cancel(self._live_diag_after)
            except Exception: pass
        self._live_diag_after = self.root.after(180, self._run_live_diagnostics)

    def _run_live_diagnostics(self):
        self._live_diag_after = None
        text = self.editor.get("1.0", "end-1c")
        declared = set(re.findall(r"\b(?:let|maybe)\s+([A-Za-z_]\w*)", text))
        known = set(["reveal","let","maybe","rewind","suppose","otherwise","attempt","rescue","ask","fast_ram","byte","write","read"])
        problems=[]
        for ln, raw in enumerate(text.splitlines(),1):
            line=raw.strip()
            if not line or line.startswith("//") or line.startswith("|>"): continue
            m=re.fullmatch(r"reveal//(.+)//", line)
            if m and not (m.group(1) in declared or re.fullmatch(r"-?\d+(?:\.\d+)?",m.group(1))):
                problems.append((ln,"MEM-001",f"'{m.group(1)}' is not defined in this source."))
                continue
            m=re.match(r"let\s+\w+\s*=\s*(.+)",line)
            if m:
                for token in re.findall(r"\b[A-Za-z_]\w*\b",m.group(1)):
                    if token not in declared and token not in known and token not in {"meters","seconds"} and not token.isdigit():
                        problems.append((ln,"MEM-001",f"'{token}' is used before it is defined.")); break
            m=re.match(r"suppose\s+(\w+)\s+(?:==|!=|<=|>=|<|>)\s+(\w+)",line)
            if m:
                for token in m.groups():
                    if not re.fullmatch(r"-?\d+(?:\.\d+)?",token) and token not in declared:
                        problems.append((ln,"MEM-001",f"'{token}' is not defined in this source.")); break
            if line.split()[0] not in known and not line.startswith("reveal/"):
                problems.append((ln,"SYN-001",f"Unknown CustomScript instruction: {line.split()[0]}"))
        self.problems = problems
        self._apply_live_problem_marks()
        self._render_problems()

    def _apply_live_problem_marks(self):
        self.editor.tag_remove("nova_live_line","1.0",tk.END)
        self.line_numbers.config(state=tk.NORMAL)
        self.line_numbers.tag_remove("nova_live_number","1.0",tk.END)
        self.editor.tag_configure("nova_live_line",background="#1D171B")
        self.line_numbers.tag_configure("nova_live_number",foreground="#F59E0B",background="#1D171B")
        for ln,_,_ in self.problems:
            self.editor.tag_add("nova_live_line",f"{ln}.0",f"{ln}.end")
            self.line_numbers.tag_add("nova_live_number",f"{ln}.0",f"{ln}.end")
        self.line_numbers.config(state=tk.DISABLED)

    def _render_problems(self):
        if not hasattr(self,"problems_console"): return
        self.problems_console.config(state=tk.NORMAL)
        self.problems_console.delete("1.0",tk.END)
        if not self.problems:
            self.problems_console.insert(tk.END,"  ✓  No problems detected in the current source.\n","nova_ok")
            self.problems_console.tag_configure("nova_ok",foreground=self.success)
        else:
            self.problems_console.insert(tk.END,f"  NOVA found {len(self.problems)} problem(s)\n\n","nova_head")
            self.problems_console.tag_configure("nova_head",foreground=self.accent)
            for i,(ln,code,msg) in enumerate(self.problems,1):
                tag=f"problem_{i}"
                self.problems_console.tag_configure(tag,foreground="#F3A6B4")
                self.problems_console.tag_bind(tag,"<Button-1>",lambda e,n=ln:self._jump_to_diagnostic(n))
                self.problems_console.tag_bind(tag,"<Enter>",lambda e:self.problems_console.config(cursor="hand2"))
                self.problems_console.tag_bind(tag,"<Leave>",lambda e:self.problems_console.config(cursor="xterm"))
                self.problems_console.insert(tk.END,f"  ×  Line {ln:<4}  {code:<8}  {msg}\n",tag)
        self.problems_console.config(state=tk.DISABLED)

    def _completion_context(self, prefix):
        line = self.editor.get(f"{self.editor.index(tk.INSERT).split('.')[0]}.0", tk.INSERT).strip()
        base=["reveal","let","maybe","rewind","suppose","otherwise","attempt","rescue","ask","fast_ram","byte","write","read"]
        source=self.editor.get("1.0","end-1c")
        vars_found=re.findall(r"\b(?:let|maybe)\s+([A-Za-z_]\w*)",source)
        if line.startswith("fast_ram"):
            base=["byte","write","read"]
        elif line.startswith("reveal//"):
            base=vars_found
        pool=list(dict.fromkeys(base+vars_found))
        return [x for x in pool if x.lower().startswith(prefix.lower())][:10]

    def _autocomplete_candidates(self,prefix):
        return self._completion_context(prefix)

    def toggle_fold_at_cursor(self):
        ln=int(self.editor.index(tk.INSERT).split('.')[0])
        lines=self.editor.get("1.0","end-1c").splitlines()
        if ln<1 or ln>len(lines): return
        # CustomScript-native folding: fold a contiguous |> scope after this line.
        if not (lines[ln-1].strip().startswith(("suppose ","otherwise","attempt","rescue"))):
            return
        end=ln
        while end<len(lines) and lines[end].strip().startswith("|>"): end+=1
        if end==ln: return
        key=(ln,end)
        hidden=self._folds.get(key,False)
        for n in range(ln+1,end+1):
            self.editor.tag_configure("nova_fold",elide=not hidden)
            self.editor.tag_add("nova_fold",f"{n}.0",f"{n}.0 lineend +1c")
        self._folds[key]=not hidden

    def unfold_all(self):
        self.editor.tag_remove("nova_fold","1.0",tk.END)
        self._folds.clear()

    # ========================= Output/Terminal =========================
    def _write(self, widget, text, color):
        widget.config(state=tk.NORMAL)
        tag = f"c{color.replace('#', '')}"
        widget.tag_config(tag, foreground=color)
        widget.insert(tk.END, text + "\n", tag)
        widget.see(tk.END)
        widget.config(state=tk.DISABLED)

    def output(self, text, color="#C7D0DB"):
        self.show_panel("output")
        self._write(self.output_console, text, color)

    def terminal_log(self, text, color="#8D99A8"):
        self._write(self.terminal_console, text, color)

    def clear_output(self):
        for widget in (self.output_console, self.terminal_console):
            widget.config(state=tk.NORMAL)
            widget.delete("1.0", tk.END)
            widget.config(state=tk.DISABLED)
        self.show_panel("output")
        self._set_status("Output cleared")

    # ========================= Runtime =========================
    def reset_memory(self):
        self.vars = {}
        self.history = {}
        self.maybe_vars = {}
        self.hardware_memory = {}
        self.skip_next_block = False
        self.last_condition_met = False
        self.in_attempt = False
        self.error_caught = False
        self.input_values = {}

    def get_starter_code(self):
        return """// CustomScript demo
reveal/Hello, World!/

let systemScore = 9500
reveal//systemScore//

let distance = 50meters
let time = 5seconds
let speed = distance / time
reveal/Speed calculated:/
reveal//speed//

maybe wind = 10 ~ 25
reveal/Random wind generated:/
reveal//wind//

let health = 100
let health = 50
let health = 10
rewind health by 2 steps
reveal/Health rewound to:/
reveal//health//

suppose health == 50
|> reveal/Player is alive!/
otherwise
|> reveal/Player took damage!/

fast_ram byte memory[4]
fast_ram write memory[2] = 255
fast_ram read memory[2]
"""

    # ========================= NOVA Autocomplete =========================
    def _schedule_autocomplete(self):
        if hasattr(self, "_autocomplete_after_id") and self._autocomplete_after_id is not None:
            try:
                self.root.after_cancel(self._autocomplete_after_id)
            except Exception:
                pass
        self._autocomplete_after_id = self.root.after(90, self._show_autocomplete)

    def _current_word(self):
        pos = self.editor.index(tk.INSERT)
        line_start = f"{pos.split('.')[0]}.0"
        before = self.editor.get(line_start, pos)
        m = re.search(r"([A-Za-z_][A-Za-z0-9_]*)$", before)
        return (m.group(1), f"{pos.split('.')[0]}.{int(pos.split('.')[1]) - len(m.group(1))}") if m else ("", pos)

    def _autocomplete_candidates(self, prefix):
        return self._completion_context(prefix)

    def _show_autocomplete(self):
        self._autocomplete_after_id = None
        prefix, _ = self._current_word()
        if len(prefix) < 2:
            self._hide_autocomplete()
            return
        candidates = self._autocomplete_candidates(prefix)
        if not candidates:
            self._hide_autocomplete()
            return

        if self._autocomplete_popup is None or not self._autocomplete_popup.winfo_exists():
            self._autocomplete_popup = tk.Toplevel(self.root)
            self._autocomplete_popup.overrideredirect(True)
            self._autocomplete_popup.configure(bg="#202733")
            self._autocomplete_list = tk.Listbox(
                self._autocomplete_popup, bg="#0F151C", fg="#DCE3EA",
                selectbackground="#183247", selectforeground="#67E8F9",
                highlightthickness=1, highlightbackground="#202733",
                relief="flat", font=("Consolas", 10), height=min(8, len(candidates)),
                activestyle="none", bd=0
            )
            self._autocomplete_list.pack(padx=1, pady=1)
            self._autocomplete_list.bind("<ButtonRelease-1>", self._autocomplete_accept)
        else:
            self._autocomplete_list.delete(0, tk.END)
            self._autocomplete_list.config(height=min(8, len(candidates)))

        for item in candidates:
            self._autocomplete_list.insert(tk.END, item)
        self._autocomplete_list.selection_set(0)

        bbox = self.editor.bbox(tk.INSERT)
        if not bbox:
            self._hide_autocomplete()
            return
        x, y, w, h = bbox
        screen_x = self.editor.winfo_rootx() + x
        screen_y = self.editor.winfo_rooty() + y + h + 2
        self._autocomplete_popup.geometry(f"230x{min(8, len(candidates))*22 + 2}+{screen_x}+{screen_y}")
        self._autocomplete_popup.lift()

    def _autocomplete_accept(self, event=None):
        if not self._autocomplete_list or not self._autocomplete_popup or not self._autocomplete_popup.winfo_exists():
            return None if event else False
        selection = self._autocomplete_list.curselection()
        if not selection:
            return "break"
        word = self._autocomplete_list.get(selection[0])
        prefix, start = self._current_word()
        end = self.editor.index(tk.INSERT)
        self.editor.delete(start, end)
        self.editor.insert(start, word)
        self.editor.mark_set(tk.INSERT, f"{start}+{len(word)}c")
        self._hide_autocomplete()
        self._editor_changed()
        return "break"

    def _autocomplete_key(self, event):
        if not self._autocomplete_list or not self._autocomplete_popup or not self._autocomplete_popup.winfo_exists():
            return None
        if event.keysym == "Up":
            self._autocomplete_list.event_generate("<Up>")
            return "break"
        if event.keysym == "Down":
            self._autocomplete_list.event_generate("<Down>")
            return "break"
        if event.keysym == "Return":
            return self._autocomplete_accept(event)
        return None

    def _hide_autocomplete(self, event=None):
        if self._autocomplete_popup is not None:
            try:
                self._autocomplete_popup.destroy()
            except Exception:
                pass
        self._autocomplete_popup = None
        self._autocomplete_list = None
        return "break" if event else None

    # ========================= NOVA Diagnostics =========================
    def _clear_diagnostics(self):
        self._diagnostic_count = 0
        self._diagnostic_lines.clear()
        self.editor.tag_remove("nova_error_line", "1.0", tk.END)
        self.editor.tag_remove("nova_error_token", "1.0", tk.END)
        self.line_numbers.config(state=tk.NORMAL)
        self.line_numbers.tag_remove("nova_error_number", "1.0", tk.END)
        self.line_numbers.config(state=tk.DISABLED)

    def _error_code(self, error):
        msg = str(error)
        if msg.startswith("Undefined variable") or msg.startswith("Unknown variable"):
            return "MEM-001", "Memory lookup failed"
        if "Invalid expression" in msg or "Invalid operator" in msg or "Division by zero" in msg or "Unit mismatch" in msg:
            return "EXPR-001", "Expression could not be resolved"
        if msg.startswith("Syntax Error") or msg.startswith("Unknown command") or msg.startswith("Invalid "):
            return "SYN-001", "Command structure is not valid"
        if msg.startswith("Time paradox"):
            return "TIME-001", "Rewind request cannot be completed"
        if msg.startswith("RAM") or msg.startswith("RAM index") or msg.startswith("RAM byte"):
            return "RAM-001", "Hardware memory request failed"
        return "RUN-001", "Runtime could not complete this instruction"

    def _friendly_error_detail(self, error):
        msg = str(error)
        if msg.startswith("Undefined variable"):
            name = msg.split("'", 2)[1] if "'" in msg else "that name"
            return f"'{name}' is not defined in this run."
        if msg.startswith("Unknown variable"):
            name = msg.split(":", 1)[1].strip() if ":" in msg else "that name"
            return f"'{name}' is not available in active memory."
        if msg.startswith("Syntax Error: Unknown command"):
            return "CustomScript does not recognize this instruction."
        if "Division by zero" in msg:
            return "A calculation attempted to divide by zero."
        if "Unit mismatch" in msg:
            return msg
        if msg.startswith("Time paradox"):
            return msg
        return msg

    def _mark_error_line(self, line_num, source_line):
        self.editor.tag_remove("nova_error_line", "1.0", tk.END)
        self.editor.tag_remove("nova_error_token", "1.0", tk.END)
        self.line_numbers.config(state=tk.NORMAL)
        self.line_numbers.tag_remove("nova_error_number", "1.0", tk.END)
        self.editor.tag_add("nova_error_line", f"{line_num}.0", f"{line_num}.end")
        self.line_numbers.tag_add("nova_error_number", f"{line_num}.0", f"{line_num}.end")
        # Underline the most useful token rather than drawing a Python-style caret.
        stripped = source_line.strip()
        if stripped.startswith("reveal//") and "//" in stripped[8:]:
            name_start = source_line.find("reveal//") + 8
            name_end = source_line.find("//", name_start)
            if name_end > name_start:
                self.editor.tag_add("nova_error_token", f"{line_num}.{name_start}", f"{line_num}.{name_end}")
        elif stripped:
            leading = len(source_line) - len(source_line.lstrip())
            token = re.search(r"[A-Za-z_][A-Za-z0-9_]*", stripped)
            if token:
                a = leading + token.start()
                b = leading + token.end()
                self.editor.tag_add("nova_error_token", f"{line_num}.{a}", f"{line_num}.{b}")
        self.line_numbers.config(state=tk.DISABLED)

    def _jump_to_diagnostic(self, line_num):
        self.editor.focus_set()
        self.editor.mark_set(tk.INSERT, f"{line_num}.0")
        self.editor.see(f"{line_num}.0")
        self._mark_error_line(line_num, self.editor.get(f"{line_num}.0", f"{line_num}.end"))
        self.cursor_text.config(text=f"Ln {line_num}, Col 1")
        self._set_status(f"NOVA • jumped to line {line_num}")

    def _write_diagnostic(self, line_num, source_line, error):
        self._diagnostic_count += 1
        code, title = self._error_code(error)
        detail = self._friendly_error_detail(error)
        tag = f"nova_diag_{self._diagnostic_count}"
        self._diagnostic_lines[tag] = line_num

        box = (
            "╭─ NOVA DIAGNOSTIC ─────────────────────────────╮\n"
            f"│ {code}   •   LINE {line_num:<4}                       │\n"
            "│                                                  │\n"
            f"│ {source_line[:44]:<44} │\n"
            "│                                                  │\n"
            f"│ {title:<44} │\n"
            f"│ {detail[:44]:<44} │\n"
            "╰─ CLICK TO JUMP TO THE SOURCE ─────────────────╯\n"
        )
        self.output_console.config(state=tk.NORMAL)
        self.output_console.tag_configure(tag, foreground="#F3A6B4", underline=False)
        self.output_console.tag_bind(tag, "<Button-1>", lambda e, ln=line_num: self._jump_to_diagnostic(ln))
        self.output_console.tag_bind(tag, "<Enter>", lambda e: self.output_console.config(cursor="hand2"))
        self.output_console.tag_bind(tag, "<Leave>", lambda e: self.output_console.config(cursor="xterm"))
        self.output_console.insert(tk.END, box, tag)
        self.output_console.insert(tk.END, "\n")
        self.output_console.see(tk.END)
        self.output_console.config(state=tk.DISABLED)
        self._mark_error_line(line_num, source_line)
        self.show_panel("output")

    def execute_code(self):
        self.clear_output()
        self.reset_memory()
        self._clear_diagnostics()
        self.show_panel("output")
        self.status_dot.config(fg=self.accent)
        self._set_status("Running")
        self.terminal_log(">>> NOVA runtime started")

        code = self.editor.get("1.0", tk.END)
        lines = code.strip().split("\n")
        finished = True

        for line_num, raw_line in enumerate(lines, 1):
            line = raw_line.strip()
            if not line or line.startswith("//"):
                continue

            is_scoped = False
            if line.startswith("|>"):
                is_scoped = True
                line = line[2:].strip()

            if is_scoped and self.skip_next_block:
                self.skip_next_block = False
                continue

            try:
                self.parse_line(line)
            except Exception as e:
                if self.in_attempt:
                    self.error_caught = True
                    self.terminal_log(f"[RESCUE] Line {line_num}: {e}", "#FBBF24")
                    self.skip_next_block = True
                else:
                    self._write_diagnostic(line_num, raw_line, e)
                    self.terminal_log(f"NOVA halted at line {line_num}", self.error)
                    finished = False
                    break

            if is_scoped:
                self.skip_next_block = False

        self.terminal_log(">>> Execution finished" if finished else ">>> Execution stopped with diagnostic",
                         self.success if finished else self.error)
        self.status_dot.config(fg=self.success if finished else self.error)
        self._set_status("Ready" if finished else "Error • NOVA diagnostic")

    def parse_token(self, token):
        token = token.strip()
        if token in self.maybe_vars:
            min_v, max_v = self.maybe_vars[token]
            return random.randint(min_v, max_v), None
        if token in self.vars:
            return self.vars[token]
        match = re.match(r"^(-?\d+(?:\.\d+)?)([a-zA-Z]*)$", token)
        if match:
            raw = match.group(1)
            val = float(raw) if "." in raw else int(raw)
            unit = match.group(2) or None
            return val, unit
        raise ValueError(f"Unknown variable: {token}")

    def eval_expr(self, expr):
        tokens = expr.split()
        if len(tokens) == 1:
            return self.parse_token(tokens[0])
        if len(tokens) != 3:
            raise ValueError(f"Invalid expression: {expr}")

        val1, unit1 = self.parse_token(tokens[0])
        op = tokens[1]
        val2, unit2 = self.parse_token(tokens[2])

        if op == "+":
            if unit1 != unit2:
                raise ValueError(f"Unit mismatch: Cannot add {unit1} to {unit2}")
            return val1 + val2, unit1
        if op == "-":
            if unit1 != unit2:
                raise ValueError(f"Unit mismatch: Cannot subtract {unit2} from {unit1}")
            return val1 - val2, unit1
        if op == "*":
            return val1 * val2, f"{unit1}*{unit2}" if unit1 and unit2 else (unit1 or unit2)
        if op == "/":
            if val2 == 0:
                raise ValueError("Division by zero")
            return val1 / val2, f"{unit1}/{unit2}" if unit1 and unit2 else (unit1 or unit2)
        raise ValueError(f"Invalid operator: {op}")

    def _ask_value(self, name, kind):
        """CustomScript-native NOVA input dialog."""
        win = tk.Toplevel(self.root)
        win.title("CustomScript Input")
        win.configure(bg=self.chrome)
        win.transient(self.root)
        win.grab_set()
        win.resizable(False, False)
        win.geometry("430x190")
        tk.Label(win, text="CUSTOMSCRIPT INPUT", bg=self.chrome, fg=self.accent, font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=22, pady=(20, 4))
        prompt = f"Input needed for  {name}" + (f"  •  {kind}" if kind != "text" else "")
        tk.Label(win, text=prompt, bg=self.chrome, fg=self.text, font=("Segoe UI", 10)).pack(anchor="w", padx=22, pady=(0, 12))
        entry = tk.Entry(win, bg=self.editor_bg, fg=self.text, insertbackground=self.accent, relief="flat", font=("Consolas", 12))
        entry.pack(fill=tk.X, padx=22, ipady=7); entry.focus_set()
        result={"value":None,"cancelled":False}
        def submit(event=None):
            raw=entry.get()
            try:
                if kind == "number": value=float(raw) if "." in raw else int(raw)
                elif kind == "text": value=raw
                else:
                    if not re.fullmatch(r"-?\d+(?:\.\d+)?", raw): raise ValueError(f"Expected a numeric value with unit '{kind}'")
                    value=(float(raw) if "." in raw else int(raw), kind)
                result["value"]=value; win.destroy()
            except ValueError as exc:
                tk.Label(win,text=str(exc),bg=self.chrome,fg=self.error,font=("Segoe UI",9)).pack(anchor="w",padx=22,pady=(6,0)); entry.focus_set()
        def cancel(): result["cancelled"]=True; win.destroy()
        row=tk.Frame(win,bg=self.chrome); row.pack(fill=tk.X,padx=22,pady=14)
        tk.Button(row,text="Enter",command=submit,bg="#18232B",fg=self.accent,activebackground="#20323D",activeforeground="white",relief="flat",cursor="hand2",padx=16).pack(side=tk.RIGHT)
        tk.Button(row,text="Cancel",command=cancel,bg=self.chrome,fg=self.muted,activebackground=self.chrome,activeforeground=self.text,relief="flat",cursor="hand2").pack(side=tk.RIGHT,padx=(0,8))
        entry.bind("<Return>",submit); entry.bind("<Escape>",lambda e:cancel()); win.protocol("WM_DELETE_WINDOW",cancel)
        self.root.wait_window(win)
        if result["cancelled"]: raise ValueError(f"Input for '{name}' was cancelled")
        return result["value"]

    def parse_line(self, line):
        # Ask for user input
        if line.startswith("ask "):
            match = re.fullmatch(r"ask (\w+)(?: as (text|number|[A-Za-z]+))?", line)
            if not match: raise ValueError("Invalid ask statement. Use: ask name, ask age as number, or ask distance as meters")
            var, kind = match.groups(); kind = kind or "text"
            value=self._ask_value(var,kind)
            if isinstance(value,tuple): val,unit=value
            else: val,unit=value,None
            self.history.setdefault(var,[]).append((val,unit)); self.vars[var]=(val,unit); self.input_values[var]=kind
            self.terminal_log(f"[Input] {var} received")
            return

        # RAM reserve
        if line.startswith("fast_ram byte "):
            match = re.fullmatch(r"fast_ram byte (\w+)\[(\d+)\]", line)
            if not match:
                raise ValueError("Invalid fast_ram declaration")
            var, size = match.groups()
            self.hardware_memory[var] = [0] * int(size)
            self.output(f"[Hardware] Reserved {size} bytes for '{var}'", "#4EC9B0")
            return

        # RAM write
        match = re.fullmatch(r"fast_ram write (\w+)\[(\d+)\] = (-?\d+)", line)
        if match:
            var, idx, value = match.groups()
            if var not in self.hardware_memory:
                raise ValueError(f"RAM '{var}' is not reserved")
            idx, value = int(idx), int(value)
            if not 0 <= idx < len(self.hardware_memory[var]):
                raise ValueError(f"RAM index out of range: {idx}")
            if not 0 <= value <= 255:
                raise ValueError("RAM byte must be between 0 and 255")
            self.hardware_memory[var][idx] = value
            self.terminal_log(f"[Hardware] {var}[{idx}] <- {value}")
            return

        # RAM read
        match = re.fullmatch(r"fast_ram read (\w+)\[(\d+)\]", line)
        if match:
            var, idx = match.groups()
            if var not in self.hardware_memory:
                raise ValueError(f"RAM '{var}' is not reserved")
            idx = int(idx)
            if not 0 <= idx < len(self.hardware_memory[var]):
                raise ValueError(f"RAM index out of range: {idx}")
            self.output(f"[Hardware] {var}[{idx}] = {self.hardware_memory[var][idx]}", "#4EC9B0")
            return

        # Maybe
        if line.startswith("maybe "):
            match = re.fullmatch(r"maybe (\w+) = (-?\d+) ~ (-?\d+)", line)
            if not match:
                raise ValueError("Invalid maybe declaration")
            var, min_v, max_v = match.groups()
            min_v, max_v = int(min_v), int(max_v)
            if min_v > max_v:
                raise ValueError("maybe minimum cannot exceed maximum")
            self.maybe_vars[var] = (min_v, max_v)
            return

        # Let
        if line.startswith("let "):
            match = re.fullmatch(r"let (\w+) = (.+)", line)
            if not match:
                raise ValueError("Invalid let statement")
            var, expr = match.groups()
            val, unit = self.eval_expr(expr)
            self.history.setdefault(var, []).append((val, unit))
            self.vars[var] = (val, unit)
            return

        # Rewind
        if line.startswith("rewind "):
            match = re.fullmatch(r"rewind (\w+) by (\d+) steps", line)
            if not match:
                raise ValueError("Invalid rewind statement")
            var, steps = match.groups()
            steps = int(steps)
            if var not in self.history or len(self.history[var]) <= steps:
                raise ValueError(f"Time paradox: Not enough history to rewind {var}")
            self.history[var] = self.history[var][:-steps]
            self.vars[var] = self.history[var][-1]
            self.output(f"[Time Travel] '{var}' rewound {steps} steps.", "#C586C0")
            return

        # Variable reveal MUST come before raw reveal
        match = re.fullmatch(r"reveal//(.+)//", line)
        if match:
            name = match.group(1).strip()
            if name in self.vars:
                val, unit = self.vars[name]
                self.output(f"{val}{unit or ''}", "#B5CEA8")
            elif name in self.maybe_vars:
                lo, hi = self.maybe_vars[name]
                self.output(f"{random.randint(lo, hi)} (Dynamic)", "#B5CEA8")
            else:
                try:
                    self.output(str(int(name)), "#B5CEA8")
                except ValueError:
                    raise ValueError(f"Undefined variable '{name}'")
            return

        # Raw reveal
        match = re.fullmatch(r"reveal/(.*)/", line)
        if match:
            self.output(match.group(1), "#CE9178")
            return

        # Suppose
        if line.startswith("suppose "):
            parts = line[8:].split()
            if len(parts) != 3:
                raise ValueError("Invalid suppose statement")
            left, op, right = parts
            v1, _ = self.parse_token(left)
            v2, _ = self.parse_token(right)
            checks = {
                "==": v1 == v2, "!=": v1 != v2,
                "<": v1 < v2, ">": v1 > v2,
                "<=": v1 <= v2, ">=": v1 >= v2,
            }
            if op not in checks:
                raise ValueError(f"Unknown comparison operator: {op}")
            self.last_condition_met = checks[op]
            self.skip_next_block = not self.last_condition_met
            return

        if line == "otherwise":
            self.skip_next_block = self.last_condition_met
            return

        # Attempt / rescue
        if line == "attempt":
            self.in_attempt = True
            self.error_caught = False
            return
        if line == "rescue":
            self.in_attempt = False
            self.skip_next_block = not self.error_caught
            return

        raise ValueError(f"Syntax Error: Unknown command '{line}'")


if __name__ == "__main__":
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass

    root = tk.Tk()
    app = ModernLanguageIDE(root)
    root.mainloop()
