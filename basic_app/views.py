from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from json import dumps, loads

from .models import Portfolio, Client, Stock
from .forms import CreateUserForm
from .sectorPerformance import sectorPerformance
from .decorators import unauthenticated_user, allowed_users
from basic_app.stock_data import candlestick_data, get_data, get_name, get_price
from basic_app.FA import piotroski
from basic_app.get_news import getNews, getNewsWithSentiment
from basic_app.get_stock_info import getStockInfo
from basic_app.ProphetTrend import forecast
from decimal import Decimal
from django.shortcuts import redirect
from basic_app.stock_data import get_price


def dashboard(request):
    return render(request,"basic_app/dashboard.html")

@csrf_exempt
@require_http_methods(["POST", "OPTIONS"])
def emotion_view(request):
    if request.method == "OPTIONS":
        # Respond to preflight request
        response = JsonResponse({})
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type"
        return response

    if request.method == "POST":
        # Handle your POST logic here
        return JsonResponse({"message": "Emotion endpoint works!"})

@login_required(login_url='basic_app:login')
@allowed_users(allowed_roles=['Client'])
def index(request):
    if request.method == "POST":
        data = request.POST.get('searchData')
        if data:
            stock_data = getStockInfo(data)
            if stock_data:
                return JsonResponse({'data': [stock_data]})
            else:
                return JsonResponse({'data': "No stocks found.."})

    # Fetch trending news
    news = getNews('market')

    # Fetch user's latest 3 stocks in portfolio
    user = request.user
    client = Client.objects.get(user=user)
    portfolio = Portfolio.objects.get(client=client)
    portfolio_stocks = portfolio.stocks.all().order_by('-date_added')[:3]

    context = {
        'news': news,
        'portfolio_stocks': portfolio_stocks,   # <--- clear name
        'page_title': "Home"
    }
    return render(request, 'basic_app/index.html', context)


@login_required(login_url='basic_app:login')
@allowed_users(allowed_roles=['Client'])
def profile(request):
    client = request.user
    return render(request,"basic_app/profile.html",{'client':client,'page_title':"User Profile"})

@login_required(login_url='basic_app:login')
@allowed_users(allowed_roles=['Client'])
def portfolio(request):
    user = request.user
    client = Client.objects.get(user=user)
    portfolio = Portfolio.objects.get(client=client)
    stocks = portfolio.stocks.all()

    invested_value = 0
    chart_labels = []
    chart_data = []

    for s in stocks:
        if not s.stock_sector_performance:
            s.stock_sector_performance = sectorPerformance(s.stock_symbol)
        if not s.stock_price:
            price = get_price(s.stock_symbol)
            s.stock_price = str(round(price[0],2)) + " " + price[1]
        try:
            price_float = float(s.stock_price.split()[0])
            value = price_float * s.quantity
            invested_value += value

            # Add to chart
            chart_labels.append(s.stock_symbol)
            chart_data.append(round(value, 2))
        except:
            pass
        s.save()

    cash_balance = portfolio.cash_balance
    total_net_worth = invested_value + cash_balance

    # Add cash as a slice
    chart_labels.append('Cash')
    chart_data.append(round(cash_balance, 2))

    # --- RECOMMENDATION LOGIC ---
    recommendation = None
    if cash_balance > 0.3 * total_net_worth:
        recommendation = "⚠️ You are holding a high cash balance! Consider investing."
    elif invested_value == 0 and cash_balance > 0:
        recommendation = "💡 You have cash available. Consider investing in stocks."
    elif cash_balance < 50:
        recommendation = "⚠️ Your cash is running low."

    context = {
        'stocks': stocks,
        'cash_balance': cash_balance,
        'invested_value': invested_value,
        'total_net_worth': total_net_worth,
        'recommendation': recommendation,
        'chart_labels': chart_labels,   # NEW
        'chart_data': chart_data,        # NEW
        'page_title': "Your Portfolio",
    }

    return render(request, "basic_app/portfolio.html", context)



