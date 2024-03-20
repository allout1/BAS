"""In this code
we are taking the book name as the input
then converting it into the form of .*W1.*W2 where
.* is any sequence if letters
and W1, W2 are words of the string book name
LIMITATIONS
If there is any spelling mistake then it will return a wrong result
CONDITIONS
Remeber that all the input into the database should be in LOWERCASE
    """
import re
import string
books = [
    "Structures: Or Why Things Don't Fall Down by J.E. Gordon",
    "The Design of Everyday Things by Donald A. Norman",
    "To Engineer Is Human: The Role of Failure in Successful Design by Henry Petroski",
    "Design Patterns: Elements of Reusable Object-Oriented Software by Erich Gamma et al.",
    "Stuff Matters: Exploring the Marvelous Materials That Shape Our Man-Made World by Mark Miodownik",

    # Mechanics & Materials:
    "Mechanics of Materials by Ferdinand Beer and E. Russell Johnston Jr.",
    "Mechanical Engineering Design by Joseph Shigley",
    "Materials Science and Engineering: An Introduction by William D. Callister Jr.",
    "Strength of Materials by Andrew Pytel and Ferdinand Beer",
    "Machine Design: An Integrated Approach by Robert Norton",

    # Electrical & Computer Engineering:
    "The Art of Electronics by Paul Horowitz and Winfield Hill",
    "Digital Design: An Introduction by Frank Vahid",
    "Computer Architecture: A Quantitative Approach by John Hennessy and David Patterson",
    "Signals and Systems by Alan Oppenheim",
    "Electromagnetics for Engineers and Technologists by Steven Cumings",

    # Civil Engineering:
    "Steel Design for Buildings by Thomas Salmon",
    "Reinforced Concrete Design by Edward Nawy",
    "Prestressed Concrete Design by M. Prestressed Concrete Institute",
    "Surveying: Principles and Applications by Barry Kavanagh",
    "Environmental Engineering by Howard Peavy",

    # Chemical Engineering:
    "Elements of Chemical Reaction Engineering by Octave Levenspiel",
    "Introduction to Chemical Engineering Thermodynamics by J. M. Smith",
    "Unit Operations of Chemical Engineering by Warren McCabe et al.",
    "Perry's Chemical Engineers' Handbook (Ed. 9)",
    "Separation Process Engineering by Ernest J. Henley",

    # Other Engineering Disciplines:
    "Feynman Lectures on Physics by Richard Feynman",
    "Engineering Mechanics: Statics and Dynamics by Ferdinand Beer",
    "Introduction to Aerospace Engineering by David Anderson and John Moore",
    "Fundamentals of Nuclear Reactor Physics by Elmer E. Lewis",
    "Software Engineering: A Practitioner's Approach by Roger Pressman",

    # Engineering History & Biographies:
    "Skunk Works: A History of Lockheed Martin by Ben Rich",
    "Elon Musk: Tesla, SpaceX, and the Quest for a Fantastic Future by Ashlee Vance",
    "Surely You're Joking, Mr. Feynman! by Richard P. Feynman",
    "Chief Engineer: Washington Roebling, The Man Who Built the Brooklyn Bridge by Erica Wagner",
    "The Innovators: How a Group of Hackers, Geniuses, and Misfits Pioneered the Digital Revolution by Walter Isaacson",

    # Additional Resources (Consider consulting these for further exploration):
    # * Online resources: Goodreads lists, engineering university libraries' recommended readings.
    # * Specific engineering disciplines: Search for books relevant to your area of interest.
    # * Award-winning books: Look for titles recognized by engineering organizations or publications.
]

book_name = input("enter the name of the book\n")
book_name.lower()
book_name = book_name.split(" ")
y = ".*"
for i in book_name:
    y += (i+  ".*")
result = list()
for i in books:
    if(re.search(y,i)):
        result.append(i)
print(result)
