import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

# 1. Kursdaten abrufen
ticker = 'TSLA'  # Oder ein anderer Ticker wie 'AAPL', 'MSFT'
data = yf.download(ticker, start='2020-01-01', end='2023-12-31')

# Daten prüfen
if data.empty:
    print("❌ Fehler: Keine Kursdaten geladen.")
    exit()
    
# 2. SMAs berechnen
data['SMA20'] = data['Close'].rolling(window=20).mean()
data['SMA50'] = data['Close'].rolling(window=50).mean()

# 3. Signale erzeugen (Kreuzung der SMAs)
data['Signal'] = 0
for i in range(1, len(data)):
    if data['SMA20'].iloc[i - 1] < data['SMA50'].iloc[i - 1] and data['SMA20'].iloc[i] > data['SMA50'].iloc[i]:
        data.loc[data.index[i], 'Signal'] = 1  # Kaufsignal
    elif data['SMA20'].iloc[i - 1] > data['SMA50'].iloc[i - 1] and data['SMA20'].iloc[i] < data['SMA50'].iloc[i]:
        data.loc[data.index[i], 'Signal'] = -1  # Verkaufssignal

data['Position'] = data['Signal']

# 4. Backtest durchführen
initial_cash = 10000
cash = initial_cash
shares = 0
position = 0
trades = 0

for i in range(len(data)):
    price = float(data['Close'].iloc[i])  # <== float erzwingen!
    if data['Position'].iloc[i] == 1 and position == 0:
        shares = cash / price
        cash = 0
        position = 1
        trades += 1
    elif data['Position'].iloc[i] == -1 and position == 1:
        cash = shares * price
        shares = 0
        position = 0
        trades += 1
# 6.1. Trades in Liste sammeln
trade_log = []
position = 0
cash = initial_cash
shares = 0

for i in range(len(data)):
    date = data.index[i]
    price = float(data['Close'].iloc[i])
    signal = data['Position'].iloc[i]

    if signal == 1 and position == 0:
        shares = cash / price
        cash = 0
        position = 1
        trade_log.append({"Datum": date, "Aktion": "Kauf", "Preis": price})
    elif signal == -1 and position == 1:
        cash = shares * price
        shares = 0
        position = 0
        trade_log.append({"Datum": date, "Aktion": "Verkauf", "Preis": price})

# 6.2. Trade-Log als CSV speichern
df_trades = pd.DataFrame(trade_log)
df_trades.to_csv("trade_log.csv", index=False)
print("💾 Trades wurden in 'trade_log.csv' gespeichert.")

# 5. Endkapital berechnen
last_price = float(data['Close'].iloc[-1])
final_value = shares * last_price if position == 1 else cash
profit = final_value - initial_cash

# 6. Ergebnisse anzeigen
print("=== BACKTEST ERGEBNISSE ===")
print(f"Aktie:             {ticker}")
print(f"Zeitraum:          {data.index[0].date()} bis {data.index[-1].date()}")
print(f"Anzahl Trades:     {trades}")
print(f"Initiales Kapital: {initial_cash:.2f} $")
print(f"Endkapital:        {final_value:.2f} $")
print(f"Gewinn/Verlust:    {profit:.2f} $")
print("===========================")

# 7. Kurs-Chart mit Signalen anzeigen
plt.figure(figsize=(14, 7))
plt.plot(data['Close'], label='Kurs', alpha=0.5)
plt.plot(data['SMA20'], label='SMA20', color='orange')
plt.plot(data['SMA50'], label='SMA50', color='magenta')

plt.plot(data[data['Position'] == 1].index,
         data['SMA20'][data['Position'] == 1],
         '^', label='Kaufen', color='green', markersize=10)

plt.plot(data[data['Position'] == -1].index,
         data['SMA20'][data['Position'] == -1],
         'v', label='Verkaufen', color='red', markersize=10)

plt.title(f'SMA Crossover Strategie – {ticker}')
plt.xlabel('Datum')
plt.ylabel('Kurs in $')
plt.legend()
plt.grid()
plt.tight_layout()
plt.show()