from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import JsonResponse
from json import dumps

@login_required(login_url='basic_app:login')
def stock(request, symbol):
    data = candlestick_data(symbol)
    print("[DEBUG CANDLESTICK DATA]", data)  

    item = getStockInfo(symbol)
    info = get_data(symbol)
    piotroski_score = piotroski(symbol)

    # Get news with sentiment
    news = getNewsWithSentiment(info['shortName'])
    print("[News Fetched]", news)

    # Sentiment analysis
    sentiment_news_chart = {'positive': 0, 'negative': 0, 'neutral': 0}
    for i in range(len(news)):
        try:
            sentiment = news[i].get('sentiment', 'neutral')
            if sentiment in sentiment_news_chart:
                sentiment_news_chart[sentiment] += 1
        except Exception as e:
            print(f"[Warning] Failed to process sentiment for news[{i}]: {e}")

    print("[Sentiment Count]", sentiment_news_chart)

    # Recommendation logic
    recommendation = False
    overall_sentiment = sentiment_news_chart['positive'] - sentiment_news_chart['negative']
    if piotroski_score > 5 and overall_sentiment > 0:
        recommendation = True

    print("[Recommendation]", recommendation)

    # Pass everything to frontend
    context = {
        'data': data,                    
        'item': item,                    
        'info': info,                           
        'piotroski_score': piotroski_score,
        'sentiment_data': sentiment_news_chart,   
        'page_title': symbol + " Info",
        'recommendation': recommendation
    }

    return render(request, "basic_app/stock.html", context)


@unauthenticated_user
def loginPage(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request,username =username, password=password)

        if user is not None:
            login(request,user)
            if user.groups.filter(name='Admin').exists():
                return redirect("basic_app:stats")
            else:
                return redirect("basic_app:index")
        else:
            messages.info(request,"Incorrect username or password")
            return redirect("basic_app:login")


    return render(request,"basic_app/login.html",{'page_title':"Login"})

@login_required(login_url='basic_app:login')
def logoutUser(request):
    logout(request)
    return redirect("basic_app:login")

@unauthenticated_user
def registerPage(request):
    form = CreateUserForm()
    if request.method == "POST":
        form = CreateUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            group = Group.objects.get(name='Client')
            user.groups.add(group)
            client = Client.objects.create(user=user)
            portfolio = Portfolio.objects.create(client=client)
            return redirect('basic_app:login')

    context = {'form':form,'page_title':"Register"}
    return render(request,"basic_app/register.html",context)

@login_required(login_url='basic_app:login')
@allowed_users(allowed_roles=['Admin'])
def statisticsAdmin(request):
    return render(request,"basic_app/statisticsAdmin.html")

def price_prediction(request, symbol):
    image_base64 = forecast(symbol)
    return render(request, "basic_app/price_prediction.html", {
        'price_prediction': image_base64,
        'page_title': "Price Prediction"
    })

def addToPortfolio(request,symbol):
    user = request.user
    run =False
    print(user)
    client = Client.objects.get(user=user)
    portfolio = Portfolio.objects.get(client=client)
    stocks = portfolio.stocks.all()
    for stock in stocks:
        if symbol == stock.stock_symbol:
            stock.quantity+=1
            stock.save()
            run = True

    name = get_name(symbol)
    if run != True:
        new_stock = Stock.objects.create(parent_portfolio = portfolio,stock_symbol=symbol,stock_name=name)
        new_stock.quantity = 1;
        new_stock.save()
    #print(stock)
    return redirect('basic_app:portfolio')


def removeFromPortfolio(request,symbol):
    user = request.user
    print(user)
    client = Client.objects.get(user=user)
    portfolio = Portfolio.objects.get(client=client)
    stocks = portfolio.stocks.all()
    for stock in stocks:
        if symbol == stock.stock_symbol:
            stock.delete()

    return redirect("basic_app:portfolio")


