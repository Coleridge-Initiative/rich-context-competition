#!/bin/bash

# rich context contest bash script

#===============================================================================
# variables
#===============================================================================

# load config
config_file_path="./config.sh"
action_arg="1"
while getopts "c:" opt; do
    case $opt in
        c) config_file_path="$OPTARG"
            action_arg="3"
        ;;
        \?) echo "Invalid option -$OPTARG" >&2
        ;;
    esac
done

# other variables
current_time_stamp=$(date +%Y-%m-%d-%H-%M-%S)
archive_folder_path=
now_archive_folder_path=
empty_value="EMPTYEMPTYEMPTYEMPTY"

#===============================================================================
# functions
#===============================================================================

# return reference
absolute_path_OUT=

function absolute_path()
{

    # input parameters
    local path_IN=$1

    # declare variables
    local absolute_path=

    # clear output reference
    absolute_path_OUT=

    # call realpath
    #absolute_path=$( realpath "${1}" )

    # call readlink -f
    #absolute_path=$( readlink -f "${1}" )

    # something less platform-specific:
    # https://stackoverflow.com/questions/4175264/bash-retrieve-absolute-path-given-relative
    absolute_path="$(cd "$(dirname "${1}")"; pwd)/$(basename "${1}")"

    # return result
    absolute_path_OUT="${absolute_path}"

} #-- END function absolute_path() --#


function init_archive_folders()
{

    # Accepts base folder path, makes sure an archive folder exists and
    #     then checks for a nested folder for the current run's timestamp.
    #     If no time stamp folder, creates one, as well.
    # Postconditions: sets archive_folder_path and now_archive_folder_path
    #     to the paths it initializes.

    # input parameters
    local base_folder_path_IN=${1:=${BASE_FOLDER_PATH_IN}}

    # declare variables
    local time_stamp="${current_time_stamp}"

    # check if ./archive folder
    archive_folder_path="${base_folder_path_IN}/archive"
    if [[ ! -d "${archive_folder_path}" ]]
    then

        # no archive folder.  Create one.
        mkdir "${archive_folder_path}"

    fi

    # create nested folder from date-time?
    now_archive_folder_path="${archive_folder_path}/${time_stamp}"
    if [[ ! -d "${now_archive_folder_path}" ]]
    then

        # no current timestamp folder.  Create one.
        mkdir "${now_archive_folder_path}"

    fi

} #-- END function init_archive_folders() --#


function reset_folder()
{

    # input parameters
    local base_folder_path_IN=${1:=${BASE_FOLDER_PATH_IN}}
    local git_folder_path_IN=${2:=${GIT_REPO_FOLDER_PATH_IN}}
    local folder_name_IN=${3:=${empty_value}}
    
    # declare variables
    local folder_path=
    local template_folder_path=
    local is_folder_present=false

    # DEBUG
    if [[ $DEBUG = true ]]
    then
        echo "In reset_folder()"
        echo "- base_folder_path_IN: \"${base_folder_path_IN}\""
        echo "- git_folder_path_IN: \"${git_folder_path_IN}\""
        echo "- folder_name_IN: \"${folder_name_IN}\""
    fi

    # got a folder name?
    if [[ folder_name_IN != "${empty_value}" ]]
    then

        # initialize paths
        folder_path="${base_folder_path_IN}/${folder_name_IN}"
        template_folder_path="${git_folder_path_IN}/${folder_name_IN}"

        # check if folder currently in the base directory.
        if [[ -d "${folder_path}" ]]
        then

            # folder present.
            is_folder_present=true

        fi

        # need to archive project folder?
        if [[ $is_folder_present = true ]]
        then

            # yes - make sure archive folders are initialized
            # - sets archive_folder_path and now_archive_folder_path
            init_archive_folders "${base_folder_path_IN}"

            # move folder to now_archive_folder_path
            mv "${folder_path}" "${now_archive_folder_path}"
            echo "==> ARCHIVE: Moved existing folder \"${folder_name_IN}\" from ${folder_path} to ${now_archive_folder_path}"

        fi #-- END check if need to archive --#

        # copy stuff from git repo.
        # does git repo path exist?
        if [[ -d "${git_folder_path_IN}" ]]
        then

            # it does - copy "project" folder to base folder...
            cp -R "${template_folder_path}" "${base_folder_path_IN}"

        fi #-- END check to see if git folder --#

    fi #-- END check for folder name. --#

} #-- END function reset_folder() --#


