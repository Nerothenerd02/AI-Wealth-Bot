import pandas as pd
import yfinance as yf

def piotroski(ticker):
    ticker_data = yf.Ticker(ticker)
    bs = ticker_data.balance_sheet
    inc = ticker_data.financials
    cf = ticker_data.cashflow

    def safe_get(df, key, index=0, default=0):
        try:
            return df.loc[key].iloc[index]
        except (KeyError, IndexError):
            return default

    longTermDebt     = safe_get(bs, 'Long Term Debt')
    longTermDebtPre  = safe_get(bs, 'Long Term Debt', 1)
    totalAssets      = safe_get(bs, 'Total Assets')
    totalAssetsPre   = safe_get(bs, 'Total Assets', 1)
    totalAssetsPre2  = safe_get(bs, 'Total Assets', 2)

    currentAssets        = safe_get(bs, 'Total Current Assets')
    currentAssetsPre     = safe_get(bs, 'Total Current Assets', 1)
    currentLiabilities   = safe_get(bs, 'Total Current Liabilities')
    currentLiabilitiesPre = safe_get(bs, 'Total Current Liabilities', 1)

    revenue         = safe_get(inc, 'Total Revenue')
    revenuePre      = safe_get(inc, 'Total Revenue', 1)
    grossProfit     = safe_get(inc, 'Gross Profit')
    grossProfitPre  = safe_get(inc, 'Gross Profit', 1)
    netIncome       = safe_get(inc, 'Net Income')
    netIncomePre    = safe_get(inc, 'Net Income', 1)

    operatingCashFlow    = safe_get(cf, 'Total Cash From Operating Activities')
    operatingCashFlowPre = safe_get(cf, 'Total Cash From Operating Activities', 1)

    commonStock     = safe_get(bs, 'Common Stock')
    commonStockPre  = safe_get(bs, 'Common Stock', 1)

    # Prevent division by zero
    avg_total_assets = (totalAssets + totalAssetsPre) / 2 or 1
    avg_total_assets_pre = (totalAssetsPre + totalAssetsPre2) / 2 or 1

    # Piotroski Score Components
    ROAFS = int(netIncome / avg_total_assets > 0)
    CFOFS = int(operatingCashFlow > 0)
    ROADFS = int((netIncome / avg_total_assets) > (netIncomePre / avg_total_assets_pre))
    CFOROAFS = int((operatingCashFlow / totalAssets) > (netIncome / avg_total_assets))
    LTDFS = int(longTermDebt <= longTermDebtPre)

    # Check current ratios safely
    CRFS = int((currentAssets / (currentLiabilities or 1)) > (currentAssetsPre / (currentLiabilitiesPre or 1)))
    NSFS = int(commonStock <= commonStockPre)
    GMFS = int((grossProfit / (revenue or 1)) > (grossProfitPre / (revenuePre or 1)))
    ATOFS = int((revenue / avg_total_assets) > (revenuePre / avg_total_assets_pre))

    return ROAFS + CFOFS + ROADFS + CFOROAFS + LTDFS + CRFS + NSFS + GMFS + ATOFS

# Remove print during production setup
# print(piotroski('msft'))
