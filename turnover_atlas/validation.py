import six
from filters.schema import base_query_params_schema
from filters.validations import IntegerLike

turnover_data_schema = base_query_params_schema.extend(
    {
        "id": IntegerLike(),
        "Protein_Group": six.text_type,
        "Protein_Ids": six.text_type,
        "Protein_Names": six.text_type,
        "Genes": six.text_type,
        "Proteotypic": IntegerLike(),
        "Stripped_Sequence": six.text_type,
        "Modified_Sequence": six.text_type,
        "Precursor_Id": six.text_type,
        "n_Samples": IntegerLike(),
        "n_TimePoints": IntegerLike(),
        "Engine": six.text_type,
        "Tissue": six.text_type,
    }
)

accession_id_map_schema = base_query_params_schema.extend(
    {
        "id": IntegerLike(),
        "Protein_Group": six.text_type,
        "Genes": six.text_type,
    }
)