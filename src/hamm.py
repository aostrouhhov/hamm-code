# Made according to this (many thanks):
# http://www.eecs.umich.edu/courses/eecs373.w05/lecture/hamming.html

# Each byte is separated into two 4-bit parts, each part is encoded to 8-bit code (i.e. 1 encoded byte = 16 bits) 

import os
from random import randint

# [8,4] Hamming code table suitable for single error correction, double error detection
G = ['00000000', '11010010', '01010101', '10000111',
    '10011001', '01001011', '11001100', '00011110', 
    '11100001', '00110011', '10110100', '01100110', 
    '01111000', '10101010', '00101101', '11111111']

def byteToBits(hex):
    result = ''
    
    # Shift 00000001 from right to left 7 times
    mask = 1 << 7
    
    # Emulate do while loop
    while True:
        c = '1' if ( hex & mask ) != 0 else '0'
        result += c
        
        mask >>= 1
        if mask <= 0:
            break
    
    return result

def spoilOneBitInByte(string):
    # Add one-bit random error to each encoded byte
    
    spoiled = ''

    while len(string) >= 16:
        nibble = string[0:16]
        i = randint(0, 15)

        if nibble[i] == '1':
            nibble = nibble[:i] + '0' + nibble[i+1:]
        else:
            nibble = nibble[:i] + '1' + nibble[i+1:]
        
        spoiled += nibble
        string = string[16:]

    return spoiled

def spoilTwoBitsInByte(string):
    # Add two-bit random errors to each encoded byte
    # Only one error for 8 bits (to be able to restore)
    
    spoiled = ''

    while len(string) >= 8:
        nibble = string[0:8]
        i = randint(0, 7)

        if nibble[i] == '1':
            nibble = nibble[:i] + '0' + nibble[i+1:]
        else:
            nibble = nibble[:i] + '1' + nibble[i+1:]
        
        spoiled += nibble
        string = string[8:]

    return spoiled

def encode(string):
    # Read 4 bits at a time and write out those plus parity bits
    
    encoded = ''

    while len(string) >= 4:
        nibble = string[0:4]
        encoded += toHamming(nibble)
        string = string[4:]

    return encoded

def toHamming(bits):
    # Return given 4 bits plus parity bits for bits (1,2,3), (2,3,4), (1,3,4) and the entire code combination
    
    p1 = parity(bits, [0,1,3])
    p2 = parity(bits, [0,2,3])
    p3 = parity(bits, [1,2,3])
    p = parity(p1 + p2 + bits[0] + p3 + bits[1:], [0,1,2,3,4,5,6])

    return p1 + p2 + bits[0] + p3 + bits[1:] + p

def parity(string, indicies):
    # Compute the parity bit for the given string and indicies
    
    sub = ''

    for i in indicies:
        sub += string[i]

    return str(str.count(sub, "1") % 2)

def decode(string):
    # Read 8 bits at a time, decode them and write out 4 bits of message

    decoded = ''

    while len(string) >= 8:
        nibble = string[0:8]
        nibble = fromHamming(nibble)

        if nibble != None:
            decoded += nibble
        else:
           return None
 
        string = string[8:]
    
    return decoded

def fromHamming (bits):
    # Compare given bits with hamming codes from table G and return decoded message, corrected and decoded message or 'None' (cannot decode)

    for code in G:
        hamm1 = [int(k) for k in bits]
        hamm2 = [int(k) for k in code]

        diff = []
    
        i = 0
        while i < 8: 
            if hamm1[i] != hamm2[i]:
                diff.append(i+1)
            i += 1
        
        if len(diff) == 0: # No mistakes
            return bits[2] + bits[4] + bits[5] + bits[6]
        
        if len(diff) == 1:
            print("1 mistake in 4 bits, correction is possible.")
            return code[2] + code[4] + code[5] + code[6]
        
        if len(diff) == 2:
            print("2 mistakes in 4 bits, cannot correct.")
            return None

    print("3 or more mistakes in 4 bits, cannot correct.")
    return None

if __name__ == "__main__":
    print('Opening file...')

    file = open(os.path.join(os.pardir, 'message.txt'), 'rb')
    data = file.read()
    file.close()

    source = ''

    for byte in data:
        bin = byteToBits(byte)
        source += bin

    print('Encoding file...')
    encoded = encode(source)
    
    file = open('encoded.txt', 'xt')
    file.write(encoded)
    file.close()

    # Add one-bit error to one encoded byte
    # encoded = spoilOneBitInByte(encoded)

    # Add two-bit errors to one encoded byte
    # encoded = spoilTwoBitsInByte(encoded)

    print('Decoding message...')
    decoded = decode(encoded)

    if decoded == None:
        print('Message is broken and should be recycled!')
    else:
        print('Successfully decoded.')

    input('Press ENTER to exit')