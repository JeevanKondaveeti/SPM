import random
import string
"""
otp = ''.join(random.choice(string.digits) for _ in range(6))
otp1= ''.join(random.choice(string.ascii_letters) for _ in range(6))
print(otp)
print(otp1)
"""
def genotp():
    otp_len = 3
    otp = ""
    for i in range(0,otp_len):
        char = random.choice(string.ascii_letters)
        num =str(random.choice(string.digits))
        otp = otp + char + num
    return otp

#genotp(3)