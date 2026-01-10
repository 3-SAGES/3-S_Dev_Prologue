import sys
from stats import get_num_words, get_num_chars, get_sorted_char_counts

def get_book_text(path_to_file):
    with open(path_to_file) as f:
        return f.read()

def main():
    
    if len(sys.argv) < 2:
        print("Usage: python3 main.py <path_to_book>")
        sys.exit(1)
    book_path = sys.argv[1]

    test1 = get_book_text(book_path)
    char_counts = get_num_chars(test1)
    sorted_char_counts = get_sorted_char_counts(char_counts)

    print("============ BOOKBOT ============")
    print(f"Analyzing book found at {book_path}...")
    print("----------- Word Count ----------")
    print(f"Found {get_num_words(test1)} total words")
    print("--------- Character Count -------")
    
    for char in sorted_char_counts:
        if char[0].isalpha():
            print(f"{char[0]}: {char[1]}")
    print("============= END ==============")

main()