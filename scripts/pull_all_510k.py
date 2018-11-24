import networkx

import fda

db_510k = fda.db.get_510k_db()

regulatory_graph = networkx.DiGraph()
regulatory_graph.add_node(fda.empty)

for index, k_number in enumerate(sorted(db_510k["KNUMBER"].unique())):
    if index % 10000 == 0:
        print(index, k_number)
    fda.populate_predicates(regulatory_graph, fda.FDAApproval(k_number))
