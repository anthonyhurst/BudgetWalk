import argparse
import json
import datetime
import pytz
import numpy
import pandas
import matplotlib
matplotlib.use('Agg')

def readFile(filename):
    f = open(filename, 'r')
    content = f.read()
    f.close()
    return content

def readJson(filename):
    return json.loads(readFile(filename))

def readCsv(filename, types=[]):
    header = None
    records = []
    for line in readFile(filename).split("\n"):
        if not line.strip(): # skip empty lines
            continue
        if header == None:
            header = line.split(",")
            continue
        i = 0
        record = {}
        for column in line.split(","):
            if len(types): # strongly typed if types available
                column = types[i](column)
            record[header[i]] = column
            i+=1
        records.append(record)
    return records

def getBudgetInstructions(data):
    result = {}
    for each in data:
        dayOfMonth = each['dayOfMonth']
        delta = each['delta']
        reason = each['reason']
        if not dayOfMonth in result:
            result[dayOfMonth] = []
        rec = {
            "delta": delta,
            "reason": reason
        }
        result[dayOfMonth].append(rec)
    return result
        
    
        
def budgetWalk(config):
    balance = config['StartingBalance']

    utc = pytz.utc
    eastern = pytz.timezone('US/Eastern')

    dt = utc.localize(datetime.datetime.now())
    local = dt.astimezone(eastern)

    instructions = getBudgetInstructions(config['Data'])

    dayDelta = datetime.timedelta(days=1)
    daysToShow = 30 if not 'DaysToShow' in config else config['DaysToShow']
    minBalance = 0 if not 'MinimumBalance' in config else config['MinimumBalance']

    dfRecords = []
    dfRecords2 = []

    for i in range(daysToShow):
        reasons = ""
        if local.day in instructions:
            print(local.strftime('%Y-%m-%d'), end="\t")
            dayBalance = 0
            dayReasons = []
            for instruction in instructions[local.day]:
                balance += instruction['delta']
                balance = round(balance,2)
                dayBalance += balance
                dayBalance = round(dayBalance,2)
                dayReasons.append(instruction['reason'])
                if balance < minBalance:
                    raise Exception("Current balance goes below minimum: $" + str(balance) + " on " + str(local.strftime("%Y-%m-%d") + " because of " + instruction['reason']))
                if instruction['delta'] < 0 and i <= 30:
                    dfRecords2.append([pandas.to_datetime(local.strftime('%Y-%m-%d'), format='%Y-%m-%d'), -1*instruction['delta'], instruction['reason']])
            reasons = ",".join(dayReasons)
            print("${:,.2f}".format(balance), end="\t")
            print(reasons)
        dfRecords.append([pandas.to_datetime(local.strftime('%Y-%m-%d'), format='%Y-%m-%d'), balance, reasons])
        local += dayDelta

    xticks = pandas.date_range(start=dfRecords[0][0], end=dfRecords[-1][0])

    df = pandas.DataFrame.from_records(dfRecords)
    df.index = xticks 
    df.columns = ['Date', 'Balance', 'Reasons']

    ax = df.plot(figsize=(20,10))

    figure = ax.get_figure()

    ax.set_ylabel('Balance')
    ax.set_xlabel('Date')
    ax.set_title('BudgetWalk')

    ax.grid(True, which='major')
    ax.yaxis.grid(True, which='major')

    yvals = ax.get_yticks()
    ax.set_yticklabels(['${:,.2f}'.format(x) for x in yvals])

    ax.xaxis.set_minor_locator(matplotlib.dates.WeekdayLocator(byweekday=(1), interval=1))
    ax.xaxis.set_minor_formatter(matplotlib.dates.DateFormatter('%m-%d'))

    figure.savefig(config['GraphOutputFile'])

    df2 = pandas.DataFrame.from_records(dfRecords2)
    df2.columns = ['Date', 'Delta', 'Reason']
    df2.index = df2['Reason']

    ax2 = df2.plot(kind='pie', y='Delta', figsize=(20,20))
    
    figure2 = ax2.get_figure()
    figure2.savefig(config['PieGraphOutputFile'])
    
    
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Walk a budget to visualize current balance')
    parser.add_argument('--config', dest='config', default='config.json', help='Configuration file to use')
    parser.add_argument('--budgetFile', dest='budgetFile', default=None, help='Budget CSV file')
    parser.add_argument('--startingBalance', dest='startingBalance', default=None, type=float, help='Starting balance')

    args = parser.parse_args()
    
    config = readJson(args.config)
    if args.budgetFile is not None:
        config['BudgetFile'] = args.budgetFile
    if args.startingBalance is not None:
        config['StartingBalance'] = args.startingBalance

    config['Data'] = readCsv(config['BudgetFile'], types=[int, float, str]) 
    
    budgetWalk(config)
    
