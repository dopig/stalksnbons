from __future__ import print_function, division
from datetime import date
from dateutil.relativedelta import relativedelta

import numpy as np
import pandas as pd
from flask import Flask, render_template, url_for, request, redirect
from bokeh.plotting import figure as bok_fig
from bokeh.embed import components as bok_comp

app = Flask(__name__)

def render_stock(symbol, plist):
    def lookup_stock(symbol):
        month_ago = str(date.today() + relativedelta(months=-1))
        Qkey = '&api_key=RnJytZXXdR6i8UytSYvG' 
        url = 'https://www.quandl.com/api/v3/datasets/WIKI/'\
               +symbol.upper().strip()+'.csv?start_date='+month_ago+Qkey
        df = pd.read_csv(url, index_col=0,  parse_dates=['Date'])
        return df

    df = lookup_stock(symbol)
    x = df.index

    if 'close' in plist:
        y = df.Close
        rangeY = np.append(df.High, df.Low[::-1])
        legend = "Closing"
    else:
        y = df['Adj. Close']
        rangeY = np.append(df['Adj. High'], df['Adj. Low'][::-1])
        legend = "Closing (adjusted)"

    plot = bok_fig(title=symbol+' stock prices from Quandle',\
                   x_axis_label='date', x_axis_type='datetime',\
                   y_axis_label = "price ($'s)")    
    plot.line(x, y, legend = legend, line_width=2)

    if 'show_range' in plist:
        rangeX = np.append(df.index, df.index[::-1])
        plot.patch(rangeX, rangeY, legend = "Range", alpha = 0.2,\
                   color = 'navy', line_width = 0)  
    return bok_comp(plot)


@app.route('/', methods = ['GET', 'POST'])
def main():
    if request.method == 'POST':       
        symbol = request.form['stockSym'].strip()
        if not symbol:
            return redirect(url_for('main'))

        plist = request.form.getlist('priceType')
        script, div = render_stock(symbol, plist)
        return render_template("index.html", script=script, div=div,\
                               symbol = symbol)
    else:
        return render_template("index.html")


if __name__ == "__main__":
    #app.debug = True
    #app.run(host = '0.0.0.0')
    app.run()
