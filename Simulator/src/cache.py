import math, block, response
import pprint

class Cache:
    def __init__(self, name, word_size, block_size, n_blocks, associativity, hit_time, write_time, write_back, logger, next_level=None, prev_level=None, policy=None):
        #Parameters configured by the user
        self.name = name
        self.word_size = word_size
        self.block_size = block_size
        self.n_blocks = n_blocks
        self.associativity = associativity
        self.hit_time = hit_time
        self.write_time = write_time
        self.write_back = write_back
        self.logger = logger
        
        #Total number of sets in the cache
        self.n_sets = int(n_blocks / associativity)
        
        #Dictionary that holds the actual cache data
        self.data = {}
        
        #Pointer to the next lowest level of memory
        #Main memory gets the default None value
        self.next_level = next_level

        #Pointer to the next highest level of memory
        #L1 gets the default None value
        self.prev_level = prev_level

        #Setting the policy to Inclusive or Exclusive or None
        self.policy = policy

        #Figure out spans to cut the binary addresses into block_offset, index, and tag
        self.block_offset_size = int(math.log(self.block_size, 2))
        self.index_size = int(math.log(self.n_sets, 2))

        #Initialize the data dictionary
        if next_level:
            for i in range(self.n_sets):
                index = str(bin(i))[2:].zfill(self.index_size)
                if index == '':
                    index = '0'
                self.data[index] = {} #Create a dictionary of blocks for each set

    def __str__(self):
        return 'name- {}, word_size- {}, block_size- {}, n_blocks- {}, associativity- {}, hit_time- {}, write_time- {}, write_back- {}, next_level_name- {}, prev_level_name- {}, policy- {}, n_sets- {}, block_offset_size- {}, index_size- {}'.format(
                self.name, self.word_size,
                self.block_size, self.n_blocks, self.associativity,
                self.hit_time, self.write_time, self.write_back,
                self.next_level.name if self.next_level else None,
                self.prev_level.name if self.prev_level else None,
                self.policy, self.n_sets, self.block_offset_size,
                self.index_size)

    def read(self, address, current_step):
        r = None
        #Check if this is main memory
        #Main memory is always a hit
        if not self.next_level:
            r = response.Response({self.name:True}, self.hit_time)
        else:
            #Parse our address to look through this cache
            block_offset, index, tag = self.parse_address(address)

            #Get the tags in this set
            in_cache = list(self.data[index].keys())
            
            #If this tag exists in the set, this is a hit
            if tag in in_cache:
                if self.policy == 'Exclusive':
                    print('Exclusive cache')

                    if self.name != 'cache_1':
                        '''
                        Block needs to be moved from lower level cache to
                        higher level cache and removed from here
                        Remove from here directly and insertion will get handled
                        in the lower level cache automatically
                        '''
                        del self.data[index][tag]
                r = response.Response({self.name:True}, self.hit_time)
            else:
                #Read from the next level of memory
                r = self.next_level.read(address, current_step)
                r.deepen(self.write_time, self.name)

                if self.policy == 'Inclusive':
                    print('Inclusive cache')
                    '''
                    Delete the blocks having invalidate requests passed up from
                    the lower level caches

                    The following code snippet won't be required in case the 
                    prev level method is used, see comments below
                    '''
                    if self.next_level.name in r.invalidate_list.keys():
                        for addr in r.invalidate_list[self.next_level.name]:
                            blk_off, ind, tg = self.parse_address(addr)
                            in_cach = list(self.data[ind].keys())
                            if tg in in_cach:
                                del self.data[ind][tg]
                        r.invalidate_list[self.next_level.name].clear()

                    if len(in_cache) < self.associativity:
                        self.data[index][tag] = block.Block(self.block_size, current_step, False, address)
                    else:
                        '''
                        Update the tags in this set since a higher level cache
                        could have evicted a block from this set via the nested
                        read sequence called after this set's blocks were
                        initially populated at the start of this level's read
                        '''
                        in_cache = list(self.data[index].keys())
                        oldest_tag = in_cache[0] 
                        for b in in_cache:
                            if self.data[index][b].last_accessed < self.data[index][oldest_tag].last_accessed:
                                oldest_tag = b
                        if self.write_back:
                            if self.data[index][oldest_tag].is_dirty():
                                self.logger.info('\tWriting back block ' + address + ' to ' + self.next_level.name)
                                temp = self.next_level.write(self.data[index][oldest_tag].address, True, current_step)
                                r.time += temp.time

                        '''
                        Store invalidate request to be passed up to every higher
                        level cache

                        The check for L1 is not really required since the only 
                        parameters accessed from the returned response are
                        going to be hit_list and time
                        '''
                        if self.name != 'cache_1':
                            r.invalidate(self.name, self.data[index][oldest_tag].address)

                        '''
                        The other way of performing the same invalidate
                        operation as above, by defining prev level instead of
                        using response to pass up invalidation requests to 
                        higher level caches

                        Advantage- L2 can directly invalidate for L1 rather
                        than waiting to return back to L1 and then L1 doing it
                        for itself
                        '''
                        #if self.prev_level:
                        #    self.invalidate(self.data[index][oldest_tag].address)

                        del self.data[index][oldest_tag]
                        self.data[index][tag] = block.Block(self.block_size, current_step, False, address)
                elif self.policy == 'Exclusive':
                    print('Exclusive cache')
                    '''
                    In case of lowest level cache, nothing to be done at its
                    level, and block read from memory will directly be passed to
                    the higher level cache via the response
                    '''
                    if self.next_level != 'mem':
                        if len(in_cache) < self.associativity:
                            self.data[index][tag] = block.Block(self.block_size, current_step, False, address)
                        else:
                            oldest_tag = in_cache[0] 
                            for b in in_cache:
                                if self.data[index][b].last_accessed < self.data[index][oldest_tag].last_accessed:
                                    oldest_tag = b
                            '''
                            Write back classification not required here, since 
                            the block needs to be inserted into the higher level
                            cache anyways, though dirty bit still needs to be 
                            set accordingly
                            '''
                            self.logger.info('\tWriting back block ' + address + ' to ' + self.next_level.name)
                            temp = self.next_level.write(self.data[index][oldest_tag].address, self.data[index][oldest_tag].is_dirty(), current_step)
                            r.time += temp.time

                            del self.data[index][oldest_tag]
                            self.data[index][tag] = block.Block(self.block_size, current_step, False, address)
                else:
                    print('NINE')
                    #If there's space in this set, add this block to it
                    if len(in_cache) < self.associativity:
                        self.data[index][tag] = block.Block(self.block_size, current_step, False, address)
                    else:
                        #Find the oldest block and replace it
                        oldest_tag = in_cache[0] 
                        for b in in_cache:
                            if self.data[index][b].last_accessed < self.data[index][oldest_tag].last_accessed:
                                oldest_tag = b
                        #Write the block back down if it's dirty and we're using write back
                        if self.write_back:
                            if self.data[index][oldest_tag].is_dirty():
                                self.logger.info('\tWriting back block ' + address + ' to ' + self.next_level.name)
                                temp = self.next_level.write(self.data[index][oldest_tag].address, True, current_step)
                                r.time += temp.time
                        #Delete the old block and write the new one
                        del self.data[index][oldest_tag]
                        self.data[index][tag] = block.Block(self.block_size, current_step, False, address)

        return r   

    def write(self, address, from_cpu, current_step):
        #wat is cache pls
        r = None
        if not self.next_level:
            r = response.Response({self.name:True}, self.write_time)
        else:
            block_offset, index, tag = self.parse_address(address)
            in_cache = list(self.data[index].keys())

            if tag in in_cache:
                #Set dirty bit to true if this block was in cache
                self.data[index][tag].write(current_step)

                if self.policy == 'Exclusive':
                    print('Exclusive cache')

                    r = response.Response({self.name:True}, self.write_time)

                    '''
                    Same explanation as in case of read, see in read above
                    '''
                    if self.name != 'cache_1':
                        del self.data[index][tag]
                else:   
                    if self.write_back:
                        r = response.Response({self.name:True}, self.write_time)
                    else:
                        #Send to next level cache and deepen results if we have write through
                        self.logger.info('\tWriting through block ' + address + ' to ' + self.next_level.name)
                        r = self.next_level.write(address, from_cpu, current_step)
                        r.deepen(self.write_time, self.name)
            else: 
                if self.policy == 'Inclusive':
                    print('Inclusive cache')
                    '''
                    If this method were to be used, for every write call to the
                    higher level caches, the response gotten in the current
                    level would need to be checked for invalidate requests,
                    using the below code snippet (where this code snippet will
                    not be placed here but after every nested write call
                    present in the write function)
                    '''
                    #if self.next_level.name in r.invalidate_list.keys():
                    #    for addr in r.invalidate_list[self.next_level.name]:
                    #        blk_off, ind, tg = self.parse_address(addr)
                    #        in_cach = list(self.data[ind].keys())
                    #        if tg in in_cach:
                    #            del self.data[ind][tg]
                    #    r.invalidate_list[self.next_level.name].clear()

                    if len(in_cache) < self.associativity:
                        self.data[index][tag] = block.Block(self.block_size, current_step, from_cpu, address)
                        if self.write_back:
                            r = response.Response({self.name:False}, self.write_time)
                        else:
                            self.logger.info('\tWriting through block ' + address + ' to ' + self.next_level.name)
                            r = self.next_level.write(address, from_cpu, current_step)
                            r.deepen(self.write_time, self.name) 
                    elif len(in_cache) == self.associativity:
                        oldest_tag = in_cache[0]
                        for b in in_cache:
                            if self.data[index][b].last_accessed < self.data[index][oldest_tag].last_accessed:
                                oldest_tag = b
                        if self.write_back:
                            if self.data[index][oldest_tag].is_dirty():
                                self.logger.info('\tWriting back block ' + address + ' to ' + self.next_level.name)
                                r = self.next_level.write(self.data[index][oldest_tag].address, from_cpu, current_step)
                                r.deepen(self.write_time, self.name)
                        else:
                            self.logger.info('\tWriting through block ' + address + ' to ' + self.next_level.name)
                            r = self.next_level.write(address, from_cpu, current_step)
                            r.deepen(self.write_time, self.name)

                        if not r:
                            r = response.Response({self.name:False}, self.write_time)

                        '''
                        Using the prev level method instead below
                        '''
                        #if self.name != 'cache_1':
                        #    r.invalidate(self.name, self.data[index][oldest_tag].address)
                   
                        '''
                        Invalidate higher level cache block
                        '''
                        if self.prev_level:
                            self.invalidate(self.data[index][oldest_tag].address)

                        del self.data[index][oldest_tag]

                        self.data[index][tag] = block.Block(self.block_size, current_step, from_cpu, address)
                elif self.policy == 'Exclusive':
                    print('Exclusive cache')
                    if len(in_cache) < self.associativity:
                        self.data[index][tag] = block.Block(self.block_size, current_step, from_cpu, address)
                        '''
                        If the to be inserted block in current level is present 
                        in the lower level, remove it and add lower level's
                        access time to the response
                        '''
                        if self.next_level.name != 'mem':
                            self.remove(address)
                        r = response.Response({self.name:False}, self.write_time + self.next_level.write_time)
                    elif len(in_cache) == self.associativity:
                        oldest_tag = in_cache[0]
                        for b in in_cache:
                            if self.data[index][b].last_accessed < self.data[index][oldest_tag].last_accessed:
                                oldest_tag = b
                        '''
                        Write back / through condition checking not required here
                        '''
                        self.logger.info('\tWriting back block ' + address + ' to ' + self.next_level.name)
                        '''
                        Need to write the block being evicted from the current
                        level into the lower level
                        '''
                        r = self.next_level.write(self.data[index][oldest_tag].address, self.data[index][oldest_tag].is_dirty(), current_step)
                        r.deepen(self.write_time, self.name)
                        '''
                        If the to be inserted block in current level is present 
                        in the lower level, remove it but don't add lower
                        level's access time to the response since it has
                        already been considered in the deepen response done
                        above
                        '''
                        if self.next_level.name != 'mem':
                            self.remove(address)

                        del self.data[index][oldest_tag]

                        self.data[index][tag] = block.Block(self.block_size, current_step, from_cpu, address)
                else:
                    print('NINE')

                    if len(in_cache) < self.associativity:
                        #If there is space in this set, create a new block and set its dirty bit to true if this write is coming from the CPU
                        self.data[index][tag] = block.Block(self.block_size, current_step, from_cpu, address)
                        if self.write_back:
                            r = response.Response({self.name:False}, self.write_time)
                        else:
                            self.logger.info('\tWriting through block ' + address + ' to ' + self.next_level.name)
                            r = self.next_level.write(address, from_cpu, current_step)
                            r.deepen(self.write_time, self.name) 
                    elif len(in_cache) == self.associativity:
                        #If this set is full, find the oldest block, write it back if it's dirty, and replace it
                        oldest_tag = in_cache[0]
                        for b in in_cache:
                            if self.data[index][b].last_accessed < self.data[index][oldest_tag].last_accessed:
                                oldest_tag = b
                        if self.write_back:
                            if self.data[index][oldest_tag].is_dirty():
                                self.logger.info('\tWriting back block ' + address + ' to ' + self.next_level.name)
                                r = self.next_level.write(self.data[index][oldest_tag].address, from_cpu, current_step)
                                r.deepen(self.write_time, self.name)
                        else:
                            self.logger.info('\tWriting through block ' + address + ' to ' + self.next_level.name)
                            r = self.next_level.write(address, from_cpu, current_step)
                            r.deepen(self.write_time, self.name)
                        del self.data[index][oldest_tag]

                        self.data[index][tag] = block.Block(self.block_size, current_step, from_cpu, address)
                        if not r:
                            r = response.Response({self.name:False}, self.write_time)

        return r

    '''
    Invalidate higher level cache's block
    '''
    def invalidate(self, address):
        block_offset, index, tag = self.prev_level.parse_address(address)
        in_cache = list(self.prev_level.data[index].keys())
        if tag in in_cache:
            del self.prev_level.data[index][tag]

    '''
    Remove lower level cache's block
    '''
    def remove(self, address):
        block_offset, index, tag = self.next_level.parse_address(address)
        in_cache = list(self.next_level.data[index].keys())
        if tag in in_cache:
            del self.next_level.data[index][tag]

    def parse_address(self, address):
        #Calculate our address length and convert the address to binary string
        address_size = len(address) * 4
        binary_address = bin(int(address, 16))[2:].zfill(address_size)

        block_offset = binary_address[-self.block_offset_size:]
        index = binary_address[-(self.block_offset_size+self.index_size):-self.block_offset_size]
        if index == '':
            index = '0'
        tag = binary_address[:-(self.block_offset_size+self.index_size)]
        return (block_offset, index, tag)

class InvalidOpError(Exception):
    pass