function reset_data_folder()
{

    # input parameters
    local base_folder_path_IN=${1:=${BASE_FOLDER_PATH_IN}}
    local git_folder_path_IN=${2:=${GIT_REPO_FOLDER_PATH_IN}}
    
    # declare variables
    # DEBUG
    if [[ $DEBUG = true ]]
    then
        echo "In reset_data_folder():"
        echo "- base_folder_path_IN: \"${base_folder_path_IN}\""
        echo "- git_folder_path_IN: \"${git_folder_path_IN}\""
    fi

    # data folder - if present, archive, then move over new copy of original.
    reset_folder "${base_folder_path_IN}" "${git_folder_path_IN}" "data"

} #-- END function reset_data_folder() --#


function reset_project_folder()
{

    # input parameters
    local base_folder_path_IN=${1:=${BASE_FOLDER_PATH_IN}}
    local git_folder_path_IN=${2:=${GIT_REPO_FOLDER_PATH_IN}}
    
    # declare variables
    # DEBUG
    if [[ $DEBUG = true ]]
    then
        echo "In reset_project_folder():"
        echo "- base_folder_path_IN: \"${base_folder_path_IN}\""
        echo "- git_folder_path_IN: \"${git_folder_path_IN}\""
    fi

    # project folder - if present, archive, then move over new copy of original.
    reset_folder "${base_folder_path_IN}" "${git_folder_path_IN}" "project"

} #-- END function reset_project_folder() --#


function reset_file()
{

    # "replace" means archive current out of the way, then
    #     copy new in.  Existing is replaced, not overwritten.

    # input parameters - all required
    local base_folder_path_IN=${1:=${BASE_FOLDER_PATH_IN}}
    local git_folder_path_IN=${2:=${GIT_REPO_FOLDER_PATH_IN}}
    local file_name_IN=${3:=${empty_value}}
    local do_replace_IN=${4:-false}
    local template_path_IN=${5:-${empty_value}}
    
    # declare variables
    local file_name=
    local file_path=
    local template_file_path=

    # do we have a file name?
    if [[ $file_name_IN != $empty_value ]]
    then

        # init file info
        file_name="${file_name_IN}"
        file_path="${base_folder_path_IN}/${file_name}"
        if [[ $template_path_IN != $empty_value ]]
        then
    
            # include additional path information.
            template_file_path="${git_folder_path_IN}/${template_path_IN}/${file_name}"

        else

            # no additional path information.
            template_file_path="${git_folder_path_IN}/${file_name}"

        fi

        # DEBUG
        if [[ $DEBUG = true ]]
        then
            echo "In reset_file()"
            echo "- base_folder_path_IN: \"${base_folder_path_IN}\""
            echo "- git_folder_path_IN: \"${git_folder_path_IN}\""
            echo "- file_name_IN: \"${file_name_IN}\""
            echo "- do_replace_IN: \"${do_replace_IN}\""
            echo "- template_path_IN: \"${template_path_IN}\""
        fi

        # does git repo path exist?
        if [[ -d "${git_folder_path_IN}" ]]
        then

            # do we replace?
            if [[ $do_replace_IN = true ]]
            then

                # check if file already there.
                if [[ -f "${file_path}" ]]
                then

                    # yes - make sure archive folders are initialized
                    # - sets archive_folder_path and now_archive_folder_path
                    init_archive_folders "${base_folder_path_IN}"

                    # move the current file to "${now_archive_folder_path}"
                    mv "${file_path}" "${now_archive_folder_path}"
                    echo "==> ARCHIVE: Moved existing ${file_name} from ${file_path} to ${now_archive_folder_path}"

                fi #-- END check if file present. --#

            fi #-- END check to see if we are replacing --#

            # copy into place if not already present.
            if [[ ! -f "${file_path}" ]]
            then

                # copy
                cp "${template_file_path}" "${base_folder_path_IN}"

            fi #-- check if file present --#

        fi #-- END check to see if git repo path --#

    else

        echo "ERROR: You must pass in a file name."

    fi #-- END check to see if file name --#

} #-- END function reset_file() --#


