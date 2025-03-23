from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import Expense
import urllib
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.db import models
from .forms import *
from .utils import *
from .models import *
from django.contrib import messages
from django.db.models import Sum
from datetime import datetime
from django.utils import timezone
from django.core.files.storage import default_storage, FileSystemStorage
from django.conf import settings
import cv2
import csv
import re
import time
import pytesseract
from PIL import Image
import os
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import base64
import io
import requests
from datetime import date
def login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        pwd = request.POST['password']
        remember_me = request.POST.get('remember_me', False)
        user = authenticate(request, username=username, password=pwd)
        print(user, username, pwd)
        if user is not None:
            login(request, user)
            if not remember_me:
                request.session.set_expiry(0)
            else:
                request.session.set_expiry(1209600)
            return redirect('home/')
        else:
            context={
                'error': '**Invalid username or password',
            }
            return render(request, 'login.html', context)

    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('/')

def signup_view(request):
    if request.method == "POST":
            username = request.POST['username']
            email = request.POST['email']
            password = request.POST['password']
            cpassword = request.POST['cpassword']
            if User.objects.filter(username=username).exists():
                context={
                    'user_error': '**Username already exists'
                }
                return render(request, 'register.html', context)
            if password != cpassword:
                context={
                    'pass_error': '**Passwords do not match'
                }
                return render(request, 'register.html', context)
            
            User.objects.create_user(username = username, email = email, password = cpassword)
            return redirect('/')

    return render(request, 'register.html')

@login_required
def home(request):
    expenses =Expense.objects.filter(user=request.user)
    total_transactions=expenses.count()
    total_expense = expenses.aggregate(total=models.Sum('amount'))['total'] or 0
    Budget = MonthlyBudget.objects.filter(user=request.user).order_by('-year','-month').first()
    s_budget = Budget.amount if Budget else 0
    sum_budget = MonthlyBudget.objects.filter(user=request.user).order_by('-year','-month')
    budgets = sum_budget.aggregate(budgets=Sum('amount'))['budgets'] or 0
    balance = budgets-total_expense
    user_pref, _ = UserPreferences.objects.get_or_create(user=request.user)
    selected_currency = user_pref.currency
    if balance==0:
        score=0
    else:
        score = balance/s_budget*100
    score = max(0, min(100, score))  # Ensure score stays within 0-100
    financial_profile, created = FinancialProfile.objects.get_or_create(user=request.user)
    financial_profile.health_score = int(score)
    financial_profile.save()
    if score >= 80:
        badge = "Financial Master"
    elif score >= 60:
        badge = "Balanced saver"
    elif score >= 40:
        badge = "Spending Enthusiast"
    elif score >=20:
        badge = "Broke Legend"
    else:
        badge = "Money Loser( Try to save money )"
    username = request.user.username
    return render(request, 'dashboard.html', {'username': username, 'expenses': expenses, 'total_transactions': total_transactions, 'total_expense': total_expense, 'total_budget': s_budget , 'balance': balance, 'selected_currency':selected_currency, "badge": badge, "score": score})

def forget_view(request):
    if request.method=='POST':
        email = request.POST['email']
        password = request.POST['npassword']
        user = User.objects.get(email=email)
        user.set_password(password)
        user.save()
        return redirect('/')
    return render(request, 'forget.html')

@login_required
def transaction(request):
    if request.method == 'POST':
        form = Expenseform(request.POST, request.FILES)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()
            messages.success(request, 'Expense added successfully')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
            
    else:
        form = Expenseform()
        return render(request, 'transaction.html', {'form': form})

@login_required
def delete_expense(request, expense_id):
    expense = get_object_or_404(Expense, id=expense_id, user=request.user)
    expense.delete()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@login_required
def sip_calc(request):
    return render(request, 'SIP_calc.html')

@login_required
def loan_calc(request):
    return render(request, 'loan.html')

@login_required
def budget_management(request):
    # Get all budgets for the current user
    budgets = MonthlyBudget.objects.filter(user=request.user)
    
    if request.method == 'POST':
        form = MonthlyBudgetForm(request.POST)
        if form.is_valid():
            budget = form.save(commit=False)
            budget.user = request.user  # Assign the logged-in user
            budget.save()
            messages.success(request, 'Budget added successfully!')
            return redirect('budget_management')
    else:
        form = MonthlyBudgetForm()

    return render(request, 'budget.html', {'form': form, 'budgets': budgets})

