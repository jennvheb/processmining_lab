# processmining_lab

Process Mining Webservice (Alpha and Heuristic Miner Implementation)

This webservice is implemented in Python and Flask.

# dependencies
```sh
$ pip install -r requirements.txt
```

# usage
```sh
$ python main.py
```

Will start the webservice, where the user can upload an event log in the form of an xes-file.

Selecting Alpha Miner generates a Petri Net, whereas the Heuristic Miner generates a Causal Net, from the uploaded event log.

# credits
The process mining algorithms are based on the concepts presented in the book "Process Mining: Data Science in Action" (2nd Edition) by Wil van der Aalst. 

The webservice is a project of the lab "Implementation of Process Mining Algorithms: Transformative Business Knowledge" at the Technical University Munich.

The folder data which contains xes-files that can be used as test inputs are owned by the Chair of Information Systems and Business Process Management at the Technical University of Munich.


