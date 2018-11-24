import networkx

import fda

# Da Vinci robotic system
regulatory_graph = networkx.DiGraph()
regulatory_graph.add_node(fda.empty)

seeds = [fda.FDAApproval("K173585"),
         fda.FDAApproval("K081113")]
for seed in seeds:
    fda.populate_predicates(regulatory_graph, seed)

for seed in seeds:
    subgraph = fda.networkx_to_graphviz(
        fda.get_subgraph(regulatory_graph, seed))
    subgraph.body = list(filter(lambda edge: "000000" not in edge,
                                subgraph.body))
    subgraph.render(seed.id)
