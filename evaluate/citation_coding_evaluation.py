# imports
import json
import numpy
import six
import sklearn
from sklearn import metrics

class CitationCodingEvaluation( object ):
    
    #============================================================================
    # CONSTANTS-ish
    #============================================================================

    
    # result types
    RESULT_TYPE_BASELINE = "baseline"
    RESULT_TYPE_DERIVED = "derived"
    VALID_RESULT_TYPE_LIST = []
    VALID_RESULT_TYPE_LIST.append( RESULT_TYPE_BASELINE )
    VALID_RESULT_TYPE_LIST.append( RESULT_TYPE_DERIVED )
    
    # JSON property names
    JSON_NAME_PUBLICATION_ID = "publication_id"
    JSON_NAME_DATA_SET_ID = "data_set_id"
    JSON_NAME_SCORE = "score"
    JSON_NAME_DATA_SET_MAP = "data_set_map"

    # list types
    LIST_TYPE_BASELINE = "baseline"
    LIST_TYPE_DERIVED_RAW = "derived_raw"
    LIST_TYPE_DERIVED_BINARY = "derived_binary"
    LIST_TYPE_PUBLICATION_ID = "publication_id"
    LIST_TYPE_DATA_SET_ID = "data_set_id"
    
    # details key values
    DETAILS_INCLUDED_ARTICLE_COUNT = "included_article_count"
    DETAILS_INCLUDED_ARTICLE_ID_LIST = "included_article_id_list"
    DETAILS_EXCLUDED_ARTICLE_COUNT = "excluded_article_count"
    DETAILS_EXCLUDED_ARTICLE_ID_LIST = "excluded_article_id_list"


    #============================================================================
    # ! ==> Built-in Instance methods
    #============================================================================


    def __init__( self, *args, **kwargs ):
        
        # initialize variables
        self.debug_flag = False
        self.m_citation_map = {}
        self.m_lists_by_publication = {}
        self.m_cutoff = 0.0

        # built lists, per citation (article-data set pair)
        self.m_baseline_list = []
        self.m_derived_binary_list = []
        self.m_derived_raw_list = []
        self.m_publication_id_list = []
        self.m_data_set_id_list = []
        
        # variable to hold white list of IDs of articles whose data we want to
        #     include in calculations.
        self.m_excluded_article_tag_list = []
        self.m_included_article_tag_list = []
        self.m_included_article_id_list = []

    #-- END method __init__() --#


    def __str__( self, fancy_print_IN = True, *args, **kwargs ):

        # return reference
        string_OUT = ""
        
        # note the class
        string_OUT = "CitationCodingEvaluation"
        
        return string_OUT
        
    #-- END method __str__() --#
    

    #============================================================================
    # instance methods
    #============================================================================


    def create_evaluation_lists(self):
        
        '''
        Works with the data already loaded into this instance from JSON files
            using "process_citation_json()".
            
        Loops over nested         
        
        Returns details dictionary that includes:
        - "included_article_count" (DETAILS_INCLUDED_ARTICLE_COUNT) - count of articles included in evaluation.
        - "included_article_id_list" (DETAILS_INCLUDED_ARTICLE_ID_LIST) - list of IDs of articles included in evaluation.
        - "excluded_article_count" (DETAILS_EXCLUDED_ARTICLE_COUNT) - count of articles excluded from evaluation.
        - "excluded_article_id_list" (DETAILS_EXCLUDED_ARTICLE_ID_LIST) - list of IDs of articles excluded from evaluation.
        '''

        # return reference
        details_OUT = {}

        # declare variables
        citation_map = None
        baseline_list = None
        derived_binary_list = None
        derived_raw_list = None
        publication_id_per_citation_list = None
        data_set_id_per_citation_list = None
        cutoff_value = None
        publication_id_list = None
        publication_id = None
        publication_dict = None
        data_set_map = None
        data_set_id_list = None
        data_set_id = None
        data_set_found_map = None
        baseline_score = -1
        derived_score = -1

        # declare variables - per-publication lists
        pub_list_dictionary = None
        pub_baseline_list = None
        pub_derived_binary_list = None
        pub_derived_raw_list = None
        pub_publication_id_per_citation_list = None
        pub_data_set_id_per_citation_list = None
        
        # declare variables - included publications
        included_pub_id_list = None
        do_filter_articles = None
        do_process_pub = None
        included_article_count = -1
        included_article_id_list = None
        excluded_article_count = -1
        excluded_article_id_list = None

        # get citation_map
        citation_map = self.get_citation_map()

        # init lists
        baseline_list = self.set_baseline_list( [] )
        derived_binary_list = self.set_derived_binary_list( [] )
        derived_raw_list = self.set_derived_raw_list( [] )
        publication_id_per_citation_list = self.set_publication_id_list( [] )
        data_set_id_per_citation_list = self.set_data_set_id_list( [] )

        # cutoffs
        cutoff_value = self.get_cutoff()
        
        # see if there is a list of included article IDs.
        included_pub_id_list = self.get_included_article_id_list()
        if ( ( included_pub_id_list is not None ) and ( len( included_pub_id_list ) > 0 ) ):
        
            # we have an article ID filter list.  Use it.
            do_filter_articles = True
        
        else:
        
            # not filtering.
            do_filter_articles = False
            
        #-- END check to see if we have a publication ID white list. --#

        # so we can get publication ID list
        publication_id_list = list( six.viewkeys( citation_map ) )
        publication_id_list.sort()

        # loop over publications, and then data sets within.
        included_article_count = 0
        included_article_id_list = []
        excluded_article_count = 0
        excluded_article_id_list = []
        for publication_id in publication_id_list:
        
            # are we filtering publications?
            if ( do_filter_articles == True ):
            
                # we are.  Check to see if the current publication ID is in the
                #    icluded ID list.
                if ( publication_id in included_pub_id_list ):
                
                    # it is in our list.  Process it.
                    do_process_pub = True
                    included_article_count += 1
                    included_article_id_list.append( publication_id )

                    # DEBUG
                    if ( self.debug_flag == True ):
                        print( "INCLUDING Publication ID: {}".format( publication_id ) )
                    # -- END DEBUG --#
                    
                else:
                
                    # it is not in our list.  Do not process.
                    do_process_pub = False
                    excluded_article_count += 1
                    excluded_article_id_list.append( publication_id )
                    
                    # DEBUG
                    if ( self.debug_flag == True ):
                        print( "SKIPPING Publication ID: {}".format( publication_id ) )
                    # -- END DEBUG --#
    
                #-- END check to see if publication ID is in included list. --#
                
            
            else:
            
                # not filtering.  Just process the publication.
                do_process_pub = True                
                included_article_count += 1
                included_article_id_list.append( publication_id )
                
            #-- END check to see if we are filtering articles --#
    
            # do we process this publication?
            if ( do_process_pub == True ):
    
                # get lists for publication
                pub_list_dictionary = self.get_lists_for_publication( publication_id )
                pub_baseline_list = pub_list_dictionary.get( self.LIST_TYPE_BASELINE, None )
                pub_derived_binary_list = pub_list_dictionary.get( self.LIST_TYPE_DERIVED_BINARY, None )
                pub_derived_raw_list = pub_list_dictionary.get( self.LIST_TYPE_DERIVED_RAW, None )
                pub_publication_id_per_citation_list = pub_list_dictionary.get( self.LIST_TYPE_PUBLICATION_ID, None )
                pub_data_set_id_per_citation_list = pub_list_dictionary.get( self.LIST_TYPE_DATA_SET_ID, None )
    
                # DEBUG
                if ( self.debug_flag == True ):
                    print( "Publication ID: {}".format( publication_id ) )
                # -- END DEBUG --#
    
                # get publication map
                publication_dict = citation_map.get( publication_id, None )
    
                # get the data set map and ID list.
                data_set_map = publication_dict.get( self.JSON_NAME_DATA_SET_MAP, None )
                data_set_id_list = list( six.viewkeys( data_set_map ) )
                data_set_id_list.sort()
    
                # loop over data set ID list.
                for data_set_id in data_set_id_list:
    
                    # DEBUG
                    if ( self.debug_flag == True ):
                        print( "==> Data Set ID: {}".format( data_set_id ) )
                    # -- END DEBUG --#
    
                    # get the data_set_found_map
                    data_set_found_map = data_set_map.get( data_set_id, None )
    
                    # get the scores.
                    baseline_score = data_set_found_map.get( self.RESULT_TYPE_BASELINE, 0.0 )
                    derived_score = data_set_found_map.get( self.RESULT_TYPE_DERIVED, 0.0 )
    
                    # DEBUG
                    if ( self.debug_flag == True ):
                        print( "            baseline: {}".format( baseline_score ) )
                        print( "            derived.: {}".format( derived_score ) )
                    # -- END DEBUG --#
    
                    # add them to the lists
    
                    # baseline lists
                    baseline_list.append( baseline_score )
                    pub_baseline_list.append( baseline_score )
    
                    # derived_raw lists
                    derived_raw_list.append( derived_score )
                    pub_derived_raw_list.append( derived_score )
    
                    # derived_binary lists
                    if derived_score > cutoff_value:
                        derived_binary_list.append( 1.0 )
                        pub_derived_binary_list.append( 1.0 )
                    else:
                        derived_binary_list.append( 0.0 )
                        pub_derived_binary_list.append( 0.0 )
                    # -- END binary value assignment --#
    
                    # add the publication and data set IDs to the per-citation lists.
                    publication_id_per_citation_list.append( publication_id )
                    pub_publication_id_per_citation_list.append( publication_id )
                    data_set_id_per_citation_list.append( data_set_id )
                    pub_data_set_id_per_citation_list.append( data_set_id )
    
                #-- END loop over data set IDs. --#
    
            else:
            
                # not processing publication.
                # DEBUG
                if ( self.debug_flag == True ):
                    print( "SKIPPED Publication ID: {}".format( publication_id ) )
                # -- END DEBUG --#

            #-- END check to see if we process current publication --#

        # -- END loop over publication IDs. --#
        
        # store details
        details_OUT[ self.DETAILS_INCLUDED_ARTICLE_COUNT ] = included_article_count
        details_OUT[ self.DETAILS_INCLUDED_ARTICLE_ID_LIST ] = included_article_id_list
        details_OUT[ self.DETAILS_EXCLUDED_ARTICLE_COUNT ] = excluded_article_count
        details_OUT[ self.DETAILS_EXCLUDED_ARTICLE_ID_LIST ] = excluded_article_id_list

        return details_OUT

    # -- END method create_evaluation_lists() --#


    def get_baseline_list( self ):
    
        # return reference
        value_OUT = None
        
        # declare variables
        instance = None
        
        # get instance
        value_OUT = self.m_baseline_list
        
        # got anything?
        if ( value_OUT is None ):
        
            # make list instance.
            instance = []
            
            # store the instance.
            self.set_baseline_list( instance )
            
            # get the instance.
            value_OUT = self.get_baseline_list()
        
        #-- END check to see if instance initialized. --#
        
        return value_OUT
    
    #-- END method get_baseline_list --#


    def get_citation_map( self ):
    
        # return reference
        value_OUT = None
        
        # declare variables
        dict_instance = None
        
        # get m_dictionary
        value_OUT = self.m_citation_map
        
        # got anything?
        if ( value_OUT is None ):
        
            # make dictionary instance.
            dict_instance = {}
            
            # store the instance.
            self.set_citation_map( dict_instance )
            
            # get the instance.
            value_OUT = self.get_citation_map()
        
        #-- END check to see if dictionary initialized. --#
        
        return value_OUT
    
    #-- END method get_citation_map --#


    def get_cutoff( self ):
    
        # return reference
        value_OUT = None
        
        # get m_dictionary
        value_OUT = self.m_cutoff
                
        return value_OUT
    
    #-- END method get_cutoff --#


    def get_data_set_id_list( self ):

        # return reference
        value_OUT = None

        # declare variables
        instance = None

        # get instance
        value_OUT = self.m_data_set_id_list

        # got anything?
        if (value_OUT is None):

            # make list instance.
            instance = []

            # store the instance.
            self.set_data_set_id_list( instance )

            # get the instance.
            value_OUT = self.get_data_set_id_list()

        # -- END check to see if instance initialized. --#

        return value_OUT

    # -- END method get_data_set_id_list --#


    def get_derived_binary_list( self ):
    
        # return reference
        value_OUT = None
        
        # declare variables
        instance = None
        
        # get instance
        value_OUT = self.m_derived_binary_list
        
        # got anything?
        if ( value_OUT is None ):
        
            # make list instance.
            instance = []
            
            # store the instance.
            self.set_derived_binary_list( instance )
            
            # get the instance.
            value_OUT = self.get_derived_binary_list()
        
        #-- END check to see if instance initialized. --#
        
        return value_OUT
    
    #-- END method get_derived_binary_list --#


    def get_derived_raw_list( self ):
    
        # return reference
        value_OUT = None
        
        # declare variables
        instance = None
        
        # get instance
        value_OUT = self.m_derived_raw_list
        
        # got anything?
        if ( value_OUT is None ):
        
            # make list instance.
            instance = []
            
            # store the instance.
            self.set_derived_raw_list( instance )
            
            # get the instance.
            value_OUT = self.get_derived_raw_list()
        
        #-- END check to see if instance initialized. --#
        
        return value_OUT
    
    #-- END method get_derived_raw_list --#


    def get_excluded_article_tag_list( self ):

        # return reference
        value_OUT = None

        # declare variables
        instance = None

        # get instance
        value_OUT = self.m_excluded_article_tag_list

        # got anything?
        if (value_OUT is None):

            # make list instance.
            instance = []

            # store the instance.
            self.set_excluded_article_tag_list( instance )

            # get the instance.
            value_OUT = self.get_excluded_article_tag_list()

        # -- END check to see if instance initialized. --#

        return value_OUT

    # -- END method get_exncluded_article_tag_list --#


    def get_included_article_id_list( self ):

        # return reference
        value_OUT = None

        # declare variables
        instance = None

        # get instance
        value_OUT = self.m_included_article_id_list

        # got anything?
        if (value_OUT is None):

            # make list instance.
            instance = []

            # store the instance.
            self.set_included_article_id_list( instance )

            # get the instance.
            value_OUT = self.get_included_article_id_list()

        # -- END check to see if instance initialized. --#

        return value_OUT

    # -- END method get_included_article_id_list --#


    def get_included_article_tag_list( self ):

        # return reference
        value_OUT = None

        # declare variables
        instance = None

        # get instance
        value_OUT = self.m_included_article_tag_list

        # got anything?
        if (value_OUT is None):

            # make list instance.
            instance = []

            # store the instance.
            self.set_included_article_tag_list( instance )

            # get the instance.
            value_OUT = self.get_included_article_tag_list()

        # -- END check to see if instance initialized. --#

        return value_OUT

    # -- END method get_included_article_tag_list --#


    def get_lists_by_publication(self):

        # return reference
        value_OUT = None

        # declare variables
        instance = None

        # get instance
        value_OUT = self.m_lists_by_publication

        # got anything?
        if (value_OUT is None):

            # make instance.
            instance = {}

            # store the instance.
            self.set_lists_by_publication( instance )

            # get the instance.
            value_OUT = self.get_lists_by_publication()

        # -- END check to see if instance initialized. --#

        return value_OUT

    # -- END method get_lists_by_publication --#


    def get_lists_for_publication( self, publication_id_IN ):

        # return reference
        value_OUT = None

        # declare variables
        pub_lists = None
        instance = None

        # do we have a publication ID?
        if ( ( publication_id_IN is not None ) and ( publication_id_IN != "" ) ):

            # get lists for publications
            pub_lists = self.get_lists_by_publication()

            # see if publication already has lists.
            if ( publication_id_IN not in pub_lists ):

                # not yet.  Make a dictionary...
                pub_list_dict = {}

                # ...add empty lists for each of the 4 types...
                pub_list_dict[ self.LIST_TYPE_BASELINE ] = []
                pub_list_dict[ self.LIST_TYPE_DERIVED_RAW ] = []
                pub_list_dict[ self.LIST_TYPE_DERIVED_BINARY ] = []
                pub_list_dict[ self.LIST_TYPE_PUBLICATION_ID ] = []
                pub_list_dict[ self.LIST_TYPE_DATA_SET_ID ] = []

                # ...store it in pub lists...
                pub_lists[ publication_id_IN ] = pub_list_dict

                # retrieve lists dictionary for publication ID.
                value_OUT = self.get_lists_for_publication( publication_id_IN )

            else:

                value_OUT = pub_lists.get( publication_id_IN, None )

            #-- END check to see if publication ID in pub lists map. --#

        else:

            print( "No publication ID passed in, so can't retrieve lists." )

        #-- END check to see if publication ID --#

        return value_OUT

    # -- END method get_lists_for_publication --#


    def get_publication_id_list( self ):

        # return reference
        value_OUT = None

        # declare variables
        instance = None

        # get instance
        value_OUT = self.m_publication_id_list

        # got anything?
        if (value_OUT is None):

            # make list instance.
            instance = []

            # store the instance.
            self.set_publication_id_list( instance )

            # get the instance.
            value_OUT = self.get_publication_id_list()

        # -- END check to see if instance initialized. --#

        return value_OUT

    # -- END method get_publication_id_list --#


    def process_citation_json( self, citation_list_json_IN, result_type_IN ):

        # return reference
        status_OUT = None

        # declare variables
        status_string = None
        citation_map = None
        publication_id = None
        data_set_id = None
        raw_score = None
        citation_json = None
        raw_score = None
        publication_dict = None

        # make sure we have output map.
        citation_map = self.get_citation_map()
        if ( citation_map is not None ):

            # make sure we have JSON
            if ( citation_list_json_IN is not None ):

                # valid result type?
                if ( ( result_type_IN is not None )
                    and ( result_type_IN != "" )
                    and ( result_type_IN in self.VALID_RESULT_TYPE_LIST ) ):

                    # loop over citation items in 
                    for citation_json in citation_list_json_IN:

                        # get the publication ID, data set ID, and score.
                        publication_id = citation_json.get( self.JSON_NAME_PUBLICATION_ID )
                        data_set_id = citation_json.get( self.JSON_NAME_DATA_SET_ID )
                        raw_score = citation_json.get( self.JSON_NAME_SCORE, None )

                        # look up the publication in the publication to data set map.
                        if publication_id not in citation_map:

                            # init publication dictionary.
                            publication_dict = {}
                            publication_dict[ self.JSON_NAME_PUBLICATION_ID ] = publication_id
                            publication_dict[ self.JSON_NAME_DATA_SET_MAP ] = {}

                            # store it in the map
                            citation_map[ publication_id ] = publication_dict

                        else:

                            # get the dictionary.
                            publication_dict = citation_map.get( publication_id, None )

                        #-- END check to see if publication is in list. --#

                        # retrieve citation map and id list.
                        data_set_map = publication_dict.get( self.JSON_NAME_DATA_SET_MAP, None )

                        # check to see if data set ID is in the map.
                        if ( data_set_id not in data_set_map ):

                            # no - make a dictionary and add it.
                            data_set_found_map = {}
                            data_set_found_map[ self.JSON_NAME_DATA_SET_ID ] = data_set_id
                            data_set_found_map[ self.RESULT_TYPE_BASELINE ] = 0.0
                            data_set_found_map[ self.RESULT_TYPE_DERIVED ] = 0.0
                            data_set_map[ data_set_id ] = data_set_found_map

                        else:

                            # get it.
                            data_set_found_map = data_set_map.get( data_set_id, None )

                        #-- END check to see if in map --#

                        # update the found map.
                        if ( raw_score is not None ):

                            # yes - store it.
                            data_set_found_map[ result_type_IN ] = raw_score

                        else:

                            # no - binary - FOUND! (1.0)
                            data_set_found_map[ result_type_IN ] = 1.0

                        #-- END check to see if raw score or not. --#

                    #-- END loop over citations in JSON --#

                else:

                    status_OUT = "ERROR - result type of {} is not valid.  Should be one of: {}".format( result_type_IN, VALID_RESULT_TYPE_LIST )

                #-- END check to see if valid result_type_IN --#

            else:

                status_OUT = "WARNING - no JSON passed in, nothing to do."

            #-- END check to see if JSON passed in --#

        else:

            status_OUT = "ERROR - no citation map, returning None."

        #-- END check to see if citation map passed in. --#
        
        if ( ( self.debug_flag == True ) and ( status_OUT is not None ) and ( status_OUT != "" ) ):
            
            print( status_OUT )
            
        #-- END check to see if status set --#

        return status_OUT

    #-- END method process_citation_json() --#
    
    
    def set_baseline_list( self, instance_IN ):
        
        '''
        Accepts list.  Stores it and returns it.
        '''
        
        # return reference
        value_OUT = None
        
        # use store dictionary.
        self.m_baseline_list = instance_IN
        
        # return it.
        value_OUT = self.m_baseline_list
        
        return value_OUT
        
    #-- END method set_baseline_list() --#


    def set_citation_map( self, instance_IN ):
        
        '''
        Accepts dictionary.  Stores it and returns it.
        '''
        
        # return reference
        value_OUT = None
        
        # use store dictionary.
        self.m_citation_map = instance_IN
        
        # return it.
        value_OUT = self.m_citation_map
        
        return value_OUT
        
    #-- END method set_citation_map() --#


    def set_cutoff( self, value_IN ):
        
        '''
        Accepts value.  Stores it and returns it.
        '''
        
        # return reference
        value_OUT = None
        
        # store value.
        self.m_cutoff = value_IN
        
        # return it.
        value_OUT = self.m_cutoff
        
        return value_OUT
        
    #-- END method set_cutoff() --#


    def set_data_set_id_list(self, instance_IN):

        '''
        Accepts list.  Stores it and returns it.
        '''

        # return reference
        value_OUT = None

        # store value.
        self.m_data_set_id_list = instance_IN

        # return it.
        value_OUT = self.m_data_set_id_list

        return value_OUT

    # -- END method set_data_set_id_list() --#


    def set_derived_binary_list( self, instance_IN ):
        
        '''
        Accepts list.  Stores it and returns it.
        '''
        
        # return reference
        value_OUT = None
        
        # use store dictionary.
        self.m_derived_binary_list = instance_IN
        
        # return it.
        value_OUT = self.m_derived_binary_list
        
        return value_OUT
        
    #-- END method set_derived_binary_list() --#


    def set_derived_raw_list( self, instance_IN ):
        
        '''
        Accepts list.  Stores it and returns it.
        '''
        
        # return reference
        value_OUT = None
        
        # use store dictionary.
        self.m_derived_raw_list = instance_IN
        
        # return it.
        value_OUT = self.m_derived_raw_list
        
        return value_OUT
        
    #-- END method set_derived_raw_list() --#


    def set_excluded_article_tag_list( self, instance_IN):

        '''
        Accepts list.  Stores it and returns it.
        '''

        # return reference
        value_OUT = None

        # store value.
        self.m_excluded_article_tag_list = instance_IN

        # return it.
        value_OUT = self.m_excluded_article_tag_list

        return value_OUT

    # -- END method set_excluded_article_tag_list() --#


    def set_included_article_id_list( self, instance_IN):

        '''
        Accepts list.  Stores it and returns it.
        '''

        # return reference
        value_OUT = None

        # store value.
        self.m_included_article_id_list = instance_IN

        # return it.
        value_OUT = self.m_included_article_id_list

        return value_OUT

    # -- END method set_included_article_id_list() --#


    def set_included_article_tag_list( self, instance_IN):

        '''
        Accepts list.  Stores it and returns it.
        '''

        # return reference
        value_OUT = None

        # store value.
        self.m_included_article_tag_list = instance_IN

        # return it.
        value_OUT = self.m_included_article_tag_list

        return value_OUT

    # -- END method set_included_article_tag_list() --#


    def set_lists_by_publication(self, instance_IN):

        '''
        Accepts dictionary.  Stores it and returns it.
        '''

        # return reference
        value_OUT = None

        # store dictionary.
        self.m_lists_by_publication = instance_IN

        # return it.
        value_OUT = self.m_lists_by_publication

        return value_OUT

    # -- END method set_lists_by_publication() --#


    def set_publication_id_list(self, instance_IN):

        '''
        Accepts list.  Stores it and returns it.
        '''

        # return reference
        value_OUT = None

        # use store dictionary.
        self.m_publication_id_list = instance_IN

        # return it.
        value_OUT = self.m_publication_id_list

        return value_OUT

    # -- END method set_publication_id_list() --#


#-- END class CitationCodingEvaluation --#
