def trainagle(r):
    for i in range(1,r+1):
        for j in range(r-i):
            print(" ",end="")
        for k in range(i):
            print("*",end=" ")
        print()
trainagle(7)                

def tri(r):
    for i in range(1, r + 1):
        # Print leading spaces
        for j in range(r - i):
            print(" ", end="")

        # Print stars (increasing by 1 each row)
        for k in range(i):
            print("*", end=" ")

        # Move to next line
        print()

# Example usage
tri(7)