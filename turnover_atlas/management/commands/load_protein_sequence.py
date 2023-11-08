import json
import re
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from turnover_atlas.models import ProteinSequence
from uniprotparser.betaparser import UniprotSequence

class Command(BaseCommand):
    """
    A command that read fasta sequence data from a file and save into ProteinSequence model.
    """
    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path to the fasta file to be processed')

    def handle(self, *args, **options):
        file_path = options['file_path']
        with transaction.atomic():
            with open(file_path, "r") as f:
                current_acc = ""
                current_seq = ""
                for i in f:
                    if i.startswith(">"):
                        acc = UniprotSequence(i.strip(), True)
                        if acc.accession:
                            accd = str(acc)
                            if current_acc != "" and current_acc != accd and current_seq != "":
                                ProteinSequence.objects.create(
                                    AccessionID=current_acc[:],
                                    Sequence=current_seq[:]
                                )
                            current_acc = accd

                            current_seq = ""
                        else:
                            current_acc = ""
                    else:
                        current_seq += i.strip()
                if current_acc != "" and current_seq != "":
                    ProteinSequence.objects.create(
                        AccessionID=current_acc,
                        Sequence=current_seq
                    )


