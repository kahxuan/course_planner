# Course Planner

This application guides students on planning their course structure by generating a personalised course map based on the student's intake, specialisation and units completed. This overcomes the struggle in course planning given that some units are only offered in selected semester. Currently, this course planner is only available for Monash University Malaysia computer science units.

Try it out at: https://getcoursemap.herokuapp.com/

Alternatively, download this project and run `python app.py` in the command line, then nagivate to http://localhost:5000 in your browser.

![alt Text](https://github.com/kahxuan/course_planner/blob/master/static/images//demo.gif)

### Data files
| Filename | Description |
| -------- | ------------|
| raw.json | Raw data collected from https://handbook.monash.edu, contains the details for all computer science units (including units that are not offered in Malaysia campus) |
| grad_req.json | Course completion and specialisation requirements |
| fit_code_msia.txt | List of unit codes |
| fit_unit_msia.csv | [Cleaned](https://github.com/kahxuan/course_planner/blob/master/scripts/clean_data.ipynb) unit details (from raw.json) |
| offering_msia.csv | List of of units offerings (from raw.json) |

## How it works

The set of units and requirements is modelled as a directed graph, where units are represented as nodes and requirements are represented as edges. A node's requirements are satisfied when its incoming edge count is 0.

This algorithm is based on topological sorting, but with one or more priority queues to store the list of nodes without incoming edge.

### Requirements as edges

X is a prerequisite to Y:

![](https://github.com/kahxuan/course_planner/blob/master/static/images/basic-prereq.png/)


Any two of (W, X, Y) can together be a prerequisite to Z:

![](https://github.com/kahxuan/course_planner/blob/master/static/images/optional-prereq.png)


X is a prohibition to Y:

![](https://github.com/kahxuan/course_planner/blob/master/static/images/prohibition.png)

When X is visited, the incoming edge count of Y will be incremented.

### Flow
For each semester, units are selected using the following steps until the course requirements are met:
1. From the list of nodes (units) with no incoming edge, select the unit with the highest priority repeatedly until the credit hour limit is reached.
2. Clear all outgoing edges for nodes selected in the previous step.
3. Evaluate adjacent nodes: add to the list if they have no incoming edge and all requirements are met.
4. Clear all intermediate nodes and their outgoing edges and evaluate adjacent nodes.

![](https://github.com/kahxuan/course_planner/blob/master/static/images/graph-illustration.gif)

### Priority queues

Separate heaps containing ready nodes are maintained for the two different semesters, where each heap only contains the units offered in the corresponding semester. The heaps are used alternately in each iteration (semester). In the heaps, core units and prerequisite units are assigned to a higher priority.
