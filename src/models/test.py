import BedtoolsCommands
import Statistics
import General
from pathlib import Path

# General.adjust_dyad_positions(
#     dyad_file=Path('/media/cam/Data9/CortezAnalysis/Cam_calls/nucleosome_stuff/dyads.bed')
# )

# BedtoolsCommands.bedtools_getfasta(
#     dyad_file=Path('/media/cam/Data9/CortezAnalysis/Cam_calls/nucleosome_stuff/dyads_plus-minus_500.bed'),
#     fasta_file=Path('/media/cam/Data9/CortezAnalysis/pipeline_files/hg19.fa')
# )

# fasta_counter = Statistics.DyadFastaCounter(Path('/media/cam/Data9/CortezAnalysis/Cam_calls/nucleosome_stuff/dyads_plus-minus_500.fa'))
# fasta_counter.run()

fasta_counter = Statistics.DyadFastaCounter(Path('/media/cam/Data9/CortezAnalysis/Cam_calls/nucleosome_stuff/head1000.fa'))
fasta_counter.run()

# def count_line(sequence: str):
#         # creates a dictionary that will hold onto the nucleotide position and the counts of each nucleotide
#         counts = {}
#         for i in range(-500, 501):
#             counts.setdefault(i, [0, 0, 0, 0, 0])

#         # counts the nucleotides at each position
#         for i, base in zip(range(-500, 501), sequence):
#             if base == 'A':
#                 counts[i][0] += 1
#             elif base == 'C':
#                 counts[i][1] += 1
#             elif base == 'G':
#                 counts[i][2] += 1
#             elif base == 'T':
#                 counts[i][3] += 1
#             else:
#                 counts[i][4] += 1

#         # return counts
#         return counts
# print(count_line('taaaagtatcccttacgggaaatgaagggatgggccggaataaaggggtgggtttggctagttatctgcagcaggagcatgccctgatggcacagatcgctcatgctatgtttgtggtttgagaacgtctttcagcggttttccaccctgggcgggtcaggtgttccttgccctcattccggtaaacccacaaccttccagcgtgggcgttagggccattatgaacatgtcacagtgctgcagagattttgtttatggccagttttgtggccagtttatggccagattttggggggcctgttcccaacaGTAACCAATATTAAGTCATTCTCATTTCAACATTTAAACTCTTCCAACTGAATGCATTAAAAAACAAAAGTCACACACCACTGTACCCCTTATATGTACACAGCGGTCGGCAAACATGTGACAGGTGGAGGTCCTGAGGCACCACTGGGAGCTTGTGAGCGGATGGGCGTCTTCCAGAACGCACTCTGCAGGCACTCGGCAACGTGAAGTGTTCACGTCCTGTGATGCAGCCTCTGCTCCAGGCCACTTCCGGAACTGCGAGGGAACAGCTGTGGGCGCGCTCATTTCAGCTTTGCTTCAGATCCTGGGAGTTGGGGGCACCttctttttttttttttttttttttagacggagtcttgctctgtcacccaggctggagtgcagtggcgcgatctcggctcactgcaagctccgcctcccgggttcacgccattctcctgcctcagcctcccgagtagctgggactacaggcgcccgccaccgtgcctggctaattttttgtatttttagtacagacggggtttcaccatgttagccaggatggtctcgatctcctgacctcgtgatccgcccatctcggcctcccataaagtgctgggattacaggcatgagccaccgcgcccggcTGGGGGCACCTTCTGGCCCACAGTGAGGGAATAAGCAAACCAGAATGGGGGGTGCCTGCACGGAA'.upper()))