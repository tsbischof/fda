import networkx

import fda

graph = networkx.DiGraph()
graph.add_node(fda.empty)

doc = fda.FDAApproval("K173585")

fda.populate_predicates(graph, doc)

subgraph = fda.networkx_to_graphviz(fda.get_subgraph(graph, doc))
subgraph.body = list(filter(lambda edge: "000000" not in edge, subgraph.body))
subgraph.render(view=True)
