import argparse
import json

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
        
            
    

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Walk a budget to visualize current balance')
    parser.add_argument('--config', dest='config', default='config.json', help='Configuration file to use')
    parser.add_argument('--budgetCsv', dest='budgetCsv', default='budget.csv', help='Budget CSV file')
    parser.add_argument('--start', dest='start', default=0.00, type=float, help='Starting balance')

    args = parser.parse_args()
    
    print(readJson(args.config))
    print(readCsv(args.budgetCsv, types=[int, float])) 
