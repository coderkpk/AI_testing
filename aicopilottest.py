def is_prime(n):
    if n <= 1:
        return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            return False
    return True

def is_leap_year(year):
    return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)

while True:
    print("\nMenu:")
    print("1. Check Prime Number")
    print("2. Check Leap Year")
    print("3. Exit")
    choice = input("Enter your choice (1-3): ")

    if choice == '1':
        num = int(input("Enter a number to check for prime: "))
        if is_prime(num):
            print(f"{num} is a prime number.")
        else:
            print(f"{num} is not a prime number.")
    elif choice == '2':
        year = int(input("Enter a year to check for leap year: "))
        if is_leap_year(year):
            print(f"{year} is a leap year.")
        else:
            print(f"{year} is not a leap year.")
    elif choice == '3':
        print("Exiting program.")
        break
    else:
        print("Invalid choice. Please try again.")