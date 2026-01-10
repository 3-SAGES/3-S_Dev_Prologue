def get_num_words(text):
    words = text.split()
    return len(words)

def get_num_chars(text):
    l_text = text.lower()
    char_dict = {}
    for char in l_text:
        if char not in char_dict:
            char_dict[char] = 1
        else:
            char_dict[char] += 1
    return char_dict

def get_sorted_char_counts(char_dict):
    return sorted(char_dict.items(), reverse=True, key=lambda item: item[1])