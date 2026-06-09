import hashlib
import bisect


class VNodeConsistentHash:
    def __init__(self, replicas=100):
        self.replicas = replicas
        self.ring = []  # Sorted list of virtual node hashes
        self.nodes = {}  # Maps virtual node hash to physical node name

    def _hash(self, key: str) -> int:
        return int(hashlib.md5(key.encode('utf-8')).hexdigest(), 16)

    def add_node(self, node_name: str, weight: int = 1):
        # Weight allows us to give larger servers more virtual nodes
        total_vnodes = self.replicas * weight
        for i in range(total_vnodes):
            # Create a unique string for the virtual node
            vnode_key = f"{node_name}:vnode:{i}"
            vnode_hash = self._hash(vnode_key)

            bisect.insort(self.ring, vnode_hash)
            self.nodes[vnode_hash] = node_name

    def remove_node(self, node_name: str, weight: int = 1):
        total_vnodes = self.replicas * weight
        for i in range(total_vnodes):
            vnode_key = f"{node_name}:vnode:{i}"
            vnode_hash = self._hash(vnode_key)

            if vnode_hash in self.nodes:
                self.ring.remove(vnode_hash)
                del self.nodes[vnode_hash]

    def get_node(self, item_key: str) -> str:
        if not self.ring:
            return None

        item_hash = self._hash(item_key)
        index = bisect.bisect_right(self.ring, item_hash)

        if index == len(self.ring):
            index = 0

        return self.nodes[self.ring[index]]


# --- Usage Example ---
cluster = VNodeConsistentHash(replicas=100)
# Server A is twice as powerful, so it gets double the weight
cluster.add_node("10.0.0.1 (Large)", weight=2)
cluster.add_node("10.0.0.2 (Small)", weight=1)

print(f"Image_992 routes to: {cluster.get_node('image_992')}")

