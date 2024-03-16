"""In this code
we are taking the author name as the input
then converting it into the form of .*A1.*A2 where
.* is any sequence if letters
and A1, A2 are letters of the string author
LIMITATIONS
If there is any spelling mistake then it will return a wrong result
CONDITIONS
Remeber that all the input into the database should be in LOWERCASE
    """
import re
import string
indian_authors = [
    "rabindranath tagore",
    "r.k. Narayan",
    "salman rushdie",
    "arundhati roy",
    "amitav ghosh",
    "khushwant singh",
    "vikram seth",
    "a.p. j. abdul kalam",
    "chetan bhagat",
    "ruskin bond"
]
author_name = input("enter the name of the author\n")
author_name.lower()
y = ".*"
result = list()
for i in author_name:
    y += (i+  ".*")
for i in indian_authors:
    if(re.search(y,i)):
        result.append(i)
print(result)
