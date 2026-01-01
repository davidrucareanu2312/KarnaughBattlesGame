def get_binary(n, num_vars):
    return format(n, f'0{num_vars}b')

def combine_terms(t1, t2):
    diff_count = 0
    res = []
    for c1, c2 in zip(t1, t2):
        if c1 == c2:
            res.append(c1)
        else:
            diff_count += 1
            res.append('-')
    
    if diff_count == 1:
        return "".join(res)
    return None

def get_prime_implicants(minterms, num_vars):
    groups = {}
    for m in minterms:
        count = m.count('1')
        if count not in groups: groups[count] = set()
        groups[count].add(m)
    
    prime_implicants = set()
    checked = set()
    
    while True:
        new_groups = {}
        changed = False
        sorted_counts = sorted(groups.keys())
        
        for i in range(len(sorted_counts) - 1):
            c1 = sorted_counts[i]
            c2 = sorted_counts[i+1]
            
            if c2 != c1 + 1 and '-' not in next(iter(groups[c1])): 
                pass

            for t1 in groups[c1]:
                for t2 in groups[c2]:
                    merged = combine_terms(t1, t2)
                    if merged:
                        checked.add(t1)
                        checked.add(t2)
                        
                        c_new = merged.count('1')
                        if c_new not in new_groups: new_groups[c_new] = set()
                        new_groups[c_new].add(merged)
                        changed = True
        
        for c in groups:
            for t in groups[c]:
                if t not in checked:
                    prime_implicants.add(t)
        
        if not changed:
            break
            
        groups = new_groups
        checked = set()
        
    return prime_implicants

def solve_karnaugh(cells, dont_care_indices, num_vars):
    minterm_indices = []
    dc_indices = set(dont_care_indices)
    
    for i, val in enumerate(cells):
        if val == 1 and i not in dc_indices:
            minterm_indices.append(i)
    
    if not minterm_indices:
        return "0"
        
    if len(minterm_indices) + len(dc_indices) == len(cells):
        return "1"

    all_indices = minterm_indices + list(dc_indices)
    binary_terms = [get_binary(i, num_vars) for i in all_indices]
    
    pis = get_prime_implicants(binary_terms, num_vars)
    
    pi_coverage = {}
    for pi in pis:
        pi_coverage[pi] = set()
        for m_idx in minterm_indices:
            m_bin = get_binary(m_idx, num_vars)
            match = True
            for k in range(num_vars):
                if pi[k] != '-' and pi[k] != m_bin[k]:
                    match = False
                    break
            if match:
                pi_coverage[pi].add(m_idx)
                
    final_pis = []
    uncovered_minterms = set(minterm_indices)
    
    while uncovered_minterms:
        best_pi = None
        best_cover_count = -1
        
        for pi, covered_set in pi_coverage.items():
            current_cover = covered_set.intersection(uncovered_minterms)
            if len(current_cover) > best_cover_count:
                best_cover_count = len(current_cover)
                best_pi = pi
        
        if best_pi is None:
            break
            
        final_pis.append(best_pi)
        uncovered_minterms -= pi_coverage[best_pi]
        del pi_coverage[best_pi]

    if not final_pis: return "0"
    
    full_var_names = ['A', 'B', 'C', 'D']
    var_names = full_var_names[:num_vars]
    
    text_terms = []
    
    for pi in final_pis:
        term = ""
        for i, char in enumerate(pi):
            if char == '0':
                term += var_names[i] + "'"
            elif char == '1':
                term += var_names[i]
        if term == "": term = "1"
        text_terms.append(term)
        
    return " + ".join(text_terms)