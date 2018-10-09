# rich-context-contest

This repository contains supporting files for working on and submitting an entry for the [Rich Context Text Analysis Competition](https://coleridgeinitiative.org/richcontextcompetition).  Here you will find all the materials and instructions you will need to build your competition submission.  You should develop (train and test) your model on your own machine or server.  Once you are ready to submit, you will use the files and scripts here to create a docker container that contains all code, libraries, and additional data and resources required to train and run your model.  Each group of participants will be given access to a private Box folder shared with contest organizers that will be pre-populated with this repository along with a dev fold, sample data folder, sample project folder, and the train-test data for the competition.  To submit, inside their Box folder, each group will:

- place their trained model's data and code in a project folder along with a script that accepts a data folder path and runs the model against the specified data directory (standard data directory layout specified below).
- implement a Dockerfile that can be run anywhere, built on the ubuntu 18.04 base image, that installs and configures a docker image that can call the model execution script and run it against any directory that has a standard data folder layout (described below).

Below are instructions to assist you setting up and configuring your submission container.

# Rules of Engagement

We suggest that you build, train, and test your model in an environment you are comfortable with, then once you have it working, migrate it to a docker container.

The Rich Context Contest staff will do our best to help you with problems related to storing your model and data in a git repo and updating the other related files so we can accept and run it in a docker image.  We can not provide support for software you use to implement your model.

# Technical Details

## Requirements

Please make sure you have Docker installed on your machine before you start work on preparing your submission.

For Windows 10 Pro or macOS computers, install Docker Desktop:

- [https://www.docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop)

For versions of Windows other than Windows 10 Pro, we recommend installing a virtualization program like VirtualBox and working inside an Ubuntu 18.04 linux virtual machine.

For linux, Find your version of linux in the Docker Community Edition product page and click through to find instructions:

- [https://store.docker.com/search?type=edition&offering=community](https://store.docker.com/search?type=edition&offering=community)

Linux notes:

- if you can, we recommend installing the latest from the docker repos, not the versions that are included in base OS repositories.
- consider adding your user to the "docker" OS group so you can manage docker without having to be root (from [https://docs.docker.com/install/linux/linux-postinstall/#manage-docker-as-a-non-root-user](https://docs.docker.com/install/linux/linux-postinstall/#manage-docker-as-a-non-root-user))_:

    - add group docker (`sudo groupadd docker`) - your OS might create it as part of install.  If so, you'll get an error message something like "groupadd: group 'docker' already exists".  This is fine.  No harm no foul.  Proceed to the next step.
    - add your user to the docker group (`sudo usermod -aG docker $USER`).
    - log out and log back in.  On a VM, you might have to reboot the VM for this to stick (from the doc, not sure why).
    - try running docker without sudo.
    - if you initially ran docker commands as root, you might see error "WARNING: Error loading config file: /home/user/.docker/config.json - stat /home/user/.docker/config.json: permission denied".  This means your `~/.docker` folder is owned by root.  To fix, either remove `~/.docker` and run a docker command to recreate (you'll lose custom settings), or change owner for the folder and all children to your user and default group and update all permissions to the normal umask default (group rwx):
	
            $ sudo chown "$USER":"$USER" /home/"$USER"/.docker -R
            $ sudo chmod g+rwx "$HOME/.docker" -R(`chown -R `)

This project was created using Docker version `Docker version 18.06.1-ce, build e68fc7a`.  Please make sure to use the current version at the time of submission to avoid version-related issues.

## Helper script `rcc.sh`

We created bash shell helper script, "`rcc.sh`", to facilitate making and testing a submission and working with Docker. To run the script, navigate into the root of your group's Box folder, then run `./rcc.sh <action>`.  The supported actions are listed below.  Certain specifics of your environment must be specified in a separate configuration shell script (config.sh), that we provide pre-populated with examples that you can use to test all the actions.

Notes:

- on linux, by default, docker is installed so it can only be managed by the root user.  This means you'll have to run "`rcc.sh`" script actions that interact with docker as root, as well (all the `build` and `run` actions, for example).  You can use `sudo` or `su` to root and do this as needed, but this can get messy in terms of the permissions of the files in this submission folder.  One option to consider if you can on your server is to configure your user so it is in the docker OS group, and so able to manage docker without root access: [https://docs.docker.com/install/linux/linux-postinstall/#manage-docker-as-a-non-root-user](https://docs.docker.com/install/linux/linux-postinstall/#manage-docker-as-a-non-root-user).  See detailed instructions above in the "Requirements" section.
- If you download the contents of your group's Box folder and move them to a linux machine or virtual machine to work on preparing your submission, be aware that even though the shell script files are stored in git with permissions to allow them to be executed, Box does not persist those permissions, and so you might need to update shell scripts to be executable once you uncompress the contents of the Box folder (specifically, "`rcc.sh`", "`project/code.sh`", and "`config.sh`" - `chmod 755 <file_name>`).

### Configuration script

#!/bin/bash
	
    # The config file can include:
    # - `BASE_FOLDER_IN` - base folder (usually where this script lives).
    # - `DATA_FOLDER_PATH_IN` (`-d` option) - path to the data folder for a given run of the model.
    # - `PROJECT_FOLDER_PATH_IN` (`-p` option) - path to the project folder for the current model.
    # - `GIT_REPO_FOLDER_PATH_IN` - the path to the git repo (defaults to "/rich-context-contest" inside the base folder).
    # - `EVALUATE_FOLER_PATH_IN` - path to the evaluate code folder inside the git repository.
    # - `TEMPLATE_FOLDER_PATH_IN` - path to the template code folder inside the git repository.
    # - `DOCKER_IMAGE_NAME_IN` - Image name to use locally for submission image, defaults to "my_rcc".
    # - `DOCKER_CONTAINER_NAME_IN` - Container name to use locally for the instance of the image used to test and run your model, defaults to "${DOCKER_IMAGE_NAME_IN}_run"
    # - `USE_BUILD_CACHE_IN` - default behavior for build cache use with the base "build" action.  Defaults to false (no cache).
    # - `DEBUG` - set to "`true`" or "`false`".  If set to "`true`", results in much more verbose output.

    # set configuration variables
    BASE_FOLDER_PATH_IN="."

    # model-related folders
    DATA_FOLDER_PATH_IN="${BASE_FOLDER_PATH_IN}/data"
    PROJECT_FOLDER_PATH_IN="${BASE_FOLDER_PATH_IN}/project"

    #===============================================================================
    # WARNING - do not alter below this point unless you know what you are doing.
    #===============================================================================

    # git repo folders
    GIT_REPO_FOLDER_PATH_IN="${BASE_FOLDER_PATH_IN}/rich-context-contest"
    EVALUATE_FOLDER_PATH_IN="${GIT_REPO_FOLDER_PATH_IN}/evaluate"
    TEMPLATE_FOLDER_PATH_IN="${GIT_REPO_FOLDER_PATH_IN}/templates"

    # docker
    DOCKER_IMAGE_NAME_IN="my_rcc"
    DOCKER_CONTAINER_NAME_IN="${DOCKER_IMAGE_NAME_IN}_run"
    USE_BUILD_CACHE_IN=false

    # debug
    DEBUG=true

You should only need to set the variables `DATA_FOLDER_PATH_IN` and `PROJECT_FOLDER_PATH_IN`.  The rest you should leave set to defaults unless you really know what you are doing.

### rcc.sh actions - setup and cleanup

- **`init`** performs all set up needed to initialize a base competition folder from a copy of this git repo.  On an empty directory, this will copy example "`./data`" and "`./project`" folders into the base folder and put in place a copy of "`config.sh`", "`rcc.sh`", and a basic functional "`DockerFile`" template with example commands.  When run on an already initialized folder, it will reset the default "`data`" and "`project`" folders and grab an updated copy of the "`rcc.sh`" script, but leave the "`config.sh`" and "`Dockerfile`" files alone.
- **`reset-data-folder`** - Replaces the folder "`./data`" in the root folder with a copy of the default dev fold data folder.  If a "`./data`" folder is already present, archives it to "`./archive/YYYY-MM-DD-HH-MM-SS`".
- **`reset-project-folder`** - Replaces the folder "`./project`" in the root folder with a copy of the default template project folder.  If a "`./project`" folder is already present, archives it to "`./archive/YYYY-MM-DD-HH-MM-SS`".
- **`reset-config-file`** - Replaces the file "`./config.sh`" in the root folder with a copy of the default "`./config.sh`".  If a "`./config.sh`" file is already present, archives it to "`./archive/YYYY-MM-DD-HH-MM-SS`".
- **`reset-dockerfile`** - Replaces the file "`./Dockerfile`" in the root folder with a copy of the default example "`./Dockerfile`".  If a "`./Dockerfile`" file is already present, archives it to "`./archive/YYYY-MM-DD-HH-MM-SS`".
- **`reset-rcc-script`** - Replaces the file "`./rcc.sh`" in the root folder with a copy of the default "`./rcc.sh`".  If a "`./rcc.sh`" file is already present, archives it to "`./archive/YYYY-MM-DD-HH-MM-SS`".

_NOTE: for all "`reset-*`" actions, if a file or folder is replaced in the base folder, the original will first be archived in a folder named "`archive/YYYY-MM-DD-HH-MM-SS`" created off the root submission folder, and a message will be output by the "`rcc.sh`" script telling you something was archive._

### rcc.sh actions - docker image actions

- **`build`** will create a local docker image from the DockerFile in this repository.  By default, does not use a cache, so you get latest from git repo, remote package repositories, etc. every time.
	
	If successful, you should see in the final lines of output something like: 

	`Successfully built 0c5fd3e0cdf4
	 Successfully tagged my_rcc:latest`

- **`build-no-cache`** will create a local docker image from the DockerFile in the root of the folder, without use of cache so you get latest from git repo, remote package repositories, etc. every time.
- **`build-use-cache`** will create a local docker image from the DockerFile in this repository, using cache of layers as docker deems it appropriate to minimize the time it takes to build.
- **`remove-docker-image`** will use the "`docker rmi`" command to delete your image, so you can rebuild it from your Dockerfile.  You must "`stop`" your container before the image can be removed.

### rcc.sh actions - running the docker container

- **`run`** will mount the folder specified in the variable `PROJECT_FOLDER_PATH_IN` to "`/project`" and the folder specified in `DATA_FOLDER_PATH_IN` to "`/data`" in the container, then run the code stored in file "`/project/code.sh"`.  The data folder will be formatted as specified below, and your code should be able to run against any data folder that fits this specification.  _NOTE: In order to re-run, you must "`./rcc.sh stop`" before you can "`./rcc.sh run`" again._
- **`run-interactive`** will run the container with a interactive bash shell instead of running in the background as with `run`. This is useful during development or debugging.
- **`stop`** stops the container to start fresh.  _NOTE: After you "`./rcc.sh run`", you must "`./rcc.sh stop`" before you can "`./rcc.sh run`" again._
- **`run-stop`** combines "`./rcc.sh run`" and then "`./rcc.sh stop`", for quick repeated executions.

### rcc.sh actions - evaluating a model 

- **`evaluate`** compares the baseline for the dev fold with output in the current configured data folder's output directory.  Uses the official evaluation script to calculate and output precision, recall and accuracy.

### rcc.sh - clean run against dev fold

To rebuild your container and run it against a fresh dev fold data directory, execute the following commands:

- `./rcc.sh stop`
- `./rcc.sh remove-docker-image`
- `./rcc.sh reset-data-folder`
- `./rcc.sh run-stop`
- `./rcc.sh evaluate`

## Data folder specification

The standard data folder layout:

- data

    - input

        - files

		    - text
			- pdf

	- output

### Input files

The input folder will have a "`publications.json`" file that lists the articles to be processed in the current run of the model.  Publication plain text is stored in /input/files/text, one text file to a publication, with a given publication's text named "`<publication_id>.txt`".  The original PDF files are stored in /input/files/pdf, one PDF file to a publication, with a given publication's text named "`<publication_id>.pdf`".  The **`publications.json`** file is a JSON list of JSON objects, each of which contains:

- `pub_date` - Publication date of the article, in "YYYY-MM-DD" format.
- `unique_identifier` - Unique identifier provided by the publication's source.  Could be a URL or other URI, etc.
- `text_file_name` - file name of the publication's text file, "`<publication_id>.txt`".  Does not include path information.  All text files are stored in `/input/files/text`.
- `pdf_file_name` - file name of the publication's PDF file, "`<publication_id>.pdf`".  Does not include path information.  All PDF files are stored in `/input/files/pdf`.
- `title` - text title of the publication.
- `publication_id` - Integer ID of the publication, unique within the set of publications stored in a given "`publications.json`" file.  This is the ID that should be referred to in output JSON files when you tie your results to a given publication.

Example:

[
	{
	    "pub_date": "1982-01-01",
        "unique_identifier": "http://www.jstor.org/stable/1963728",
        "text_file_name": "1.txt",
        "pdf_file_name": "1.pdf",
        "title": "The decline of electoral participation in America",
        "publication_id": 1
	},
    {
        "pub_date": "1986-01-01",
        "unique_identifier": "http://www.jstor.org/stable/2111292",
        "text_file_name": "2.txt",
        "pdf_file_name": "2.pdf",
        "title": "Generational Replacement and Value Change in Six West European Societies",
        "publication_id": 2
    },
	...
]

### Output files

4 expected output files should be placed in the folder `data/output` after each run of the model:

- **dataset_citations.json** - A JSON file that contains publication-dataset pairs for each detected mention of any of the data sets provided in the contest `data_sets.json` file.  The JSON file should contain a JSON list of objects, where each object represents a single publication-dataset pair and includes four properties:

    - `publication_id` - The integer `publication_id` of the publication from `publications.json`.
    - `data_set_id` - The integer `data_set_id` that identifies the cited dataset.
    - `score` - A score on a scale of 0 to 1 representing the level of confidence that the dataset is referenced in the publication.
    - `mention_list` - A list of the text of explicit mentions of the data set in the publication.

- **dataset_mentions.json** - A JSON file that should contain a list of JSON objects, where each object contains a single publication-mention pair for every data set mention detected within each publication, regardless of whether a gvien data set is one of the data sets provided in the contest data set file. Each mention JSON object will includes three properties:

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

# How to compete?

## Reviewing your submission

When we receive your submission, we will:
 1. Move the contents of your group's Box folder to an evaluation server.
 1. Update config.sh so the data folder is one that contains our **evaluation holdback data** 
 1. Execute a **clean run against dev fold** (_see documentation on "`rcc.sh`" above_).
 1. Gather and compare the results on the `project/example_output` folder
 
Please do the same process against the **development fold** (the data in the provided default data folder) to make sure your code works:

1. Configure "`config.sh`" so it refers to your project folder and the default data folder and execute a **clean run against dev fold** (_see documentation on "`rcc.sh`" above_).  If you have a copy of your image already built, you need not rebuild, you can just:
2. Run "`./rcc.sh run-stop`" to run your model on the default dev fold data.
3. Run "`./rcc.sh evaluate`" to use our evaluation script to compare your results to those for the dev fold and see back precision, recall, and accuracy scores.

**Note**: Please make sure to test your solution using the above mentioned method against the **development fold** before submitting it to verify that it is reading and writing data correctly.  If we can't run your submission, we will not be able to include it in evaluation for the competition.
