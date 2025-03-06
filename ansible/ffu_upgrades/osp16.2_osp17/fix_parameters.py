#!/usr/libexec/platform-python

import argparse

REPLACE_KEY='namespace: registry.redhat.io/rhosp-rhel9'
remove_map = {
        '- horizon': None,
        '- heat-engine': None,
        '- neutron-server': None}
replace_map = {REPLACE_KEY: {
    'line': None,
    'replacement': '      namespace: registry.redhat.io/rhosp-rhel8'}}

def replace_last_instance(file_path, remove_map, replace_map):
    # Read the file contents into a list of lines
    with open(file_path, 'r') as in_file:
        lines = in_file.readlines()

    # Find the last occurrence of the search line
    for index, line in enumerate(lines):
        key = line.strip()
        if key in replace_map.keys():
            replace_map[key]['line'] = index
        elif key in remove_map.keys():
            remove_map[key] = index

    # Replace the line if found
    replace_dict = replace_map[REPLACE_KEY]
    if replace_dict['line'] is not None:
        lines[replace_dict['line']] = replace_dict['replacement'] + '\n'

    remove_indeces = [val for val in remove_map.values() if val]

    # Write the modified lines back to the file
    with open(file_path, 'w') as out_file:
        for index, line in enumerate(lines):
            if index in remove_indeces:
                continue
            out_file.write(line)


def main():
    parser = argparse.ArgumentParser(description='Fix containers prepare parameter file')

    file_path = '/home/stack/containers-prepare-parameter.yaml'
    parser.add_argument("-f", "--file",
	              help="Containers prepare parameter file path",
		      dest="file_path")
    options = parser.parse_args()
    if options.file_path:
        file_path = options.file_path
    replace_last_instance(file_path, remove_map, replace_map)

if __name__ == "__main__":
    main()
