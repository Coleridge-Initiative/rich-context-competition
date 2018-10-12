# Rich Context Contest Evaluation and Submission Kit

This repository contains supporting files for self-evaluation (with a development fold corpus) and submitting an entry for the [Rich Context Text Analysis Competition](https://coleridgeinitiative.org/richcontextcompetition). Here you will find all the materials and instructions you will need to build your competition submission. 

You should develop (train and test) your model on your own machine or server. Once you are ready to submit, you will use the files and scripts here to create a docker container that contains all code, libraries, and additional data and resources required to train and run your model. Each group of participants will be given access to a private Box folder shared with contest organizers that will be pre-populated with this repository along with the dev fold, a sample data folder, a sample project folder, and the train-test data for the competition. To submit, inside their Box folder, each group will:

* Place their trained model's data and code in a project folder along with a script that accepts a data folder path and runs the model against the specified data directory (standard data directory layout specified below).

* Implement a Dockerfile that can be run anywhere (see [Dockerfile Setup](https://github.com/Coleridge-Initiative/rich-context-competition/wiki/Dockerfile-Setup) for more details), built on the Ubuntu 18.04 base image, that installs and configures a docker image that can call the model execution script and run it against any directory that has a standard data folder layout (described [below](#data-folder-specification)).

Below are instructions and specifications to assist you setting up and configuring your submission container.

# Rules of Engagement

We suggest that you build, train, and test your model in an environment you are comfortable with, then once you have it working, migrate it to a docker container.

The Rich Context Contest staff will do our best to help you with problems related to storing your model and data in a git repo and updating the other related files so we can accept and run it in a docker image. We can not provide support for software you use to implement your model.


# Technical Details

## Requirements - Installing Docker

Please make sure you have Docker installed on your machine before you start work on performing the dev fold evaluation or preparing your submission. This project was created using Docker version `Docker version 18.06.1-ce, build e68fc7a`. Please make sure to use the current version at the time of submission to avoid version-related issues.

See details for installing Docker on your system in our [Docker Installation](https://github.com/Coleridge-Initiative/rich-context-competition/wiki/Docker-Installation) notes.

## Helper script `rcc.sh`

We created bash shell helper script, "`rcc.sh`", to facilitate making and testing a submission and working with Docker. To run the script, navigate into the root of your group's Box folder, then run `./rcc.sh <action>`. The supported actions are listed in specific on our wiki section for [Helper Script (rcc.sh)](https://github.com/Coleridge-Initiative/rich-context-competition/wiki/Helper-Script-(rcc.sh)). 

Certain specifics of your environment must be specified in a separate configuration shell script (config.sh), that [we provide pre-populated with examples](https://github.com/Coleridge-Initiative/rich-context-competition/blob/master/config.sh) that you can use to test all the actions.

Notes:

- On linux, by default, docker is installed so it can only be managed by the root user. This means you'll have to run "`rcc.sh`" script actions that interact with docker as root, as well (all the `build` and `run` actions, for example). You can use `sudo` or `su` to root and do this as needed, but this can get messy in terms of the permissions of the files in this submission folder. One option to consider if you can on your server is to configure your user so it is in the docker OS group, and so able to manage docker without root access: [https://docs.docker.com/install/linux/linux-postinstall/#manage-docker-as-a-non-root-user](https://docs.docker.com/install/linux/linux-postinstall/#manage-docker-as-a-non-root-user). See detailed instructions above in the "Requirements" section.

- Box doesn't reliably track execute permissions of files from unix-based OSes.  So when you either navigate to your group's project folder synced by Box on macOS or download the contents of your group's Box folder and move them to a linux machine or virtual machine to work on preparing your submission, be aware that even though the shell script files are stored in git with permissions to allow them to be executed, Box does not persist those permissions, and so you will need to update the shell scripts in your project folder to be executable.  Commands to do this for the necessary scripts:

    - rcc.sh - `chmod u+x rcc.sh`
    - config.sh - `chmod u+x config.sh`
    - project/code.sh - `chmod u+x project/code.sh`

### Configuration script

    #!/bin/bash
	
    # The config file can include:
    # - `BASE_FOLDER_IN` - base folder (usually where this script lives).
    # - `DATA_FOLDER_PATH_IN` (`-d` option) - path to the data folder for a given run of the model.
    # - `PROJECT_FOLDER_PATH_IN` (`-p` option) - path to the project folder for the current model.
    # - `GIT_REPO_FOLDER_PATH_IN` - the path to the git repo (defaults to "/rich-context-competition" inside the base folder).
    # - `EVALUATE_FOLER_PATH_IN` - path to the evaluate code folder inside the git repository.
    # - `TEMPLATE_FOLDER_PATH_IN` - path to the template code folder inside the git repository.
    # - `DOCKER_IMAGE_NAME_IN` - Image name to use locally for submission image, defaults to "my_rcc".
    # - `DOCKER_CONTAINER_NAME_IN` - Container name to use locally for the instance of the image used to test and run your model, defaults to "${DOCKER_IMAGE_NAME_IN}_run"
    # - `USE_BUILD_CACHE_IN` - default behavior for build cache use with the base "build" action. Defaults to false (no cache).
    # - `DEBUG` - set to "`true`" or "`false`". If set to "`true`", results in much more verbose output.

    # set configuration variables
    BASE_FOLDER_PATH_IN="."

    # model-related folders
    DATA_FOLDER_PATH_IN="${BASE_FOLDER_PATH_IN}/data"
    PROJECT_FOLDER_PATH_IN="${BASE_FOLDER_PATH_IN}/project"

    #===============================================================================
    # WARNING - do not alter below this point unless you know what you are doing.
    #===============================================================================

    # git repo folders
    GIT_REPO_FOLDER_PATH_IN="${BASE_FOLDER_PATH_IN}/rich-context-competition"
    EVALUATE_FOLDER_PATH_IN="${GIT_REPO_FOLDER_PATH_IN}/evaluate"
    TEMPLATE_FOLDER_PATH_IN="${GIT_REPO_FOLDER_PATH_IN}/templates"

    # docker
    DOCKER_IMAGE_NAME_IN="my_rcc"
    DOCKER_CONTAINER_NAME_IN="${DOCKER_IMAGE_NAME_IN}_run"
    USE_BUILD_CACHE_IN=false

    # debug
    DEBUG=true

You should only need to set the variables `DATA_FOLDER_PATH_IN` and `PROJECT_FOLDER_PATH_IN`. The rest you should leave set to defaults unless you really know what you are doing.

### rcc.sh - Test that everything works

After you download this repo directory and have [Docker installed](https://github.com/Coleridge-Initiative/rich-context-competition/wiki/Docker-Installation) on your computer, navigate to the home direcotry where the `./rcc.sh` is located and run the following commands:

- `./rcc.sh build`
- `./rcc.sh run`
- `./rcc.sh stop`
- `./rcc.sh evaluate`

You should see some boilerplate output and no errors. If all goes well, you should do a cleanup and reset with:

- `./rcc.sh stop`
- `./rcc.sh remove-docker-image`
- `./rcc.sh reset-data-folder`
- `./rcc.sh run-stop`


### rcc.sh - Clean run against dev fold

To rebuild your container and run it against a fresh dev fold data directory, execute the following commands:

- `./rcc.sh stop`
- `./rcc.sh remove-docker-image`
- `./rcc.sh reset-data-folder`
- `./rcc.sh run-stop`
- `./rcc.sh evaluate`

## Data folder specification

The standard data folder layout:

    data
    |_input
    |   |_files
    |      |_text
    |      |_pdf
    |_output


### Input files

The input folder will have a "`publications.json`" file that lists the articles to be processed in the current run of the model. Publication plain text is stored in /input/files/text, one text file to a publication, with a given publication's text named "`<publication_id>.txt`". The original PDF files are stored in /input/files/pdf, one PDF file to a publication, with a given publication's text named "`<publication_id>.pdf`". 

- The **`publications.json`** file is a JSON list of JSON objects, each of which contains:

    - `pub_date` - Publication date of the article, in "YYYY-MM-DD" format.
    - `unique_identifier` - Unique identifier provided by the publication's source. Could be a URL or other URI, etc.
    - `text_file_name` - file name of the publication's text file, "`<publication_id>.txt`". Does not include path information. All text files are stored in `/input/files/text`.
    - `pdf_file_name` - file name of the publication's PDF file, "`<publication_id>.pdf`". Does not include path information. All PDF files are stored in `/input/files/pdf`.
    - `publication_id` - Integer ID of the publication, unique within the set of publications stored in a given "`publications.json`" file. This is the ID that should be referred to in output JSON files when you tie your results to a given publication.

Example:

    [
    	 {
            "text_file_name": "166.txt",
            "unique_identifier": "10.1093/geront/36.4.464",
            "pub_date": "1996-01-01",
            "title": "Nativity, declining health, and preferences in living arrangements among elderly Mexican Americans: Implications for long-term care",
            "publication_id": 166,
            "pdf_file_name": "166.pdf"
        },
        {
            "text_file_name": "167.txt",
            "unique_identifier": "10.1093/geronb/56.5.S275",
            "pub_date": "2001-01-01",
            "title": "Duration or disadvantage? Exploring nativity, ethnicity, and health in midlife",
            "publication_id": 167,
            "pdf_file_name": "167.pdf"
        },
    	...
    ]

### Output files

4 expected output files should be placed in the folder `data/output` after each run of the model:


- **data_set_citations.json** - A JSON file that contains publication-dataset pairs for each detected mention of any of the data sets provided in the contest `data_sets.json` file.  The JSON file should contain a JSON list of objects, where each object represents a single publication-dataset pair and includes four properties:

    - `publication_id` - The integer `publication_id` of the publication from `publications.json`.
    - `data_set_id` - The integer `data_set_id` that identifies the cited dataset.
    - `score` - A score on a scale of 0 to 1 representing the level of confidence that the dataset is referenced in the publication.
    - `mention_list` - A list of the text of explicit mentions of the data set in the publication.

        ```
        [
            {"publication_id": 102,
            "data_set_id": 44,
            "score": 0.678,
            "mention_list":[
                "survey of consumer practices",
                "consumer practice study"
            ]
            },
            {"publication_id": 55,
            "data_set_id": 434,
            "score": 0.568,
            "mention_list":[
                "corporate balance sheet data",
                "corporate balance sheet statistics",
                "corporate balance sheets"
            ]
            }
            ....
        ]
        ```

- **data_set_mentions.json** - A JSON file that should contain a list of JSON objects, where each object contains a single publication-mention pair for every data set mention detected within each publication, regardless of whether a gvien data set is one of the data sets provided in the contest data set file. Each mention JSON object will includes three properties:

    - `publication_id` - The integer `publication_id` of the publication from `publications.json`.
    - `mention` - The specific data set mention text found in the publication. Each mention gets its own JSON object in this list.
    - `score` - A score on a scale of 0 to 1 representing the level of confidence that the mention text references data.

        ```
        [
            {
                "publication_id": 1088,
                "mention": "American Community Survey (ACS)",
                "score": 0.770,
            },
            {
                "publication_id": 1088,
                "mention": "ACS",
                "score": 0.590,
            },
            {
                "publication_id": 1902,
                "mention": "Health and Wellness Study",
                "score": 0.880,
            },
            ....
        ]
        ```

- **methods.json** - A JSON file that should contain a list of JSON objects, where each object captures publication-method pairs via three properties:

    - `publication_id` - The integer `publication_id` of the publication from `publications.json`.
    - `method` - The inferred method used by the research in the publication.
    - `score` - A score on a scale of 0 to 1 representing the level of confidence that the method is used in the publication.

        ```
        [
            {
                "publication_id": 876,
                "method": "opinion poll",
                "score": 0.680,
            },
            {
                "publication_id": 223,
                "method": "sampling",
                "score": 0.458,
            },
            {
                "publication_id": 223,
                "method": "ethnography",
                "score": 0.916,
            },
            ....
        ]
        ```

- **research_fields.json** - A JSON file that should contain a list of JSON objects, where each object captures publication-research field pairs via three properties:

    - `publication_id` - The integer `publication_id` of the publication from `publications.json`.
    - `research_field` - The inferred research field of the research in the publication.
    - `score` - A score on a scale of 0 to 1 representing the level of confidence that the publication is in the stated research field.

        ```
        [
            {
                "publication_id": 1008,
                "research_field": "Public Health",
                "score": 0.747,
            },
            {
                "publication_id": 1073,
                "research_field": "Urban Planning",
                "score": 0.690,
            },
            {
                "publication_id": 2133,
                "research_field": "Economics",
                "score": 0.900,
            },
            ....
        ]
        ```

# How to compete?

## Preparing your model for submission:

To prepare your model for submission:

- test docker installation:

    - run "`./rcc.sh build`" using the default provided Dockerfile.
    - do a "basic test" of the container:
    
        - "`./rcc.sh run`"
        - "`./rcc.sh stop`"
        - "`./rcc.sh evaluate`"

- reset data folder: "`./rcc.sh reset-data-folder`"
- make your model.
- update the "`Dockerfile`" file so everything your model needs is installed in the container.
- get container working - repeat the following until build succeeds:

    - "`./rcc.sh remove-docker-image`"
    - "`./rcc.sh build`"

- put model into projects folder

    - put model, scripts, needed files, etc., into "project" folder.
    - update code.sh in project folder so it runs your model on "/data" inside the container.
    - your model should:

        - use the file "/data/input/publications.json" (inside the container) to figure out which publications need to be processed.
        - process each.
        - output the following files to the "/data/output" folder (path is correct inside the container - mapped to data folder in your submission folder):

            - dataset_citations.json
            - dataset_mentions.json
            - methods.json
            - research_fields.json

- use the "`./rcc.sh run`" command to work through getting your model to run. "`./rcc.sh stop`" after each run, or just use "`./rcc.sh run-stop`".
- once your model is running, run and evaluate against the dev fold:

    - use the "`./rcc.sh run`" command to run your model against the dev fold.
    - "`./rcc.sh stop`"
    - run the "`./rcc.sh evaluate`" command to see how your model did.

## Reviewing your submission

When we receive your submission, we will:
 1. Move the contents of your group's Box folder to an evaluation server.
 1. Update config.sh so the data folder is one that contains our **evaluation holdback data** 
 1. Execute a **clean run against dev fold** (_see documentation on "`rcc.sh`" [above](#helper-script-rccsh)_).
 1. Gather and compare the results on the `project/example_output` folder
 
Please do the same process against the **development fold** (the data in the provided default data folder) to make sure your code works:

1. Configure "`config.sh`" so it refers to your project folder and the default data folder and execute a **clean run against dev fold** (_see documentation on "`rcc.sh`" above_). If you have a copy of your image already built, you need not rebuild, you can just:
2. Run "`./rcc.sh run-stop`" to run your model on the default dev fold data.
3. Run "`./rcc.sh evaluate`" to use our evaluation script to compare your results to those for the dev fold and see back precision, recall, and accuracy scores.

**Note**: Please make sure to test your solution using the above mentioned method against the **development fold** before submitting it to verify that it is reading and writing data correctly. If we can't run your submission, we will not be able to include it in evaluation for the competition.

## Getting Started

### Self Evaluation

### Submission

