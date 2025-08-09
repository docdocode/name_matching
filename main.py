from matcher import match_name

if __name__ == "__main__":
    customer_name = input("Enter customer's name: ")
    matches = match_name(customer_name, threshold=90)

    if matches:
        print("\nPossible Matches:")
        for match in matches:
            print(f"{match['full_name']} ({match['country']}) - "
                  f"Score: {match['score']} - Notes: {match['notes']}")
    else:
        print("No close matches found.")
