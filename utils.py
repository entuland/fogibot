

def tokenize(message):
    parts = message.split()
    tokens = []
    for part in parts:
        token = part.strip(" .,:;!?'\"")
        if token:
            tokens.append(token)
    return tokens, len(tokens)