# processmining_lab

Process Mining Webservice (Alpha and Heuristic Miner Implementation)

This webservice is implemented in Python and Flask.

# Dependencies
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
The process mining algorithms are based on the book: Process Mining by Wil van der Aalst (second edition). 
The webservice is a project of the lab "Implementation of Process Mining Algorithms: Transformative Business Knowledge" at the Technical University Munich.


