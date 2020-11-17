import pandas as pd
from requests import get
from io import StringIO
from urllib.error import HTTPError
from simplejson import dumps

def get_pulls(fullname: str, tokens: list = None):
    """[summary]

    Args:
        fullname (str): Repository full name in form 
        token (list[str] or None, optional): [description]. Defaults to None.

    Returns:
        DataFrame: [description]
    """
    url = f"https://api.github.com/repos/{fullname}/pulls?state=closed"
    if tokens:
        headers = {'Authorization': f'token {tokens[0]}'}
    else:
        headers = None
    try:
        req = get(url=url, headers=headers)
        json = dumps(req, ignore_nan=True)
        buffer = StringIO(json)
        df = pd.read_json(buffer)
        return df
    except HTTPError:
        if tokens:
            get_pulls(fullname, tokens[1:])
        else:
            return None
    except Exception as error:
        print(error)
        return None


def filter_pulls(pulls: pd.DataFrame):
    pass


def check_csv(filepath: str):
    try:
        f = open(filepath, 'r', encoding='UTF-8', newline='')
        f.close()
    except FileNotFoundError:
        try:
            f = open(filepath, 'w+', encoding='UTF-8', newline='')
            f.close()
        except:
            print('Could not open or create the file')
            return False
    return True


def read_input(filepath: str):
    if check_csv(filepath):
        df = pd.read_csv(filepath, sep=",", encoding="UTF-8")
        return list(df[df.columns[0]])
    return []


def main():
    # Misc
    dict_count = lambda value, dictionaries: sum([list(d.values()).count(value) for d in dictionaries])

    # Inputing
    tokens = read_input("tokens.csv")
    repositories_full_names = read_input("repositories.csv")  # Repositories full name: "owner/repo"

    # 
    for full_name in repositories_full_names:
        # Getting Pulls
        pulls = get_pulls(full_name, tokens)
        
        
        pass


if __name__ == "__main__":
    main()