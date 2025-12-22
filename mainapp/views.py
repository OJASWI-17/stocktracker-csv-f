from django.shortcuts import render,redirect
from django.http.response import HttpResponse

from django.http import JsonResponse
import pandas as pd
from .tasks import update_stock
from asgiref.sync import sync_to_async


from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login

from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required



# Path to CSV file
CSV_FILE_PATH = "C:/projects/stocktracker/stockproject/mainapp/generated_stock_data.csv"

# Load CSV into a DataFrame
df = pd.read_csv(CSV_FILE_PATH)

# Dictionary to store current index for each stock
stock_indices = {ticker: 0 for ticker in df["ticker"].unique()}

def get_stock_updates(selected_stocks):
    """Fetch stock data from CSV and simulate real-time updates."""
    global stock_indices
    data = {}

    for ticker in selected_stocks:
        stock_data = df[df["ticker"] == ticker]
        index = stock_indices.get(ticker, 0)

        # If we reach the end of the dataset, loop back to the beginning
        if index >= len(stock_data):
            index = 0

        row = stock_data.iloc[index]

        data[ticker] = {
            "current_price": row["current_price"],
            "previous_close": row["previous_close"],
            "volume": row["volume"],
            "market_cap": row["market_cap"],
            "open_price": row["open_price"],
            "day_high": row["day_high"],
            "day_low": row["day_low"],
        }

        # Move to the next index for the next call
        stock_indices[ticker] = index + 1

    return data


@login_required(login_url="login")
def stockPicker(request):
    stock_picker = df["ticker"].unique().tolist()
    return render(request, "mainapp/stockpicker.html", {"stock_picker": stock_picker})




    
@login_required(login_url="login")
def stockTracker(request):
    selected_stocks = request.GET.getlist("stock_picker")

    if not selected_stocks:
        return JsonResponse({"error": "No stocks selected"}, status=400)

    initial_data = get_stock_updates(selected_stocks)
    update_stock.delay(selected_stocks)

    return render(
        request,
        "mainapp/stocktracker.html",
        {"room_name": "track", "data": initial_data}
    )







def register(request):
    if request.method == "POST":
        
        username = request.POST.get("username")
        password = request.POST.get("password")

        # Check if username already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect("register")

        # Create user (password will be hashed)
        user = User.objects.create_user(
            username=username,
            password=password
        )

        messages.success(request, "Account created successfully")
        return redirect("login")

    return render(request, "mainapp/register.html")




def login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is None:
            messages.error(request, "Invalid username or password")
            return redirect("login")

        auth_login(request, user)
        messages.success(request, "Logged in successfully")
        return redirect("stockpicker") 

    return render(request, "mainapp/login.html")

