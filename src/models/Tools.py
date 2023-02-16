import itertools

def contexts_in_iupac(iupac_val: str):
    """Takes a string that has IUPAC characters and returns all of the possible nucleotide sequences that fit that 
    IUPAC character as a list

    Args:
        iupac_val (str): the IUPAC format of the desired nucleotide sequences

    Returns:
        possible combinations (list): a list of all possible nucleotide combinations that fit within that iupac form
    """

    iupac_trans = { "R":"AG", "Y":"CT", "S":"GC", "W":"AT", "K":"GT",
                    "M":"AC","B":"CGT", "D":"AGT", "H":"ACT", "V":"ACG",
                    "N":"ACTG", 'A':'A', 'T':'T', 'C':'C', 'G':'G'}
    possible_contexts = []
    
    def convertTuple(tup):
        """
        converts a tuple to a string
        """
        str = ''
        for item in tup:
            str = str + item
        return str

    list1 = []
    list1[:0] = iupac_val
    possible_combinations = []
    for combination in itertools.product(list1):
        possible_contexts.append(iupac_trans[convertTuple(combination)])
    ranges = [x for x in possible_contexts]
    for i in itertools.product(*ranges):
        possible_combinations.append(convertTuple(i))
    return possible_combinations

def reverse_complement(seq: str):
    """returns the reverse complement of nucleotide sequences in standard or IUPAC notation

    Args:
        seq (str): sequence of DNA in standard or IUPAC form that

    Returns:
        reverse_complement (str): the reverse complement of the input sequence
    """

    complement = {'A': 'T', 'C': 'G', 'G': 'C', 'T': 'A',
                        "R":"Y", "Y":"R", "S":"S", "W":"W", "K":"M",
                        "M":"K","B":"V", "D":"H", "H":"D", "V":"B",
                        "N":"N"}
    return "".join(complement.get(base, base) for base in reversed(seq))