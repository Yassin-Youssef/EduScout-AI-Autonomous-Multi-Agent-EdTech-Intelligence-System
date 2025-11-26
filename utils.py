#this is the utils file which has helper functions
from typing import List
def load_companies_from_file(path: str = "companies.txt") -> List[str]:
    # Reads a text file containing company names and returns a clean Python list.
    # Lines starting with '#' are treated as comments and ignored.
    # Empty lines are ignored.
    # Everything else is treated as a company name.

    companies: List[str] = [] #creating emptylist
    try:
        #opening the file in read mode
        with open(path, "r", encoding="utf-8") as f:
            for line in f:#read it line by line
                name = line.strip()#remove spaces at start and end
                if not name:#skip empty lines
                    continue
                if name.startswith('#'):#skip #
                    continue
                companies.append(name)
    except FileNotFoundError:
        print(f"error could not find the file: {path}")
    except Exception as e:
        print(f"error failed to read {path}: {e}")
    return companies