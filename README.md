# PRA - Pull Requests Analyzer

A simple Python script to measure how many Pull-Requests are products of merge or rebase integration methods, and thus help in understanding the software repositories on Github.

This project is under development, and may gain new features or change drastically, but trying to keep it simple

## **Requirements**

This script uses [Python 3.x](https://www.python.org/) and [Github API v3](https://developer.github.com/v3/) through the Python library [PyGithub](https://pygithub.readthedocs.io/en/latest/introduction.html). To install it use:

```$ pip install PyGithub```

Or clone it on [Github](https://github.com/PyGithub/PyGithub).

## **Usage**

It cab be used a script or as a lib in another projects. You will need use a github [personal access token](https://github.com/settings/tokens) if you want to analyze private repository that  require authentication or many repositories at once, because as the Github API imposes a lower hourly request limit without the token. (60/hour without a token and 5000/hour with a token) 

> Note: This program currently makes 6 + 2 * n requests at Github API per repository. (n = Amount closed pull-requests. And per standard, in this program there is a limit of 200 pull requests per repository.)

### **Inputting method**

Create a [CSV](https://en.wikipedia.org/wiki/Comma-separated_values) file named *repositories* and *tokens* (if you'd like use github tokens) in the project's root folder, it must be in the format below:

- **tokens.csv**
```csv
OUATH-TOKEN1
OUATH-TOKEN2
OUATH-TOKEN3
...
```

- **repositories.csv**
```csv
owner1/repo1
owner2/repo2
owner3/repo3
owner4/repo4
...
```


> Note: You can analyze different repositories from different owners simultaneously

Then run the program:

```$ python main.py```
