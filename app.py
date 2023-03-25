from flask import Flask, render_template, request
import requests
 
app = Flask(__name__)

# Where EUR is the base currency
api_key = "b6d4b859aa0cc800da4b3234"
url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/EUR"

cur_list = ("AUD", "CAD", "CHF", "EGP", "EUR", "GBP", "NOK", "RUB", "SEK", "USD")
headings = ("Intermediary Currency", " to IC", "IC to ", "PROFIT")

# Truncate fractional part of 'cents'
def trun(n,d):
    s=repr(n).split('.')
    if (len(s)==1):
        return int(s[0])
    return float(s[0]+'.'+s[1][:d])

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        try:
            amount = request.form['amount']
            amount = float(amount)
            from_c = request.form['from_c']
            to_c = request.form['to_c']
            response = requests.get(url).json()
            exchange_rates = response["conversion_rates"]
        
            BFC = { 'currency' : "", 'amount' : 0 }
            BFS = { 'currency' : "", 'profit' : 0 }
            o = []

            for c in cur_list:
                if c not in [from_c,to_c]:

                    original_amount = amount / exchange_rates[from_c]
                    am1 = original_amount * exchange_rates[c]
                    # Keep fractions of cents during conversion
                    oa1 = trun(am1,2) / exchange_rates[c]
                    converted_amount = oa1 * exchange_rates[to_c]
                    profit = converted_amount - trun(converted_amount,2)
                    # BFC == 'Best for customer', BFS == 'Best for service provider'
                    if BFC['amount'] < converted_amount :
                        BFC = {'currency' : c, 'amount' : converted_amount}
                    if BFS['profit'] < profit :
                        BFS = {'currency' : c, 'profit' : profit}
                    o.append( [c, round(am1,4), round(converted_amount,4), round(profit,4)] )
                    # print(o,flush=True)

            time = response["time_last_update_utc"]

            return render_template('home.html', headings=headings, cur_list=cur_list, \
                                    amount=amount, from_c=from_c, to_c=to_c, data=o, \
                                    bfc=BFC['currency'], bfs=BFS['currency'], time=time)
        except Exception as e:
            return '<h1>Bad Request : {}</h1>'.format(e)
  
    else:
        return render_template('home.html')
  
  
if __name__ == "__main__":
    app.run(debug=True)
