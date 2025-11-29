import sys
import random
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QTableWidget, 
                             QTableWidgetItem, QTextEdit, QHeaderView, QMessageBox, 
                             QGroupBox, QSpinBox, QSplitter)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QColor, QBrush

# ==========================================
#  BACKEND LOGIC (Unchanged)
# ==========================================
class TransportationSolver:
    def __init__(self, costs, supply, demand):
        self.costs = costs
        self.supply = list(supply)
        self.demand = list(demand)
        self.rows = len(costs)
        self.cols = len(costs[0])
        self.allocation = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        self.logs = [] 

    def log(self, message, style="normal"):
        self.logs.append((message, style))

    def solve(self):
        self.log("Initializing Basic Feasible Solution (NWCM)...", "header")
        self.nwcm()
        initial_cost = self.calculate_total_cost()
        self.log(f"Initial BFS Cost: ${initial_cost}", "bold")

        iteration = 1
        while True:
            self.log(f"--- Optimization Iteration {iteration} ---", "header")
            self.fix_degeneracy()
            u, v = self.calculate_uv()
            
            if u is None: 
                self.log("Graph disconnected (Degeneracy error). Stopping.", "error")
                break

            min_d = 0
            entering_cell = None

            for r in range(self.rows):
                for c in range(self.cols):
                    if self.allocation[r][c] == 0:
                        d_val = self.costs[r][c] - (u[r] + v[c])
                        if d_val < min_d:
                            min_d = d_val
                            entering_cell = (r, c)

            if min_d >= -1e-9: 
                self.log("All opportunity costs >= 0. Solution is Optimal!", "success")
                break
            
            self.log(f"Negative opp. cost ({min_d}) at {entering_cell}. Improving...", "highlight")

            path = self.get_closed_loop(entering_cell)
            if not path:
                self.log("Closed loop not found. Stopping.", "error")
                break

            minus_cells_values = []
            for i in range(1, len(path), 2):
                r, c = path[i]
                minus_cells_values.append(self.allocation[r][c])
            
            theta = min(minus_cells_values)
            self.log(f"Shifting {theta} units along the loop.", "normal")

            for i, (r, c) in enumerate(path):
                if i % 2 == 0: self.allocation[r][c] += theta
                else: self.allocation[r][c] -= theta

            iteration += 1

        return self.allocation, round(self.calculate_total_cost(),0), self.logs

    def nwcm(self):
        r, c = 0, 0
        cur_supply, cur_demand = list(self.supply), list(self.demand)
        while r < self.rows and c < self.cols:
            qty = min(cur_supply[r], cur_demand[c])
            self.allocation[r][c] = qty
            cur_supply[r] -= qty
            cur_demand[c] -= qty
            if cur_supply[r] == 0: r += 1
            elif cur_demand[c] == 0: c += 1

    def calculate_total_cost(self):
        return sum(self.allocation[r][c] * self.costs[r][c] for r in range(self.rows) for c in range(self.cols))

    def fix_degeneracy(self):
        count = sum(1 for r in range(self.rows) for c in range(self.cols) if self.allocation[r][c] > 0)
        req = self.rows + self.cols - 1
        if count < req:
            for r in range(self.rows):
                for c in range(self.cols):
                    if self.allocation[r][c] == 0:
                        self.allocation[r][c] = 1e-10 
                        count += 1
                        if count == req: return

    def calculate_uv(self):
        u = [None] * self.rows
        v = [None] * self.cols
        u[0] = 0
        changed = True
        while changed:
            changed = False
            for r in range(self.rows):
                for c in range(self.cols):
                    if self.allocation[r][c] > 0 or self.allocation[r][c] == 1e-10:
                        if u[r] is not None and v[c] is None:
                            v[c] = self.costs[r][c] - u[r]
                            changed = True
                        elif u[r] is None and v[c] is not None:
                            u[r] = self.costs[r][c] - v[c]
                            changed = True
        if None in u or None in v: return None, None
        return u, v

    def get_closed_loop(self, start_node):
        def get_neighbors(curr, prev_dir):
            neighbors = []
            if prev_dir == 'H': 
                c = curr[1]
                for r in range(self.rows):
                    if r != curr[0] and (self.allocation[r][c] > 0 or self.allocation[r][c] == 1e-10):
                        neighbors.append(((r, c), 'V'))
            else: 
                r = curr[0]
                for c in range(self.cols):
                    if c != curr[1] and ((r,c) == start_node or self.allocation[r][c] > 0 or self.allocation[r][c] == 1e-10):
                        neighbors.append(((r, c), 'H'))
            return neighbors

        stack = [(start_node, [start_node], 'V')]
        while stack:
            curr, path, p_dir = stack.pop()
            for n_node, n_dir in get_neighbors(curr, p_dir):
                if n_node == start_node and len(path) >= 3: return path
                if n_node not in path: stack.append((n_node, path + [n_node], n_dir))
        return None

