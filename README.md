[generator]: images/generator.png "Generator Example"
[community]: images/community.png "Community Detection"
[dc]: images/dc.png "Degree Centrality"
[cc]: images/cc.png "Closeness Centrality"
[bc]: images/bc.png "Betweenness Centrality"
[ec]: images/ec.png "Eigenvector Centrality"
[ul1]: images/ul1.png "User Level 1"
[ul2]: images/ul2.png "User Level 2"
[ulr1]: images/ulr1.png "User Level with Ranges 1"
[ulr2]: images/ulr2.png "User Level with Ranges 2"
[cl1]: images/cl1.png "City Level 1"
[cl2]: images/cl2.png "City Level 2"
[cl3]: images/cl3.png "City Level 3"

# Network Analyst and Simulator Online

This repository is the online version of network analyst and simulator from the original desktop one to achieve fundamental network analysis and simulation functions.

## Features

* Multiple generators for networks
* Centrality computation and statistics
* Community detection
* Information spreading simultions graphically and geographically

## Prerequisites

* [Python 2.7.x]()
* [NumPy]()
* [Flask]()
* [MongoDB 3.6+]()
* [PyMongo]()
* [SNAP]()

## Quick Start

**1. Add *FLASK_APP* environment for the project.**

For Linux or Mac OS:

```
export FLASK_APP=simulator/app.py
```

For WIndows Command Prompt:

```
set FLASK_APP="simulator/app.py"
```

For WIndows PowerShell:

```
set $env:FLASK_APP = "simulator/app.py"
```

**2. Start the project.**

```
flask run

# or

python -m flask run
```

## Screenshots

![Generator Example][generator]

![Degree Centrality][dc]

![Closeness Centrality][cc]

![Betweenness Centrality][bc]

![Eigenvector Centrality][ec]

![Community Detection][community]

![User Level 1][ul1]

![User Level 2][ul2]

![User Level with Ranges 1][ulr1]

![User Level with Ranges 2][ulr2]

![City Level 1][cl1]

![City Level 2][cl2]

![City Level 3][cl3]
