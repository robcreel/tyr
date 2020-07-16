# Tyr

This app uses a LDA (latent Dirichlet allocation) topic model implemented in gensim to read a given text file and find other files on similar topics.  The intended use case is legal personnel hunting for cases pertinent to some presently important case file, but there are wider use cases of LDA as well.  See wikipedia for more.

## Directory Structure
.
├── LICENSE
├── README.md
├── requirements.txt
└── **tyrapp**
    ├── config.py
    ├── run.py
    ├── setup.py
    └── **tyrapp**
        ├── archiver.py
        ├── **data**
        ├── __init__.py
        ├── LDA.py
        ├── munge.py
        ├── **static**
        │   ├── **css**
        │   │   └── style.css
        │   └── **text**
        │       └── **uploads**
        ├── **templates**
        │   └── **public**
        │       ├── index.html
        │       ├── **templates**
        │       │   └── public_template.html
        │       └── upload.html
        └── views.py


## Installation
1. From console, navigate to the directory you'd like to install this tool, then run:
`git clone https://github.com/robcreel/tyr`

2. In the console, navigate into the repo in the INNER tyrapp directory, then run
`python munge.py <number>`
 where "number" is an optional argument specifying the max number of documents you wish to preprocess to train your model. If no argument is given, the default is to munge every document available, which might overwhelm your machine. 
 If it's the first time running munge, it may take quite a while, since python is grabbing a bulk file, from the case law access api, decompressing it, and then reorganizing your directory structure.

3. In the console, while still in the inner tyrapp directory, run 
`python LDA.py <doc_num> <topic_num>`
This trains the model based on the documents munged in the previous step and stores it in ROM.
Both console arguments are optional, but they are useful if you would like to override the default training hyperparameters of the model. 

4. Be sure to set the environment variable from the root directory:
`export FLASK_APP=tyr_app`
## Usage

1. Now navigate to the OUTER tyrapp directory and run the following: 
`flask run`
Depending on the size of your corpus, this might take a little to load into memory and create the app instance. Once the app router starts listening to port, you are ready to proceed

2. Upload a text file to the website from a browser. The app is defaulted to listen at `localhost:5000/`. The server parses up this uploaded document, maps it to LDA space, and compares that transformed image against all documents in the database using a formula called the "hellinger metric". Then, depending on those comparisons, it sends the browser a zipfile containing the most topically relevant cases.


## Components
* **Munge.py** preprocesses the documents into a form we can train our model on.
* **LDA.py** generates the LDA model we use to compare all documents.
* **archiver.py** collects deliverables from the database, writes them to file, and zips them up for flask
* **Flask** serves the front end and houses app logic.
* **MongoDB** houses the document corpus and a lookup list of IDs and case names.





