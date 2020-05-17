import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'planner'))
from flask import *
from planner import get_units, plan, check_fixed
from config import data_dir

app = Flask(__name__)

@app.route('/', methods = ['POST', 'GET'])
def show_index():
    return redirect(url_for('show_edit', 
        major='adv_cs',
        start_year=2019, 
        start_sem=1,
        fixed=[[] for i in range(6)]))

@app.route('/edit/<major>/<start_year>/<start_sem>/<fixed>', methods = ['POST', 'GET'])
def show_edit(major, start_year, start_sem, fixed):

    if request.method == 'POST':
        fixed = []
        i = 1
        while str(i) + "_1" in request.form:
            j = 1
            units = []
            while str(i) + "_" + str(j) in request.form:
                if len(request.form[str(i) + "_" + str(j)]) > 0:
                    units.append(request.form[str(i) + "_" + str(j)])
                j += 1
            fixed.append(units)
            i += 1

        errors = check_fixed(fixed, int(request.form['start_sem']))
        if len(errors) > 0:
            return redirect(url_for('show_errors', 
                major=request.form['major'], 
                start_year=request.form['start_year'],
                start_sem=request.form['start_sem'],
                fixed=fixed,
                errors=errors))

        return redirect(url_for('show_planned', 
            major=request.form['major'], 
            start_year=request.form['start_year'],
            start_sem=request.form['start_sem'],
            fixed=fixed))

    fixed = eval(fixed) + ([] * (6 - len(fixed)))
    plan = [None] * len(fixed)
    for i in range(len(fixed)):
        plan[i] = fixed[i] + max(0, 4 - len(fixed[i])) * [None]

    context = {}
    context['units'] = sorted(get_units())
    context['major'] = major
    context['start_year'] = int(start_year)
    context['start_sem'] = int(start_sem)
    context['plan'] = plan
    return render_template("index.html", **context)

@app.route('/planned/<major>/<start_year>/<start_sem>/<fixed>/<errors>', methods = ['POST', 'GET'])
def show_errors(major, start_year, start_sem, fixed, errors):
    if request.method == 'POST':
        return redirect(url_for('show_edit', 
            major=major, 
            start_year=start_year,
            start_sem=start_sem,
            fixed=fixed))

    context = {}
    context['major'] = major
    context['start_year'] = int(start_year)
    context['start_sem'] = int(start_sem)
    context['errors'] = eval(errors)
    return render_template("error.html", **context)


@app.route('/planned/<major>/<start_year>/<start_sem>/<fixed>', methods = ['POST', 'GET'])
def show_planned(major, start_year, start_sem, fixed):
    if request.method == 'POST':
        return redirect(url_for('show_edit', 
            major=major, 
            start_year=start_year,
            start_sem=start_sem,
            fixed=fixed))
    context = {}
    context['major'] = major
    context['start_year'] = int(start_year)
    context['start_sem'] = int(start_sem)
    context['plan'] = plan(context['major'], context['start_sem'], eval(fixed))
    return render_template("planned.html", **context)


if __name__ == "__main__":
  app.run()