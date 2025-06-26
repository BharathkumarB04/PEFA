![logo](https://github.com/user-attachments/assets/e015b663-e623-4277-aa41-9d6e5fc748b8)Personal Finance Assistant (PeFA) - An comprehensive financial Web application

Overview
Personal Finance Assistant (PeFA) is a comprehensive financial management tool designed to help users track expenses, set budgets, plan savings, and analyze investments. It features data visualization, expense prediction, and seamless import/export capabilities, making financial management effortless.

Features
 1. **Dashboard**
   - Displays transaction history
   - Provides data visualization for insights
   - Shows balance and budget tracking

2. **Transactions**
   - Add, delete, and view expenses and income

3. **Tools**
   - SIP Calculator for mutual fund investments
   - Loan/EMI Calculator

4. **Savings Goal Manager**
   - Create, track, and delete savings goals
   - Visualizes progress
   - Auto-categorizes saved money

5. **Budget Planner**
   - Set and adjust budgets for effective financial control

6. **Expense Predictor**
   - Uses past transactions to predict future expenses

7. **Stock & SIP Investment Tracker**
   - Real-time stock price tracking (Alpha Vantage API)
   - SIP investment analysis and tracking

8. **Settings**
   - Currency conversion support

 9. **Import/Export Feature**
   - Upload Excel files to migrate financial data (e.g., from Andromoney)

Tech Stack
- **Frontend:** HTML, TailwindCSS
- **Backend:** Python (Django)
- **Database:** MySQL
- **Visualization:** Matplotlib
- **APIs:** Alpha Vantage (for stock/SIP tracking)
- **Machine Learning:** OCR & ML for expense prediction

Installation & Setup
1. **Clone the Repository:**
   ```bash
   git clone https://github.com/your-repo/pefa.git
   cd pefa
   ```
2. **Set up Virtual Environment (Optional but Recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate   # On Windows use `venv\Scripts\activate`
   ```
3. **Install Backend Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Set Up Database:**
   ```bash
   python manage.py migrate
   ```
5. **Run the Server:**
   ```bash
   python manage.py runserver
   ```
License : 
MIT License

Usage
- Sign up or log in to start managing your finances.
- Add expenses, set budgets, and track investments.
- Use tools like EMI calculators and SIP trackers for financial insights.
- Visualize your financial trends and predict future expenses.
- Export or import financial data with ease.

Screenshots
<img src="images/signup.jpg" alt="Signup" width=100>

