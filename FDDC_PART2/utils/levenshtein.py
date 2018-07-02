from jellyfish import levenshtein_distance


def edit_distance(s1, s2):
    return levenshtein_distance(s1, s2)


print(edit_distance('jellyfish', 'mellyfish'))
