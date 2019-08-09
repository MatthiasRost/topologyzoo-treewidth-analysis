
# Overview

The **topologyzoo-treewidth-analysis** provides basic **Python 3.6** functionality for analyzing the treewidth of the graph stored in the **[Topology Zoo](http://www.topology-zoo.org/)**. Within this repository, you can find the results of the analysis in the **[output](output)** directory together with its log in the **[log](log)** directory.

Note that most of the source code of this repository stems from our **[vnep-approx Github](https://github.com/vnep-approx)** repositories.

# Dependencies and Requirements

This library was written for **Python3.6** and requires the libraries stated in **[setup.py](setup.py)**. 

For re-computing the treeewidths, you need to install Tamaki's algorithm for computing tree decompositions.
The algorithm was presented in the [paper at ESA 2017](http://drops.dagstuhl.de/opus/volltexte/2017/7880/pdf/LIPIcs-ESA-2017-68.pdf) and computes optimal tree decompositions (efficiently). The corresponding GitHub repository [TCS-Meiji/PACE2017-TrackA](https://github.com/TCS-Meiji/PACE2017-TrackA) must be cloned locally and the environment variable **PACE_TD_ALGORITHM_PATH** must be set to point the location of the repository: PACE_TD_ALGORITHM_PATH="$PATH_TO_PACE/PACE2017-TrackA".
 
 Furthermore, for recomputing the treewdiths, the environment variable **EXPERIMENT_HOME** should be set to a path,
such that the subfolders output/ and log/ exist. If this variable is not set, the first folder having both subfolders is chosen to store the log and the output.

**Note**: Our source was only tested on Linux (specifically Ubuntu 16.04).  

# Installation

To install **topologyzoo-treewidth-analysis**, we provide a setup script. Simply execute from within alib's root directory: 

```
pip install .
```

Furthermore, if the code base will be edited by you, we propose to install it as editable:
```
pip install -e .
```
When choosing this option, sources are not copied during the installation but the local sources are used: changes to
the sources are directly reflected in the installed package.

We generally propose to install **topologyzoo-treewidth-analysis** into a virtual environment.

# Usage

You may either use our code via our API by importing the library or via our command line interface:

```
python -m topologyzoo_treewidth_analysis.cli

Usage: cli.py [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  compute-topologyzoo-treewidths
```

# Contact

If you have any questions, simply write a mail to mrost(AT)inet.tu-berlin(DOT)de.