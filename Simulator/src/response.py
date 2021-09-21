class Response:
    def __init__(self, hit_list, time, data='', invalidate_list={}):
        self.hit_list = hit_list
        self.time = time
        self.data = data
        self.invalidate_list = invalidate_list

    def deepen(self, time, name):
        self.hit_list[name] = False
        self.time += time

    '''
    Add invalidate request for the higher level cache to invalidate the block at
    this address if present
    '''
    def invalidate(self, name, address):
        if name not in self.invalidate_list.keys():
            self.invalidate_list[name] = [address]
        else:
            self.invalidate_list[name].append(address)
    
