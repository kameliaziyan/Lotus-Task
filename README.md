# Lotus 

# web application for developer burnout analysis

A full stack application that predicts burnout risk using a custom Decision Tree algorithm built entirely from scratch.

the model is trained on a dataset that captures common developer work habits, including sleep patterns, meeting load, weekend work frequency, and stress levels.
In addition to making predictions, the application visualizaes the trained decision tree through an interactive and color coded diagram, allowing users to understand exactly how decisions are made.

**NOTE:** For the backend part of this project, I used Python with FastAPI, since these are the languages I'm used to and feel most comfortable working with. I know that FastAPI can be easily connected to a frontend built with TypeScript, which made it a good choice for this full stack app. For the frontend part, I don't have as much experience, so I used AI assistance to help me. At first, the AI helped me understand some of the basic concepts, and then it also helped me implement the frontend according to my requests and requirements.


# Development Approach

This project was developed using software engineering practices learned during a Backend Development Bootcamp, with a strong focus on:

**clean code priniples**<br>
**layered architecture**<br>
**separation of concerns**<br>
**maintainability and testability**<br>

I used some of what i learned in the bootcamp, like the configuration and tooling files listed below:

**requirements.txt**<br>
**lint.sh**<br>
**setup.cfg**<br>
**.gitignore**<br>


# Architecture 

I used a this layered structure because each layer is responsible for a single concern and only interacts with the layer directly below it.

Services Layer - Contains the core Decision Tree algorithm and business logic.

API Layer - Acts as a lightweight translator between HTTP requests and the algorithm.

Repository Layer - Handles persistence and loading of the trained model from disk.

This way, if we need to make changes in the future, it's easy to find exactly where to make them we don't need to touch the rest of the code.

Also This separation ensures that each component can be tested.


# How the Algorithm works 

**entropy.py**

This file calculates Entropy and Information Gain. It measures how impure(mixed) the dataset is, calculates how much that impuritly drops after a split, and provides the scoring mechanism used when deciding which split is best.

**split_finder.py**

This file searches for the best possible across every available feature It evaluates each candidate feature one by one, tests every possible split point for that feature, calculates the Information Gain for each candidate, and finally returns the feature and threshold that scored highest.


**tree_builder.py**

This file builds the decision tree recursively. At each node, it finds the best split, then creates the child nodes by calling itself again on each branch. When a stopping condition is met, it creates a lleaf node insted. It also provides the prediction functiuon used to traverse a finished tree for new inputs, and calculates tree statistics like depth and leaf count. The recursion stops when the node becomes pure, the maximum depth is reached, too few samples remain, or no split improves the Information Gain. 



# Running locally

Two terminals are requires 

**(for mac)**

**Backend**

cd task
source ./venv/bin/activate
pip install -r requirements.txt
python3 -m backend.app

The API will run at:

http://127.0.0.1:5001

Interactive API documentation:

http://127.0.0.1:5001/docs

**frontend**

cd task/frontend

npm install

npm run dev

Open:

http://localhost:5173

in your browser.




# Error Handling

The app validates input and handles errors on both ends: the backend returns structured JSON errors with proper HTTP status codes (400/404/500) and uses Pydantic to reject bad data before it reaches the algorithm, while the frontend shows inline validation messages and disables the Predict button until all inputs are valid.

# AI Usage


During the planning phase of the project, I used AI to better understand the concepts behind Decision Trees, including entropy, information gain, split selection, and recursive tree construction. The goal was to strengthen my understanding of the algorithm before implementing it from scratch.

AI was also used while creating the dataset. It helped generate ideas for realistic developer-related features and sample scenarios, which I later reviewed and adjusted manually to better fit the project's goals.

Throughout development, AI served as a debugging assistant. When I encountered errors or unexpected behavior, I used it to analyze error messages, explore possible causes, and consider different approaches to solving the issue.

During frontend development, AI provided guidance on React, TypeScript, form validation, and component structure. I have primarily worked on backend development and had very limited experience with frontend work, so AI helped me better understand how things work on the frontend and assisted in translating my ideas and requirements into TypeScript with clearer understanding.

For the user interface, AI was used to brainstorm design ideas, layouts, and styling improvements. These suggestions helped create a cleaner and more user-friendly experience.

AI also assisted in generating test ideas and identifying edge cases that were worth validating. This helped improve the overall quality and reliability of the application.
In addition, I asked the AI to review and fix my comments, to make sure they are clear and easy to understand for anyone who goes through the code.







