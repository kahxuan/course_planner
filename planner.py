import json
import pandas as pd
from graph import CourseGraph
import os
import sys
sys.path.append(os.path.dirname(os.path.realpath(__file__)))
from config import data_dir

if __name__ == "__main__":

    units = pd.read_csv(os.path.join(data_dir, 'fit_unit_msia.csv'))
    units['prohibition'] = units['prohibition'].apply(eval)
    units['prerequisite'] = units['prerequisite'].apply(eval)

    offers = pd.read_csv(os.path.join(data_dir, 'offering_msia.csv'))
    offers = offers[(offers['code'] != 'FIT3045') & (offers['code'] != 'FIT3199')]

    with open(os.path.join(data_dir, 'grad_req.json')) as f:
        grad_req = json.load(f)

    # major = 'data_sc'
    major = 'adv_cs'
    start_sem = 2
    fixed = [['FIT1045', 'FIT1047', 'MAT1841'], ['MAT1830', 'FIT2099', 'FIT1008', 'FIT1055'], ['FIT2004', 'FIT2086'], [], ['FIT3161']]

    cp = grad_req['credit_point']
    req = grad_req[major]
    req['credit_point'] = cp
    req['core'] += grad_req['core']

    print(req)


    g = CourseGraph(units, offers)
    g.finalise_initial(req)
    order = g.plan(start_sem, fixed)

    print('==============')
    for sem in order:
        for item in sem:
            if item is not None:
                print(item.unit_code, units['name'][units['code'] == item.unit_code])
            else:
                print(None)
        print('===============')

    print(g.grad)
