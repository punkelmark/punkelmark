import random
import os

def CLEAR():
    clear = lambda: os.system('cls')
    clear()

def get_new_index():
    pos = random.randrange(0, len(word_list))
    return pos

word_list = ["Apple","Mango"]



while True:
    x = input("\nEnter to continue... ")
    CLEAR()
    
    WORD = word_list[get_new_index()]

    print('Your word is: ', WORD)
    
    guess = 'M'
    result = []

    # Find index of matched guess
    for i in range(len(WORD)):
        if (WORD[i] == guess):
            print(i)