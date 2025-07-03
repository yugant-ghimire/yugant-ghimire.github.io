
<h1> Disk Structure</h1>
- Blocks: data is stored on the block
- Tracks
- Sectors

<h2> Index </h2>
- pointer towards the actual record
- index is also stored in a block
- extremely small amount of blocks required to store index because it is so small
- all the searching is done through index
- no of blocks in index + 1 more block after getting the location through index (this is all the traversal needed)

<h3> Multi-level Index </h3>
- this would be a sparse index
- one pointer towards a block of the data in the index (maybe our index can store 30 data in one block)
- acts as a entry point for the index block access
- reduces the number of entry for blocks

- if too many data in database: we should use multiple multilevel indexes. This reduces the time for searches as it reduces the number of data points to check.
- we want self managed multi-level indices

<h4> M-way Search Tree </h4>
- binary search tree
- binary means 2 children
- k1 < k2 < k3
- 2key search tree can have 3 children
- m way can have m-1 keys and m is the number of children
- 
