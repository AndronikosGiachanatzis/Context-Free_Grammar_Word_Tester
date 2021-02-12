"""
Author: Andronikos Giachanatzis Grammatikopoulos

Description: Developed as an assignment during my fourth year in the University of Macedonia. This module is the main
            execution point of the program. Given a context-free grammar (inside a file in specific format) it searches
            whether a given word can be derived from that grammar.

Usage: Prepare a file that follows the template in the file: 'descriprion_template.txt'. This file must contain the
    description of a context-free grammar. Note that the Empty Word is identified by the character '@'. After you
    prepare this file execute the cfg_test.py file using the -f flag followed by the name of the file containing the
    description of the automaton as such: 'python3 cfg_test.py -f grammar_description.txt'.
    Afterwards you will be prompted to enter the word which you want to check if it can be derived from the grammar of
    the file passed as an argument. After you press Enter the result will be printed.
    After you see the result you will be prompted to state whether you want to check another word. If you want to quit
    answer with the character 'n' and if you want to continue press any other key.
"""


import argparse
import treenode
import re

# suppose that the empty word is denoted by the character @. That character cannot belong to any of the symbols set
# in the grammar
EMPTY_WORD = "@"


def getFilename():
    '''
    Creates a command line argument parser and retrieves the filename passed as an argument
    :return (str): The name of the file of the description of the grammar
    '''
    parser = argparse.ArgumentParser(description="A program that checks whether a word belongs to a language of a "
                                                 "context-free grammar.",
                                     usage="python3  assignment2.py -f <description-file.txt>")

    parser.add_argument("-f", help="The file containing the description of the grammar.",
                        dest="file")

    args = parser.parse_args()
    return args.file


def readDescription(filename):
    '''
    Reads the description of the grammar from a file
    :param filename (str): The name of the file which contains the description of the grammar
    :return (dict): The description of the grammar
    '''
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
    '''
    Creates the root node of the tree
    :param initial_symbol (str): The initial symbol of the grammar
    :return (list): A list with a single element, the root of the tree
    '''

    root = treenode.TreeNode(initial_symbol, None, None)
    return [root]


def createChild(expression, rule, parent):
    '''
    Creates the child of a node based on a given
    :param expression (str): The expression of the child
    :param rule (str): The rule which was used to create the child's expression from its father's expression
    :param parent (treenode): The parent of the child node
    :return (treenode): The new child node
    '''

    return treenode.TreeNode(expression, parent, rule)


def findChildren(node, description_dict):
    '''
    Creates all the children that can be created from a given node's expression using the rules of the grammar
    :param node (treenode): The parent node
    :param description_dict (dict): The description of the grammar
    :return (list): A list containing all the node's children
    '''
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
    '''
    Checks if a given node's expression is the target word
    :param node (treenode): The node of which the expression is compared to the target node
    :param word (str): the target node
    :return (bool): True if the node's expression is the target node / False, otherwise
    '''
    return node.expression == word


def getSolution(node):
    '''
    Follows the branches of the tree from the child-solution up to the the root of the tree to map the way that the
    target word was created
    :param node (treenode):
    :return (list): The sequence of replacements using the rules of the grammar that leads to the target word
    '''
    solution_path = [node.expression]
    curr_node = node.parent

    # follow the branches from the child to the root
    while curr_node is not None:
        # add the current expression to the solution path
        solution_path.append(curr_node.expression)
        # move to the parent of the current node
        curr_node = curr_node.parent

    solution_path.reverse()
    return solution_path


