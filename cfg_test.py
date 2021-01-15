import argparse


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

def main():
    # get the filename from the arguments of the command line
    filename = getFilename()
    # read the description from the file
    description_dict = readDescription(filename)

    while True:
        # read the word
        word = input("Enter the word: ")




        choice = input("Do you want to check another word? y/n")
        if choice == 'n':
            break


if __name__ == "__main__":
    main()