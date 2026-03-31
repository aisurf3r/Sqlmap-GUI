
import sys
import os
import json
import re
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QPlainTextEdit, QTabWidget,
    QCheckBox, QComboBox, QGroupBox, QScrollArea, QFileDialog,
    QSpinBox, QDoubleSpinBox, QStatusBar, QListWidget,
    QAbstractItemView, QMessageBox, QInputDialog, QTableWidget,
    QTableWidgetItem, QTabWidget as QInnerTabWidget
)
from PyQt6.QtCore import Qt, QProcess, QTimer
from PyQt6.QtGui import QFont, QIcon


class SqlmapGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🔮 sqlmap GUI ")
        self.resize(1000, 750)
        self.setStyleSheet(self.dark_style())

        self.process = None
        self.widgets = {}
        self.enum_checks = {}
        self.tamper_scripts = self.get_tamper_scripts()
        self._updating = False

        self.init_ui()
        self.setup_profiles()

    def dark_style(self):
        return """
        QMainWindow, QWidget { background-color: #1e1e1e; color: #e0e0e0; }
        QLabel { color: #ffffff; font-size: 12px; }
        QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {
            background-color: #2d2d2d; color: #ffffff; border: 1px solid #444;
            padding: 5px; border-radius: 4px;
        }
        QPlainTextEdit {
            background-color: #252526; color: #dcdcdc;
            font-family: 'Consolas', 'Courier New', monospace; font-size: 11px;
            border: 1px solid #444;
        }
        QPushButton {
            background-color: #007acc; color: white; padding: 8px 10px;
            border: none; border-radius: 5px; font-weight: bold;
        }
        QPushButton:hover { background-color: #005a9e; }
        QPushButton:disabled { background-color: #555; }
        QTabWidget::pane { border: 0; background: #252526; }
        QTabBar::tab {
            background: #2d2d2d; color: #ffffff; padding: 10px 15px;
            margin: 2px; border-top-left-radius: 5px; border-top-right-radius: 5px;
        }
        QTabBar::tab:selected { background: #007acc; }
        QGroupBox { border: 1px solid #444; margin-top: 8px; padding: 5px; font-weight: bold; }
        QGroupBox::title { padding: 0 5px; }
        """

    def get_tamper_scripts(self):
        tamper_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tamper")
        scripts = []
        if os.path.exists(tamper_dir):
            for f in os.listdir(tamper_dir):
                if f.endswith(".py") and not f.startswith("__"):
                    scripts.append(f[:-3])
        if not scripts:
            scripts = ["0eunion", "apostrophemask", "apostrophenullencode", "appendnullbyte", "base64encode", "between", "binary", "bluecoat", "chardoubleencode", "charencode", "charunicodeencode", "charunicodeescape", "commalesslimit", "commalessmid", "commentbeforeparentheses", "concat2concatws", "decentities", "dunion", "equaltolike", "equaltorlike", "escapequotes", "greatest", "halfversionedmorekeywords", "hex2char", "hexentities", "htmlencode", "if2case", "ifnull2casewhenisnull", "ifnull2ifisnull", "informationschemacomment", "least", "lowercase", "luanginx", "luanginxmore", "misunion", "modsecurityversioned", "modsecurityzeroversioned", "multiplespaces", "ord2ascii", "overlongutf8", "overlongutf8more", "percentage", "plus2concat", "plus2fnconcat", "randomcase", "randomcomments", "schemasplit", "scientific", "sleep2getlock", "sp_password", "space2comment", "space2dash", "space2hash", "space2morecomment", "space2morehash", "space2mssqlblank", "space2mssqlhash", "space2mysqlblank", "space2mysqldash", "space2plus", "space2randomblank", "substring2leftright", "symboliclogical", "unionalltounion", "unmagicquotes", "uppercase", "varnish", "versionedkeywords", "versionedmorekeywords", "xforwardedfor"]
        return sorted(scripts)

    def init_ui(self):
        container = QWidget()
        self.setCentralWidget(container)
        layout = QVBoxLayout(container)

        title = QLabel("🚀 sqlmap GUI")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        layout.addWidget(title)

        self.command_bar = QLineEdit()
        self.command_bar.setReadOnly(True)
        self.command_bar.setStyleSheet("background-color: #2d2d2d; color: #00ff00; font-family: Consolas; padding: 5px;")
        layout.addWidget(QLabel("Comando actual:"))
        layout.addWidget(self.command_bar)

        toolbar = QHBoxLayout()
        self.copy_button = QPushButton("📋 Copiar Comando")
        self.save_profile_button = QPushButton("💾 Guardar Perfil")
        self.load_profile_button = QPushButton("📂 Cargar Perfil")
        self.clear_all_button = QPushButton("🗑️ Limpiar Todo")
        self.stealth_button = QPushButton("🛡️ Stealth")
        self.bazoka_button = QPushButton("💥 Bazoka")
        self.paranoia_button = QPushButton("🧠 Paranoia")
        self.takeover_button = QPushButton("🧨 Takeover")

        self.copy_button.clicked.connect(self.export_command)
        self.save_profile_button.clicked.connect(self.save_profile)
        self.load_profile_button.clicked.connect(self.load_profile)
        self.clear_all_button.clicked.connect(self.reset_all)
        self.stealth_button.clicked.connect(lambda: self.load_wizard("stealth"))
        self.bazoka_button.clicked.connect(lambda: self.load_wizard("bazoka"))
        self.paranoia_button.clicked.connect(lambda: self.load_wizard("paranoia"))
        self.takeover_button.clicked.connect(lambda: self.load_wizard("takeover"))

        for btn in [self.stealth_button, self.bazoka_button, self.paranoia_button, self.takeover_button]:
            btn.setFixedSize(110, 35)

        toolbar.addWidget(self.copy_button)
        toolbar.addWidget(self.save_profile_button)
        toolbar.addWidget(self.load_profile_button)
        toolbar.addWidget(self.clear_all_button)
        toolbar.addStretch()
        toolbar.addWidget(self.stealth_button)
        toolbar.addWidget(self.bazoka_button)
        toolbar.addWidget(self.paranoia_button)
        toolbar.addWidget(self.takeover_button)
        layout.addLayout(toolbar)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        self.tabs = QTabWidget()
        scroll.setWidget(self.tabs)
        layout.addWidget(scroll)

        self.create_target_tab()
        self.create_request_tab()
        self.create_optimization_tab()
        self.create_injection_tab()
        self.create_detection_tab()
        self.create_techniques_tab()
        self.create_enumeration_tab()
        self.create_os_access_tab()
        self.create_file_access_tab()
        self.create_registry_tab()
        self.create_general_tab()
        self.create_misc_tab()
        self.create_console_tab()
        self.create_results_tab()

        btn_layout = QHBoxLayout()
        self.run_button = QPushButton("▶️ Ejecutar sqlmap")
        self.stop_button = QPushButton("⏹️ Detener")
        self.clear_output_button = QPushButton("🗑️ Limpiar Consola")
        self.run_button.clicked.connect(self.run_sqlmap)
        self.stop_button.clicked.connect(self.stop_sqlmap)
        self.clear_output_button.clicked.connect(self.clear_output)
        self.stop_button.setEnabled(False)
        btn_layout.addWidget(self.run_button)
        btn_layout.addWidget(self.stop_button)
        btn_layout.addWidget(self.clear_output_button)
        layout.addLayout(btn_layout)

        self.statusBar().showMessage("✅ GUI lista.")

        if os.path.exists("icon.ico"):
            self.setWindowIcon(QIcon("icon.ico"))

        self.connect_widgets_for_update()
        self.update_command_display()

    def connect_widgets_for_update(self):
        self._updating = True
        for key, widget in self.widgets.items():
            if isinstance(widget, QLineEdit):
                widget.textChanged.connect(self.update_command_display)
            elif isinstance(widget, QSpinBox):
                widget.valueChanged.connect(self.update_command_display)
            elif isinstance(widget, QDoubleSpinBox):
                widget.valueChanged.connect(self.update_command_display)
            elif isinstance(widget, QCheckBox):
                widget.stateChanged.connect(self.update_command_display)
            elif isinstance(widget, QComboBox):
                widget.currentTextChanged.connect(self.update_command_display)
        for cb in self.enum_checks.values():
            cb.stateChanged.connect(self.update_command_display)
        self.tamper_list.itemSelectionChanged.connect(self.update_command_display)
        self.technique_list.itemSelectionChanged.connect(self.update_command_display)
        self._updating = False

    def update_command_display(self):
        if self._updating:
            return
        cmd = self.build_command()
        command_text = " ".join(cmd) if len(cmd) > 2 else "Esperando configuración..."
        self.command_bar.setText(command_text)

    def setup_profiles(self):
        self.profiles_dir = os.path.join(os.getcwd(), "profiles")
        if not os.path.exists(self.profiles_dir):
            os.makedirs(self.profiles_dir)

        default_profiles = {
            "stealth": {"delay": 1.0, "timeout": 30, "retries": 3, "level": 1, "risk": 1, "threads": 1,
                        "time_sec": 5, "crawl": 0, "start": 0, "stop": 0, "technique_list": ["B"],
                        "tamper_list": ["randomcase"], "enumerate": ["dbs"]},
            "bazoka": {"delay": 0, "timeout": 30, "retries": 5, "level": 5, "risk": 3, "threads": 5,
                       "time_sec": 5, "crawl": 0, "start": 0, "stop": 0, "technique_list": ["B", "E", "U", "S", "T", "Q"],
                       "tamper_list": [], "enumerate": ["dbs", "tables", "columns", "dump"]},
            "paranoia": {"delay": 0.1, "timeout": 45, "retries": 5, "level": 5, "risk": 2, "threads": 1,
                         "time_sec": 5, "crawl": 0, "start": 0, "stop": 0, "technique_list": ["B", "E", "T"],
                         "tamper_list": ["space2comment", "randomcase", "charencode"], "enumerate": ["dbs", "tables"]},
            "takeover": {"delay": 0, "timeout": 30, "retries": 5, "level": 5, "risk": 3, "threads": 3,
                         "time_sec": 5, "crawl": 0, "start": 0, "stop": 0, "technique_list": ["B", "E", "U", "S", "T", "Q"],
                         "tamper_list": [], "enumerate": ["dbs", "tables", "columns", "dump"]}
        }

        for name, profile in default_profiles.items():
            filepath = os.path.join(self.profiles_dir, f"{name}.json")
            if not os.path.exists(filepath):
                with open(filepath, 'w') as f:
                    json.dump(profile, f, indent=2, ensure_ascii=False)

    def create_target_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        self.add_form_row(layout, "🎯 URL Objetivo:", "target_url", QLineEdit())
        self.add_form_row(layout, "💾 DB Directa:", "direct", QLineEdit())
        self.add_browse_button(layout, "direct")
        self.add_form_row(layout, "📄 Log File:", "logfile", QLineEdit())
        self.add_browse_button(layout, "logfile")
        self.add_form_row(layout, "📦 Archivo Múltiple:", "bulkfile", QLineEdit())
        self.add_browse_button(layout, "bulkfile")
        self.add_form_row(layout, "📨 Request File:", "requestfile", QLineEdit())
        self.add_browse_button(layout, "requestfile")
        self.add_form_row(layout, "🔍 Google Dork:", "googledork", QLineEdit())
        self.add_form_row(layout, "🔢 Página Google:", "gpage", QSpinBox())
        self.widgets["gpage"].setRange(1, 999)
        self.widgets["gpage"].setValue(1)
        self.add_form_row(layout, "⚙️ Config File:", "configfile", QLineEdit())
        self.add_browse_button(layout, "configfile")
        tab.setLayout(layout)
        self.tabs.addTab(tab, "🎯 Objetivo")

    def create_request_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        self.add_form_row_with_checkbox(layout, "⏱️ Delay (seg):", "delay", QDoubleSpinBox(), 0.0, 10.0, 0.5)
        self.add_form_row_with_checkbox(layout, "⏳ Timeout (seg):", "timeout", QSpinBox(), 1, 300, 30)
        self.add_form_row_with_checkbox(layout, "🔁 Retries:", "retries", QSpinBox(), 0, 10, 3)
        self.add_form_row(layout, "👤 User-Agent:", "agent", QLineEdit())
        self.add_form_row(layout, "🌐 Host:", "host", QLineEdit())
        self.add_form_row(layout, "↩️ Referer:", "referer", QLineEdit())
        self.add_form_row(layout, "🍪 Cookie:", "cookie", QLineEdit())
        self.add_form_row(layout, "📎 Headers Extra:", "headers", QLineEdit())
        self.add_form_row(layout, "📤 POST Data (--data):", "data", QLineEdit())
        self.add_form_row(layout, "📤 Método HTTP:", "method", QLineEdit())

        auth_layout = QHBoxLayout()
        auth_layout.addWidget(QLabel("🔐 Auth Type"))
        auth_type = QComboBox()
        auth_type.addItems(["", "Basic", "Digest", "NTLM", "PKI"])
        self.widgets["auth_type"] = auth_type
        auth_layout.addWidget(auth_type)
        layout.addLayout(auth_layout)

        self.add_form_row(layout, "🔑 Auth Cred:", "auth_cred", QLineEdit())
        self.add_form_row(layout, "📡 Proxy:", "proxy", QLineEdit())
        self.add_form_row(layout, "🧩 Tor:", "tor", QCheckBox("Usar red Tor"))
        self.add_form_row(layout, "📱 Mobile:", "mobile", QCheckBox("Imitar móvil"))
        self.add_form_row(layout, "🎲 Random Agent:", "random_agent", QCheckBox("Usar agente aleatorio"))
        layout.addStretch()
        tab.setLayout(layout)
        self.tabs.addTab(tab, "📡 Petición")

    def create_optimization_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        self.add_form_row_with_checkbox(layout, "🔗 Keep-Alive:", "keep_alive", QCheckBox("Conexiones persistentes"))
        self.add_form_row_with_checkbox(layout, "👻 Null Connection:", "null_connection", QCheckBox("Sin cuerpo de respuesta"))
        self.add_form_row(layout, "🧵 Hilos:", "threads", QSpinBox())
        self.widgets["threads"].setRange(1, 10)
        self.widgets["threads"].setValue(1)
        layout.addStretch()
        tab.setLayout(layout)
        self.tabs.addTab(tab, "⚙️ Optimización")

    def create_injection_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        self.add_form_row(layout, "🧪 Parámetro a probar (-p):", "testparameter", QLineEdit())
        self.add_form_row(layout, "🚫 Saltar parámetro:", "skip", QLineEdit())
        dbms_combo = QComboBox()
        dbms_combo.addItems(["", "mysql", "postgresql", "mssql", "oracle", "sqlite", "access", "db2", "firebird", "sybase", "maxdb", "informix", "mariadb"])
        self.add_form_row(layout, "🛠️ DBMS:", "dbms", dbms_combo)
        self.add_form_row(layout, "🖥️ OS:", "os", QLineEdit())
        self.add_form_row(layout, "➕ Prefijo:", "prefix", QLineEdit())
        self.add_form_row(layout, "➖ Sufijo:", "suffix", QLineEdit())
        tamper_group = QGroupBox("🎭 Scripts de Ofuscación (Tamper)")
        tamper_layout = QVBoxLayout()
        self.tamper_list = QListWidget()
        self.tamper_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.tamper_list.addItems(self.tamper_scripts)
        tamper_layout.addWidget(self.tamper_list)
        tamper_group.setLayout(tamper_layout)
        layout.addWidget(tamper_group)
        layout.addStretch()
        tab.setLayout(layout)
        self.tabs.addTab(tab, "💉 Inyección")

    def create_detection_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        self.add_form_row_with_checkbox(layout, "🔍 Level (1-5):", "level", QSpinBox(), 1, 5, 1)
        self.add_form_row_with_checkbox(layout, "⚠️ Risk (1-3):", "risk", QSpinBox(), 1, 3, 1)
        self.add_form_row(layout, "✅ String Verdadero:", "string", QLineEdit())
        self.add_form_row(layout, "❌ String Falso:", "not_string", QLineEdit())
        self.add_form_row(layout, "🔢 Código HTTP:", "code", QLineEdit())
        self.add_form_row_with_checkbox(layout, "🧠 Smart Mode:", "smart", QCheckBox("Solo pruebas si hay indicios"))
        layout.addStretch()
        tab.setLayout(layout)
        self.tabs.addTab(tab, "🔍 Detección")

    def create_techniques_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        technique_group = QGroupBox("⚔️ Técnicas de Inyección")
        t_layout = QVBoxLayout()
        self.technique_list = QListWidget()
        self.technique_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        techniques = [("B", "Boolean-based blind"), ("E", "Error-based"), ("U", "Union query-based"),
                      ("S", "Stacked queries"), ("T", "Time-based blind"), ("Q", "Inline queries")]
        for code, desc in techniques:
            self.technique_list.addItem(f"{code} - {desc}")
        t_layout.addWidget(self.technique_list)
        technique_group.setLayout(t_layout)
        layout.addWidget(technique_group)

        self.add_form_row(layout, "⏱️ Time-Sec:", "time_sec", QSpinBox())
        self.widgets["time_sec"].setRange(1, 30)
        self.widgets["time_sec"].setValue(5)

        self.add_form_row(layout, "🔀 Union Cols:", "union_cols", QLineEdit())
        self.add_form_row(layout, "🟥 Union Char:", "union_char", QLineEdit())
        self.add_form_row(layout, "🌐 DNS Domain:", "dns_domain", QLineEdit())
        layout.addStretch()
        tab.setLayout(layout)
        self.tabs.addTab(tab, "🧪 Técnicas")

    def create_enumeration_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        enum = QGroupBox("Enumeración")
        e_layout = QVBoxLayout()
        opts = [("banner", "Obtener banner DBMS"), ("current_user", "Usuario actual"), ("current_db", "Base de datos actual"),
                ("hostname", "Nombre del host"), ("is_dba", "¿Es DBA?"), ("users", "Listar usuarios"),
                ("passwords", "Listar contraseñas"), ("privileges", "Listar privilegios"), ("roles", "Listar roles"),
                ("dbs", "Listar bases de datos"), ("tables", "Listar tablas"), ("columns", "Listar columnas"),
                ("schema", "Esquema completo"), ("count", "Contar entradas"), ("dump", "Extraer datos"),
                ("dump_all", "Extraer todo"), ("search", "Buscar en DBs"), ("statements", "Consultas SQL activas"),
                ("sql_shell", "Shell SQL interactiva")]
        for key, label in opts:
            cb = QCheckBox(label)
            e_layout.addWidget(cb)
            self.enum_checks[key] = cb
        enum.setLayout(e_layout)
        layout.addWidget(enum)

        self.add_form_row(layout, "📚 DB:", "db", QLineEdit())
        self.add_form_row(layout, "📋 Tabla:", "tbl", QLineEdit())
        self.add_form_row(layout, "🧩 Columna:", "col", QLineEdit())
        self.add_form_row(layout, "👨 Usuario:", "user", QLineEdit())
        self.add_form_row(layout, "FilterWhere:", "where", QLineEdit())

        self.add_form_row(layout, "⏩ Inicio:", "start", QSpinBox())
        self.widgets["start"].setRange(0, 99999)
        self.widgets["start"].setValue(0)

        self.add_form_row(layout, "⏹️ Fin:", "stop", QSpinBox())
        self.widgets["stop"].setRange(1, 99999)
        self.widgets["stop"].setValue(0)

        layout.addStretch()
        tab.setLayout(layout)
        self.tabs.addTab(tab, "📊 Enumeración")

    def create_os_access_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        self.add_form_row(layout, "💻 Comando OS:", "os_cmd", QLineEdit())
        self.add_form_row(layout, "🖥️ OS Shell:", "os_shell", QCheckBox("Abrir shell interactiva"))
        self.add_form_row(layout, "🧨 OS Pwn:", "os_pwn", QCheckBox("Meterpreter / VNC"))
        self.add_form_row(layout, "🔧 Priv Esc:", "priv_esc", QCheckBox("Escalada de privilegios"))
        self.add_form_row(layout, "📁 MSF Path:", "msf_path", QLineEdit())
        self.add_form_row(layout, "📁 Temp Path:", "tmp_path", QLineEdit())
        layout.addStretch()
        tab.setLayout(layout)
        self.tabs.addTab(tab, "💻 Acceso al OS")

    def create_file_access_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        self.add_form_row(layout, "📄 Leer archivo:", "file_read", QLineEdit())
        self.add_form_row(layout, "📥 Escribir archivo:", "file_write", QLineEdit())
        self.add_form_row(layout, "📤 Destino remoto:", "file_dest", QLineEdit())
        layout.addStretch()
        tab.setLayout(layout)
        self.tabs.addTab(tab, "📂 Acceso a Archivos")

    def create_registry_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        reg_group = QGroupBox("Registro Windows")
        r_layout = QVBoxLayout()
        r_layout.addWidget(QLabel("Operaciones de registro (solo Windows)"))
        self.add_form_row(r_layout, "🔑 Leer:", "reg_read", QCheckBox("Leer clave"))
        self.add_form_row(r_layout, "🖊️ Escribir:", "reg_add", QCheckBox("Escribir clave"))
        self.add_form_row(r_layout, "🗑️ Borrar:", "reg_del", QCheckBox("Eliminar clave"))
        self.add_form_row(r_layout, "Clave:", "reg_key", QLineEdit())
        self.add_form_row(r_layout, "Valor:", "reg_value", QLineEdit())
        self.add_form_row(r_layout, "Datos:", "reg_data", QLineEdit())
        self.add_form_row(r_layout, "Tipo:", "reg_type", QLineEdit())
        reg_group.setLayout(r_layout)
        layout.addWidget(reg_group)
        layout.addStretch()
        tab.setLayout(layout)
        self.tabs.addTab(tab, "🪟 Registro")

    def create_general_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        self.add_form_row(layout, "💾 Session:", "sessionfile", QLineEdit())
        self.add_form_row(layout, "📊 Traffic Log:", "trafficfile", QLineEdit())
        self.add_form_row(layout, "🗂️ Output Dir:", "output_dir", QLineEdit())
        self.add_browse_button(layout, "output_dir", is_dir=True)
        self.add_form_row(layout, "🧹 Flush Session:", "flush_session", QCheckBox("Limpiar sesión"))
        self.add_form_row(layout, "🌐 Crawl Depth:", "crawl", QSpinBox())
        self.widgets["crawl"].setRange(0, 10)
        self.widgets["crawl"].setValue(0)
        self.add_form_row(layout, "🚷 Crawl Exclude:", "crawl_exclude", QLineEdit())
        self.add_form_row(layout, "📦 Batch Mode:", "batch", QCheckBox("No preguntar (batch)"))
        layout.addStretch()
        tab.setLayout(layout)
        self.tabs.addTab(tab, "⚙️ General")

    def create_misc_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        self.add_form_row(layout, "🔄 Update:", "update", QCheckBox("Actualizar sqlmap"))
        self.add_form_row(layout, "🧙 Wizard:", "wizard", QCheckBox("Modo asistente"))
        self.add_form_row(layout, "🔔 Beep:", "beep", QCheckBox("Hacer sonido al encontrar SQLi"))
        self.add_form_row(layout, "📋 List Tampers:", "list_tampers", QCheckBox("Listar scripts de ofuscación"))
        self.add_form_row(layout, "🧹 Purge:", "purge", QCheckBox("Eliminar datos temporales"))
        layout.addStretch()
        tab.setLayout(layout)
        self.tabs.addTab(tab, "🧩 Misc")

    def create_console_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        self.output = QPlainTextEdit()
        self.output.setReadOnly(True)
        self.output.setFont(QFont("Consolas", 10))
        layout.addWidget(self.output)
        tab.setLayout(layout)
        self.tabs.addTab(tab, "🖥️ Consola")

    def create_results_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        self.results_tabs = QInnerTabWidget()
        layout.addWidget(self.results_tabs)
        clear_btn = QPushButton("🗑️ Limpiar resultados")
        clear_btn.clicked.connect(self.clear_results)
        layout.addWidget(clear_btn)
        tab.setLayout(layout)
        self.tabs.addTab(tab, "📊 Resultados")

    def clear_results(self):
        self.results_tabs.clear()

    def add_form_row(self, parent_layout, label, key, widget, placeholder=""):
        row = QHBoxLayout()
        row.addWidget(QLabel(label))
        if isinstance(widget, QLineEdit):
            widget.setPlaceholderText(placeholder)
        row.addWidget(widget, 1)
        parent_layout.addLayout(row)
        self.widgets[key] = widget

    def add_form_row_with_checkbox(self, parent_layout, label, key, widget, min_val=None, max_val=None, default_val=None):
        row = QHBoxLayout()
        checkbox = QCheckBox("Usar")
        row.addWidget(checkbox)
        row.addWidget(QLabel(label))
        if isinstance(widget, QSpinBox):
            widget.setRange(min_val, max_val)
            widget.setValue(default_val)
        elif isinstance(widget, QDoubleSpinBox):
            widget.setRange(min_val, max_val)
            widget.setValue(default_val)
            widget.setSingleStep(0.1)
        row.addWidget(widget, 1)
        parent_layout.addLayout(row)
        self.widgets[key] = widget
        self.widgets[f"chk_{key}"] = checkbox

    def add_browse_button(self, parent_layout, key, is_dir=False):
        btn = QPushButton("📁")
        btn.setFixedWidth(40)
        btn.clicked.connect(lambda: self.browse_file(key, is_dir))
        last = parent_layout.itemAt(parent_layout.count() - 1)
        if isinstance(last, QHBoxLayout):
            last.addWidget(btn)

    def browse_file(self, key, is_dir=False):
        if is_dir:
            folder = QFileDialog.getExistingDirectory(self, "Seleccionar carpeta")
            if folder:
                self.widgets[key].setText(folder)
        else:
            file, _ = QFileDialog.getOpenFileName(self, "Seleccionar archivo")
            if file:
                self.widgets[key].setText(file)

    def build_command(self):
        cmd = ["python", "sqlmap.py"]

        if self.widgets["target_url"].text():
            cmd += ["-u", self.widgets["target_url"].text()]
        if self.widgets.get("direct") and self.widgets["direct"].text():
            cmd += ["-d", self.widgets["direct"].text()]
        if self.widgets.get("logfile") and self.widgets["logfile"].text():
            cmd += ["-l", self.widgets["logfile"].text()]
        if self.widgets.get("bulkfile") and self.widgets["bulkfile"].text():
            cmd += ["-m", self.widgets["bulkfile"].text()]
        if self.widgets.get("requestfile") and self.widgets["requestfile"].text():
            cmd += ["-r", self.widgets["requestfile"].text()]
        if self.widgets.get("googledork") and self.widgets["googledork"].text():
            cmd += ["-g", self.widgets["googledork"].text()]
        if self.widgets["gpage"].value() > 1:
            cmd += ["--gpage", str(self.widgets["gpage"].value())]
        if self.widgets.get("configfile") and self.widgets["configfile"].text():
            cmd += ["-c", self.widgets["configfile"].text()]

        if self.widgets.get("chk_delay") and self.widgets["chk_delay"].isChecked():
            cmd += ["--delay", str(self.widgets["delay"].value())]
        if self.widgets.get("chk_timeout") and self.widgets["chk_timeout"].isChecked():
            cmd += ["--timeout", str(self.widgets["timeout"].value())]
        if self.widgets.get("chk_retries") and self.widgets["chk_retries"].isChecked():
            cmd += ["--retries", str(self.widgets["retries"].value())]

        if self.widgets.get("agent") and self.widgets["agent"].text():
            cmd += ["--user-agent", self.widgets["agent"].text()]
        if self.widgets.get("host") and self.widgets["host"].text():
            cmd += ["--host", self.widgets["host"].text()]
        if self.widgets.get("referer") and self.widgets["referer"].text():
            cmd += ["--referer", self.widgets["referer"].text()]
        if self.widgets.get("cookie") and self.widgets["cookie"].text():
            cmd += ["--cookie", self.widgets["cookie"].text()]
        if self.widgets.get("headers") and self.widgets["headers"].text().strip():
            cmd += ["--headers", self.widgets["headers"].text().strip()]
        if self.widgets.get("data") and self.widgets["data"].text():
            cmd += ["--data", self.widgets["data"].text()]
        if self.widgets.get("method") and self.widgets["method"].text():
            cmd += ["--method", self.widgets["method"].text()]

        if self.widgets.get("auth_type") and self.widgets["auth_type"].currentText():
            cmd += ["--auth-type", self.widgets["auth_type"].currentText()]
        if self.widgets.get("auth_cred") and self.widgets["auth_cred"].text():
            cmd += ["--auth-cred", self.widgets["auth_cred"].text()]
        if self.widgets.get("proxy") and self.widgets["proxy"].text():
            cmd += ["--proxy", self.widgets["proxy"].text()]
        if self.widgets.get("tor") and self.widgets["tor"].isChecked():
            cmd.append("--tor")
        if self.widgets.get("mobile") and self.widgets["mobile"].isChecked():
            cmd.append("--mobile")
        if self.widgets.get("random_agent") and self.widgets["random_agent"].isChecked():
            cmd.append("--random-agent")

        if self.widgets.get("chk_keep_alive") and self.widgets["chk_keep_alive"].isChecked():
            cmd.append("--keep-alive")
        if self.widgets.get("chk_null_connection") and self.widgets["chk_null_connection"].isChecked():
            cmd.append("--null-connection")
        if self.widgets.get("threads") and self.widgets["threads"].value() > 1:
            cmd += ["--threads", str(self.widgets["threads"].value())]

        if self.widgets.get("testparameter") and self.widgets["testparameter"].text():
            cmd += ["-p", self.widgets["testparameter"].text()]
        if self.widgets.get("skip") and self.widgets["skip"].text():
            cmd += ["--skip", self.widgets["skip"].text()]
        if self.widgets.get("dbms") and self.widgets["dbms"].currentText():
            cmd += ["--dbms", self.widgets["dbms"].currentText()]
        if self.widgets.get("os") and self.widgets["os"].text():
            cmd += ["--os", self.widgets["os"].text()]
        if self.widgets.get("prefix") and self.widgets["prefix"].text():
            cmd += ["--prefix", self.widgets["prefix"].text()]
        if self.widgets.get("suffix") and self.widgets["suffix"].text():
            cmd += ["--suffix", self.widgets["suffix"].text()]

        selected_tampers = [self.tamper_list.item(i).text() for i in range(self.tamper_list.count()) if self.tamper_list.item(i).isSelected()]
        if selected_tampers:
            cmd += ["--tamper=" + ",".join(selected_tampers)]

        if self.widgets.get("chk_level") and self.widgets["chk_level"].isChecked():
            cmd += ["--level", str(self.widgets["level"].value())]
        if self.widgets.get("chk_risk") and self.widgets["chk_risk"].isChecked():
            cmd += ["--risk", str(self.widgets["risk"].value())]
        if self.widgets.get("string") and self.widgets["string"].text():
            cmd += ["--string", self.widgets["string"].text()]
        if self.widgets.get("not_string") and self.widgets["not_string"].text():
            cmd += ["--not-string", self.widgets["not_string"].text()]
        if self.widgets.get("code") and self.widgets["code"].text():
            cmd += ["--code", self.widgets["code"].text()]
        if self.widgets.get("chk_smart") and self.widgets["chk_smart"].isChecked():
            cmd.append("--smart")

        selected_techniques = [self.technique_list.item(i).text().split(" - ")[0] 
                               for i in range(self.technique_list.count()) 
                               if self.technique_list.item(i).isSelected()]
        if selected_techniques:
            cmd += ["--technique", "".join(selected_techniques)]

        if self.widgets.get("time_sec") and self.widgets["time_sec"].value() != 5:
            cmd += ["--time-sec", str(self.widgets["time_sec"].value())]

        if self.widgets.get("union_cols") and self.widgets["union_cols"].text():
            cmd += ["--union-cols", self.widgets["union_cols"].text()]
        if self.widgets.get("union_char") and self.widgets["union_char"].text():
            cmd += ["--union-char", self.widgets["union_char"].text()]
        if self.widgets.get("dns_domain") and self.widgets["dns_domain"].text():
            cmd += ["--dns-domain", self.widgets["dns_domain"].text()]

        for key, cb in self.enum_checks.items():
            if cb.isChecked():
                cmd.append(f"--{key}")

        if self.widgets.get("db") and self.widgets["db"].text():
            cmd += ["-D", self.widgets["db"].text()]
        if self.widgets.get("tbl") and self.widgets["tbl"].text():
            cmd += ["-T", self.widgets["tbl"].text()]
        if self.widgets.get("col") and self.widgets["col"].text():
            cmd += ["-C", self.widgets["col"].text()]
        if self.widgets.get("user") and self.widgets["user"].text():
            cmd += ["-U", self.widgets["user"].text()]
        if self.widgets.get("where") and self.widgets["where"].text():
            cmd += ["--where", self.widgets["where"].text()]

        if self.widgets.get("start") and self.widgets["start"].value() > 0:
            cmd += ["--start", str(self.widgets["start"].value())]
        if self.widgets.get("stop") and self.widgets["stop"].value() > 1:
            cmd += ["--stop", str(self.widgets["stop"].value())]

        if self.widgets.get("file_read") and self.widgets["file_read"].text():
            cmd += ["--file-read", self.widgets["file_read"].text()]
        if self.widgets.get("file_write") and self.widgets["file_write"].text():
            cmd += ["--file-write", self.widgets["file_write"].text()]
        if self.widgets.get("file_dest") and self.widgets["file_dest"].text():
            cmd += ["--file-dest", self.widgets["file_dest"].text()]

        if self.widgets.get("os_cmd") and self.widgets["os_cmd"].text():
            cmd += ["--os-cmd", self.widgets["os_cmd"].text()]
        if self.widgets.get("os_shell") and self.widgets["os_shell"].isChecked():
            cmd.append("--os-shell")
        if self.widgets.get("os_pwn") and self.widgets["os_pwn"].isChecked():
            cmd.append("--os-pwn")
        if self.widgets.get("priv_esc") and self.widgets["priv_esc"].isChecked():
            cmd.append("--priv-esc")

        if self.widgets.get("msf_path") and self.widgets["msf_path"].text():
            cmd += ["--msf-path", self.widgets["msf_path"].text()]
        if self.widgets.get("tmp_path") and self.widgets["tmp_path"].text():
            cmd += ["--tmp-path", self.widgets["tmp_path"].text()]

        if self.widgets.get("reg_read") and self.widgets["reg_read"].isChecked():
            cmd.append("--reg-read")
        if self.widgets.get("reg_add") and self.widgets["reg_add"].isChecked():
            cmd.append("--reg-add")
        if self.widgets.get("reg_del") and self.widgets["reg_del"].isChecked():
            cmd.append("--reg-del")
        if self.widgets.get("reg_key") and self.widgets["reg_key"].text():
            cmd += ["--reg-key", self.widgets["reg_key"].text()]
        if self.widgets.get("reg_value") and self.widgets["reg_value"].text():
            cmd += ["--reg-value", self.widgets["reg_value"].text()]
        if self.widgets.get("reg_data") and self.widgets["reg_data"].text():
            cmd += ["--reg-data", self.widgets["reg_data"].text()]
        if self.widgets.get("reg_type") and self.widgets["reg_type"].text():
            cmd += ["--reg-type", self.widgets["reg_type"].text()]

        if self.widgets.get("sessionfile") and self.widgets["sessionfile"].text():
            cmd += ["-s", self.widgets["sessionfile"].text()]
        if self.widgets.get("trafficfile") and self.widgets["trafficfile"].text():
            cmd += ["-t", self.widgets["trafficfile"].text()]
        if self.widgets.get("output_dir") and self.widgets["output_dir"].text():
            cmd += ["--output-dir", self.widgets["output_dir"].text()]
        if self.widgets.get("flush_session") and self.widgets["flush_session"].isChecked():
            cmd.append("--flush-session")
        if self.widgets.get("crawl") and self.widgets["crawl"].value() > 0:
            cmd += ["--crawl", str(self.widgets["crawl"].value())]
        if self.widgets.get("crawl_exclude") and self.widgets["crawl_exclude"].text():
            cmd += ["--crawl-exclude", self.widgets["crawl_exclude"].text()]
        if self.widgets.get("batch") and self.widgets["batch"].isChecked():
            cmd.append("--batch")

        if self.widgets.get("update") and self.widgets["update"].isChecked():
            cmd.append("--update")
        if self.widgets.get("wizard") and self.widgets["wizard"].isChecked():
            cmd.append("--wizard")
        if self.widgets.get("beep") and self.widgets["beep"].isChecked():
            cmd.append("--beep")
        if self.widgets.get("list_tampers") and self.widgets["list_tampers"].isChecked():
            cmd.append("--list-tampers")
        if self.widgets.get("purge") and self.widgets["purge"].isChecked():
            cmd.append("--purge")

        return cmd

    def run_sqlmap(self):
        cmd = self.build_command()
        if len(cmd) == 2:
            self.output.appendPlainText("❌ No se especificó objetivo.")
            return
        self.output.appendPlainText("🚀 Ejecutando: " + " ".join(cmd))
        self.output.appendPlainText("-" * 60)

        self.process = QProcess()
        self.process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        self.process.readyRead.connect(self.read_output)
        self.process.finished.connect(self.process_finished)
        self.run_button.setEnabled(False)
        self.stop_button.setEnabled(True)
        self.process.start(cmd[0], cmd[1:])

    def read_output(self):
        if self.process:
            data = self.process.readAll().data().decode(errors='replace')
            self.output.appendPlainText(data.strip())

    def process_finished(self):
        self.output.appendPlainText("\n✅ Proceso finalizado.")
        self.run_button.setEnabled(True)
        self.stop_button.setEnabled(False)

    def stop_sqlmap(self):
        if self.process and self.process.state() == QProcess.ProcessState.Running:
            self.process.terminate()
            QTimer.singleShot(2000, self.force_kill)

    def force_kill(self):
        if self.process and self.process.state() == QProcess.ProcessState.Running:
            self.process.kill()
            self.output.appendPlainText("\n🛑 Proceso detenido forzosamente.")

    def clear_output(self):
        self.output.clear()

    def export_command(self):
        cmd = self.build_command()
        clipboard = QApplication.clipboard()
        clipboard.setText(" ".join(cmd))
        self.output.appendPlainText("📋 Comando copiado al portapapeles")

    def reset_all(self):
        for key, widget in self.widgets.items():
            if isinstance(widget, QLineEdit):
                widget.clear()
            elif isinstance(widget, QSpinBox):
                widget.setValue(0)
            elif isinstance(widget, QDoubleSpinBox):
                widget.setValue(0.0)
            elif isinstance(widget, QCheckBox):
                widget.setChecked(False)
            elif isinstance(widget, QComboBox):
                widget.setCurrentIndex(0)
        for cb in self.enum_checks.values():
            cb.setChecked(False)
        self.tamper_list.clearSelection()
        self.technique_list.clearSelection()
        self.results_tabs.clear()
        self.output.clear()
        self.command_bar.clear()

    # ==================== MÉTODOS CORREGIDOS ====================

    def save_profile(self):
        name, ok = QInputDialog.getText(self, "Guardar Perfil", "Nombre del perfil:")
        if not ok or not name:
            return
        profile = {}
        for key, widget in self.widgets.items():
            if key.startswith("chk_"):
                continue
            if isinstance(widget, QLineEdit):
                profile[key] = widget.text()
            elif isinstance(widget, (QSpinBox, QDoubleSpinBox)):
                profile[key] = widget.value()
            elif isinstance(widget, QCheckBox):
                profile[key] = widget.isChecked()
            elif isinstance(widget, QComboBox):
                profile[key] = widget.currentText()

        selected_tampers = [self.tamper_list.item(i).text() for i in range(self.tamper_list.count()) if self.tamper_list.item(i).isSelected()]
        selected_techniques = [self.technique_list.item(i).text().split(" - ")[0] for i in range(self.technique_list.count()) if self.technique_list.item(i).isSelected()]

        profile["tamper_list"] = selected_tampers
        profile["technique_list"] = selected_techniques
        for key, cb in self.enum_checks.items():
            profile[f"enum_{key}"] = cb.isChecked()

        filepath = os.path.join(self.profiles_dir, f"{name}.json")
        with open(filepath, 'w') as f:
            json.dump(profile, f, indent=2, ensure_ascii=False)

        self.output.appendPlainText(f"💾 Perfil '{name}' guardado")

    def load_profile(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Cargar Perfil", self.profiles_dir, "JSON Files (*.json)")
        if not files:
            return
        try:
            with open(files[0], 'r') as f:
                profile = json.load(f)

            for key, value in profile.items():
                if key.startswith("enum_"):
                    checkbox_name = key[5:]
                    if checkbox_name in self.enum_checks:
                        self.enum_checks[checkbox_name].setChecked(value)
                elif key == "tamper_list":
                    self.tamper_list.clearSelection()
                    for script in value:
                        for i in range(self.tamper_list.count()):
                            if self.tamper_list.item(i).text() == script:
                                self.tamper_list.item(i).setSelected(True)
                elif key == "technique_list":
                    self.technique_list.clearSelection()
                    for tech in value:
                        for i in range(self.technique_list.count()):
                            if self.technique_list.item(i).text().startswith(tech):
                                self.technique_list.item(i).setSelected(True)
                elif key in self.widgets:
                    widget = self.widgets[key]
                    if isinstance(widget, QLineEdit):
                        widget.setText(str(value))
                    elif isinstance(widget, (QSpinBox, QDoubleSpinBox)):
                        widget.setValue(value)
                    elif isinstance(widget, QCheckBox):
                        widget.setChecked(value)
                    elif isinstance(widget, QComboBox):
                        widget.setCurrentText(str(value))

            self.update_command_display()
            self.statusBar().showMessage("Perfil cargado correctamente", 2000)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo cargar el perfil:\n{e}")

    def load_wizard(self, profile_name):
        filepath = os.path.join(self.profiles_dir, f"{profile_name}.json")
        if not os.path.exists(filepath):
            self.output.appendPlainText(f"❌ Perfil '{profile_name}' no encontrado.")
            return

        try:
            with open(filepath, 'r') as f:
                profile = json.load(f)

            current_url = self.widgets["target_url"].text()

            for key, value in profile.items():
                if key == "target_url":
                    continue
                if key in self.widgets:
                    widget = self.widgets[key]
                    if isinstance(widget, QLineEdit):
                        widget.setText(str(value))
                    elif isinstance(widget, (QSpinBox, QDoubleSpinBox)):
                        widget.setValue(value)
                    elif isinstance(widget, QCheckBox):
                        widget.setChecked(value)
                    elif isinstance(widget, QComboBox):
                        widget.setCurrentText(str(value))

            if "technique_list" in profile:
                self.technique_list.clearSelection()
                for tech in profile["technique_list"]:
                    for i in range(self.technique_list.count()):
                        if self.technique_list.item(i).text().startswith(tech):
                            self.technique_list.item(i).setSelected(True)

            if "tamper_list" in profile:
                self.tamper_list.clearSelection()
                for tamper in profile["tamper_list"]:
                    for i in range(self.tamper_list.count()):
                        if self.tamper_list.item(i).text() == tamper:
                            self.tamper_list.item(i).setSelected(True)

            if "enumerate" in profile:
                for key in self.enum_checks:
                    self.enum_checks[key].setChecked(key in profile["enumerate"])

            if current_url:
                self.widgets["target_url"].setText(current_url)

            self.update_command_display()
            self.statusBar().showMessage(f"✅ Modo '{profile_name}' aplicado (URL mantenida)", 2500)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo aplicar el modo '{profile_name}': {e}")

    def highlight_button(self, button):
        original = button.styleSheet()
        button.setStyleSheet("background-color: #ff6b35; font-weight: bold;")
        QTimer.singleShot(1000, lambda: button.setStyleSheet(original))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SqlmapGUI()
    window.show()
    sys.exit(app.exec())