from tabulate import tabulate

# Function to perform the CYK Algorithm and print tables for each substring length with applied rules
def cykParse(w):
    n = len(w)
    applied_rules = []  # List to store applied rules
    
    # Initialize the table as a 2D list of sets
    T = [[set() for _ in range(n)] for _ in range(n)]

    # Filling in the table for length 1 substrings
    for j in range(n):
        for lhs, rule in R.items():
            for rhs in rule:
                # If a terminal is found, place it in the table
                if len(rhs) == 1 and rhs[0] == w[j]:
                    T[j][j].add(lhs)
                    applied_rules.append(f"Applied Rule: {lhs}[{j+1},{j+1}] --> {rhs[0]}")

    # Print table for length 1 substrings
    print("\nCYK Table for substrings of length 1:")
    printTable(T, w)

    # Filling the table for substrings of length 2 and more
    for length in range(2, n + 1):  # Length of substring
        for i in range(n - length + 1):  # Start index of substring
            j = i + length - 1  # End index of substring
            for k in range(i, j):  # Partition index
                for lhs, rule in R.items():
                    for rhs in rule:
                        # Check if the rule applies by combining symbols
                        if len(rhs) == 2 and rhs[0] in T[i][k] and rhs[1] in T[k + 1][j]:
                            T[i][j].add(lhs)
                            applied_rules.append(
                                f"Applied Rule: {lhs}[{i+1},{j+1}] --> {rhs[0]}[{i+1},{k+1}] {rhs[1]}[{k+2},{j+1}]"
                            )
        
        # Print the table for the current substring length
        print(f"\nCYK Table for substrings of length {length}:")
        printTable(T, w)

    # Print all applied rules
    print("\nApplied Rules:")
    for rule in applied_rules:
        print(rule)

    # Final result based on whether the start symbol S is in the last cell
    if len(T[0][n-1]) != 0:
        print("Accepted")
    else:
        print("Rejected")

# Helper function to print the CYK table using tabulate
def printTable(T, w):
    n = len(w)
    headers = [""] + w  # Create headers with input symbols
    table = []

    for i in range(n):
        row = [w[i]]  # Row header with input symbol
        for j in range(n):
            # Fill cell content with parsed non-terminals or empty braces for lower triangle
            cell_content = "{" + ", ".join(T[i][j]) + "}" if T[i][j] else "{}"
            row.append(cell_content)
        table.append(row)

    print(tabulate(table, headers=headers, tablefmt="fancy_grid"))

# Non-terminal symbols
non_terminals = ["S", "A", "B", "C", "D"]

# Terminal symbols
terminals = ["a", "b"]

# Grammar rules
R = {
    "S": [["D", "S"], ["B", "A"], ["a"]],
    "A": [["B", "C"]],
    "B": [["a"]],
    "C": [["D", "A"], ["a"], ["b"]],
    "D": [["b"]]
}
# # Non-terminal symbols
# non_terminals = ["NP", "Nom", "Det", "AP", 
#                   "Adv", "A"]
# terminals = ["book", "orange", "man", 
#              "tall", "heavy", 
#              "very", "muscular"]
 
# # Rules of the grammar
# R = {
#      "NP": [["Det", "Nom"]],
#      "Nom": [["AP", "Nom"], ["book"], 
#              ["orange"], ["man"]],
#      "AP": [["Adv", "A"], ["heavy"], 
#             ["orange"], ["tall"]],
#      "Det": [["a"]],
#      "Adv": [["very"], ["extremely"]],
#      "A": [["heavy"], ["orange"], ["tall"], 
#            ["muscular"]]
#     }

# Input string
print("Masukkan string (pisahkan setiap karakter dengan spasi):")
w = input().split()

# Function Call
cykParse(w)
