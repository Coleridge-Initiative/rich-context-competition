The 4 expected output files that should be placed in the folder `/data/output` after each run of the model:

- **data_set_citations.json** - A JSON file that contains publication-dataset pairs for each detected mention of any of the data sets provided in the contest `data_sets.json` file.  The JSON file should contain a JSON list of objects, where each object represents a single publication-dataset pair and includes four properties:

    - `publication_id` - The integer `publication_id` of the publication from `publications.json`.
    - `data_set_id` - The integer `data_set_id` that identifies the cited dataset.
    - `score` - A score on a scale of 0 to 1 representing the level of confidence that the dataset is referenced in the publication.
    - `mention_list` - A list of the text of explicit mentions of the data set in the publication.

- **data_set_mentions.json** - A JSON file that should contain a list of JSON objects, where each object contains a single publication-mention pair for every data set mention detected within each publication, regardless of whether a gvien data set is one of the data sets provided in the contest data set file. Each mention JSON object will includes three properties:

    - `publication_id` - The integer `publication_id` of the publication from `publications.json`.
    - `mention` - The specific data set mention text found in the publication.  Each mention gets its own JSON object in this list.
    - `score` - A score on a scale of 0 to 1 representing the level of confidence that the mention text references data.

- **methods.json** - A JSON file that should contain a list of JSON objects, where each object captures publication-method pairs via three properties:

    - `publication_id` - The integer `publication_id` of the publication from `publications.json`.
    - `method` - The inferred method used by the research in the publication.
    - `score` - A score on a scale of 0 to 1 representing the level of confidence that the method is used in the publication.

- **research_fields.json** - A JSON file that should contain a list of JSON objects, where each object captures publication-research field pairs via three properties:

    - `publication_id` - The integer `publication_id` of the publication from `publications.json`.
    - `research_field` - The inferred research field of the research in the publication.
    - `score` - A score on a scale of 0 to 1 representing the level of confidence that the publication is in the stated research field.
