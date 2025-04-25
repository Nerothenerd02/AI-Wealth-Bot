from django.shortcuts import render,redirect
from .models import Portfolio,Client,Stock
from .forms import CreateUserForm
from .sectorPerformance import  sectorPerformance
from .decorators import unauthenticated_user,allowed_users
from basic_app.stock_data import candlestick_data,get_data,get_name,get_price
from basic_app.FA import piotroski
# Create your views here.
from django.http import HttpResponse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from django.contrib.auth.models import User,Group
from django.contrib.auth.decorators import login_required
from basic_app.get_news import getNews,getNewsWithSentiment
from basic_app.get_stock_info import getStockInfo
from django.http import JsonResponse
from json import dumps,loads
from basic_app.ProphetTrend import forecast

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
        stock_data = getStockInfo(data)
        if stock_data:
            return JsonResponse({'data': [stock_data]})
        else:
            return JsonResponse({'data': "No stocks found.."})

    # Fetch trending news
    news = getNews('market')  # You can change 'market' to 'stocks', or 'finance'

    return render(request, 'basic_app/index.html', {'news': news})    

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
    # Sentiment = {}
    # for s in stocks:
    #     sentiment = 0;
    #     for i in range(12):
    #         news = getNewsWithSentiment(s.stock_symbol)
    #         if news[i]['sentiment'] == 'positive':
    #             sentiment+=1
    #         elif news[i]['sentiment'] == 'negative':
    #             sentiment-=1
    #
    #     if sentiment >0:
    #         s.stock_sentiment = "Positive"
    #     elif sentiment<0:
    #         s.stock_sentiment = "Negative"
    #     else:
    #         s.stock_sentiment = "Neutral"
    #
    SP = {}
    for s in stocks:
        if(not s.stock_sector_performance):
            s.stock_sector_performance = sectorPerformance(s.stock_symbol)
        if(not s.stock_price):
            price = get_price(s.stock_symbol)
            s.stock_price = str(round(price[0],2))+ "  " + price[1]
        s.save()

    context = {'stocks':stocks,'page_title':"Your Portfolio"}
    return render(request,"basic_app/portfolio.html",context)

@login_required(login_url='basic_app:login')
def stock(request, symbol):
    data = candlestick_data(symbol)
    item = getStockInfo(symbol)
    info = get_data(symbol)
    piotroski_score = piotroski(symbol)

    # Get news with sentiment using full company name
    news = getNewsWithSentiment(info['shortName'])
    print("[News Fetched]", news)

    # Initialize sentiment counter
    sentiment_news_chart = {'positive': 0, 'negative': 0, 'neutral': 0}

    # Safely loop through all news items
    for i in range(len(news)):
        try:
            sentiment = news[i].get('sentiment', 'neutral')  # Use 'neutral' as fallback
            if sentiment in sentiment_news_chart:
                sentiment_news_chart[sentiment] += 1
        except Exception as e:
            print(f"[Warning] Failed to process sentiment for news[{i}]: {e}")

    print("[Sentiment Count]", sentiment_news_chart)

    # Recommendation logic
    recommendation = False
    overall_sentiment = sentiment_news_chart['positive'] - sentiment_news_chart["negative"]
    if piotroski_score > 5 and overall_sentiment > 0:
        recommendation = True

    print("[Recommendation]", recommendation)

    context = {
        'data': dumps(data),
        'item': dumps(item),
        'info': info,
        'piotroski_score': piotroski_score,
        'sentiment_data': dumps(sentiment_news_chart),
        'page_title': symbol + " Info",
        'recommendation': recommendation
    }

    # Handle AJAX portfolio add
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        data = request.POST.get('myData')
        action = request.POST.get('action')
        name = request.POST.get('name')

        user = request.user
        client = Client.objects.get(user=user)
        portfolio = Portfolio.objects.get(client=client)
        stocks = portfolio.stocks.all()

        run = False
        for stock in stocks:
            if data == stock.stock_symbol:
                stock.quantity += 1
                stock.save()
                run = True

        if not run:
            new_stock = Stock.objects.create(
                parent_portfolio=portfolio,
                stock_symbol=data,
                stock_name=name,
                quantity=1
            )
            new_stock.save()

        return JsonResponse({})

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


def quantityAdd(request,symbol):
    user = request.user
    print(user)
    client = Client.objects.get(user=user)
    portfolio = Portfolio.objects.get(client=client)
    stocks = portfolio.stocks.all()
    for stock in stocks:
        if symbol == stock.stock_symbol:
            stock.quantity+=1
            stock.save()
    return redirect("basic_app:portfolio")

def quantitySub(request,symbol):
    user = request.user
    print(user)
    client = Client.objects.get(user=user)
    portfolio = Portfolio.objects.get(client=client)
    stocks = portfolio.stocks.all()
    for stock in stocks:
        if symbol == stock.stock_symbol:
            stock.quantity-=1

            if stock.quantity == 0:
                stock.delete()
            else:
                stock.save()

    return redirect("basic_app:portfolio")



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