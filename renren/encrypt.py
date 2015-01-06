#-*-coding:utf-8-*-

# 分段加密
CHUNK_SIZE = 30

# RSA加密
def encrypt(e, m, c):
    return pow(c, e, m)

# 加密一段
def encryptChunk(e, m, chunk):
    chunk = list(map(ord, chunk))
    # 补成偶数长度
    if not len(chunk) % 2 == 0:
        chunk.append(0)

    nums = [ chunk[i] + (chunk[i+1] << 8) for i in range(0, len(chunk), 2) ]

    c = sum([n << i*16 for i, n in enumerate(nums)])

    encrypted = encrypt(e, m, c)
    return "%x" % encrypted

# 加密字符串，如果比较长，则分段加密
def encryptString(e, m, s):
    e, m = int(e, 16), int(m, 16)

    chunks = [ s[:CHUNK_SIZE], s[CHUNK_SIZE:] ] if len(s) > CHUNK_SIZE else [s]

    result = [encryptChunk(e, m, chunk) for chunk in chunks]
    return ' '.join(result)

if __name__ == '__main__':
    print(encryptString('10001', '856381005a1659cb02d13f3837ae6bb0fab86012effb3a41c8b84badce287759', 'abcdef'))