function reset_config_file()
{

    # input parameters
    local base_folder_path_IN=${1:=${BASE_FOLDER_PATH_IN}}
    local git_folder_path_IN=${2:=${GIT_REPO_FOLDER_PATH_IN}}
    local do_replace_IN=${3:-true}
    
    # declare variables

    # DEBUG
    if [[ $DEBUG = true ]]
    then
        echo "In reset_config_file():"
        echo "- base_folder_path_IN: \"${base_folder_path_IN}\""
        echo "- git_folder_path_IN: \"${git_folder_path_IN}\""
        echo "- do_replace_IN: \"${do_replace_IN}\""
    fi

    # reset config file, archive and replace as requested if already there.
    reset_file "${base_folder_path_IN}" "${git_folder_path_IN}" "config.sh" "${do_replace_IN}" "templates"

} #-- END function reset_config_file() --#


function reset_dockerfile()
{

    # input parameters
    local base_folder_path_IN=${1:=${BASE_FOLDER_PATH_IN}}
    local git_folder_path_IN=${2:=${GIT_REPO_FOLDER_PATH_IN}}
    local do_replace_IN=${3:-true}
    
    # declare variables

    # DEBUG
    if [[ $DEBUG = true ]]
    then
        echo "In reset_dockerfile():"
        echo "- base_folder_path_IN: \"${base_folder_path_IN}\""
        echo "- git_folder_path_IN: \"${git_folder_path_IN}\""
        echo "- do_replace_IN: \"${do_replace_IN}\""
    fi

    # reset Dockerfile, archive and replace if already there.
    reset_file "${base_folder_path_IN}" "${git_folder_path_IN}" "Dockerfile" "${do_replace_IN}"

} #-- END function reset_dockerfile() --#


function reset_rcc_script()
{

    # input parameters
    local base_folder_path_IN=${1:=${BASE_FOLDER_PATH_IN}}
    local git_folder_path_IN=${2:=${GIT_REPO_FOLDER_PATH_IN}}
    local do_replace_IN=${3:-true}
    
    # declare variables

    # DEBUG
    if [[ $DEBUG = true ]]
    then
        echo "In reset_rcc_script():"
        echo "- base_folder_path_IN: \"${base_folder_path_IN}\""
        echo "- git_folder_path_IN: \"${git_folder_path_IN}\""
        echo "- do_replace_IN: \"${do_replace_IN}\""
    fi

    # reset rcc.sh, archive and replace if already there.
    reset_file "${base_folder_path_IN}" "${git_folder_path_IN}" "rcc.sh" "${do_replace_IN}"
    chmod 775 "${base_folder_path_IN}/rcc.sh"

} #-- END function reset_rcc_script() --#


function init()
{

    # input parameters
    local base_folder_path_IN=${1:=${BASE_FOLDER_PATH_IN}}
    local git_folder_path_IN=${2:=${GIT_REPO_FOLDER_PATH_IN}}
    
    # declare variables

    # DEBUG
    if [[ $DEBUG = true ]]
    then
        echo "In init():"
        echo "- base_folder_path_IN: \"${base_folder_path_IN}\""
        echo "- git_folder_path_IN: \"${git_folder_path_IN}\""
    fi

    # data folder - if present, archive, then move over new copy of original.
    reset_data_folder "${base_folder_path_IN}" "${git_folder_path_IN}"

    # project folder - if present, archive, then move over new copy of original.
    reset_project_folder "${base_folder_path_IN}" "${git_folder_path_IN}"

    # reset config file, but don't replace if already there.
    reset_config_file "${base_folder_path_IN}" "${git_folder_path_IN}" false

    # reset Dockerfile, but don't replace if already there.
    reset_dockerfile "${base_folder_path_IN}" "${git_folder_path_IN}" false

    # reset rcc.sh script, replace if already there.
    reset_rcc_script "${base_folder_path_IN}" "${git_folder_path_IN}" true

} #-- END function init() --#


