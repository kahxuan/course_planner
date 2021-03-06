import json
import pandas as pd
from graph import CourseGraph
import os
import sys
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..'))
from config import data_dir

def get_units():
    
    offers = pd.read_csv(os.path.join(data_dir, 'offering_msia.csv'))
    return offers['code'].unique().tolist()


def check_fixed(units, start_sem):

    offers = pd.read_csv(os.path.join(data_dir, 'offering_msia.csv'))

    errors = []
    count = {}
    dup = []

    for i in range(len(units)):
        for unit in units[i]:
            if (start_sem + i) % 2 == 1:
                period = "First semester"
            else:
                period = "Second semester"

            if offers[(offers['period'] == period) & (offers['code'] == unit)].empty:
                errors.append(' is not offered in the '.join([unit, period.lower()]))

            if unit not in count:
                count[unit] = 1
            else:
                count[unit] += 1
                if count[unit] == 2:
                    dup.append(unit)

    for unit in dup:
        errors.append("{} is repeated {} times".format(unit, count[unit]))

    return errors


def plan(major, start_sem, fixed):

    units = pd.read_csv(os.path.join(data_dir, 'fit_unit_msia.csv'))
    units['prohibition'] = units['prohibition'].apply(eval)
    units['prerequisite'] = units['prerequisite'].apply(eval)

    offers = pd.read_csv(os.path.join(data_dir, 'offering_msia.csv'))
    
    with open(os.path.join(data_dir, 'grad_req.json')) as f:
        grad_req = json.load(f)

    cp = grad_req['credit_point']
    req = grad_req[major]
    req['credit_point'] = cp
    req['core'] += grad_req['core']

    g = CourseGraph(units, offers)
    g.finalise_initial(req)
    return g.plan(start_sem, fixed)


if __name__ == "__main__":
    units = pd.read_csv(os.path.join(data_dir, 'fit_unit_msia.csv'))

    major = 'data_sc'
    # major = 'adv_cs'
    start_sem = 2
    fixed = [['FIT1008', 'FIT1045', 'FIT1043', 'FIT1047'], ['FIT1047'], [], [], ['FIT2086']]

    order = plan(major, start_sem, fixed)

    print('==============')
    for sem in order:
        for item in sem:
            if item is not None:
                print(item.unit_code, units['name'][units['code'] == item.unit_code])
            else:
                print(None)
        print('===============')
