
        super().__init__()
        self.setWindowTitle("Optimal Delivery Allocation System")
        self.resize(1000, 900)
        self.setup_ui()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(10)

        # --- 1. Header (Fixed) ---
        title = QLabel("Optimal Delivery Allocation System")
        font = title.font()
        font.setPointSize(16)
        font.setBold(True)
        title.setFont(font)
        
        subtitle = QLabel("Algorithm: North West Corner Method + MODI Optimization")
        subtitle.setStyleSheet("color: gray;")
        
        main_layout.addWidget(title)
        main_layout.addWidget(subtitle)

        # --- 2. Configuration (Fixed) ---
        config_group = QGroupBox("Configuration")
        config_layout = QHBoxLayout(config_group)
        
        config_layout.addWidget(QLabel("Number of Warehouses:"))
        self.spin_rows = QSpinBox()
        self.spin_rows.setRange(2, 50)
        self.spin_rows.setValue(3)
        self.spin_rows.setFixedWidth(60)
        config_layout.addWidget(self.spin_rows)

        config_layout.addSpacing(20)

        config_layout.addWidget(QLabel("Number of Destinations:"))
        self.spin_cols = QSpinBox()
        self.spin_cols.setRange(2, 50)
        self.spin_cols.setValue(3)
        self.spin_cols.setFixedWidth(60)
        config_layout.addWidget(self.spin_cols)

        config_layout.addStretch()

        self.btn_gen = QPushButton("Generate Empty Grid")
        self.btn_gen.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_gen.clicked.connect(self.generate_grid)
        config_layout.addWidget(self.btn_gen)

        self.btn_random = QPushButton("Random Balanced Data")
        self.btn_random.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_random.clicked.connect(self.generate_random_data)
        config_layout.addWidget(self.btn_random)
        
        main_layout.addWidget(config_group)

        # --- 3. SPLITTER (Three Sections) ---
        self.splitter = QSplitter(Qt.Orientation.Vertical)
        
        # --- Section A: The Table (Top) ---
        self.table = QTableWidget()
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.splitter.addWidget(self.table)

        # --- Section B: The Button (Fixed Height Middle) ---
        self.btn_container = QWidget()
        btn_layout = QVBoxLayout(self.btn_container)
        
        btn_layout.setContentsMargins(0, 5, 0, 5) 
        btn_layout.setSpacing(0)
        
        self.btn_solve = QPushButton("Calculate Optimal Allocation")
        self.btn_solve.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_font = self.btn_solve.font()
        btn_font.setPointSize(11)
        btn_font.setBold(True)
        self.btn_solve.setFont(btn_font)
        
        self.btn_solve.setFixedHeight(40)
        self.btn_solve.clicked.connect(self.run_solver)
        
        btn_layout.addWidget(self.btn_solve)
        self.btn_container.setFixedHeight(50)
        
        self.splitter.addWidget(self.btn_container)

        # --- Section C: Text Output (Bottom) ---
        self.txt_output = QTextEdit()
        self.txt_output.setReadOnly(True)
        self.txt_output.setPlaceholderText("Results will appear here...")
        self.splitter.addWidget(self.txt_output)

        # Splitter Configuration
        self.splitter.setStretchFactor(0, 5) 
        self.splitter.setStretchFactor(1, 0)
        self.splitter.setStretchFactor(2, 3)
        self.splitter.setCollapsible(1, False) 

        main_layout.addWidget(self.splitter)
        
        # Initialize
        self.generate_grid()

    def generate_grid(sel