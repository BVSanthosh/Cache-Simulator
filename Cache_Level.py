import math

'''
This file contains the CacheLevel Class which represnts each cache level in the hierarchy
'''

ADDRESS_SIZE = 64   #size (in bits) of the memory address in the trace file
TWO_WAY = 2   #number of cache lines in 2-way set-associative cache
FOUR_WAY = 4   #number of cache lines in 4-way set-associative cache
EIGHT_WAY = 8   #number of cache lines in 8-way set-associative cache

class CacheLevel:
    def __init__(self, name, size, line_size, kind, replacement_policy):
        self.name = name   #cache name
        self.line_size = line_size   #cache line size
        self.line_num = size // line_size   #number of cache lines
        self.size = size   #cache size
        self.kind = kind   #cache kind
        self.hits = 0   #number of hits
        self.misses = 0   #number of misses
    
        self.set_replacement_policy(replacement_policy)   #sets the replacement policy
        self.initialise_cache()   #creates the cache store
        self.set_partition_bits()   #calculates the parition bits for the memory address

    #sets up an array representing the cache store based on the cache kind
    def initialise_cache(self):
        if self.kind == "direct":
            self.cache = [None] * self.line_num   #1D array for the cache store
        elif self.kind == "full":
            self.cache = [None] * self.line_num   #1D array for the cache store
            self.initialise_meta_data_cache(self.line_num)   #sets up the meta data array
        elif self.kind == "2way":
            self.set_size = TWO_WAY   #number of cache lines in each set
            self.set_num = self.line_num // TWO_WAY   #number of sets
            self.cache = [[None for j in range(TWO_WAY)] for i in range(self.set_num)]   #2D array for the cache store
            self.initialise_meta_data_cache(TWO_WAY)   #sets up the meta data array
        elif self.kind == "4way": 
            self.set_size = FOUR_WAY   #number of cache lines in each set
            self.set_num = self.line_num // FOUR_WAY   #number of sets
            self.cache = [[None for j in range(FOUR_WAY)] for i in range(self.set_num)]   #2D array for the cache store
            self.initialise_meta_data_cache(FOUR_WAY)   #sets up the meta data array
        elif self.kind == "8way":
            self.set_size = EIGHT_WAY   #number of cache lines in each set
            self.set_num = self.line_num // EIGHT_WAY   #number of sets
            self.cache = [[None for j in range(EIGHT_WAY)] for i in range(self.set_num)]   #2D array for the cache store
            self.initialise_meta_data_cache(EIGHT_WAY)   #sets up the meta data array
        else:
            print("Invalid cache kind")
    
    #creates a seperate array to store the meta data (used to implement the replacement policy)
    def initialise_meta_data_cache(self, way_num):
        if self.replacement_policy == "lru" or self.replacement_policy == "lfu":   #checks whether the replacement policy is round robin or not
            if self.kind == "full":   #checks whether the cahce kind is fully-associative or not
                self.meta_data_cache = [0] * self.line_num   #1D array for the meta data if fully-associative
            else:
                self.meta_data_cache = [[0 for j in range(way_num)] for i in range(self.set_num)]   #2D array for the meta data if set-associative
        else:
            self.meta_data_cache = None   #no meta data array needed if the replacement polciy is round robin
        
        #checks which cache kind to initialise the appropriate counter variable
        if self.replacement_policy == "lfu":
            self.lfu_counter = 0   #counter variable for least frequently used (count for each cache line indcating the number of times it has been accessed)
        elif self.replacement_policy == "lru": 
            self.lru_counter = 0   #counter variable for least recently used (maintains the order of access of each cache line to identify the one that hasn't been used the recently)
        else:
            self.rr_counter = 0   #counter variable for round robin (indicates the current cache line to replace)
    
    #sets the replacement policy based on the cache kind
    def set_replacement_policy(self, replacement_policy):
        if self.kind == "direct":   #checks if the cache kind is direct or not
            self.replacement_policy = ""   #if direct then replacement policy is needed
        elif self.kind == "full" or self.kind == "2way" or self.kind == "4way" or self.kind == "8way":
            if replacement_policy != "rr" and replacement_policy != "lru" and replacement_policy != "lfu": #checks if the appropriate replacement policy has been specified
                self.replacement_policy = "rr"   #if not then round robin is the default policy used
            else:
                self.replacement_policy = replacement_policy   #otherwise the specified one is used
        else:
            print("Invalid cache kind")
    
    #calculates the number of bits for the tag, index and offset based on the memory address
    def set_partition_bits(self):
        if self.kind == "direct":   #checks if cache kind is direct
            self.index_bits = int(math.log2(self.line_num))   #if so index bits is calculated using the number of cache lines
        elif self.kind == "2way" or self.kind == "4way" or self.kind == "8way":   #checks if cache kind is set-associative
            self.index_bits = int(math.log2(self.set_num))   #if so index bits is calculates using the number of sets
        else:
            self.index_bits = 0   #if fully-associative then no index bits is needed

        self.offset_bits = int(math.log2(self.line_size))   #calculates the number of offset bits based on the cache line size
        self.tag_bits  = ADDRESS_SIZE - (self.index_bits + self.offset_bits)   #calculates the number of tag bits 
    
    #splits the memory address into tag, index and offset
    def partition_address(self, address):
        hex_to_int = int(address, 16)   #converts hex to int
        binary_string = bin(hex_to_int)   #converts int to binary
        binary_string = binary_string[2:]
        binary_string = binary_string.zfill(ADDRESS_SIZE)   #recovers leading 0 bits lost during conversion

        self.tag = binary_string[:self.tag_bits]   #extrats the tag bits from the binary memory address
        self.index = binary_string[self.tag_bits:ADDRESS_SIZE - self.offset_bits]   #extrats the index bits from the binary memory address
        self.offset = binary_string[-self.offset_bits:]   #extrats the offset bits from the binary memory address
    
    #calls the relevant function to perform the cache access based on the cache kind
    def search_cache(self, address):
        if self.kind == "direct":   #if direct
            return self.search_direct(address)
        elif self.kind == "full":   #if fully-associative
            return self.search_fully_ass(address)
        elif self.kind == "2way":   #if set-associative
            return self.search_set_ass(TWO_WAY, address)
        elif self.kind == "4way":   #if set-associative
            return self.search_set_ass(FOUR_WAY, address)
        elif self.kind == "8way":   #if set-associative
            return self.search_set_ass(EIGHT_WAY, address)

        else:
            print("Invalid cache kind")
    
    #checks the cache lines in direct mapped cache
    def search_direct(self, address):
        self.partition_address(address)   #paritions the memory address
        index_int = int(self.index, 2)   #converts the index bits to identify the relvant cache line 

        if self.tag == self.cache[index_int]:   #checks if the cache line contains the tag bits
            self.hits += 1   #increments the hit counter on a hit
            return True
        else:
            self.cache[index_int] = self.tag   #stores the tag in the cache line
            self.misses += 1   #increments the miss counter on a miss
            return False
    
    #checks the cache lines in fully associative cache
    def search_fully_ass(self, address):
        self.partition_address(address)   #paritions the memory address

        for i in range(self.line_num):   #goes through each cache line
            if self.tag == self.cache[i]:   #checks if current cache line contains the tag bits
                self.hits += 1   #hit counter incremented on a hit 

                if self.replacement_policy != "rr":   #checks if the replacement policy isn't round robin
                    self.update_meta_data(0, i, True)   #if not then updates the meta data based on the current cache access
                    
                return True
            elif self.cache[i] == None:   #checks if current cache line is empty 
                self.cache[i] = self.tag   #if so stores the tag bits in that cache line
                self.misses += 1   #increments miss counter on a miss
                
                if self.replacement_policy != "rr":   #checks if the replacement policy isn't round robin
                    self.update_meta_data(0, i, True)   #if not then updates the meta data based on the current cache access
                    
                return False
            
        self.replace_cacheline(0)   #if the entire cache is traversed and the tag bits weren't found and all the cache lines are occupied then a replacement needs to happen
        return False
    
    #checks the cache lines in set-associative cache
    def search_set_ass(self, set_size, address):
        self.partition_address(address)    #paritions the memory address
        index_int = int(self.index, 2)   #converts the index bits to int to identify the relevant set

        for i in range(set_size):   #goes through the set
            if self.tag == self.cache[index_int][i]:   #checks if current cache line contains the tag bits
                self.hits += 1   #hit counter incremented on a hit 
                
                if self.replacement_policy != "rr":   #checks if the replacement policy isn't round robin
                    self.update_meta_data(index_int, i, False)    #if not then updates the meta data based on the current cache access
                    
                return True
            elif self.cache[index_int][i] == None:   #checks if current cache line is empty 
                self.cache[index_int][i] = self.tag   #if so stores the tag bits in that cache line
                self.misses += 1   #increments miss counter on a miss

                if self.replacement_policy != "rr":   #checks if the replacement policy isn't round robin
                    self.update_meta_data(index_int, i, False)    #if not then updates the meta data based on the current cache access
                    
                return False
            
        self.replace_cacheline(index_int)   #if the entire cache is traversed and the tag bits weren't found and all the cache lines are occupied then a replacement needs to happen
        return False
    
    #updates the meta data based on the cache access for fully-associative cache and set-associative cache
    def update_meta_data(self, index1, index2 , isFull):
        if isFull:   #checks if cache kind is fully-associative or not
            if self.replacement_policy == "lfu":   #if replacement policy is least frequently used
                self.meta_data_cache[index2] += 1   #increments the specified index in the meta data array corresponding to the accessed cache line in the cache array
            elif self.replacement_policy == "lru":   #if replacement policy is least recently used
                self.meta_data_cache[index2] = self.lru_counter   #assigns the current order count to the index specified
                self.lru_counter += 1   #increments the counter
        else:
            if self.replacement_policy == "lfu":   #if replacement policy is least frequently used
                self.meta_data_cache[index1][index2] += 1   #increments the index in the meta data array corresponding to the accessed cache line in the cache array
            elif self.replacement_policy == "lru":   #if replacement policy is least recently used
                self.meta_data_cache[index1][index2] = self.lru_counter   #assigns the current order count to the index specified
                self.lru_counter += 1   #increments the counter

    #calls the relevant function based on the replacement policy
    def replace_cacheline(self, index_int):
        if self.replacement_policy == "rr":   #if round robin
            self.round_robin(index_int)
        elif self.replacement_policy == "lru":   #if least recently used
            self.least_recently_used(index_int)
        elif self.replacement_policy == "lfu":   #if least frequently used 
            self.least_frequently_used(index_int)
        else:
            print("Invalid replacement policy")
    
    #replaces a cache line based on the round robin replacement policy
    def round_robin(self, index_int):
        self.misses += 1   #increments the miss coutner on a miss
        
        if self.kind == "full":    #checks if cache kind is fully-associative or not
            self.cache[self.rr_counter] = self.tag   #stores the tag bits in the index specified by the round robin counter
            self.rr_counter += 1   #increments the round robin counter

            if self.rr_counter == self.line_num:   #resets the counter to 0 if the value exceeds the number of cache lines
                self.rr_counter = 0
        else:
            self.cache[index_int][self.rr_counter] = self.tag   #stores the tag bits in the index specified by the round robin counter
            self.rr_counter += 1   #increments the round robin counter

            if self.rr_counter == self.set_size:   #resets the counter to 0 if the value exceeds the number of cache lines in each set
                self.rr_counter = 0
    
    #replaces a cache line based on the least recently used replacement policy
    def least_recently_used(self, index_int):
        self.misses += 1   #increments the miss coutner on a miss

        if self.kind == "full":    #checks if cache kind is fully-associative or not
            min_index = self.meta_data_cache.index(min(self.meta_data_cache))   #gets the array index of the cache line with the lowest order value
            self.cache[min_index] = self.tag   #stores the tag bits in the cache line specified by the index
            self.meta_data_cache[min_index] = self.lru_counter   #updates the order value of the current cache line
            self.lru_counter += 1   #increments the least recently used counter
        else:
            min_index = self.meta_data_cache[index_int].index(min(self.meta_data_cache[index_int]))   #gets the array index of the cache line with the lowest order value
            self.cache[index_int][min_index] = self.tag   #stores the tag bits in the cache line specified by the index
            self.meta_data_cache[index_int][min_index] = self.lru_counter   #updates the order value of the current cache line
            self.lru_counter += 1   #increments the least recently used counter
    
    #replaces a cache line based on the least frequently used replacement policy
    def least_frequently_used(self, index_int):
        self.misses += 1   #increments the miss coutner on a miss
        
        if self.kind == "full":    #checks if cache kind is fully-associative or not
            min_index = self.meta_data_cache.index(min(self.meta_data_cache))   #gets the array index of the cache line with the lowest value
            self.cache[min_index] = self.tag   #stores the tag bits in the cache line specified by the index
            self.meta_data_cache[min_index] += 1   #increments the least frequently used counter
        else:
            min_index = self.meta_data_cache[index_int].index(min(self.meta_data_cache[index_int]))   #gets the array index of the cache line with the lowest value
            self.cache[index_int][min_index] = self.tag   #stores the tag bits in the cache line specified by the index
            self.meta_data_cache[index_int][min_index] += 1   #increments the least frequently used counter
    
    #helper function to print the cache configuration
    def print_config(self):
        print(f"Cache: {self.name}, Line Size: {self.line_size}, Number of lines: {self.line_num}, Size: {self.size}, Kind: {self.kind}")