def getRegex(expression, terminals, nonterminals, initial):
    '''
    Creates a regular expression string given an incomplete expression, that is an expression that does not contain only
    terminal letters but some non-terminal as well
    :param expression (str): The incomplete expression from which a regex will be created
    :param terminals (list): The terminal letters of the grammar
    :param nonterminals (list): The non-terminal letters of the grammar
    :param initial (str): The initial letter of the grammar

    :return:
    '''

    regex = expression
    if len(expression) > 0:
        # if the first letter is a terminal letter then the regex must take into consideration that the word should begin
        # with those letters
        if expression[0] in terminals:
            regex = "^" + expression

        # if the last letter is a terminal letter then the regex must take into consideration that the word should end
        # with those letters
        if expression[-1] in terminals:
            regex = regex + "$"

        for c in nonterminals:
            regex = regex.replace(c, ".*")

        regex.replace(initial, ".*")

    return regex


def prune(node, word, description_dict, nodes):
    '''
    Checks whether a given node needs to be pruned by checking if the node's expression satisfies certain criteria.
    A node will be pruned (will not be analyzed further if):
        - The node's expression is the same with an expression from another node already present in the tree
        - The potential length of the expression exceeds the length of the target word
    :param node (treenode): The node to be pruned
    :param word (str): The target word
    :param description_dict (dict): The description of the grammar
    :param nodes (list): The nodes of the tree
    :return (bool): True if the node has to be pruned / False, otherwise
    '''
    # count occurrences of not-terminal symbols
    empty_rules = 0
    for c in node.expression:
        if c.isupper():
            if EMPTY_WORD in description_dict["rules"][c]:
                empty_rules += 1

    # create the regular expression
    regex = getRegex(node.expression, description_dict["terminals"], description_dict["nonterminals"], description_dict["initial"])
    # search if the expression so far can match the word using the regex
    result = re.search(rf"{regex}", word)

    # if the expression does not belong already to the treee and if the word can be derived somehow from the expression
    # the node must not be pruned
    if node.expression not in nodes.keys() and result is not None:
        return False
    else: # one of the above criteria is not satisfied so the node must be pruned
        return True


def search(word, frontier, description_dict):
    '''
    Searches whether a word can be derived from a certain context-free grammar
    :param word (str): The target word
    :param frontier (list): The search frontier
    :param description_dict (dict): The description of the grammar
    :return (list): The first element of the list is a bool stating whether the word is valid or not (True or False
                    respectively. The second element is either a string containing the replacement sequence that leads
                    to the valid word or None if the word isn't valid
    '''

    nodes = dict()

    # while the frontier is not empty continue searching
    # if the word is proved not to be valid then a break will occur
    while frontier:
        # handle the first element of the frontier
        node = frontier[0]
        nodes[node.expression] = node

        # check if the current node is a solution
        if isSolution(node, word):
            return [True, getSolution(node)]

        # find all the children of the current node
        children = findChildren(node, description_dict)
        # remove it from the search frontier
        frontier.pop(0)
        # add only the useful children to the tree
        for child in children:
            # add the child to the tree and the frontier only if it doesn't need to be pruned
            if not prune(child, word, description_dict, nodes):
                frontier.append(child)
                nodes[child.expression] = child

    # if this point is reached that means that the word is not valid
    return [False, None]


def main():
    '''
    The main execution point of the program. Reads the filename from the command line, prompts the user iteratively
    to enter a word and checks if the word can be derived from the grammar in the description file. Finally, it
    prints to the user the result of the search.
    :return (None):
    '''
    # get the filename from the arguments of the command line
    filename = getFilename()
    # read the description from the file
    description_dict = readDescription(filename)

    # if there was some error while reading the description file
    if description_dict == 1:
        return

    # search until the user doesn't want to search another word
    while True:
        # read the word
        word = input("Enter the word: ")

        # initialize the search. Create the root node
        frontier = None
        frontier = initializeTree(description_dict["initial"])

        # start searching
        result = search(word, frontier, description_dict)

        # print the result of the search
        if result[0]:
            print("[+] The word IS valid!")
            print(f"\tProduction of the word: {' -> '.join(result[1])}")
        else:
            print("[+] The word is NOT valid!")

        choice = input("\nDo you want to check another word? y/n: ")
        if choice == 'n':
            break

    return


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Keyboard Interrupt detected. Exiting.")
        exit(1)
