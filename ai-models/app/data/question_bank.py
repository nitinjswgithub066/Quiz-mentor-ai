"""
question_bank.py
-----------------
Hardcoded MCQ bank for the first "real content" test. 30 beginner
questions, 5 each across python/java/c/html/css/javascript.

This stands in for AI-generated questions for now. Once the LLM +
RAG pieces are built, generated questions should be stored in the
`questions` SQLite table in this same shape (language, difficulty,
question, options, correct_index) so the delivery/scoring code below
doesn't need to change.
"""

QUESTIONS = [
    # --- python ---
    {"id": 1, "language": "python", "difficulty": 1,
     "question": "What does len([1, 2, 3]) return?",
     "options": ["2", "3", "4", "Error"], "correct_index": 1},
    {"id": 2, "language": "python", "difficulty": 1,
     "question": "Which keyword defines a function in Python?",
     "options": ["def", "function", "func", "lambda"], "correct_index": 0},
    {"id": 3, "language": "python", "difficulty": 1,
     "question": "What is the output of print(2 ** 3)?",
     "options": ["6", "8", "9", "5"], "correct_index": 1},
    {"id": 4, "language": "python", "difficulty": 1,
     "question": "Which of these data types is immutable in Python?",
     "options": ["list", "dict", "tuple", "set"], "correct_index": 2},
    {"id": 5, "language": "python", "difficulty": 1,
     "question": "How do you start a single-line comment in Python?",
     "options": ["//", "#", "/* */", "--"], "correct_index": 1},

    # --- java ---
    {"id": 6, "language": "java", "difficulty": 1,
     "question": "Which keyword is used to create a class in Java?",
     "options": ["class", "Class", "struct", "define"], "correct_index": 0},
    {"id": 7, "language": "java", "difficulty": 1,
     "question": "What is the entry point method of a Java application?",
     "options": ["start()", "main()", "run()", "init()"], "correct_index": 1},
    {"id": 8, "language": "java", "difficulty": 1,
     "question": "Which of these is a valid Java primitive type?",
     "options": ["string", "Integer", "int", "bool"], "correct_index": 2},
    {"id": 9, "language": "java", "difficulty": 1,
     "question": "What symbol ends most statements in Java?",
     "options": [":", ";", ".", ","], "correct_index": 1},
    {"id": 10, "language": "java", "difficulty": 1,
     "question": "Which keyword is used for a class to inherit another class in Java?",
     "options": ["implements", "extends", "inherits", "super"], "correct_index": 1},

    # --- c ---
    {"id": 11, "language": "c", "difficulty": 1,
     "question": "Which function is used to print output in C?",
     "options": ["echo()", "print()", "printf()", "console.log()"], "correct_index": 2},
    {"id": 12, "language": "c", "difficulty": 1,
     "question": "Which header file is needed to use printf in C?",
     "options": ["<stdlib.h>", "<stdio.h>", "<string.h>", "<math.h>"], "correct_index": 1},
    {"id": 13, "language": "c", "difficulty": 1,
     "question": "How do you correctly declare an integer variable in C?",
     "options": ["int x;", "var x;", "let x;", "x = int;"], "correct_index": 0},
    {"id": 14, "language": "c", "difficulty": 1,
     "question": "Which symbol starts a single-line comment in C?",
     "options": ["#", "//", "--", "'"], "correct_index": 1},
    {"id": 15, "language": "c", "difficulty": 1,
     "question": "What does sizeof(int) typically return (in bytes) on most systems?",
     "options": ["2", "4", "8", "1"], "correct_index": 1},

    # --- html ---
    {"id": 16, "language": "html", "difficulty": 1,
     "question": "Which tag is used to create a hyperlink in HTML?",
     "options": ["<link>", "<a>", "<href>", "<url>"], "correct_index": 1},
    {"id": 17, "language": "html", "difficulty": 1,
     "question": "What does HTML stand for?",
     "options": ["Hyper Trainer Marking Language", "HyperText Markup Language",
                 "Hyperlinks Text Mark Language", "Home Tool Markup Language"],
     "correct_index": 1},
    {"id": 18, "language": "html", "difficulty": 1,
     "question": "Which tag is used for the largest heading?",
     "options": ["<h6>", "<heading>", "<h1>", "<head>"], "correct_index": 2},
    {"id": 19, "language": "html", "difficulty": 1,
     "question": "Which attribute specifies an image's source?",
     "options": ["src", "href", "alt", "link"], "correct_index": 0},
    {"id": 20, "language": "html", "difficulty": 1,
     "question": "Which tag defines an unordered (bulleted) list?",
     "options": ["<ol>", "<ul>", "<list>", "<li>"], "correct_index": 1},

    # --- css ---
    {"id": 21, "language": "css", "difficulty": 1,
     "question": "Which property changes text color in CSS?",
     "options": ["font-color", "text-color", "color", "fgcolor"], "correct_index": 2},
    {"id": 22, "language": "css", "difficulty": 1,
     "question": "How do you select an element by its class in CSS?",
     "options": ["#name", ".name", "*name", "name"], "correct_index": 1},
    {"id": 23, "language": "css", "difficulty": 1,
     "question": "Which property controls spacing OUTSIDE an element's border?",
     "options": ["padding", "margin", "spacing", "border-space"], "correct_index": 1},
    {"id": 24, "language": "css", "difficulty": 1,
     "question": "Which property makes text bold in CSS?",
     "options": ["font-weight", "text-style", "font-bold", "bold"], "correct_index": 0},
    {"id": 25, "language": "css", "difficulty": 1,
     "question": "What does display: none; do to an element?",
     "options": ["Hides it but keeps its space", "Removes it from the layout entirely",
                 "Makes it transparent", "Makes it unclickable"],
     "correct_index": 1},

    # --- javascript ---
    {"id": 26, "language": "javascript", "difficulty": 1,
     "question": "Which keyword is the modern way to declare a reassignable variable?",
     "options": ["const", "let", "final", "static"], "correct_index": 1},
    {"id": 27, "language": "javascript", "difficulty": 1,
     "question": "What does === check in JavaScript?",
     "options": ["Value only", "Type only", "Value and type", "Reference only"],
     "correct_index": 2},
    {"id": 28, "language": "javascript", "difficulty": 1,
     "question": "Which array method adds an element to the end of an array?",
     "options": ["push()", "pop()", "shift()", "unshift()"], "correct_index": 0},
    {"id": 29, "language": "javascript", "difficulty": 1,
     "question": "What is the correct way to declare a function in JavaScript?",
     "options": ["function myFunc()", "function:myFunc()", "def myFunc()", "func myFunc()"],
     "correct_index": 0},
    {"id": 30, "language": "javascript", "difficulty": 1,
     "question": "Which symbol starts a single-line comment in JavaScript?",
     "options": ["#", "//", "<!-- -->", "'"], "correct_index": 1},
]