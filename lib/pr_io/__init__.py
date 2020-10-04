import pandas as pd

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

def read_files(filepath: str):
    if check_csv(filepath):
        df = pd.read_csv(filepath, sep=",", encoding="UTF-8")
        return list(df[df.columns[0]])
    return []
