import hashlib
import json
import time

class Block:
    def __init__(self, index, data, previous_hash):
        self.index = index
        self.timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        self.data = data
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        block_string = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp,
            "data": self.data,
            "previous_hash": self.previous_hash
        }, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()


class Blockchain:
    def __init__(self):
        self.chain = []
        self.create_genesis_block()

    def create_genesis_block(self):
        genesis = Block(0, {
            "message": "Genesis Block — Blockchain initialized by Ansh | CGC",
            "type": "genesis"
        }, "0")
        self.chain.append(genesis)

    def get_last_block(self):
        return self.chain[-1]

    def add_block(self, data):
        previous_hash = self.get_last_block().hash
        new_block = Block(len(self.chain), data, previous_hash)
        self.chain.append(new_block)
        return new_block

    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i - 1]
            if current.hash != current.calculate_hash():
                return False
            if current.previous_hash != previous.hash:
                return False
        return True

    def find_document(self, doc_hash):
        for block in self.chain:
            if isinstance(block.data, dict) and block.data.get("document_hash") == doc_hash:
                return block
        return None

    def get_chain_data(self):
        return [{
            "index": block.index,
            "timestamp": block.timestamp,
            "data": block.data,
            "hash": block.hash,
            "previous_hash": block.previous_hash
        } for block in self.chain]