# Example code with a large number of warnings

import os
import sys
import time
from collections import deque
from typing import List, Tuple, Dict, Optional

# Redefining built-in names (lots of these!)
list = [1, 2, 3]
dict = {"a": 1, "b": 2}
tuple = (4, 5, 6)
file = open("temp.txt", "w")
file.close()
dir = "/tmp"
id = 10
input = "some input"
open = "not a file object"
print = "not a function"
str = "a string"
bytes = b"some bytes"
bytearray = bytearray(b"some bytes")
complex = 1j
round = 1.0
slice = slice(1, 2)
type = "a type"
vars = {"x": 1}
__builtins__ = None
__name__ = "not main"
__file__ = "not this file"
__package__ = "not a package"

# Unused variables (lots of these!)
unused_var1 = 1
unused_var2 = "hello"
unused_var3 = [7, 8, 9]
unused_var4 = {"c": 3}
unused_var5 = (10, 11)
unused_var6 = open("temp2.txt", "w")
unused_var6.close()
unused_var7 = os.getcwd()
unused_var8 = sys.version
unused_var9 = time.time()
unused_var10 = deque([1, 2])
unused_var11: List[int] = [4, 5]
unused_var12: Tuple[str, int] = ("a", 1)
unused_var13: Dict[str, float] = {"b": 2.0}
unused_var14: Optional[bool] = True

def some_function(arg1, arg2):
    local_var1 = arg1 + 1 # Unused local variable
    local_var2 = arg2 * 2 # Unused local variable
    return None

def another_function(param1):
    if False:
        unused_in_if = 100 # Unused variable in conditional block
    value = 5
    value = 6 # Reassignment with no use in between
    return value

result = another_function(5)

# Importing but not using (a few of these)
import math
import random

if __name__ == "__main__":
    print("This script generates a lot of warnings.")

# Clean up the temporary files (to be a bit responsible)
try:
    os.remove("temp.txt")
    os.remove("temp2.txt")
except FileNotFoundError:
    pass