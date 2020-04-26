import pandas as pd
from graph import CourseGraph

if __name__ == "__main__":

    units = pd.read_csv('fit_unit_msia.csv')
    units['prohibition'] = units['prohibition'].apply(eval)
    units['prerequisite'] = units['prerequisite'].apply(eval)
    offers = pd.read_csv('offering.csv')
    g = CourseGraph(units, offers)
    order = g.plan(start_sem=1)

    print('==============')
    for sem in order:
        for item in sem:
            if item is not None:
                print(item.unit_code, units['name'][units['code'] == item.unit_code])
            else:
                print(None)
        print('===============')