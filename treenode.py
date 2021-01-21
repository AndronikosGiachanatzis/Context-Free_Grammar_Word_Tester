
class TreeNode:

    def __init__(self, expression, parent, rule):
        self.parent = parent
        self.rule = rule
        self.expression = expression

    def __str__(self):
        return "Node: \"" + self.expression + "\""