@login_required
def delete_budget(request, budget_id):
    # Get the budget to delete
    budget = get_object_or_404(MonthlyBudget, id=budget_id, user=request.user)
    budget.delete()
    messages.success(request, 'Budget deleted successfully!')
    return redirect('budget_management')

@login_required
def savings_goals_view(request):
    goals = SavingsGoal.objects.filter(user=request.user)
    
    if request.method == 'POST':
        # Adding new goal
        if 'add_goal' in request.POST:
            form = SavingsGoalForm(request.POST)
            if form.is_valid():
                goal_user = form.save(commit=False)
                goal_user.user=request.user
                goal_user.save()
                messages.success(request, "New savings goal added!")
                return redirect('savings_goals')
        # Updating saved amount
        elif 'update_saved_amount' in request.POST:
            goal_id = request.POST.get('goal_id')
            saved_amount = float(request.POST['saved_amount'])
            goal = SavingsGoal.objects.get(id=goal_id, user=request.user)
            
            if saved_amount > goal.remaining_amount:
                messages.error(request, "Saved amount cannot exceed remaining amount.")
            else:
                goal.saved_amount += saved_amount
                goal.remaining_amount -= saved_amount
                goal.save()
                
                # Create an expense record
                Expense.objects.create(
                    user=request.user,
                    title=f"Savings for {goal.title}",
                    amount=saved_amount,
                    date=timezone.now()
                )
                messages.success(request, "Saved amount added to goal and expense!")

            return redirect('savings_goals')
        # Deleting a goal
        elif 'delete_goal' in request.POST:
            goal_id = request.POST.get('goal_id')
            goal = SavingsGoal.objects.get(id=goal_id)
            goal.delete()
            messages.success(request, "Savings goal deleted!")
            return redirect('savings_goals')

    form = SavingsGoalForm()
    return render(request, 'savings.html', {'goals': goals, 'form': form})

def extract_text(image_path):
    """Extract text from an image using OCR"""
    if not os.path.exists(image_path):
        raise ValueError(f"File does not exist: {image_path}")
    
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"Image not loaded properly. File: {image_path}")
    
    # Image Preprocessing to improve OCR accuracy (Thresholding)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  # Convert to grayscale
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)  # Apply binary thresholding to enhance contrast
    
    # Use pytesseract to extract text from preprocessed image
    text = pytesseract.image_to_string(thresh)
    
    # Print the extracted text for debugging
    print("Extracted Text: ", text)
    
    return text

# Extract total amount from OCR text
def extract_amount(text):
    """Extract total amount from OCR text"""
    # Updated regex pattern to capture amounts with commas and decimals (e.g., 3,950, 3950.00)
    amount_pattern = r'(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)'
    
    # Find all amounts that match the pattern
    amounts = re.findall(amount_pattern, text)
    
    # Print the amounts to see what we're extracting
    print("Extracted Amounts:", amounts)
    
    if amounts:
        # Remove commas to fix cases like 3,950 -> 3950
        cleaned_amount = amounts[-1].replace(',', '')  # Remove commas
        cleaned_amount = cleaned_amount.split('.')[0]  # Remove any decimal part
        
        # Print the cleaned amount for debugging
        print("Cleaned Amount:", cleaned_amount)
        
        return cleaned_amount
    
    return None  # If no amount is found

# Extract date from OCR text
def extract_date(text):
    """Extract date from OCR text"""
    date_pattern = r'(\d{2}/\d{2}/\d{4})'  # Match dates like 12/02/2024
    dates = re.findall(date_pattern, text)
    return dates[0] if dates else None  # Take first date

# Check if the file is a valid image
def check_valid_image(image_path):
    try:
        with Image.open(image_path) as img:
            img.verify()  # Check if the file is a valid image
        return True
    except (IOError, SyntaxError):
        return False

