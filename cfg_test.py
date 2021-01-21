import argparse
import treenode

# suppose that the empty word is denoted by the character @. That character cannot belong to any of the symbols set
# in the grammar
EMPTY_WORD = "@"

def getFilename():
    parser = argparse.ArgumentParser(description="A program that checks whether a word belongs to a language of a "
                                                 "context-free grammar.",
                                     usage="python3  assignment2.py -f <description-file.txt>")

    parser.add_argument("-f", help="The file containing the description of the grammar.",
                        dest="file")

    args = parser.parse_args()
    return args.file


def readDescription(filename):
    # the dictionary storing the description of the grammar
    description = dict()
    # try to open the file given in the command line
    try:
        file = open(filename)
    except FileNotFoundError:
        print("[-] File does't exist. Check the name of the file. Exiting.")
        return (1)

    description["terminal_num"] = int(file.readline().replace("\n", ""))
    description["terminals"] = list(file.readline().replace("\n", ""))
    description["nonterminal_num"] = int(file.readline().replace("\n", ""))
    description["nonterminals"] = list(file.readline().replace("\n", ""))
    description["initial"] = file.readline().replace("\n", "")
    description["rules_num"] = int(file.readline().replace("\n", ""))

    # a dictionary containing the rules (a list), grouped by the left part of the rule
    description["rules"] = dict()
    for i in range(description["rules_num"]):
        rule = file.readline().replace("\n", "")
        rule = rule.split()
        left = rule[0]
        right = rule[1]
        if left not in description["rules"].keys():
            description["rules"][left] = list()
        description["rules"][left].append(right)

    file.close()
    return description


def initializeTree(initial_symbol):

    root = treenode.TreeNode(initial_symbol, None, None)
    return [root]


def createChild(expression, rule, parent):

    return treenode.TreeNode(expression, parent, rule)


def findChildren(node, description_dict):
    children = list()
    for c in node.expression:
        if c in description_dict["nonterminals"]:
            for r in description_dict["rules"][c]:
                expression = node.expression
                if r == "@":
                    expression = expression.replace(c, "")
                else:
                    expression = expression.replace(c, r)
                rule = f"{c} {r}"
                child = createChild(expression, rule, node)
                children.append(child)
    return children


def isSolution(node, word):
    return node.expression == word


def search(word, frontier, description_dict):

    nodes = dict()

    # while the frontier is not empty continue searching
    # if the word is proved not to be valid then a break will occur
    while frontier is not []:

        node = frontier[0]
        nodes[node.expression] = node
        if isSolution(node, word):
            return True
        children = findChildren(node, description_dict)
        frontier.pop(0)
        for child in children:
            if child.expression not in nodes.keys():
                frontier.append(child)
                nodes[child.expression] = child



def main():
    # get the filename from the arguments of the command line
    filename = getFilename()
    # read the description from the file
    description_dict = readDescription(filename)

    if description_dict == 1:
        return

    while True:
        # read the word
        word = input("Enter the word: ")

        # initialize the search. Create the root node
        frontier = None
        frontier = initializeTree(description_dict["initial"])

        result = search(word, frontier, description_dict)

        if result:
            print("[+] The word is valid!")
        else:
            print("[+] The word is not valid!")

        choice = input("Do you want to check another word? y/n")
        if choice == 'n':
            break


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        exit(1)