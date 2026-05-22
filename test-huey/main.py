from tasks import add_numbers, divide

if __name__ == "__main__":
    print("Enqueuing tasks...")
    add_numbers(3, 7)
    divide(10, 2)
    divide(1, 0)
    print("Tasks enqueued. Run the consumer to process them.")
