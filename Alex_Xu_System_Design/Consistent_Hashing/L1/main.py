import hashlib
import bisect


class BasicConsistentHash:
    def __init__(self):
        self.keys = []  # Ordered list of hash values on the ring
        self.nodes = {}  # Maps hash values to actual node names/IPs

    def _hash(self, key: str) -> int:
        # Use MD5 to distribute values evenly across the number space
        return int(hashlib.md5(key.encode('utf-8')).hexdigest(), 16)

    def add_node(self, node_name: str):
        node_hash = self._hash(node_name)
        # Keep the keys list sorted for binary search
        bisect.insort(self.keys, node_hash)
        self.nodes[node_hash] = node_name

    def remove_node(self, node_name: str):
        node_hash = self._hash(node_name)
        if node_hash in self.nodes:
            self.keys.remove(node_hash)
            del self.nodes[node_hash]

    def get_node(self, item_key: str) -> str:
        if not self.keys:
            return None

        item_hash = self._hash(item_key)
        # Find the index of the first node hash greater than the item hash
        index = bisect.bisect_right(self.keys, item_hash)

        # If we hit the end of the list, wrap around to the first node (clockwise)
        if index == len(self.keys):
            index = 0

        return self.nodes[self.keys[index]]


# --- Usage Example ---
ring = BasicConsistentHash()
ring.add_node("Cache_Server_A")
ring.add_node("Cache_Server_B")
ring.add_node("Cache_Server_C")

print(f"User 123 routes to: {ring.get_node('user_123')}")
print(f"User 456 routes to: {ring.get_node('user_456')}")

