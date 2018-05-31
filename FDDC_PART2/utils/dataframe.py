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


def firstrow(dataframe):
    return dataframe[0:1]


def firstcol(dataframe):
    return dataframe[[0]]
