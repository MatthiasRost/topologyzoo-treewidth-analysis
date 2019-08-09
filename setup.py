from setuptools import setup, find_packages

install_requires = [
    # "gurobipy",  # install this manually
    "matplotlib",
    "numpy",
    "click",
    "pyyaml",
    "jsonpickle",
    "unidecode",
    "networkx",
]

setup(
    name="topologyzoo-treewidth-analysis",
    # version="0.1",
    packages=["topologyzoo_treewidth_analysis"],
    package_data={"topologyzoo_treewidth_analysis_gml": ["data/topologyZoo/*.gml"], 
		  "topologyzoo_treewidth_analysis_graphml": ["data/topologyZoo/*.graphml"]},
    install_requires=install_requires,
    entry_points={
        "console_scripts": [
            "topologyzoo-treewidth-analysis=topologyzoo_treewidth_analysis.cli:cli"
        ]
    }
)
