from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods, require_POST
from .models import Portfolio, Client, Stock
from .forms import CreateUserForm
from .decorators import unauthenticated_user, allowed_users
from basic_app.stock_data import candlestick_data, get_data, get_name, get_price
from basic_app.FA import piotroski
from basic_app.get_news import getNews, getNewsWithSentiment
from basic_app.get_stock_info import getStockInfo
from basic_app.ProphetTrend import forecast
from decimal import Decimal
from basic_app.sectorPerformance import sectorPerformance
from django.views.decorators.cache import never_cache
import basic_app.ta as ta
import json



def dashboard(request):
    return render(request, "basic_app/dashboard.html")

@csrf_exempt
@require_http_methods(["POST", "OPTIONS"])
def emotion_view(request):
    if request.method == "OPTIONS":
        response = JsonResponse({})
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type"
        return response
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

    news = getNews('market')
    client = Client.objects.get(user=request.user)
    portfolio = Portfolio.objects.get(client=client)
    portfolio_stocks = portfolio.stocks.all().order_by('-date_added')[:3]

    context = {
        'news': news,
        'portfolio_stocks': portfolio_stocks,
        'page_title': "Home"
    }
    return render(request, 'basic_app/index.html', context)

@login_required(login_url='basic_app:login')
@allowed_users(allowed_roles=['Client'])
def profile(request):
    return render(request, "basic_app/profile.html", {'client': request.user, 'page_title': "User Profile"})

@never_cache
@login_required(login_url='basic_app:login')
@allowed_users(allowed_roles=['Client'])
def portfolio(request):
    client = Client.objects.get(user=request.user)
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
            s.stock_price = f"{round(price[0], 2)} {price[1]}"
        try:
            price_float = float(s.stock_price.split()[0])
            value = price_float * s.quantity
            invested_value += value
            chart_labels.append(s.stock_symbol)
            chart_data.append(round(value, 2))
        except:
            pass
        s.save()

    cash_balance = portfolio.cash_balance
    total_net_worth = invested_value + cash_balance

    chart_labels.append('Cash')
    chart_data.append(round(cash_balance, 2))

    recommendation = None
    if cash_balance > 0.3 * total_net_worth:
        recommendation = "⚠️ You are holding a high cash balance! Consider investing."
    elif invested_value == 0 and cash_balance > 0:
        recommendation = "💡 You have cash available. Consider investing in stocks."
    elif cash_balance < 50:
        recommendation = "⚠️ Your cash is running low."

    # --- New Rocket Science Recommendation System ---
    recommended_stocks = []

    for s in stocks:
        try:
            # Pull Piotroski score
            piotroski_score = piotroski(s.stock_symbol)

            # Pull News Sentiment
            news = getNewsWithSentiment(s.stock_name)
            sentiment_news_chart = {'positive': 0, 'negative': 0, 'neutral': 0}
            for n in news:
                if isinstance(n, dict):
                    sentiment = n.get('sentiment', 'neutral')
                    if sentiment in sentiment_news_chart:
                        sentiment_news_chart[sentiment] += 1

            # Log sentiment
            print(f"[RocketScience] {s.stock_symbol}: Piotroski {piotroski_score} | Sentiment {sentiment_news_chart}")

            # Compute recommendation
            overall_sentiment = sentiment_news_chart['positive'] - sentiment_news_chart['negative']
            is_recommended = (piotroski_score >= 5 and overall_sentiment > 0)

            if is_recommended:
                # Check affordability
                price = 0
                try:
                    price = float(s.stock_price.split()[0])
                except Exception as e:
                    print(f"[RocketScience] Failed to parse price for {s.stock_symbol}: {e}")

                if price > 0:
                    if cash_balance >= price:
                        print(f"[RocketScience] Enough cash to buy {s.stock_symbol}: ${price}")
                    else:
                        print(f"[RocketScience] NOT enough cash to buy {s.stock_symbol}: ${price}")
                else:
                    print(f"[RocketScience] No valid price found for {s.stock_symbol}.")

                # Regardless of cash, add to recommendation list
                recommended_stocks.append(s.stock_symbol)

        except Exception as e:
            print(f"[RocketScience] Failed to compute recommendation for {s.stock_symbol}: {e}")

    # Build context properly (✅ COMMA FIXED)
    context = {
        'stocks': stocks,
        'cash_balance': cash_balance,
        'invested_value': invested_value,
        'total_net_worth': total_net_worth,
        'recommendation': recommendation,
        'chart_labels': chart_labels,
        'chart_data': chart_data,
        'page_title': "Your Portfolio",
        'recommended_stocks': recommended_stocks,
    }

    return render(request, "basic_app/portfolio.html", context)


@login_required(login_url='basic_app:login')
def stock(request, symbol):
    try:
        data = candlestick_data(symbol)
        item = getStockInfo(symbol)
        info = get_data(symbol)

        if not item or item.get('price') == 'N/A':
            print(f"[STOCK] Invalid data for {symbol}, redirecting.")
            return redirect('basic_app:portfolio')

        piotroski_score = piotroski(symbol)

        news = getNewsWithSentiment(info['shortName'])
        sentiment_news_chart = {'positive': 0, 'negative': 0, 'neutral': 0}

        for n in news:
            if isinstance(n, dict):
                sentiment = n.get('sentiment', 'neutral')
                if sentiment in sentiment_news_chart:
                    sentiment_news_chart[sentiment] += 1

        print("[DEBUG] Sentiment chart:", sentiment_news_chart)

        # Recommendation logic
        recommendation = False
        overall_sentiment = sentiment_news_chart['positive'] - sentiment_news_chart['negative']
        if piotroski_score > 5 and overall_sentiment > 0:
            recommendation = True

        print("[DEBUG] Recommendation:", recommendation)

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

    except Exception as e:
        print(f"[STOCK] Exception caught for {symbol}: {e}")
        return redirect('basic_app:portfolio')




