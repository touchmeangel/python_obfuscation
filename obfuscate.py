import sys
import subprocess

CYCLES = 20
INPUT_FILE = "input.py"
OUTPUT_FILE = "keys.py"

def install(required):
  missing = get_missing(required)

  if missing:
      python = sys.executable
      subprocess.check_call([python, '-m', 'pip', 'install', *missing], stdout=subprocess.DEVNULL)

def get_missing(required):
  missing = []
  for module in required:
    try:
      __import__(module)
    except ModuleNotFoundError:
       missing.append(module)
  return missing

install(['fernet'])
from fernet import Fernet

def bytes_from_file(filename, chunksize=8192) -> bytes:
  result = b''
  with open(filename, "rb") as f:
    while (chunk := f.read(chunksize)):
        if chunk:
          result += chunk
        else:
            break
      
  return result

def encrypt(code: bytes, cycles: int = 1) -> str:
  result = code
  for _ in range(cycles):
    result = encrypt_one(result).encode(encoding="utf-8")
  return add_imports(result.decode(encoding="utf-8"))
   
def encrypt_one(code: bytes) -> bytes:
  encryption_key = Fernet.generate_key()
  cipher_suite = Fernet(encryption_key)

  encrypted_value = cipher_suite.encrypt(code)

  return encryption_data_to_code(encryption_key, encrypted_value)

def add_imports(code: str) -> str:
   return f"""import subprocess,sys
try:
  subprocess.check_call([sys.executable,'-m','pip','install','fernet']) if __import__('fernet',fromlist=['']) is None else None;
except:
  subprocess.check_call([sys.executable,'-m','pip','install','fernet'])
from fernet import Fernet;{code}"""

def encryption_data_to_code(encryption_key, encrypted_value) -> str:
  return f"exec(Fernet({encryption_key}).decrypt({encrypted_value}))"

with open(OUTPUT_FILE, "w") as output_file:
   output_file.write(encrypt(bytes_from_file(INPUT_FILE), cycles=CYCLES))