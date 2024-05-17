import sys
import json
from Cache_Level import CacheLevel

'''
This file contains the entry point for the sumulator.

(Note: the implemented simulator doesn't take into consideration the size of the data in the trace file. Therefore, when the data size exceeds 
the cache line size, it doesn't result in multiple access of the same memory address.)
'''

cache_hierarchy = []   #list representing the cache hierarchy (stores each cache level as a Cache_Level object)
mem_access = 0   #count for the number of times main memory has been accessed

def main():
    if len(sys.argv) != 3: 
        print("Usage: python Cache_Simulator.py <configuration file> <trace file>")
        return

    config_file = sys.argv[1]
    trace_file = sys.argv[2]
    
    cache_config = read_config(config_file)   #reads the congifuration
    set_up_cache(cache_config)   #sets up the cache structure using the configuration
    trace_program(trace_file)   #reads the trace file
    output_stats("output.json")   ##outputs the result
    
#reads the configuration file and prases the JSON data
def read_config(config_file):
    try:
        with open(config_file, 'r') as file:
            json_data = json.load(file)   #parses the JSON file
    except FileNotFoundError:
        print(f"File not found: {config_file}")
    except json.JSONDecodeError as e:
        print(f"JSON decoding error: {e}")
        
    return json_data

#uses the specified configuration to set up the cache hierarcy 
def set_up_cache(cache_config):
    global cache_hierarchy
    cache_levels = cache_config.get('caches', [])   #gets the cache list from the parsed configuration file

    if cache_levels:
        for cache in cache_levels:
            if len(cache) == 4:   #conditional based on whether replacement policy has been specified or not
                cache_instance = CacheLevel(cache['name'], cache['size'], cache['line_size'], cache['kind'], "")  #creates a Cache_Level object with the relevant configuration information
            else: 
                cache_instance = CacheLevel(cache['name'], cache['size'], cache['line_size'], cache['kind'], cache['replacement_policy'])
            cache_hierarchy.append(cache_instance)   #adds the cache level to the cache hierarchy list 
    else:
        print("No 'cache' array found in the JSON data.")

#reads each line in the trace file to simulate running a program   
def trace_program(trace_file):
    try:
        with open(trace_file, 'r') as file:
            for line in file:   #reads each line of the trace file
                line = line.strip()
                data = line.split()
                
                if len(data) == 4:   #conditional based on whether all the required fields are present in each line
                    mem_addr = data[1]   #reads the memory address
                    size = data[3]   #reads the size of the data (not utilised)
                else:
                    print(f"Invalid line: {line}")
                    continue

                access_cache_heirarcy(mem_addr)   #passes the memory address to check with the cache hierarchy
                
    except FileNotFoundError:
        print(f"File not found: {trace_file}")
    except Exception as e:
        print(f"Error: {e}")

#takes a memory address from the trace file to and checks each cache level for its presence
def access_cache_heirarcy(address):
    global mem_access

    for cache in cache_hierarchy:
        if cache.search_cache(address):   #conditional based on whether the memory address causes a hit or a miss in the current cache level 
            return   #stops going through the cache hierarchy if it's a hit
        else:
            continue   #checks the next cache level if it's a miss

    mem_access += 1   #checks the main memory if memory address causes a miss in all the cache levels

#outputs the result
def output_stats(output_file):
    output_JSON = {"caches": [], "main_memory_access": mem_access}   #JSON representation for the output 

    for cache in cache_hierarchy:   #gets the result of going through the trace file for each cache level in the hierachy 
        output_JSON['caches'].append({
            "hits": cache.hits,
            "misses": cache.misses,
            "name": cache.name
        })
    
    with open(output_file, 'w') as file:
        json.dump(output_JSON, file, indent=4)   #writes the results to the output JSON file

if __name__ == "__main__":
    main()