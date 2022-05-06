# UCR/ECCI/PI_redesOper Equipo 7 raspado.

## class Cypher
# responsible for encrypting and decrypting messages using the caesar algorithm
class Cypher:

	## Constructor
	# initializes the attribute that represents the shift to each character
	def __init__(self):
		self._key = 3  # shift of each character

	## Run the caesar algorithm to encrypt or decrypt the text
	# @param text string to encrypt or decrypt
	# @param action integer that indicates: 1 for encrypt, 2 for decrypt
	# @return string with the result text
	def __run_algorithm(self, text, action):
		''' action: 1 is for encrypt | 2 is for decrypt
		valid range using ascii-code: [0,125]'''
		result = ""
		for char in text:
			if action == 1:
				result += chr(ord(char) + 3 % 125) 
			else:
				result += chr(ord(char) - 3 % 125) 
		return result
	
	## Invokes the caesar algorithm to encrypt the text
	# @param text string to encrypt
	# return string with the encrypted text
	def encrypt(self, text):
		return self.__run_algorithm(text, 1)  # action is 1 (encrypt)

	## Invokes the caesar algorithm to decrypt the text
	# @param text string to decrypt
	# return string with the decrypted text
	def decrypt(self, text):
		return self.__run_algorithm(text, 2)  # action is 2 (decrypt)

# end Cypher class


# test code. To run: python Cypher.py
def main():
	# sample text:   "{\"texto\":\"ejEMplo\":\"pass\":\"BasIc91\":\"ñÁ\"}"
	print(f"\n===start===")

	cypher = Cypher()
	
	# enter 'q' to exit
	while True:
		txt = input(f"\nenter text: ")
		if txt == 'q': break
		print(f"original: {txt}")

		encrypted = cypher.encrypt(txt)
		print(f"encrypted: {encrypted}")

		decrypted = cypher.decrypt(encrypted)
		print(f"decrypted: {decrypted}")

	print(f"\n===end===\n")

if __name__ == "__main__":
  	main()
