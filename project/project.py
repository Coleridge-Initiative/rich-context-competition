# introduce myself
print( "Publication parse example:" )

# imports
import codecs
import json
import shutil

# declare variables
publications_json_path = None
json_publication_file = None
publication_list = None
publication_counter = -1
publication_info = None
pub_date = None
unique_identifier = None
text_file_name = None
pdf_file_name = None
title = None
publication_id = None
citation_file_from = None
citation_file_to = None

# set path to publications.json
publications_json_path = "/data/input/publications.json"

# open the publications.json file
with open( publications_json_path ) as json_publication_file:

    # parse it as JSON
    publication_list = json.load( json_publication_file )
    
    # loop over the elements in the list
    publication_counter = 0
    for publication_info in publication_list:

        # increment counter
        publication_counter += 1

        # get information on publication:
        pub_date = publication_info.get( "pub_date", None )
        unique_identifier = publication_info.get( "unique_identifier", None )
        text_file_name = publication_info.get( "text_file_name", None )
        pdf_file_name = publication_info.get( "pdf_file_name", None )
        title = publication_info.get( "title", None )
        publication_id = publication_info.get( "publication_id", None )

        # print.
        print( "\n" )
        print( "publication {}".format( publication_counter ) )
        print( "- pub_date: {}".format( pub_date ) )
        print( "- unique_identifier: {}".format( unique_identifier ) )
        print( "- text_file_name: {}".format( text_file_name ) )
        print( "- pdf_file_name: {}".format( pdf_file_name ) )
        print( "- title: {}".format( codecs.encode( title, "ascii", "xmlcharrefreplace" ) ) )
        print( "- publication_id: {}".format( publication_id ) )

    #-- END loop over publications --#

#-- END with...as --#

# and, finally, test ability to write to "/data/output"
citation_file_from = "/rich-context-competition/evaluate/data_set_citations.json"
citation_file_to = "/data/output/data_set_citations.json"
shutil.copyfile( citation_file_from, citation_file_to )
print( "Copied from {} to {}.".format( citation_file_from, citation_file_to ) )