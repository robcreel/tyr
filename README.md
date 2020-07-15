# tyr

This app uses a LDA (latent Dirichlet allocation) topic model implemented in gensim to read a given text file and find other files on similar topics.  The intended use case is legal personnel hunting for cases pertinent to some presently important case file, but there are wider use cases of LDA as well.  See wikipedia for more.


## Installation
1. From console, navigate to the directory you'd like to install this tool, then run:
`git clone https://github.com/robcreel/tyr`

2. From console, run
`python munge.py <number>`
 where "number" is an optional argument specifying the max number of documents you wish to preprocess to train your model. If no argument is given, the default is to munge every document available. 
 If it's the first time running munge, it may take quite a while, since python is grabbing a bulk file, from the case law access api, decompressing it, and then reorganizing your directory structure.
3. From console, run 
`python LDA.py`

This trains the model based on the documents munged in the previous step and stores it in ROM.
4. Be sure to set the environment variable from the root directory:

`export FLASK_APP=app.py`
## Usage

1. Run the app.

`flask run`

2. Upload a text file to the website, currently located at `localhost:5000/`. The server will parse and munge up this document, maps it to LDA space, and compares the file against all documents in the database, and sends zipfile containing the most topically relevant cases right to your browser! 


## Components
* **Munge.py** preprocesses the documents into a form we can train our model on.
* **LDA.py** generates the LDA model we use to compare all documents.
* **Flask** serves the front end and houses app logic.
* **MongoDB** houses the document corpus and a lookup list of IDs and case names.



## Directory Structure

**.** 
├── **app** 
│  ├── **app** 
│  │  ├── **__pycache__** 
│  │  ├── **static** 
│  │  │  ├── **css** 
│  │  │  ├── **js** 
│  │  │  └── **text** 
│  │  │    └── **uploads** 
│  │  └── **templates** 
│  │    └── **public** 
│  │      └── **templates** 
│  └── **__pycache__** 
└── **get_served**


