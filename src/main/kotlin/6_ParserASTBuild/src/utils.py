from graphviz import Digraph
from ast_definitions import ASTNode


def render_ast(node: ASTNode, graph=None, parent_id=None) -> Digraph:
    """
    Render the AST into a Graphviz Digraph for visualization.
    """
    if graph is None:
        graph = Digraph()
    node_id = str(id(node))
    label = f"{node.token_type.name}\n{node.value or ''}"
    graph.node(node_id, label=label)
    if parent_id:
        graph.edge(parent_id, node_id)
    for child in node.children:
        render_ast(child, graph, node_id)
    return graph