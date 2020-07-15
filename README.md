# tyr

This app uses a LDA (latent Dirichlet allocation) topic model implemented in gensim to read a given text file and find other files on similar topics.  The intended use case is legal personnel hunting for cases pertinent to some presently important case file, but there are wider use cases of LDA as well.  See wikipedia for more.



## Usage

1. Be sure to set the environment variable from the root directory:

`export FLASK_APP=app.py`

1. Run the app.

`flask run`

1. Upload a text file to the website, currently located at `localhost:5000/`.  



## Components

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







## Installation

