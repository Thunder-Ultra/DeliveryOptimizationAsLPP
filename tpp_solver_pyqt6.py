import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QTableWidget, 
                             QTableWidgetItem, QTextEdit, QHeaderView, QMessageBox, 
                             QGroupBox, QSpinBox)
from PyQt6.QtCore import Qt
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

        return self.allocation, self.calculate_total_cost(), self.logs

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
#  NATIVE SYSTEM GUI
# ==========================================

class NativeTransportApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Optimal Delivery Allocation System")
        self.resize(1000, 800)
        self.setup_ui()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # 1. Header
        title = QLabel("Optimal Delivery Allocation System")
        font = title.font()
        font.setPointSize(16)
        font.setBold(True)
        title.setFont(font)
        
        subtitle = QLabel("Algorithm: North West Corner Method + MODI Optimization")
        subtitle.setStyleSheet("color: gray;")
        
        main_layout.addWidget(title)
        main_layout.addWidget(subtitle)

        # 2. Controls Area (Using QGroupBox for native grouping)
        config_group = QGroupBox("Configuration")
        config_layout = QHBoxLayout(config_group)
        
        # Warehouse Input (Standard QSpinBox)
        config_layout.addWidget(QLabel("Number of Warehouses:"))
        self.spin_rows = QSpinBox()
        self.spin_rows.setRange(2, 50)
        self.spin_rows.setValue(3)
        self.spin_rows.setFixedWidth(60)
        config_layout.addWidget(self.spin_rows)

        config_layout.addSpacing(20)

        # Destination Input (Standard QSpinBox)
        config_layout.addWidget(QLabel("Number of Destinations:"))
        self.spin_cols = QSpinBox()
        self.spin_cols.setRange(2, 50)
        self.spin_cols.setValue(3)
        self.spin_cols.setFixedWidth(60)
        config_layout.addWidget(self.spin_cols)

        config_layout.addStretch()

        # Generate Button
        self.btn_gen = QPushButton("Generate Matrix")
        self.btn_gen.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_gen.clicked.connect(self.generate_grid)
        config_layout.addWidget(self.btn_gen)
        
        main_layout.addWidget(config_group)

        # 3. Data Grid
        self.table = QTableWidget()
        self.table.setAlternatingRowColors(True) # Use system alternating colors
        self.table.verticalHeader().setVisible(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        main_layout.addWidget(self.table)

        # 4. Action Button
        self.btn_solve = QPushButton("Calculate Optimal Allocation")
        self.btn_solve.setCursor(Qt.CursorShape.PointingHandCursor)
        # Increase font size slightly for emphasis, but keep native style
        btn_font = self.btn_solve.font()
        btn_font.setPointSize(11)
        btn_font.setBold(True)
        self.btn_solve.setFont(btn_font)
        self.btn_solve.setFixedHeight(40)
        self.btn_solve.clicked.connect(self.run_solver)
        main_layout.addWidget(self.btn_solve)

        # 5. Output Console
        self.txt_output = QTextEdit()
        self.txt_output.setReadOnly(True)
        self.txt_output.setPlaceholderText("Results will appear here...")
        main_layout.addWidget(self.txt_output)
        
        # Initialize
        self.generate_grid()

    def generate_grid(self):
        rows = self.spin_rows.value()
        cols = self.spin_cols.value()

        self.table.setRowCount(rows + 1)
        self.table.setColumnCount(cols + 1)

        h_labels = [f"Dest {i+1}" for i in range(cols)] + ["SUPPLY"]
        v_labels = [f"Warehouse {i+1}" for i in range(rows)] + ["DEMAND"]
        self.table.setHorizontalHeaderLabels(h_labels)
        self.table.setVerticalHeaderLabels(v_labels)

        for r in range(rows + 1):
            for c in range(cols + 1):
                item = QTableWidgetItem("0")
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                
                # Logic for semantic hints using Standard Colors
                if r == rows and c < cols:
                    # Demand Row - Mild Red background hint
                    # We use standard brushes to avoid dark mode clashes
                    item.setBackground(QColor(255, 0, 0, 30)) # Very transparent red
                    item.setToolTip("Enter Demand Here")
                elif r < rows and c == cols:
                    # Supply Column - Mild Green background hint
                    item.setBackground(QColor(0, 255, 0, 30)) # Very transparent green
                    item.setToolTip("Enter Supply Here")
                elif r == rows and c == cols:
                    # Corner - Disabled
                    item = QTableWidgetItem("")
                    item.setFlags(Qt.ItemFlag.NoItemFlags)
                    item.setBackground(Qt.GlobalColor.lightGray)
                
                self.table.setItem(r, c, item)

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

            # HTML Output using standard colors
            html = "<h3>Optimization Process Logs:</h3>"
            for msg, style in logs:
                if style == "header": 
                    html += f"<b>{msg}</b><br>"
                elif style == "success": 
                    html += f"<span style='color:green'><b>{msg}</b></span><br>"
                elif style == "error": 
                    html += f"<span style='color:red'><b>{msg}</b></span><br>"
                elif style == "highlight": 
                    html += f"<span style='color:orange'><b>{msg}</b></span><br>"
                else:
                    html += f"{msg}<br>"
            
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
                        html += f"<tr><td>Warehouse {r+1}</td><td>Dest {c+1}</td>"
                        html += f"<td><b>{int(qty)}</b></td><td>${unit_c}</td><td>${sub}</td></tr>"
            html += "</table>"

            self.txt_output.setHtml(html)

        except ValueError:
            QMessageBox.critical(self, "Input Error", "Please ensure all grid cells contain valid integers.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # The default style depends on the OS (Fusion is a good neutral fallback if needed)
    # app.setStyle("Fusion") 
    window = NativeTransportApp()
    window.show()
    sys.exit(app.exec())