from sprinter.dependencytree import DependencyTree, DependencyTreeException

LEGAL_TREE = {
    'a': ['b', 'c', 'd'],
    'd': [],
    'c': [],
    'b': ['d'],
    'e': []
}

MISSING_ENTRY_TREE = {
    'a': ['b', 'c', 'd'],
    'b': []
}

CYCLIC_TREE = {
    'a': ['b', 'c', 'd'],
    'b': [],
    'c': ['b'],
    'd': ['a']
}

LEGAL_ORDER = []


class TestDependencyTree(object):

    def test_proper_tree(self):
        """ Test whether a proper dependency tree generated the correct output. """
        dt = DependencyTree(LEGAL_TREE)
        order = dt.order
        added_elements = []
        for el in order:
            for dependency in LEGAL_TREE[el]:
                assert dependency in added_elements, \
                    "Element %s depends on %s and not added yet with order of %s!" % \
                    (el, dependency, added_elements)
            added_elements.append(el)

    def test_missing_entry_tree(self):
        """ Test if dependencytree catches a missing tree """
        try:
            DependencyTree(MISSING_ENTRY_TREE)
        except DependencyTreeException:
            return
        raise("Missing entry tree did not raise an error!")

    def test_cyclic_tree(self):
        """ Test if dependencytree catches a cycle """
        try:
            DependencyTree(CYCLIC_TREE)
        except DependencyTreeException:
            return
        raise("Cyclic tree did not raise an error!")
