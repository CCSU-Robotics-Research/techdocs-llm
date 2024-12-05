# main.py is the entry point of the program. The frontend GUI is launched from here, which then drives backend processes logged in the Terminal.

from frontend import start_frontend

# Start the frontend GUI upon program launch
def main():
    start_frontend()

if __name__ == "__main__":
    main()