#build:
#	docker build -t my_rcc --force-rm .
function build()
{
    # input parameters
    local image_name_IN=${1:=${DOCKER_IMAGE_NAME_IN}}
    local base_folder_path_IN=${2:=${BASE_FOLDER_PATH_IN}}
    local use_cache_IN=${3:-${USE_BUILD_CACHE_IN}}
    
    # declare variables
    cache_flag=

    # DEBUG
    if [[ $DEBUG = true ]]
    then
        echo "In build():"
        echo "- image_name_IN: \"${image_name_IN}\""
        echo "- base_folder_path_IN: \"${base_folder_path_IN}\""
        echo "- use_cache_IN: \"${use_cache_IN}\""
    fi

    # DEBUG
    if [[ $use_cache_IN = false ]]
    then
        cache_flag="--no-cache"
    fi

    # run the docker command.
    docker build ${cache_flag} -t ${image_name_IN} --force-rm ${base_folder_path_IN}
    
} #-- END function build() --#


# stop:
#     docker rm -f my_rcc_run
function stop()
{
    # input parameters
    local container_name_IN=${1:=${DOCKER_CONTAINER_NAME_IN}}
    
    # declare variables

    # DEBUG
    if [[ $DEBUG = true ]]
    then
        echo "container_name_IN: \"${container_name_IN}\""
    fi

    # run the docker command.
    docker rm -f ${container_name_IN}
    
} #-- END function stop() --#

# remove_docker_image:
function remove_docker_image()
{
    # input parameters
    local image_name_IN=${1:-${DOCKER_IMAGE_NAME_IN}}

    # declare variables

    # DEBUG
    if [[ $DEBUG = true ]]
    then
        echo "In remove_docker_image:"
        echo "- image_name_IN: \"${image_name_IN}\""
    fi

    # remove JSON files from output.
    docker rmi "${image_name_IN}"
    
} #-- END function remove_docker_image() --#


#run:
#    docker run -v `pwd`/project:/project -v `pwd`/data:/data --name my_rcc_run my_rcc /project/code.sh
#evaluate:
#    docker run -v `pwd`/project:/project -v `pwd`/data:/data --name my_rcc_run my_rcc /data/evaluate/evaluate.sh
function run()
{
    # input parameters
    local project_folder_path_IN=${1:=${PROJECT_FOLDER_PATH_IN}}
    local data_folder_path_IN=${2:=${DATA_FOLDER_PATH_IN}}
    local image_name_IN=${3:=${DOCKER_IMAGE_NAME_IN}}
    local container_name_IN=${4:=${DOCKER_CONTAINER_NAME_IN}}
    local script_to_run_IN=${5:-}
    local docker_custom_options_IN=${6:=${DOCKER_CUSTOM_RUN_OPTIONS_IN}}
    
    # declare variables
    local project_folder_path=
    local data_folder_path=

    # convert to absolute paths.
    
    # project folder path
    absolute_path "${project_folder_path_IN}"
    project_folder_path="${absolute_path_OUT}"

    # data folder path
    absolute_path "${data_folder_path_IN}"
    data_folder_path="${absolute_path_OUT}"

    # DEBUG
    if [[ $DEBUG = true ]]
    then
        echo "In run:"
        echo "- project_folder_path_IN: \"${project_folder_path_IN}\""
        echo "- data_folder_path_IN: \"${data_folder_path_IN}\""
        echo "- project_folder_path: \"${project_folder_path}\""
        echo "- data_folder_path: \"${data_folder_path}\""
        echo "- image_name_IN: \"${image_name_IN}\""
        echo "- container_name_IN: \"${container_name_IN}\""
    fi

    # remove JSON files from output.
    docker run ${docker_custom_options_IN} -v `pwd`:/run_folder -v ${project_folder_path}:/project -v ${data_folder_path}:/data --name ${container_name_IN} ${image_name_IN} ${script_to_run_IN}
    
} #-- END function run() --#


