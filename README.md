# Optimal Delivery Allocation System 🚚

**An AI-based Logistics Optimization Tool using Linear Programming.**

This desktop application minimizes transportation costs by optimally allocating goods from multiple warehouses to multiple delivery destinations. It utilizes the **North West Corner Method (NWCM)** for the initial basic feasible solution and the **MODI (Modified Distribution) Method** for finding the optimal solution.

---

## 📋 Table of Contents

- [Features](#-features)
- [Prerequisites](#-prerequisites)
- [Installation & Setup](#-installation--setup)
- [How to Run](#-how-to-run)
- [Algorithms Used](#-algorithms-used)
- [Project Team](#-project-team)

---

## 🌟 Features

- **Dynamic Grid System:** Automatically adapts headers (`W1`, `D1` vs `Warehouse 1`, `Dest 1`) based on window size.
- **Random Data Generator:** Instantly generates balanced Cost, Supply, and Demand matrices for testing.
- **Validation:** Automatically checks if Supply equals Demand before solving.
- **Step-by-Step Logging:** Displays the optimization process (Initial Cost -> Optimization Loops -> Final Cost) in an HTML-formatted log.
- **Responsive UI:** Resizable split-view between the Data Grid and Results.
- **Native Look & Feel:** Adapts to the user's OS theme (Light/Dark mode).

---

## 🛠 Prerequisites

Before running the application, ensure you have the following installed:

1.  **Python 3.x**: [Download Python](https://www.python.org/downloads/)
2.  **pip** (Python package installer)

---

## 📥 Installation & Setup

1.  **Clone the Repository**

    ```bash
    git clone https://github.com/your-username/optimal-delivery-system.git
    cd optimal-delivery-system
    ```

2.  **Create a Virtual Environment (Optional but Recommended)**

    ```bash
    # Windows
    python -m venv venv
    venv\Scripts\activate

    # Mac/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install Dependencies**
    The only external requirement is **PyQt6**.
    ```bash
    pip install PyQt6
    ```

---

## ▶️ How to Run

Once dependencies are installed, you can run the application directly:

```bash
python tpp_solver_pyqt6.py
```

---

## 🧠 Algorithms Used

### 1. North West Corner Method (NWCM)

Used to find the **Initial Basic Feasible Solution (IBFS)**.

- Starts at the top-left cell (0,0).
- Allocates the maximum possible quantity based on supply and demand.
- Moves right if demand is not met, or down if supply is exhausted.

### 2. MODI (Modified Distribution) Method

Used for **Optimization**.

- Calculates Row ($u_i$) and Column ($v_j$) potentials.
- Determines **Opportunity Costs** for empty cells using $d_{ij} = C_{ij} - (u_i + v_j)$.
- If a negative opportunity cost is found, a **Closed Loop** (Stepping Stone path) is identified to shift goods and reduce total cost.
- Iterates until no negative opportunity costs remain.

---

## 👥 Project Team

**Project Title:** Optimal Delivery Allocation System using Linear Programming

- **Dimpal Gogoi** (CSB22015)
- **Nabajit Paul** (CSB22034)
- **Anirban Saha** (CSB22035)
- **Tuchar Chandra Das** (CSB22041)
- **Dhitiman Gogoi** (CSB22046)

---

## 📄 License

This project is open-source and available for educational purposes.