@login_required(login_url='basic_app:login')
@allowed_users(allowed_roles=['Client'])
def quantityAdd(request, symbol):
    user = request.user
    client = Client.objects.get(user=user)
    portfolio = Portfolio.objects.get(client=client)
    stocks = portfolio.stocks.all()

    for stock in stocks:
        if stock.stock_symbol == symbol:
            # Parse stock price (it’s stored like "209.23 USD", split it)
            try:
                price_str = stock.stock_price.split()[0]
                price = float(price_str)
            except Exception as e:
                print("[Error parsing stock price]", e)
                price = 0

            if portfolio.cash_balance >= price:
                stock.quantity += 1
                portfolio.cash_balance -= price
                stock.save()
                portfolio.save()
            else:
                print("[NOT ENOUGH CASH]")
                # You could flash a Django message to the user here later if you want

    return redirect('basic_app:portfolio')

@login_required(login_url='basic_app:login')
@allowed_users(allowed_roles=['Client'])
def quantitySub(request, symbol):
    user = request.user
    client = Client.objects.get(user=user)
    portfolio = Portfolio.objects.get(client=client)
    stocks = portfolio.stocks.all()

    for stock in stocks:
        if stock.stock_symbol == symbol:
            try:
                price_str = stock.stock_price.split()[0]
                price = float(price_str)
            except Exception as e:
                print("[Error parsing stock price]", e)
                price = 0

            stock.quantity -= 1

            # Add back the cash
            portfolio.cash_balance += price

            if stock.quantity <= 0:
                stock.delete()
            else:
                stock.save()

            portfolio.save()

    return redirect('basic_app:portfolio')


    return redirect("basic_app:portfolio")
@csrf_exempt
@login_required(login_url='basic_app:login')
@allowed_users(allowed_roles=['Client'])
def searchStock(request):
    if request.method == "POST":
        data = request.POST.get('searchData')
        if data:
            stock_data = getStockInfo(data)
            print("[DEBUG SEARCH DATA]", stock_data)
            if stock_data:
                return JsonResponse({'data': [stock_data]})
            else:
                return JsonResponse({'data': "No stocks found.."})
        else:
            return JsonResponse({'data': "Invalid request."})

    return JsonResponse({'data': "Only POST requests allowed."})
@login_required(login_url='basic_app:login')
@allowed_users(allowed_roles=['Client'])
def add_cash(request):
    if request.method == "POST":
        amount = float(request.POST.get('amount', 0))
        user = request.user
        client = Client.objects.get(user=user)
        portfolio = Portfolio.objects.get(client=client)
        portfolio.cash_balance += amount
        portfolio.save()
        return redirect('basic_app:portfolio')
    return render(request, 'basic_app/add_cash.html')


@login_required(login_url='basic_app:login')
@allowed_users(allowed_roles=['Client'])
def withdraw_cash(request):
    if request.method == "POST":
        amount = float(request.POST.get('amount', 0))
        user = request.user
        client = Client.objects.get(user=user)
        portfolio = Portfolio.objects.get(client=client)
        if portfolio.cash_balance >= amount:
            portfolio.cash_balance -= amount
            portfolio.save()
        return redirect('basic_app:portfolio')
    return render(request, 'basic_app/withdraw_cash.html')

@login_required(login_url='basic_app:login')
@allowed_users(allowed_roles=['Client'])
def explore_stocks(request):
    return render(request, 'basic_app/search_stock.html', {
        'page_title': "Explore Stocks"
    })





# def search_results(request):
#     if request.headers.get('x-requested-with') == 'XMLHttpRequest':
#         data = request.POST.get('searchData')
#         return JsonResponse({'data':data})
#     return JsonResponse({})



# Underdog Stocks(already listed)
# Indian Stocks (you cant go wrong)(fundamentally strong indian companies)
# Upcoming IPOs
# Price Prediction
# Patience
# Company risk
# Most Popular (Stocks,Brokers)
# Information Section(keep learning)