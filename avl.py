# modified dynamic AVL tree from https://www.geeksforgeeks.org/deletion-in-an-avl-tree/
#   modifications:
#       - maintain parent pointers
#       - O(log n)-time search: _search
#       - O(n)-time naive neighbor-search: left_neighbor/right_neighbor
#       - O(n)-time validation method for debugging: validate

class DefaultComparator(object):
    
    def compare(self, a, b):
        '''returns -1 if a < b, 0 if a ==b, and 1 if a > b'''
        return (a > b) - (a < b)
    
class AVLNode(object):
    def __init__(self, key):
        self.key = key
        self.left = None
        self.right = None
        self.height = 1
        self.parent = None

class AVLTree(object):

    def __init__(self, comparator=DefaultComparator()):
        self.root = None
        self.comparator = comparator
        self.size = 0

    def height(self, node):
        if node is None:
            return 0
        
        return node.height

    def right_rotate(self, y):
        x = y.left
        T2 = x.right

        # Perform rotation
        x.right = y
        if x.right is not None: x.right.parent = x
        y.left = T2
        if y.left is not None: y.left.parent = y

        # Update heights
        y.height = max(self.height(y.left), 
                    self.height(y.right)) + 1
        x.height = max(self.height(x.left), 
                    self.height(x.right)) + 1

        # Return new root
        return x

    def left_rotate(self, x):
        y = x.right
        T2 = y.left

        # Perform rotation
        y.left = x
        if y.left: y.left.parent = y
        x.right = T2
        if x.right: x.right.parent = x

        # Update heights
        x.height = max(self.height(x.left), 
                       self.height(x.right)) + 1
        y.height = max(self.height(y.left), 
                       self.height(y.right)) + 1

        # Return new root
        return y

    def get_balance(self, node):
        if node is None:
            return 0
        return self.height(node.left) - self.height(node.right)
    
    def _search(self, node, key):
        '''returns the node containing the given key or None if no such node exists'''
        if node is None:
            return node
        
        c = self.comparator.compare(key, node.key)

        if c < 0:
            return self._search(node.left, key)
        elif c > 0:
            return self._search(node.right, key)
        else:
            return node

    def _insert(self, node, key):
        # 1. Perform the normal BST insertion
        if node is None:
            return AVLNode(key)
        
        c = self.comparator.compare(key, node.key)

        if c < 0:
            node.left = self._insert(node.left, key)
            if node.left is not None: node.left.parent = node
        elif c > 0:
            node.right = self._insert(node.right, key)
            if node.right is not None: node.right.parent = node
        else:  # Duplicate keys not allowed
            assert(False)

        # 2. Update height of this ancestor node
        node.height = max(self.height(node.left), 
                          self.height(node.right)) + 1

        # 3. Get the balance factor of this node
        # to check whether this node became 
        # unbalanced
        balance = self.get_balance(node)

        # If this node becomes unbalanced, then
        # there are 4 cases

        # Left Left Case
        if balance > 1 and self.comparator.compare(key, node.left.key) < 0:
            return self.right_rotate(node)

        # Right Right Case
        if balance < -1 and self.comparator.compare(key, node.right.key) > 0:
            return self.left_rotate(node)

        # Left Right Case
        if balance > 1 and self.comparator.compare(key, node.left.key) > 0:
            node.left = self.left_rotate(node.left)
            if node.left is not None: node.left.parent = node
            return self.right_rotate(node)

        # Right Left Case
        if balance < -1 and self.comparator.compare(key, node.right.key) < 0:
            node.right = self.right_rotate(node.right)
            if node.right is not None: node.right.parent = node
            return self.left_rotate(node)

        return node

    def min_value_node(self, node):
        current = node

        # loop down to find the leftmost leaf
        while current.left is not None:
            current = current.left

        return current
    
    def max_value_node(self, node):
        current = node

        while current.right is not None:
            current = current.right

        return current
    
    def insert(self, val):
        '''inserts the val from the tree, if it is not already present'''
        self.root = self._insert(self.root, val)
        if self.root is not None: self.root.parent = None        
        
        self.size += 1
    
    def delete(self, val):
        '''removes the given val from the tree'''
        self.root = self.delete_node(self.root, val)
        if self.root is not None: self.root.parent = None
        
        self.size -= 1

    def delete_node(self, root, key):
        # STEP 1: PERFORM STANDARD BST DELETE
        if root is None:
            return root
        
        c = self.comparator.compare(key, root.key)

        # If the key to be deleted is smaller 
        # than the root's key, then it lies in 
        # left subtree
        # if key < root.key:
        if c < 0:
            root.left = self.delete_node(root.left, key)
            if root.left is not None: root.left.parent = root

        # If the key to be deleted is greater 
        # than the root's key, then it lies in 
        # right subtree
        elif c > 0:
            root.right = self.delete_node(root.right, key)
            if root.right is not None: root.right.parent = root

        # if key is same as root's key, then 
        # this is the node to be deleted
        else:
            # node with only one child or no child
            if root.left is None or root.right is None:
                temp = root.left if root.left else root.right

                # No child case
                if temp is None:
                    root = None
                else:  # One child case
                    root = temp

            else:
                # node with two children: Get the 
                # inorder successor (smallest in 
                # the right subtree)
                temp = self.min_value_node(root.right)

                # Copy the inorder successor's 
                # data to this node
                root.key = temp.key

                # Delete the inorder successor
                root.right = self.delete_node(root.right, temp.key)
                if root.right is not None: root.right.parent = root

        # If the tree had only one node then return
        if root is None:
            return root

        # STEP 2: UPDATE HEIGHT OF THE CURRENT NODE
        root.height = max(self.height(root.left), 
                        self.height(root.right)) + 1

        # STEP 3: GET THE BALANCE FACTOR OF THIS 
        # NODE (to check whether this node 
        # became unbalanced)
        balance = self.get_balance(root)

        # If this node becomes unbalanced, then 
        # there are 4 cases

        # Left Left Case
        if balance > 1 and self.get_balance(root.left) >= 0:
            return self.right_rotate(root)

        # Left Right Case
        if balance > 1 and self.get_balance(root.left) < 0:
            root.left = self.left_rotate(root.left)
            return self.right_rotate(root)

        # Right Right Case
        if balance < -1 and self.get_balance(root.right) <= 0:
            return self.left_rotate(root)

        # Right Left Case
        if balance < -1 and self.get_balance(root.right) > 0:
            root.right = self.right_rotate(root.right)
            return self.left_rotate(root)

        return root

    def in_order(self):
        return self._in_order(self.root)

    def _in_order(self, root):
        '''returns a list of items in the tree, ordered from smallest to largest'''
        if root is not None:            
            ret = []
            ret.extend(self._in_order(root.left))
            ret.append(root.key)
            ret.extend(self._in_order(root.right))
            return ret
        else:
            return []
        
    def validate(self, node):
        '''helper method for debugging. verifies parent pointers are set appropriately,
        and all internal nodes' left/right children have valid comparisons'''
        if node is None:
            return
        
        if node is self.root and self.root is not None: node.parent is None

        if node.left:
            assert(node != node.left)
            assert(node.left.parent is node)
            assert(self.comparator.compare(node.left.key, node.key) < 0)

        if node.right:
            assert(node != node.right)
            assert(node.right.parent is node)
            assert(self.comparator.compare(node.right.key, node.key) > 0)

    def naive_left_neighbor(self, key):
        '''naive O(n)-time left-neighbor search'''
        keys = self.in_order()
        idx = keys.index(key)
        if idx <= 0:
            return None
        else:
            return keys[idx-1]
            
    def naive_right_neighbor(self, key):
        '''naive O(n)-time right-neighbor search'''
        keys = self.in_order()
        idx = keys.index(key)
        if idx >= len(keys)-1:
            return None
        else:
            return keys[idx+1]
        
    def left_neighbor(self, key):
        '''given a segment "seg" in the tree, return another segment in the tree, if any, 
            whose intersection with the sweep-line is closest to "seg"'s intersection with
            the sweep-line from its left side. if there is no such segment, return None.'''
        
        # TODO: Implement this method so that it runs in time proportional to the height of the tree.
        #   Use .parent, .left, and .right accordingly to navigate through the tree.

        comp_1 = None
        comp_2 = None

        current = self.root
        while current is not None:
            if not self.comparator.compare(current.key, key):
                if current.left is not None:
                    comp_1 = self.max_value_node(current.left).key
                break
            elif self.comparator.compare(current.key, key) < 0:
                if comp_2 is None or self.comparator.compare(current.key, comp_2) > 0:
                    comp_2 = current.key
                current = current.right
            elif self.comparator.compare(current.key, key):
                current = current.left

        if comp_1 is None and comp_2 is None:
            return None
        elif comp_1 is None:
            return comp_2
        elif comp_2 is None:
            return comp_1 
        elif self.comparator.compare(comp_2, comp_1) < 0:
            return comp_1
        elif self.comparator.compare(comp_2, comp_1):
            return comp_2

    def right_neighbor(self, key):
        '''given a segment "seg" in the tree, return another segment in the tree, if any, 
            whose intersection with the sweep-line is closest to "seg"'s intersection with
            the sweep-line from its right side. if there is no such segment, return None.'''
        
        # TODO: Implement this method so that it runs in time proportional to the height of the tree.
        #   Use .parent, .left, and .right accordingly to navigate through the tree.
        
        comp_1 = None
        comp_2 = None

        current = self.root
        while current is not None:
            if not self.comparator.compare(current.key, key):
                if current.right is not None:
                    comp_1 = self.min_value_node(current.right).key
                break
            elif self.comparator.compare(current.key, key) < 0:
                current = current.right
            elif self.comparator.compare(current.key, key):
                if comp_2 is None or self.comparator.compare(current.key, comp_2) < 0:
                    comp_2 = current.key
                current = current.left

        if comp_1 is None and comp_2 is None:
            return None
        elif comp_1 is None:
            return comp_2
        elif comp_2 is None:
            return comp_1 
        elif self.comparator.compare(comp_2, comp_1) < 0:
            return comp_2
        elif self.comparator.compare(comp_2, comp_1):
            return comp_1

if __name__ == "__main__":
    import random
    tree = AVLTree()
    xs = list(range(1000))
    random.shuffle(xs)
    for x in xs:
        tree.insert(x)

    import time
    start = time.time()
    for x in xs[:10]:
        left = tree.naive_left_neighbor(x)
        right = tree.naive_right_neighbor(x)
        myleft = tree.left_neighbor(x)
        myright = tree.right_neighbor(x)

        print('left/right neighbors of {}: {}, {}'.format(x,left,right))
        print('myleft/myright neighbors of {}: {}, {}'.format(x,myleft,myright))

    print(time.time() - start)