#run-interactive:
#    docker run -it -v `pwd`/project:/project -v `pwd`/data:/data --name my_rcc_run my_rcc
function run_interactive()
{
    # input parameters
    local project_folder_path_IN=${1:=${PROJECT_FOLDER_PATH_IN}}
    local data_folder_path_IN=${2:=${DATA_FOLDER_PATH_IN}}
    local image_name_IN=${3:=${DOCKER_IMAGE_NAME_IN}}
    local container_name_IN=${4:=${DOCKER_CONTAINER_NAME_IN}}
    local docker_custom_options_IN=${5:=${DOCKER_CUSTOM_RUN_OPTIONS_IN}}
    
    # declare variables
    local project_folder_path=
    local data_folder_path=

    # convert to absolute paths.

    # project folder path
    absolute_path "${project_folder_path_IN}"
    project_folder_path="${absolute_path_OUT}"

    # data folder path
    absolute_path "${data_folder_path_IN}"
    data_folder_path="${absolute_path_OUT}"

    # DEBUG
    if [[ $DEBUG = true ]]
    then
        echo "In run_interactive():"
        echo "- project_folder_path_IN: \"${project_folder_path_IN}\""
        echo "- data_folder_path_IN: \"${data_folder_path_IN}\""
        echo "- project_folder_path: \"${project_folder_path}\""
        echo "- data_folder_path: \"${data_folder_path}\""
        echo "- image_name_IN: \"${image_name_IN}\""
        echo "- container_name_IN: \"${container_name_IN}\""
    fi

    # run in interactive mode ("-it").
    docker run ${docker_custom_options_IN} -it -v `pwd`:/run_folder -v ${project_folder_path}:/project -v ${data_folder_path}:/data --name ${container_name_IN} ${image_name_IN}
    
} #-- END function run_interactive() --#


#git-pull:
function git_pull()
{
    # input parameters
    local project_folder_path_IN=${1:=${PROJECT_FOLDER_PATH_IN}}
    local data_folder_path_IN=${2:=${DATA_FOLDER_PATH_IN}}
    local image_name_IN=${3:=${DOCKER_IMAGE_NAME_IN}}
    local container_name_IN=${4:=${DOCKER_CONTAINER_NAME_IN}}
    
    # declare variables
    local project_folder_path=
    local data_folder_path=

    # convert to absolute paths.
    
    # project folder path
    absolute_path "${project_folder_path_IN}"
    project_folder_path="${absolute_path_OUT}"

    # data folder path
    absolute_path "${data_folder_path_IN}"
    data_folder_path="${absolute_path_OUT}"

    # DEBUG
    if [[ $DEBUG = true ]]
    then
        echo "In git_pull():"
        echo "- project_folder_path_IN: \"${project_folder_path_IN}\""
        echo "- data_folder_path_IN: \"${data_folder_path_IN}\""
        echo "- project_folder_path: \"${project_folder_path}\""
        echo "- data_folder_path: \"${data_folder_path}\""
        echo "- image_name_IN: \"${image_name_IN}\""
        echo "- container_name_IN: \"${container_name_IN}\""
    fi

    # pull inside container.
    #run "${project_folder_path}" "${data_folder_path}" "${image_name_IN}" "${container_name_IN}" "/rich-context-competition/bin/git_pull.sh"

    # stop the container.
    #stop "${container_name_IN}"

    # if rich-context-competition folder exists, cd into it.
    if [[ -d "rich-context-competition" ]]
    then

        cd rich-context-competition

    fi
    
    # do a local pull
    git pull

} #-- END function git_pull() --#


#===============================================================================
# main
#===============================================================================

