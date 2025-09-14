import os
import re
import json
from collections import defaultdict
from pathlib import Path
from copy import deepcopy

class SyzkallerParser:
    def __init__(self, file_content):
        self.lines = [line.strip() for line in file_content.split('\n') if line.strip() and not line.strip().startswith('#')]
        
        self.master_structs = {}
        self.master_flags = {}
        self.master_resources = {}
        self.master_includes = []
        self.syscall_definitions = []

    def parse(self):
        struct_defs = self._extract_blocks('{', '}')
        for name, block in struct_defs.items():
            self._parse_struct(name, block)

        remaining_lines = self._get_non_struct_lines()
        for line in remaining_lines:
            if line.startswith('include'):
                self.master_includes.append(line)
            elif ' = ' in line and '[' not in line:
                self._parse_flags(line)
            elif line.startswith('resource'):
                self._parse_resource(line)
            elif '(' in line and ')' in line:
                self.syscall_definitions.append(line)

    def generate_json_files(self, output_dir):
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        if not self.syscall_definitions:
            return

        for syscall_line in self.syscall_definitions:
            syscall_data = self._build_syscall_json(syscall_line)
            if syscall_data is None:
                continue
            
            syscall_name = syscall_data['name'].replace('$', '_')
            file_path = Path(output_dir) / f"{syscall_name}.json"
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(syscall_data, f, indent=4, ensure_ascii=False)

    def _build_syscall_json(self, syscall_line):
        match = re.match(r'([\w$]+)\((.*)\)', syscall_line)
        if not match:
            return None
        name, args_str = match.groups()
        
        syscall_data = {
            "name": name,
            "arguments": [],
            "dependencies": {
                "includes": self.master_includes,
                "structs": set(),
                "flags": set(),
                "resources": set()
            },
            "referenced_structures": {},
            "referenced_flags": {}
        }

        if args_str:
            args_list = re.split(r',\s*(?![^\[\]]*\])', args_str)
            for arg_string in args_list:
                parsed_arg = self._parse_argument(arg_string.strip())
                syscall_data["arguments"].append(parsed_arg)
                self._collect_dependencies(parsed_arg, syscall_data["dependencies"])
        
        for dep_type in ["structs", "flags", "resources"]:
            dep_set = syscall_data["dependencies"][dep_type]
            syscall_data["dependencies"][dep_type] = sorted(list(dep_set))
            
            if dep_type == "structs":
                for s_name in dep_set:
                    syscall_data["referenced_structures"][s_name] = deepcopy(self.master_structs[s_name])
            elif dep_type == "flags":
                for f_name in dep_set:
                    syscall_data["referenced_flags"][f_name] = self.master_flags[f_name]

        for struct_def in syscall_data["referenced_structures"].values():
            for field in struct_def.get("fields", []):
                self._enrich_field_recursively(field)
                
        return syscall_data
    
    def _enrich_field_recursively(self, field_data):
        if field_data.get("base_type") == "flags":
            flag_group = field_data.get("flag_group")
            if flag_group and flag_group in self.master_flags:
                field_data["values"] = self.master_flags[flag_group]

        if "element_type" in field_data:
            self._enrich_field_recursively(field_data["element_type"])

    def _collect_dependencies(self, parsed_element, dependencies):
        base_type = parsed_element.get('base_type')
        type_name = parsed_element.get('type')

        if base_type == 'struct' and type_name in self.master_structs:
            if type_name not in dependencies['structs']:
                dependencies['structs'].add(type_name)
                for field in self.master_structs[type_name]['fields']:
                    self._collect_dependencies(field, dependencies)
        elif base_type == 'flags' and parsed_element.get('flag_group') in self.master_flags:
            dependencies['flags'].add(parsed_element['flag_group'])
        elif base_type == 'resource' and type_name in self.master_resources:
            dependencies['resources'].add(type_name)

        if 'element_type' in parsed_element:
            self._collect_dependencies(parsed_element['element_type'], dependencies)

    def _parse_argument(self, arg_string):
        parts = arg_string.split(None, 1)
        if not parts:
            return {"name": "unknown", "raw_type": arg_string, "base_type": "unparsable"}
        
        name = parts[0]
        type_str = parts[1] if len(parts) > 1 else ""
        
        match = re.match(r'([\w\d\.$]+)(?:\[(.*)\])?', type_str)
        if match is None:
            return {"name": name, "raw_type": type_str, "base_type": "unparsable"}

        base_type, attrs_str = match.groups()
        result = {"name": name, "raw_type": type_str}

        if base_type == "flags" and attrs_str:
            result['base_type'] = 'flags'
            result['type'] = type_str
            flag_parts = [p.strip() for p in attrs_str.split(',')]
            if flag_parts:
                result['flag_group'] = flag_parts[0]
            if len(flag_parts) > 1:
                result['underlying_type'] = flag_parts[1]
        else:
            attrs, element_type_info = self._parse_attributes(attrs_str)
            result.update(attrs)
            result['base_type'] = self._determine_base_type(base_type)
            result['type'] = element_type_info if element_type_info else base_type

        if 'element_type' in result:
            nested_arg_str = f"element {result['element_type']}"
            result['element_type'] = self._parse_argument(nested_arg_str)
            del result['element_type']['name']
        
        return result

    def _parse_attributes(self, attrs_str):
        if not attrs_str:
            return {}, None
            
        attrs = {}
        element_type_info = None
        attr_list = re.split(r',\s*(?![^\[\]]*\])', attrs_str)
        
        for attr in attr_list:
            if attr in ['in', 'out', 'inout']:
                attrs['direction'] = attr
            elif attr == 'opt':
                attrs['is_optional'] = True
            elif attr.startswith('len['):
                attrs['is_len'] = True
                attrs['len_for'] = attr[4:-1]
            elif attr.startswith('array['):
                attrs['is_array'] = True
                element_type_info = attr[6:-1]
            elif attr.startswith('const['):
                attrs['is_const'] = True
                val_parts = attr[6:-1].split(',')
                attrs['const_val'] = val_parts[0].strip()
                if len(val_parts) > 1:
                    attrs['underlying_type'] = val_parts[1].strip()
            elif attr in self.master_resources:
                element_type_info = attr
        
        return attrs, element_type_info

    def _determine_base_type(self, type_name):
        if type_name in self.master_structs:
            return 'struct'
        elif type_name in self.master_resources:
            return 'resource'
        elif type_name.startswith('fd'):
            return 'file_descriptor'
        elif type_name in ['ptr', 'ptr64', 'vma', 'buffer']:
            return 'pointer'
        elif 'int' in type_name or type_name in ['len', 'const', 'proc']:
            return 'integer'
        else:
            return 'unknown'

    def _parse_struct(self, name, block_lines):
        struct_info = {"name": name, "fields": []}
        for line in block_lines:
            line = line.strip()
            if not line: continue
            parsed_field = self._parse_argument(line)
            struct_info["fields"].append(parsed_field)
        self.master_structs[name] = struct_info

    def _parse_flags(self, line):
        name, values_str = line.split(' = ')
        values = [v.strip() for v in values_str.split(',')]
        self.master_flags[name.strip()] = values

    def _parse_resource(self, line):
        match = re.match(r'resource\s+([\w\d]+)\[(.*)\]', line)
        if match:
            name, base_type = match.groups()
            self.master_resources[name] = base_type

    def _extract_blocks(self, start_delim, end_delim):
        blocks = {}
        in_block = False
        current_block_name = None
        current_block_lines = []
        block_start_re = re.compile(r'([\w\d\.$]+)\s*' + re.escape(start_delim))

        for line in self.lines:
            if not in_block:
                match = block_start_re.match(line)
                if match:
                    in_block = True
                    current_block_name = match.group(1)
            else:
                if line.startswith(end_delim):
                    in_block = False
                    blocks[current_block_name] = current_block_lines
                    current_block_name = None
                    current_block_lines = []
                else:
                    current_block_lines.append(line)
        return blocks
    
    def _get_non_struct_lines(self):
        non_struct_lines = []
        in_block = False
        block_start_re = re.compile(r'[\w\d\.$]+\s*\{')

        for line in self.lines:
            if block_start_re.search(line):
                in_block = True
            if not in_block:
                non_struct_lines.append(line)
            if '}' in line:
                in_block = False
        return non_struct_lines

if __name__ == '__main__':
    input_directory = "./syzkaller_definitions"
    output_directory = "./syscall_json"
    
    Path(input_directory).mkdir(exist_ok=True)
    
    input_files = list(Path(input_directory).glob('*.txt'))
    
    for file_path in input_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            parser = SyzkallerParser(content)
            parser.parse()
            parser.generate_json_files(output_directory)

        except Exception as e:
            pass

