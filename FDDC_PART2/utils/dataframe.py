import re


def loop(dataframe, call):
    rows = dataframe.shape[0]
    cols = dataframe.shape[1]
    for row in range(rows):
        for col in range(cols):
            cell = dataframe[col][row]
            call(cell)


def locate(dataframe, val):
    rows = dataframe.shape[0]
    cols = dataframe.shape[1]
    head = None
    for row in range(rows):
        for col in range(cols):
            cell = dataframe[col][row]
            if cell == val:
                head = dataframe[col][0]
                left = dataframe[0][row]
                break
    return head


def locateAll(dataframe, val):
    rows = dataframe.shape[0]
    cols = dataframe.shape[1]
    triggers = []
    for row in range(rows):
        for col in range(cols):
            cell = dataframe[col][row]
            if cell == val:
                top = re.sub('\s+', '', str(dataframe[col][row - 1])) if row - 1 >= 0 else ''
                left = re.sub('\s+', '', str(dataframe[col - 1][row])) if col - 1 >= 0 else ''
                top_0 = re.sub('\s+', '', str(dataframe[col][0]))
                left_0 = re.sub('\s+', '', str(dataframe[0][row]))
                triggers.append((top, left, top_0, left_0))
    return triggers


def firstrow(dataframe):
    return dataframe[0:1]


def firstcol(dataframe):
    return dataframe[[0]]
