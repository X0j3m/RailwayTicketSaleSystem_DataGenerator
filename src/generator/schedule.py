import paths_creator
import schedule_generator
import sys

if __name__ == "__main__":
    if len(sys.argv) <= 1:
        print("No arguments detected. Script usage: python schedule.py <number_of_paths>")
    else:
        try:
            num_of_paths = int(sys.argv[1])
        except ValueError:
            print("Invalid input. Please provide a valid integer.")
            sys.exit(1)
        print(f"Generating schedule with {num_of_paths} paths")
        paths_creator.generate_paths(num_of_paths)
        schedule_generator.generate_schedule()