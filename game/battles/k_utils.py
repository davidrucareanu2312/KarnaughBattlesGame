def check_complete(self):
        covered_indices = set()
        for group in self.selected_groups:
            covered_indices.update(group)

        for idx, val in enumerate(self.cells):
            if idx in self.dont_care:
                continue
            
            if val == 1 and idx not in covered_indices:
                return False
                
        return True


def is_valid_group(group, cells, dont_care, rows, cols):
    n = len(group)
    if n == 0: return False
    if n & (n-1) != 0:
        return False

    for idx in group:
        if idx in dont_care:
            continue
        
        if cells[idx] != 1:
            return False

    coords = [(idx // cols, idx % cols) for idx in group]
    row_list = sorted(r for r, c in coords)
    col_list = sorted(c for r, c in coords)

    possible_heights = [2**i for i in range(int(rows).bit_length()) if 2**i <= rows]
    possible_widths  = [2**i for i in range(int(cols).bit_length()) if 2**i <= cols]

    for h in possible_heights:
        for w in possible_widths:
            for start_r in range(rows):
                for start_c in range(cols):
                    rect_cells = set()
                    for dr in range(h):
                        for dc in range(w):
                            r = (start_r + dr) % rows
                            c = (start_c + dc) % cols
                            rect_cells.add(r*cols + c)
                    if rect_cells == group:
                        return True

    return False


def term_from_group(group, num_vars, rows, cols):
    if num_vars == 2:
        var_names = ['A', 'B']
    elif num_vars == 3:
        var_names = ['A', 'B', 'C']
    elif num_vars == 4:
        var_names = ['A', 'B', 'C', 'D']
    elif num_vars == 5:
        var_names = ['A', 'B', 'C', 'D', 'E']
    elif num_vars == 6:
        var_names = ['A', 'B', 'C', 'D', 'E', 'F']

    binary_vals = [format(idx, f'0{num_vars}b') for idx in group]

    term = ''
    for i in range(num_vars):
        bits = set(b[i] for b in binary_vals)
        
        if len(bits) == 1:
            bit_val = bits.pop()
            if bit_val == '0':
                term += var_names[i] + "'"
            else:
                term += var_names[i]
                
    return term