# This will load (including default values):
# BASE_FOLDER_IN="."
# GIT_REPO_FOLDER_PATH_IN="${BASE_FOLDER_IN}/rich-context-competition"
# EVALUATE_FOLDER_PATH_IN="${GIT_REPO_FOLDER_PATH_IN}/data/evaluate"
# TEMPLATE_FOLDER_PATH_IN="${GIT_REPO_FOLDER_PATH_IN}/templates"
# DATA_FOLDER_PATH_IN="${BASE_FOLDER_IN}/data"
# PROJECT_FOLDER_PATH_IN="${BASE_FOLDER_IN}/project"
# DEBUG=false
if [[ -f "${config_file_path}" ]]
then

    # load the configuration
    source "${config_file_path}"

    # retrieve the requested action.
    requested_action=${!action_arg}

    # DEBUG
    if [[ $DEBUG = true ]]
    then
        echo "Config file path: \"${config_file_path}\""
        echo "Requested action: \"${requested_action}\""
    fi

    # do the important work:
    case "${requested_action}" in

        "build")
            echo "BUILD!!!"
            build "${DOCKER_IMAGE_NAME_IN}" "${BASE_FOLDER_PATH_IN}"
        ;;
        "build-no-cache")
            echo "BUILD NO CACHE!!!"
            build "${DOCKER_IMAGE_NAME_IN}" "${BASE_FOLDER_PATH_IN}" false
        ;;
        "build-use-cache")
            echo "BUILD USE CACHE!!!"
            build "${DOCKER_IMAGE_NAME_IN}" "${BASE_FOLDER_PATH_IN}" true
        ;;
        "evaluate")
            echo "EVALUATE!!!"
            run "${PROJECT_FOLDER_PATH_IN}" "${DATA_FOLDER_PATH_IN}" "${DOCKER_IMAGE_NAME_IN}" "${DOCKER_CONTAINER_NAME_IN}" "/rich-context-competition/evaluate/evaluate.sh" "${DOCKER_CUSTOM_RUN_OPTIONS_IN}"
            ./rcc.sh stop
        ;;
        "init")
            echo "INIT!!!"
            init "${BASE_FOLDER_PATH_IN}" "${GIT_REPO_FOLDER_PATH_IN}"
        ;;
        "remove-docker-image")
            echo "REMOVE DOCKER IMAGE!!!"
            remove_docker_image "${DOCKER_IMAGE_NAME_IN}"
        ;;
        "reset-data-folder")
            echo "RESET DATA FOLDER!!!"
            reset_data_folder "${BASE_FOLDER_PATH_IN}" "${GIT_REPO_FOLDER_PATH_IN}"
        ;;
        "reset-project-folder")
            echo "RESET PROJECT FOLDER!!!"
            reset_project_folder "${BASE_FOLDER_PATH_IN}" "${GIT_REPO_FOLDER_PATH_IN}"
        ;;
        "reset-config-file")
            echo "RESET config.sh FILE!!!"
            reset_config_file "${BASE_FOLDER_PATH_IN}" "${GIT_REPO_FOLDER_PATH_IN}" true
        ;;
        "reset-dockerfile")
            echo "RESET Dockerfile!!!"
            reset_dockerfile "${BASE_FOLDER_PATH_IN}" "${GIT_REPO_FOLDER_PATH_IN}" true
        ;;
        "reset-rcc-script")
            echo "RESET rcc.sh SCRIPT!!!"
            reset_rcc_script "${BASE_FOLDER_PATH_IN}" "${GIT_REPO_FOLDER_PATH_IN}"
        ;;
        "run")
            echo "RUN!!!"
            run "${PROJECT_FOLDER_PATH_IN}" "${DATA_FOLDER_PATH_IN}" "${DOCKER_IMAGE_NAME_IN}" "${DOCKER_CONTAINER_NAME_IN}" "/project/code.sh" "${DOCKER_CUSTOM_RUN_OPTIONS_IN}"
        ;;
        "run-interactive")
            echo "RUN INTERACTIVE!!!"
            run_interactive "${PROJECT_FOLDER_PATH_IN}" "${DATA_FOLDER_PATH_IN}" "${DOCKER_IMAGE_NAME_IN}" "${DOCKER_CONTAINER_NAME_IN}" "${DOCKER_CUSTOM_RUN_OPTIONS_IN}"
        ;;
        "run-stop")
            echo "RUN THEN STOP!!!"
            run "${PROJECT_FOLDER_PATH_IN}" "${DATA_FOLDER_PATH_IN}" "${DOCKER_IMAGE_NAME_IN}" "${DOCKER_CONTAINER_NAME_IN}" "/project/code.sh" "${DOCKER_CUSTOM_RUN_OPTIONS_IN}"
            ./rcc.sh stop
        ;;
        "stop")
            echo "STOP!!!"
            stop "${DOCKER_CONTAINER_NAME_IN}"
        ;;
        *)
            echo ""
            echo "Requested action \"${requested_action}\" is not valid."
            echo ""
            echo "Valid actions:"
            echo "- build"
            echo "- build-no-cache"
            echo "- build-use-cache"
            echo "- evaluate"
            echo "- init"
            echo "- remove-docker-image"
            echo "- reset-data-folder"
            echo "- reset-project-folder"
            echo "- reset-config-file"
            echo "- reset-dockerfile"
            echo "- reset-rcc-script"
            echo "- run"
            echo "- run-interactive"
            echo "- run-stop"
            echo "- stop"
            echo ""
        ;;

    esac

else

    # no configuration file.  error.
    echo "No file at path \"${config_file_path}\""

fi