def upload_bill(request):
    if request.method == "POST" and request.FILES.get("bill_image"):
        uploaded_file = request.FILES["bill_image"]
        
        # Check file extension (ensure it's a valid image)
        allowed_extensions = ['jpg', 'jpeg', 'png', 'bmp']
        file_extension = uploaded_file.name.split('.')[-1].lower()  # Convert to lowercase

        if file_extension not in allowed_extensions:
            return HttpResponse("Invalid file format. Only JPG, JPEG, PNG, and BMP are allowed.", status=400)

        # Save the file to a temporary location
        file_path = default_storage.save(f"bills/{uploaded_file.name}", uploaded_file)
        
        # Get absolute path of the uploaded file
        absolute_path = default_storage.path(file_path)
        print(f"File saved at: {absolute_path}")
        
        # Validate image before processing
        if not check_valid_image(absolute_path):
            return HttpResponse("Uploaded file is not a valid image.", status=400)

        try:
            # Run OCR on the saved file
            extracted_text = extract_text(absolute_path)
            date = extract_date(extracted_text)
            amount = extract_amount(extracted_text)

            # If no date found, use today's date
            if not date:
                date = datetime.today().strftime('%Y-%m-%d')

            # Save extracted data to Expense model
            if amount:
                Expense.objects.create(
                    user=request.user,  # Assuming user authentication is used
                    title="Bill Expense",
                    amount=float(amount),
                    date=date,
                    uploaded_bill=uploaded_file
                )
            else:
                return HttpResponse("No amount found in the bill.", status=400)

        except Exception as e:
            return HttpResponse(f"Error processing the image: {str(e)}", status=500)

        return redirect("home")  # Redirect to expense list page
    
    return render(request, "bill.html")

def generate_expense_distribution(user):
    expenses = Expense.objects.filter(user=user)
    title_expenses = {expense.title: sum(exp.amount for exp in expenses if exp.title == expense.title) for expense in expenses}

    plt.figure(figsize=(8, 8))
    wedges, _, _ = plt.pie(title_expenses.values(), autopct='%1.1f%%', startangle=90)

    # Add legend instead of direct labels
    plt.legend(wedges, title_expenses.keys(), loc="best", fontsize=10)
    plt.title("Expense Distribution by Title")

    media_path = os.path.join(settings.MEDIA_ROOT, 'expense_distribution_by_title.png')
    plt.tight_layout()
    plt.savefig(media_path)
    plt.close()

    return media_path

def generate_expense_summary(user):
    expenses = Expense.objects.filter(user=user)
    total_expenses = sum([expense.amount for expense in expenses])
    title_expenses = {title: sum([expense.amount for expense in expenses if expense.title == title]) for title in set([expense.title for expense in expenses])}
    return {'total_expenses': total_expenses, 'title_expenses': title_expenses}

def export_expenses_to_csv(user):
    expenses = Expense.objects.filter(user=user)
    expenses_data = [{'Title': expense.title, 'Amount': expense.amount, 'Date': expense.date} for expense in expenses]
    df = pd.DataFrame(expenses_data)
    file_path = 'expenses_by_title.csv'
    df.to_csv(file_path, index=False)
    return file_path

def export_expenses_to_excel(user):
    expenses = Expense.objects.filter(user=user)
    expenses_data = [{'Title': expense.title, 'Amount': expense.amount, 'Date': expense.date} for expense in expenses]
    df = pd.DataFrame(expenses_data)
    file_path = 'expenses_by_title.xlsx'
    df.to_excel(file_path, index=False)
    return file_path

def export_expenses_to_pdf(user):
    expenses = Expense.objects.filter(user=user)
    file_path = 'expenses_report.pdf'
    c = canvas.Canvas(file_path, pagesize=letter)
    c.drawString(100, 750, "Expense Report")
    y_position = 730
    for expense in expenses:
        c.drawString(100, y_position, f"{expense.title}: {expense.amount}")
        y_position -= 20
    c.save()
    return file_path

@login_required
def dashboard(request):
    user = request.user
    chart_path = generate_expense_distribution(user)
    summary = generate_expense_summary(user)
    return render(request, 'report.html', {'chart_path': chart_path, 'summary': summary, 'MEDIA_URL': settings.MEDIA_URL})

