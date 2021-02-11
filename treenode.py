

"""
    This class is used to modelize a node of the tree.
    Every node has information on:
        - what is the expression of the node
        - which is the parent of the node
        - which rule was used to create this expression
        (using this rule on the parent's expression this child is created)

    It also has a method for visualizing the node as a string based on its expression
"""
class TreeNode:

    def __init__(self, expression, parent, rule):
        self.parent = parent
        self.rule = rule
        self.expression = expression

    def __str__(self):
        '''
        Visualized the node as a string based on its expression
        :return (str):
        '''
        return "Node: \"" + self.expression + "\""