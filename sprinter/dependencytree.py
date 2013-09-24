"""
dependencytree.py handles the dependency tree of sprinter formulas. It attempts to validate a dependency tree
"""
from __future__ import unicode_literals


class DependencyTreeException(Exception):
    """
    Wrapper class for dependency tree exceptions
    """
    pass


class DependencyTree(object):
    """
    DependencyTree takes a dictionary of nodes and their dependencies (also need to be included in the dependencies)
    """

    order = []  # a valid ordering of the dependency tree

    def __init__(self, node_dict):
        self.order = self.__calculate_order(node_dict)

    def __calculate_order(self, node_dict):
        """
        Determine a valid ordering of the nodes in which a node is not called before all of it's dependencies.

        Raise an error if there is a cycle, or nodes are missing.
        """
        if len(node_dict.keys()) != len(set(node_dict.keys())):
            raise DependencyTreeException("Duplicate Keys Exist in node dictionary!")
        valid_order = [node for node, dependencies in node_dict.items() if len(dependencies) == 0]
        remaining_nodes = [node for node in node_dict.keys() if node not in valid_order]
        while len(remaining_nodes) > 0:
            node_added = False
            for node in remaining_nodes:
                dependencies = [d for d in node_dict[node] if d not in valid_order]
                if len(dependencies) == 0:
                    valid_order.append(node)
                    remaining_nodes.remove(node)
                    node_added = True
            if not node_added:
                # the tree must be invalid, as it was not possible to remove a node.
                # it's hard to find all the errors, so just spit out the first one you can find.
                invalid_node = remaining_nodes[0]
                invalid_dependency = node_dict[invalid_node][0]
                if invalid_dependency not in remaining_nodes:
                    raise DependencyTreeException("The dependency list for %s is missing" % invalid_dependency)
                else:
                    raise DependencyTreeException("The dependency %s is cyclic or dependent on a cyclic dependency" % invalid_dependency)
        return valid_order
