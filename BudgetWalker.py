import argparse
import json
import datetime
import pytz

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
        if not dayOfMonth in result:
            result[dayOfMonth] = 0
        result[dayOfMonth] += delta # really we end of moving the balance by the sum of delta
    return result
        
    
        
def budgetWalk(config):
    balance = config['StartingBalance']

    utc = pytz.utc
    eastern = pytz.timezone('US/Eastern')

    dt = utc.localize(datetime.datetime.now())
    local = dt.astimezone(eastern)

    instructions = getBudgetInstructions(config['Data'])

    dayDelta = datetime.timedelta(days=1)

    for i in range(30):
        if local.day in instructions:
            print(local)
            balance += instructions[local.day]
            print(balance)
        local += dayDelta
    
    

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

    config['Data'] = readCsv(config['BudgetFile'], types=[int, float]) 
    
    budgetWalk(config)
    
