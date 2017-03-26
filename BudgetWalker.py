import argparse



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Walk a budget to visualize current balance')
    parser.add_argument('--config', dest='config', default='config.json', help='Configuration file to use')
    parser.add_argument('--budgetCsv', dest='budgetCsv', default='budget.csv', help='Budget CSV file')
    parser.add_argument('--start', dest='start', default=0.00, type='float', help='Starting balance')

    args = parser.parse_args()
    print(args.accumulate(args.integers))