@unauthenticated_user
def loginPage(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            if user.groups.filter(name='Admin').exists():
                return redirect("basic_app:stats")
            return redirect("basic_app:index")
        else:
            messages.info(request, "Incorrect username or password")
    return render(request, "basic_app/login.html", {'page_title': "Login"})

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
            Client.objects.create(user=user)
            Portfolio.objects.create(client=user.client)
            return redirect('basic_app:login')

    return render(request, "basic_app/register.html", {'form': form, 'page_title': "Register"})

@login_required(login_url='basic_app:login')
@allowed_users(allowed_roles=['Admin'])
def statisticsAdmin(request):
    return render(request, "basic_app/statisticsAdmin.html")

def price_prediction(request, symbol):
    image_base64 = forecast(symbol)
    return render(request, "basic_app/price_prediction.html", {
        'price_prediction': image_base64,
        'page_title': "Price Prediction"
    })

def addToPortfolio(request, symbol):
    client = Client.objects.get(user=request.user)
    portfolio = Portfolio.objects.get(client=client)

    for stock in portfolio.stocks.all():
        if stock.stock_symbol == symbol:
            stock.quantity += 1
            stock.save()
            return redirect('basic_app:portfolio')

    name = get_name(symbol)
    Stock.objects.create(parent_portfolio=portfolio, stock_symbol=symbol, stock_name=name, quantity=1)
    return redirect('basic_app:portfolio')

def removeFromPortfolio(request, symbol):
    client = Client.objects.get(user=request.user)
    portfolio = Portfolio.objects.get(client=client)
    portfolio.stocks.filter(stock_symbol=symbol).delete()
    return redirect("basic_app:portfolio")

@login_required(login_url='basic_app:login')
@allowed_users(allowed_roles=['Client'])
def quantityAdd(request, symbol):
    client = Client.objects.get(user=request.user)
    portfolio = Portfolio.objects.get(client=client)
    stock = portfolio.stocks.filter(stock_symbol=symbol).first()
    if stock:
        try:
            price = float(stock.stock_price.split()[0])
        except Exception as e:
            price = 0
        if portfolio.cash_balance >= price:
            stock.quantity += 1
            portfolio.cash_balance -= price
            stock.save()
            portfolio.save()
    return redirect('basic_app:portfolio')

@login_required(login_url='basic_app:login')
@allowed_users(allowed_roles=['Client'])
def quantitySub(request, symbol):
    client = Client.objects.get(user=request.user)
    portfolio = Portfolio.objects.get(client=client)
    stock = portfolio.stocks.filter(stock_symbol=symbol).first()
    if stock:
        try:
            price = float(stock.stock_price.split()[0])
        except Exception as e:
            price = 0
        stock.quantity -= 1
        portfolio.cash_balance += price
        if stock.quantity <= 0:
            stock.delete()
        else:
            stock.save()
        portfolio.save()
    return redirect('basic_app:portfolio')

@login_required(login_url='basic_app:login')
@allowed_users(allowed_roles=['Client'])
def add_cash(request):
    if request.method == "POST":
        amount = float(request.POST.get('amount', 0))
        client = Client.objects.get(user=request.user)
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
        client = Client.objects.get(user=request.user)
        portfolio = Portfolio.objects.get(client=client)
        if portfolio.cash_balance >= amount:
            portfolio.cash_balance -= amount
            portfolio.save()
        return redirect('basic_app:portfolio')
    return render(request, 'basic_app/withdraw_cash.html')

@login_required(login_url='basic_app:login')
@allowed_users(allowed_roles=['Client'])
def explore_stocks(request):
    return render(request, 'basic_app/search_stock.html', {'page_title': "Explore Stocks"})

from django.views.decorators.http import require_POST

@csrf_exempt
@login_required(login_url='basic_app:login')
@allowed_users(allowed_roles=['Client'])
@require_POST
def search_stock(request):
    print("[SEARCH] POST received.")
    query = request.POST.get('searchData', '').strip()
    print(f"[SEARCH] Query received: {query}")

    if query:
        stock_data = getStockInfo(query)
        print(f"[SEARCH] getStockInfo returned: {stock_data}")

        if stock_data and stock_data.get('name', '').lower() != "data not available":
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                # 🧠 Return dynamic suggestion if AJAX typing
                return JsonResponse({'data': [stock_data]})
            else:
                # 🚀 Normal button submit → hard redirect
                return redirect('basic_app:stock', symbol=stock_data['symbol'].upper())
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'data': []})
            else:
                return redirect('basic_app:portfolio')

    # If query was empty
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'data': []})
    return redirect('basic_app:portfolio')

@csrf_exempt
@csrf_exempt
def get_indicator(request, symbol, indicator):
    """
    Given a stock symbol and indicator name, return JSON data points for plotting.
    """
    try:
        if indicator == "SMA":
            df = ta.sma(symbol)
        elif indicator == "EMA":
            df = ta.ema(symbol)
        elif indicator == "MACD":
            df = ta.macd(symbol)
        elif indicator == "RSI":
            df = ta.rsi(symbol)
        elif indicator == "OBV":
            df = ta.obv(symbol)
        elif indicator == "BB":
            df = ta.bband(symbol)
        else:
            return JsonResponse({'error': 'Unknown indicator'}, status=400)

        return JsonResponse(df.to_dict(orient="records"), safe=False)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
