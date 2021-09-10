import logging 
from aiogram import Bot, Dispatcher, executor, types

API_TOKEN = "" # Here you must put your API TOKEN
logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

users = {}
file = open("alphabet.txt")
alphabet = file.read()
file.close()


def encrypt(input_text, encryption_key):
    global alphabet
    jumps = tuple(alphabet.index(l) for l in encryption_key)
    encrypted_text = ""
    alphabet_length = len(alphabet)
    i = 0

    for l in input_text:
        if l == " ":
            encrypted_text += ";"
            continue
        letter_index = alphabet.index(l) + jumps[i]
        if letter_index >= alphabet_length:
            encrypted_text += alphabet[abs(alphabet_length-letter_index)]
        else:
            encrypted_text += alphabet[letter_index]
        
        if i == len(jumps) - 1:
            i = 0
        else:
            i += 1
    return encrypted_text


def decrypt(input_text, encryption_key):
    global alphabet
    jumps = tuple(alphabet.index(l) for l in encryption_key)
    decrypted_text = ""
    alphabet_length = len(alphabet)
    i = 0

    for l in input_text:
        if l == ";":
            decrypted_text += " "
            continue
        letter_index = alphabet.index(l) - jumps[i]
        if letter_index >= alphabet_length:
            decrypted_text += alphabet[abs(alphabet_length-letter_index)]
        else:
            decrypted_text += alphabet[letter_index]
        
        if i == len(jumps) - 1:
            i = 0
        else:
            i += 1
    return decrypted_text


def check_in_alphabet(text):
    global alphabet
    for l in text:
        if l == " " or l == ";":
            continue
        if l not in alphabet:
            return False
    return True 


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    if message.from_user.id not in users:
        users[message.from_user.id] = {"mode": "", "key": ""}
    await message.answer("Hello, write /encrypt to encrypt message, /decrypt to decrypt message, /setkey to set encryption key.")


@dp.message_handler(commands=['encrypt'])
async def encrypt_message(message: types.Message):
    global users
    if users[message.from_user.id]["key"] == "":
        await message.answer("Please set encryption key before encrypting message. To set encryption key write /setkey")
    else:
        users[message.from_user.id]["mode"] = "encrypt"
        await message.answer("Send message to encrypt")


@dp.message_handler(commands=['decrypt'])
async def decrypt_message(message: types.Message):
    global users
    if users[message.from_user.id]["key"] == "":
        await message.answer("Please set encryption key before decrypting message. To set encryption key write /setkey")
    else:
        users[message.from_user.id]["mode"] = "decrypt"
        await message.answer("Send message to decrypt")


@dp.message_handler(commands=['setkey'])
async def set_key(message: types.Message):
    global users
    users[message.from_user.id]["mode"] = "setkey"
    await message.answer("Send an encryption key\nNOTE: Don't use any spaces in key")


@dp.message_handler()
async def main_handler(message: types.Message):
    global users
    user = users[message.from_user.id]
    if user["mode"] == "encrypt":
        if check_in_alphabet(message.text):
            await message.answer("Your encrypted message:")
            await message.answer(encrypt(message.text, user["key"]))
            user["mode"] = ""
        else:
            await message.answer("Sorry, your text has letters or symbols which not in our alphabet.")
    elif user["mode"] == "decrypt":
        if check_in_alphabet(message.text):
            await message.answer("Your decrypted message:")
            await message.answer(decrypt(message.text, user["key"]))
            user["mode"] = ""
        else:
            await message.answer("Sorry, your text has letters or symbols which not in our alphabet.")
    elif user["mode"] == "setkey":
        if " " not in message.text:
            user["key"] = message.text
            await message.answer(f"Key <em>{message.text}</em> is set", parse_mode="html")
            user["mode"] = ""
        else:
            await message.answer("Encryption key can't contain spaces. Please send another")


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
