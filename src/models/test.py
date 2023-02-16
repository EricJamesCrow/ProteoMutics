import BedtoolsCommands
import Statistics
import General
from pathlib import Path

General.adjust_dyad_positions(
    dyad_file=Path('/media/cam/Data9/CortezAnalysis/Cam_calls/nucleosome_stuff/dyads.bed')
)

BedtoolsCommands.bedtools_getfasta(
    dyad_file=Path('/media/cam/Data9/CortezAnalysis/Cam_calls/nucleosome_stuff/dyads_plus-minus_500.bed'),
    fasta_file=Path('/media/cam/Data9/CortezAnalysis/pipeline_files/hg19.fa')
)