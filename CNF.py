import os

#global variables
SIZE = 5

#colour
red, green, white, blue, yellow = 0,1,2,3,4

#nationality
british, swedish, danish, norwegian, german = 5,6,7,8,9

#drink
tea, coffee, water, beer, milk = 10,11,12,13,14

#cigarette
prince, blends, pallmall, bluemasters,dunhill = 15,16,17,18,19

#pet
dog, cat, bird, horse, fish = 20,21,22,23,24

#CNF Encoding
def category(house,attribute):
    return house + attribute * SIZE 

def neighbour(attr1,attr2):
    CNF = ['-{} {} 0'.format(category(1, attr1), category(2, attr2)),
        '-{} {} 0'.format(category(SIZE, attr1), category(SIZE - 1, attr2))]
    for i in range(2, SIZE):
        CNF.append('-{} {} {} 0'.format(category(i,attr1),category(i-1,attr2), category(i+1,attr2)))
                   
    return os.linesep.join(CNF)

#Relationship 
def relationship(attr1,attr2):
    CNF = []
    for i in range(1, SIZE+1):
        CNF.append('-{} {} 0'.format(category(i,attr1),category(i,attr2)))
        CNF.append('{} -{} 0'.format(category(i,attr1),category(i,attr2)))
                   
    return os.linesep.join(CNF)


def house(start, end):
    CNF = []
    
    #Only Once
    for i in range(start, end + 1):
        CNF.append('{} {} {} {} {} 0'.format(category(1,i), category(2,i), category(3,i), category(4,i), category(5,i)))     
        for h1 in range(1, SIZE + 1):
            for h2 in range(1, h1):
                CNF.append('-{} -{} 0'.format(category(h2, i), category(h1, i))) #unique category
            for j in range(start, end + 1):
                if i != j:
                    CNF.append('-{} -{} 0'.format(category(h1, i), category(h1, j))) # limit to one category per house

    return os.linesep.join(CNF)


def generateCNF():
    CNF = []
    literals = set()
    
    for i in range (0, 25, 5):
        CNF.append(house(i, i+4))

    
    '''Einstein's Puzzle'''    
    # The Norwegian lives in the first house.
    CNF.append('{} 0'.format(category(1, norwegian)))
    # The Norwegian lives next to the blue house.
    CNF.append('{} 0'.format(category(2, blue)))
    # The man living in the center house drinks milk.
    CNF.append('{} 0'.format(category(3, milk)))
    # The Brit lives in the red house.
    CNF.append(relationship(british,red))
    # The green house’s owner drinks coffee.
    CNF.append(relationship(green, coffee))
    # The Dane drinks tea.
    CNF.append(relationship(danish, tea))
    # The owner of the yellow house smokes Dunhill.
    CNF.append(relationship(yellow, dunhill))
    # The Swede keeps dogs as pets.
    CNF.append(relationship(swedish,dog))
    # The German smokes Prince.
    CNF.append(relationship(german, prince))
    # The person who smokes Pall Mall rears birds.
    CNF.append(relationship(pallmall, bird))
    # The owner who smokes Bluemasters drinks beer.
    CNF.append(relationship(bluemasters, beer))
    # The man who keeps the horse lives next to the man who smokes Dunhill.
    CNF.append(neighbour(horse, dunhill))
    # The man who smokes Blends lives next to the one who keeps cats.
    CNF.append(neighbour(blends, cat))
    # The man who smokes Blends has a neighbor who drinks water.
    CNF.append(neighbour(blends, water))
    # The green house is on the left of the white house.
    for white_house in range(1, SIZE+1):
        for green_house in range(SIZE, 0, -1):
            if (white_house - 1 > green_house) or (green_house > white_house):
                CNF.append('-{} -{} 0'.format(category(white_house, white), category(green_house, green)))
                
    einstein_CNF = os.linesep.join(CNF)
    lines = einstein_CNF.split(os.linesep)
    
    for line in lines:
        ls = line.split(' ')
        literals.update(list(map(lambda x:abs(int(x)), ls)))
        
    CNF_clauses = os.linesep.join(['p cnf {} {}'.format(len(literals)-1, len(lines)),einstein_CNF])
    return CNF_clauses

    
if __name__ == '__main__':
    with open('einstein_puzzle.cnf', 'w', newline='') as f:
        f.write(generateCNF())
