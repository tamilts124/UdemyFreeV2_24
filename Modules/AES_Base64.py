from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import base64


class AES_Base64:

    def __init__(self, key:base64=''):
        '''Base64 Encrypted bytes key'''
        self.key =key

    def encodeBase64(self, data:bytes)->bytes:
        return base64.encodebytes(data)

    def decodeBase64(self, data_base64:bytes)->bytes:
        return base64.decodebytes(data_base64)

    def generateKey(self)->bytes:
        keyBytes =get_random_bytes(16)
        self.key =self.encodeBase64(keyBytes)
        return self.key
    
    def encryptDataAES(self, data_base64:bytes)->(bytes, bytes, bytes):
        '''return (ciphertext, tag, nonce)'''
        cipher =AES.new(self.decodeBase64(self.key), AES.MODE_EAX)
        ciphertext, tag = cipher.encrypt_and_digest(data_base64)
        nonce = cipher.nonce
        return (self.encodeBase64(ciphertext), self.encodeBase64(tag), self.encodeBase64(nonce))

    def decryptDataAES(self, data:bytes, tag:bytes, nonce:bytes)->bytes:
        '''return data_base64'''
        cipher =AES.new(self.decodeBase64(self.key), AES.MODE_EAX, self.decodeBase64(nonce))
        data = cipher.decrypt_and_verify(self.decodeBase64(data), self.decodeBase64(tag))
        return data


if __name__ == '__main__':
    plaintext ='Hello World'.encode()

    aes =AES_Base64()
    aes.generateKey()
    plaintext_base64 =aes.encodeBase64(plaintext)
    ciphertext, tag, nonce =aes.encryptDataAES(plaintext_base64)

    text_base64 =aes.decryptDataAES(ciphertext, tag, nonce)
    decode_text =aes.decodeBase64(text_base64)

    print(plaintext, aes.key, ciphertext, decode_text)