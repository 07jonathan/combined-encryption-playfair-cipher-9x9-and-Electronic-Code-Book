def generate_playfair_matrix(key):
    alphabet = list("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 .,!?:;/@#^()|-+[]=")
    key_set = set(key)
    playfair_matrix = ""

    for char in key:
        if char not in playfair_matrix:
            playfair_matrix += char

    for char in alphabet:
        if char not in key_set and char not in playfair_matrix:
            playfair_matrix += char

    return playfair_matrix

def create_bigrams(plaintext):
    bigrams = []
    i = 0
    while i < len(plaintext):
        char1 = plaintext[i]
        if i + 1 < len(plaintext):
            char1 = plaintext[i]
            char2 = plaintext[i + 1]

            if char1 == char2:
                char2 = '^'
                i -= 1 
            bigrams.append(char1 + char2)
        else:
            char2 = ' '
            bigrams.append(char1 + char2)
        i += 2
    return bigrams

def encrypt(plaintext, matrix):
    bigrams = create_bigrams(plaintext)
    ciphertext = ""

    for bigram in bigrams:
        char1, char2 = bigram[0], bigram[1]
        row1, col1 = divmod(matrix.index(char1), 9)
        row2, col2 = divmod(matrix.index(char2), 9)

        if row1 == row2:  
            col1 = (col1 + 1) % 9
            col2 = (col2 + 1) % 9
        elif col1 == col2:  
            row1 = (row1 + 1) % 9
            row2 = (row2 + 1) % 9
        else:  
            col1, col2 = col2, col1

        ciphertext += matrix[row1 * 9 + col1] + matrix[row2 * 9 + col2]

    return ciphertext

def decrypt(ciphertext, matrix):
    bigrams = create_bigrams(ciphertext)
    plaintext = ""

    for i in range(len(bigrams)):
        bigram = bigrams[i]
        char1, char2 = bigram[0], bigram[1]
        row1, col1 = divmod(matrix.index(char1), 9)
        row2, col2 = divmod(matrix.index(char2), 9)

        if row1 == row2:  
            col1 = (col1 - 1) % 9
            col2 = (col2 - 1) % 9
        elif col1 == col2:  
            row1 = (row1 - 1) % 9
            row2 = (row2 - 1) % 9
        else:  
            col1, col2 = col2, col1

        decrypted_chars = matrix[row1 * 9 + col1] + matrix[row2 * 9 + col2]
        plaintext += decrypted_chars

    plaintext = plaintext.replace("^", '')

    return plaintext

def xor_strings(a, b):
    return ''.join(chr(ord(x) ^ ord(y)) for x, y in zip(a, b))

def encrypt_ecb(plaintext, key, shift):
    block_size = len(key)
    encrypted_blocks = []
    for i in range(0, len(plaintext), block_size):
        block = plaintext[i:i + block_size]
        encrypted_block = xor_strings(block, key)
        encrypted_block_binary = text_to_binary(encrypted_block).replace(' ', '')
        shifted_block = encrypted_block_binary[shift:] + encrypted_block_binary[:shift]
        shifted_text = binary_to_text(shifted_block)
        encrypted_blocks.append(shifted_text)
    return ''.join(encrypted_blocks)

def decrypt_ecb(ciphertext, key, shift):
    block_size = len(key)
    decrypted_blocks = []
    for i in range(0, len(ciphertext), block_size):
        block = ciphertext[i:i + block_size]
        decrypted_block_binary = text_to_binary(block).replace(' ', '')
        shifted_block = decrypted_block_binary[-shift:] + decrypted_block_binary[:-shift]
        shifted_text = binary_to_text(shifted_block)
        decrypted_block = xor_strings(shifted_text, key)
        decrypted_blocks.append(decrypted_block)
    return ''.join(decrypted_blocks)

def text_to_binary(text):
    binary_result = ' '.join(format(ord(char), '08b') for char in text)
    return binary_result

def binary_to_text(binary):
    text_result = ''.join(chr(int(binary[i:i+8], 2)) for i in range(0, len(binary), 8))
    return text_result