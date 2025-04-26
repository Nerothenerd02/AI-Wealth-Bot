var updateBtns = document.getElementsByClassName("update-portfolio");

if (updateBtns.length > 0) {
  updateBtns[0].addEventListener("click", function() {
    var stock_key = this.dataset.symbol;
    var action = this.dataset.action;
    var name = this.dataset.name;
    console.log(stock_key + "  " + action);
    console.log(name);

    $.ajax({
      type: 'POST',
      url: '',
      data: {
        'myData': stock_key,
        'action': action,
        'name': name,
        'csrfmiddlewaretoken': csrftoken
      },
      success: function() { console.log('Stock added to portfolio successfully') },
      error: function() { console.log('Failed to add stock') }
    });
  });
}

// --- Technical Analysis Chart (AnyChart) Setup ---
var passed_data = JSON.parse(document.getElementById('chart-box').dataset.candlestickData);  // get candlestick data
var info = JSON.parse(document.getElementById('chart-box').dataset.stockInfo);  // get stock info

var chart = anychart.stock();
var dataTable = anychart.data.table('Date');
dataTable.addData(passed_data);
var mapping = dataTable.mapAs({ open: "Open", high: "High", low: "Low", close: "Close" });
var series = chart.plot(0).candlestick(mapping);
series.name(info[0]["name"] + " Candlestick Chart");

chart.title(info[0]["name"] + " Candlestick Data");
chart.container('chart-box');
chart.draw();

// --- Reset Button ---
var resetBtn = document.getElementById('resetButton');
resetBtn.addEventListener('click', function() {
  chart.dispose();
  chart = anychart.stock();
  var dataTable = anychart.data.table('Date');
  dataTable.addData(passed_data);
  var mapping = dataTable.mapAs({ open: "Open", high: "High", low: "Low", close: "Close" });
  var series = chart.plot(0).candlestick(mapping);
  series.name(info[0]["name"] + " Candlestick Chart");
  chart.title(info[0]["name"] + " Candlestick Data");
  chart.container('chart-box');
  chart.draw();
  document.getElementById('indicator').value = "NONE";
});

// --- Indicators Dropdown (RSI, MACD, SMA, BB) ---
document.getElementById('indicator').addEventListener('change', function() {
  var selectedIndicator = this.value;
  var plot = chart.plot(0);

  if (selectedIndicator === "RSI") {
    var plot1 = chart.plot(1);
    plot1.rsi(mapping, 14);
  } else if (selectedIndicator === "MACD") {
    var plot1 = chart.plot(1);
    plot1.macd(mapping, 12, 26, 9);
  } else if (selectedIndicator === "SMA") {
    plot.sma(mapping, 20).series();
  } else if (selectedIndicator === "BB") {
    var bbands = plot.bbands(mapping);
    bbands.upperSeries().stroke('#bf360c');
    bbands.middleSeries().stroke('#ff6600');
    bbands.lowerSeries().stroke('#bf360c');
    bbands.rangeSeries().fill('#ffd54f 0.2');
  }
});

// --- News Sentiment Chart (Chart.js) ---
var sentiment_data = JSON.parse(document.getElementById('densityChart').dataset.sentimentData);

var ctx = document.getElementById('densityChart').getContext('2d');
new Chart(ctx, {
  type: 'bar',
  data: {
    labels: ['Positive', 'Negative', 'Neutral'],
    datasets: [{
      label: 'Sentiment Analysis',
      data: [
        sentiment_data['positive'],
        sentiment_data['negative'],
        sentiment_data['neutral']
      ],
      backgroundColor: [
        'rgba(75, 192, 192, 0.6)',
        'rgba(255, 99, 132, 0.6)',
        'rgba(255, 205, 86, 0.6)'
      ],
      borderColor: [
        'rgba(75, 192, 192, 1)',
        'rgba(255, 99, 132, 1)',
        'rgba(255, 205, 86, 1)'
      ],
      borderWidth: 1
    }]
  },
  options: {
    indexAxis: 'y'
  }
});