def export(request, format_type):
    user = request.user
    if format_type == 'csv':
        file_path = export_expenses_to_csv(user)
        response = HttpResponse(open(file_path, 'rb').read(), content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=expenses.csv'
        return response
    elif format_type == 'excel':
        file_path = export_expenses_to_excel(user)
        response = HttpResponse(open(file_path, 'rb').read(), content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename=expenses.xlsx'
        return response
    elif format_type == 'pdf':
        file_path = export_expenses_to_pdf(user)
        response = HttpResponse(open(file_path, 'rb').read(), content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename=expenses_report.pdf'
        return response

def get_monthly_expenses(user):
    from django.db.models.functions import ExtractYear, ExtractMonth

    expenses = Expense.objects.filter(user=user) \
        .annotate(Year=ExtractYear('date'), Month=ExtractMonth('date')) \
        .values('Year', 'Month') \
        .annotate(Total_Expense=Sum('amount')) \
        .order_by('Year', 'Month')

    df = pd.DataFrame(expenses)
    
    if df.empty:
        return df  
    
    return df

def predict_next_month_expense(user):
    df = get_monthly_expenses(user)

    if len(df) < 3: 
        return "Not enough data"

    df['Date_Index'] = df['Year'] * 12 + df['Month']

    X = df[['Date_Index']]
    y = df['Total_Expense']

    model = LinearRegression()
    model.fit(X, y)

    next_month_index = (df['Year'].max() * 12) + df['Month'].max() + 1
    predicted_expense = model.predict([[next_month_index]])[0]

    return round(predicted_expense, 2) 

@login_required
def prediction(request):
    user = request.user
    predicted_expense = predict_next_month_expense(user)
    
    context = {
        'predicted_expense': predicted_expense,
    }
    return render(request, 'prediction.html', context)

API_KEY = "CBJDZKLW9MNVED5J"
        
@login_required
def settings_view(request):
    user_pref, _ = UserPreferences.objects.get_or_create(user=request.user)
    user_form = UserUpdateForm(instance=request.user)
    password_form = PasswordChangeForm(request.user)
    upload_form = UploadExpenseFileForm()

    if request.method == "POST":
        # Update Currency
        if "currency" in request.POST:
            currency = request.POST.get("currency")
            if currency:
                user_pref.currency = currency
                user_pref.save()
                messages.success(request, "Currency updated successfully.")

        # Update User Info
        elif "update_user" in request.POST:
            user_form = UserUpdateForm(request.POST, instance=request.user)
            if user_form.is_valid():
                user_form.save()
                messages.success(request, "Profile updated successfully.")
        
        elif "change_password" in request.POST:
            password_form = PasswordChangeForm(request.user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)  # Keeps the user logged in after password change
                messages.success(request, "Password changed successfully.")
                return redirect("settings")  # Reload settings page to avoid form resubmission
            else:
                messages.error(request, "Error changing password. Please check the fields.")


        # Reset Data (Delete all transactions)
        elif "reset_data" in request.POST:
            Expense.objects.filter(user=request.user).delete()
            SavingsGoal.objects.filter(user=request.user).delete()
            MonthlyBudget.objects.filter(user=request.user).delete()
            SIPInvestment.objects.filter(user=request.user).delete()
            messages.success(request, "All your transactions have been reset.")

        # Import Expenses from Excel
        elif "import_data" in request.POST:
            upload_form = UploadExpenseFileForm(request.POST, request.FILES)
            if upload_form.is_valid():
                file = request.FILES["file"]
                df = pd.read_excel(file)

                # Expecting columns: Title, Amount, Date
                for _, row in df.iterrows():
                    Expense.objects.create(
                        user=request.user,
                        title=row["Title"],
                        amount=row["Amount"],
                        date=row["Date"]
                    )
                messages.success(request, "Expenses imported successfully.")

        # Delete Account
        elif "delete_account" in request.POST:
            request.user.delete()
            messages.success(request, "Your account has been deleted.")
            return redirect("/")

    return render(request, "settings.html", {
        "user_pref": user_pref,
        "user_form": user_form,
        "password_form": password_form,
        "upload_form": upload_form,
    })
BASE_URL = 'https://www.alphavantage.co/query'

TOP_10_STOCKS = [
    {"symbol": "AAPL", "name": "Apple Inc."},
    {"symbol": "MSFT", "name": "Microsoft Corp."},
    {"symbol": "GOOGL", "name": "Alphabet Inc."},
    {"symbol": "AMZN", "name": "Amazon.com Inc."},
    {"symbol": "TSLA", "name": "Tesla Inc."},
    {"symbol": "NVDA", "name": "NVIDIA Corp."},
    {"symbol": "META", "name": "Meta Platforms Inc."},
    {"symbol": "JPM", "name": "JPMorgan Chase & Co."},
    {"symbol": "XOM", "name": "Exxon Mobil Corp."},
    {"symbol": "NFLX", "name": "Netflix Inc."},
]

def get_stock_price(symbol):
    try:
        url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={API_KEY}"
        response = requests.get(url).json()

        if "Global Quote" in response and response["Global Quote"]:
            return {
                "symbol": response["Global Quote"]["01. symbol"],
                "price": response["Global Quote"]["05. price"],
                "change": response["Global Quote"]["10. change percent"],
            }
    except Exception as e:
        print(f"Error fetching stock {symbol}: {e}")
    return None  # Return None if API call fails

@login_required
def stock_list(request):
    """Fetch live stock prices & show top stocks list"""
    top_stocks = []
    
    # Fetch live stock prices with error handling
    for stock in TOP_10_STOCKS:
        stock_data = get_stock_price(stock["symbol"])
        if stock_data:  
            stock_data["name"] = stock["name"]  # Add company name
            top_stocks.append(stock_data)

    # Handle user search
    stock_data = None
    query = request.GET.get("q")
    if query:
        stock_data = get_stock_price(query)
        if stock_data:
            stock_data["name"] = query  # Display entered symbol if name is missing

    return render(request, "sip_list.html", {
        "stock_data": stock_data,
        "top_stocks": top_stocks,
        "error": "Stock not found" if query and not stock_data else None
    })

@login_required
def sip_portfolio(request):
    """Handles SIP portfolio display, investment addition, deletion, and trend chart generation."""
    
    if request.method == 'POST':
        form = SIPInvestmentForm(request.POST)
        if form.is_valid():
            sip = form.save(commit=False)
            sip.user = request.user
            update_sip_nav(sip)  # Fetch latest NAV
            sip.save()

            # Log the SIP investment as an expense
            Expense.objects.create(
                user=request.user, 
                title='Sip investment',
                amount=sip.invested_amount, 
                date=date.today()
            )

            return redirect('sip_portfolio')
    else:
        form = SIPInvestmentForm()

    sip_list = SIPInvestment.objects.filter(user=request.user)

    # Generate trend charts for each SIP
    sip_charts = {}
    for sip in sip_list:
        history = SIPNAVHistory.objects.filter(sip=sip).order_by('date')
        if history.exists():
            dates = [entry.date for entry in history]
            nav_values = [entry.nav for entry in history]

            plt.figure(figsize=(4, 2))
            plt.plot(dates, nav_values, marker='o', linestyle='-', color='b')
            plt.xlabel("Date")
            plt.ylabel("NAV")
            plt.title(f"{sip.sip_name} Trend")
            plt.xticks(rotation=45)

            buffer = io.BytesIO()
            plt.savefig(buffer, format='png')
            buffer.seek(0)
            image_png = buffer.getvalue()
            buffer.close()
            sip_charts[sip.id] = base64.b64encode(image_png).decode('utf-8')

    return render(request, 'sip_port.html', {
        'form': form, 
        'sip_list': sip_list, 
        'sip_charts': sip_charts
    })


@login_required
def delete_sip(request, sip_id):
    """Deletes a SIP investment."""
    sip = get_object_or_404(SIPInvestment, id=sip_id, user=request.user)
    sip.delete()
    return redirect('sip_portfolio')

def faq_answer(request):
    question = request.GET.get("question",'')  # Get the question from the request

    if not question:
        return JsonResponse({"error": "No question provided"}, status=400)

    try:
        faq = FAQ.objects.get(question=question)  # Fetch the answer
        return JsonResponse({"answer": faq.answer})  # Return JSON response
    except FAQ.DoesNotExist:
        return JsonResponse({"answer": "Sorry, I don't have an answer for that."})
        
def faq_page(request):
    faqs = FAQ.objects.all()  # Get all FAQs from DB
    return render(request, "chatbot.html", {"faqs": faqs})
