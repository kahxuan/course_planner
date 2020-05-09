import json
import pandas as pd
from graph import CourseGraph

if __name__ == "__main__":

    units = pd.read_csv('fit_unit_msia.csv')
    units['prohibition'] = units['prohibition'].apply(eval)
    units['prerequisite'] = units['prerequisite'].apply(eval)

    offers = pd.read_csv('offering.csv')
    offers = offers[(offers['code'] != 'FIT3045') & (offers['code'] != 'FIT3199')]
    print(offers)

    with open('grad_req.json') as f:
        grad_req = json.load(f)

    # major = 'data_sc'
    major = 'adv_cs'
    grad_req_major = grad_req[major]
    grad_req_major['core'] += grad_req['core']

    print(grad_req_major)


    g = CourseGraph(units, offers, grad_req_major)
    order = g.plan(start_sem=2)

    print('==============')
    for sem in order:
        for item in sem:
            if item is not None:
                print(item.unit_code, units['name'][units['code'] == item.unit_code])
            else:
                print(None)
        print('===============')

    print(g.grad)
