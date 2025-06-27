import argparse
from kindlemint.agents.publishing_moa import PublishingMoA

def main():
    parser = argparse.ArgumentParser(description="Generate a book with Mixture of Agents")
    parser.add_argument("--concept", type=str, required=True, help="Book concept")
    args = parser.parse_args()

    book = PublishingMoA().create_book(args.concept)
    print("\n\n--- Generated Book ---\n\n")
    print(book)

if __name__ == "__main__":
    main()