# ==========================================
#  RESIZABLE GUI
# ==========================================

class NativeTransportApp(QMainWindow):
    def __init__(self):
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

    def generate_grid(self):
        rows = self.spin_rows.value()
        cols = self.spin_cols.value()
        self._build_table_structure(rows, cols)
        
        for r in range(rows + 1):
            for c in range(cols + 1):
                if not self.table.item(r, c) or self.table.item(r,c).text() == "":
                     self._set_cell(r, c, "0")
        self._set_cell(rows,cols,"")

    def generate_random_data(self):
        rows = self.spin_rows.value()
        cols = self.spin_cols.value()
        self._build_table_structure(rows, cols)

        # Fill Costs
        for r in range(rows):
            for c in range(cols):
                self._set_cell(r, c, str(random.randint(10, 100)))

        # Fill Supply & Demand
        supplies = [random.randint(20, 100) for _ in range(rows)]
        demands = [random.randint(20, 100) for _ in range(cols)]

        # Balance
        diff = sum(supplies) - sum(demands)
        if diff > 0:
            demands[random.randint(0, cols - 1)] += diff
        elif diff < 0:
            supplies[random.randint(0, rows - 1)] += abs(diff)

        for r in range(rows):
            self._set_cell(r, cols, str(supplies[r]))
        for c in range(cols):
            self._set_cell(rows, c, str(demands[c]))

    def _build_table_structure(self, rows, cols):
        """Helper to setup headers and row/col counts"""
        self.table.setRowCount(rows + 1)
        self.table.setColumnCount(cols + 1)

        # 1. Set Default Headers (Will be updated dynamically)
        h_labels = [f"Dest {i+1}" for i in range(cols)] + ["SUPPLY"]
        v_labels = [f"Warehouse {i+1}" for i in range(rows)] + ["DEMAND"]
        
        self.table.setHorizontalHeaderLabels(h_labels)
        self.table.setVerticalHeaderLabels(v_labels)
        
        # 2. Re-Connect Signals 
        try:
            self.table.horizontalHeader().sectionResized.disconnect()
            self.table.verticalHeader().sectionResized.disconnect()
        except:
            pass

        self.table.horizontalHeader().sectionResized.connect(self.update_h_headers)
        self.table.verticalHeader().sectionResized.connect(self.update_v_headers)

        # 3. Setup Cells
        for r in range(rows + 1):
            for c in range(cols + 1):
                item = QTableWidgetItem("0")
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                if r == rows and c < cols:
                    item.setBackground(QColor(255, 0, 0, 30))
                    item.setToolTip(f"Demand at Dest {c+1}")
                elif r < rows and c == cols:
                    item.setBackground(QColor(0, 255, 0, 30))
                    item.setToolTip(f"Supply at Warehouse {r+1}")
                elif r == rows and c == cols:
                    item = QTableWidgetItem("")
                    item.setFlags(Qt.ItemFlag.NoItemFlags)
                    item.setBackground(Qt.GlobalColor.lightGray)
                
                self.table.setItem(r, c, item)
        
        # 4. FORCE UPDATE: Use QTimer to wait for the layout to apply Stretch, then check text
        QTimer.singleShot(0, self.force_header_update)

    def force_header_update(self):
        """Manually runs the update logic for all headers to catch initial compressed states"""
        cols = self.table.columnCount()
        rows = self.table.rowCount()
        
        for c in range(cols):
            self.update_h_headers(c, 0, self.table.columnWidth(c))
            
        for r in range(rows):
            self.update_v_headers(r, 0, self.table.rowHeight(r))

    # --- DYNAMIC HEADER LOGIC ---
    def update_h_headers(self, logicalIndex, oldSize, newSize):
        """Switches between 'Dest X' and 'DX' based on column width"""
        is_supply = (logicalIndex == self.table.columnCount() - 1)
        
        if is_supply:
            text = "SUPPLY" if newSize > 70 else "SUP"
        else:
            if newSize < 65:
                text = f"D{logicalIndex + 1}"
            else:
                text = f"Dest {logicalIndex + 1}"

        item = self.table.horizontalHeaderItem(logicalIndex)
        if item and item.text() != text:
            item.setText(text)

    def update_v_headers(self, logicalIndex, oldSize, newSize):
        """Switches between 'Warehouse X' and 'WX' based on row height"""
        is_demand = (logicalIndex == self.table.rowCount() - 1)
        
        if is_demand:
            text = "DEMAND" if newSize > 70 else "DEM"
        else:
            if newSize < 100:
                text = f"W{logicalIndex + 1}"
            else:
                text = f"Warehouse {logicalIndex + 1}"

        item = self.table.verticalHeaderItem(logicalIndex)
        if item and item.text() != text:
            item.setText(text)

    def _set_cell(self, r, c, value):
        item = self.table.item(r, c)
        if item:
            item.setText(value)

    def run_solver(self):
        try:
            rows = self.spin_rows.value()
            cols = self.spin_cols.value()
            
            costs = []
            supply = []
            demand = []

            for r in range(rows):
                row_costs = []
                for c in range(cols):
                    text = self.table.item(r, c).text()
                    if not text.isdigit():
                        raise ValueError(f"Invalid cost at Row {r+1}, Col {c+1}")
                    row_costs.append(int(text))
                costs.append(row_costs)
                
                s_text = self.table.item(r, cols).text()
                supply.append(int(s_text) if s_text else 0)

            for c in range(cols):
                d_text = self.table.item(rows, c).text()
                demand.append(int(d_text) if d_text else 0)

            if sum(supply) != sum(demand):
                QMessageBox.warning(self, "Unbalanced Problem", 
                                    f"Total Supply ({sum(supply)}) must equal Total Demand ({sum(demand)}).")
                return

            solver = TransportationSolver(costs, supply, demand)
            allocation, min_cost, logs = solver.solve()

            html = "<h3>Optimization Process Logs:</h3>"
            for msg, style in logs:
                if style == "header": html += f"<b>{msg}</b><br>"
                elif style == "success": html += f"<span style='color:green'><b>{msg}</b></span><br>"
                elif style == "error": html += f"<span style='color:red'><b>{msg}</b></span><br>"
                elif style == "highlight": html += f"<span style='color:orange'><b>{msg}</b></span><br>"
                else: html += f"{msg}<br>"
            
            html += "<hr>"
            html += f"<h2>MINIMUM TOTAL COST: ${min_cost}</h2>"
            html += "<table border='1' cellspacing='0' cellpadding='5' width='100%'>"
            html += "<tr style='background-color:#eee'><th>From</th><th>To</th><th>Quantity</th><th>Unit Cost</th><th>Subtotal</th></tr>"
            
            for r in range(rows):
                for c in range(cols):
                    qty = allocation[r][c]
                    if qty > 0:
                        unit_c = costs[r][c]
                        sub = qty * unit_c
                        # OUTPUT TABLE: Also uses W/D format to match grid
                        html += f"<tr><td>W{r+1}</td><td>D{c+1}</td>"
                        html += f"<td><b>{int(qty)}</b></td><td>${unit_c}</td><td>${sub}</td></tr>"
            html += "</table>"

            self.txt_output.setHtml(html)

        except ValueError:
            QMessageBox.critical(self, "Input Error", "Please ensure all grid cells contain valid integers.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NativeTransportApp()
    window.show()
    sys.exit(app.exec())