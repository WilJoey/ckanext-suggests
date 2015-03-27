import ckan.plugins as p
import ckan.plugins.toolkit as tk
import auth
import actions
import constants


class SuggestsPlugin(p.SingletonPlugin):

    p.implements(p.IActions)
    p.implements(p.IAuthFunctions)
    p.implements(p.IConfigurer)
    p.implements(p.IRoutes, inherit=True)

    ######################################################################
    ############################## IACTIONS ##############################
    ######################################################################

    def get_actions(self):
        return {
            constants.SUGGEST_CREATE: actions.suggest_create,
            constants.SUGGEST_SHOW: actions.suggest_show,
            constants.SUGGEST_UPDATE: actions.suggest_update,
            constants.SUGGEST_INDEX: actions.suggest_index,
            constants.SUGGEST_DELETE: actions.suggest_delete,
            constants.SUGGEST_CLOSE: actions.suggest_close,
            constants.SUGGEST_COMMENT: actions.suggest_comment,
            constants.SUGGEST_COMMENT_LIST: actions.suggest_comment_list,
            constants.SUGGEST_COMMENT_SHOW: actions.suggest_comment_show,
            constants.SUGGEST_COMMENT_UPDATE: actions.suggest_comment_update,
            constants.SUGGEST_COMMENT_DELETE: actions.suggest_comment_delete

        }

    ######################################################################
    ########################### AUTH FUNCTIONS ###########################
    ######################################################################

    def get_auth_functions(self):
        return {
            constants.SUGGEST_CREATE: auth.suggest_create,
            constants.SUGGEST_SHOW: auth.suggest_show,
            constants.SUGGEST_UPDATE: auth.suggest_update,
            constants.SUGGEST_INDEX: auth.suggest_index,
            constants.SUGGEST_DELETE: auth.suggest_delete,
            constants.SUGGEST_CLOSE: auth.suggest_close,
            constants.SUGGEST_COMMENT: auth.suggest_comment,
            constants.SUGGEST_COMMENT_LIST: auth.suggest_comment_list,
            constants.SUGGEST_COMMENT_SHOW: auth.suggest_comment_show,
            constants.SUGGEST_COMMENT_UPDATE: auth.suggest_comment_update,
            constants.SUGGEST_COMMENT_DELETE: auth.suggest_comment_delete
        }

    ######################################################################
    ############################ ICONFIGURER #############################
    ######################################################################

    def update_config(self, config):
        # Add this plugin's templates dir to CKAN's extra_template_paths, so
        # that CKAN will use this plugin's custom templates.
        tk.add_template_directory(config, 'templates')

        # Register this plugin's fanstatic directory with CKAN.
        tk.add_public_directory(config, 'public')

        # Register this plugin's fanstatic directory with CKAN.
        tk.add_resource('fanstatic', 'suggest')

    ######################################################################
    ############################## IROUTES ###############################
    ######################################################################

    def before_map(self, m):
        # Data Requests index
        m.connect('suggests_index', "/%s" % constants.SUGGESTS_MAIN_PATH,
                  controller='ckanext.suggests.controllers.suggest_controller:SuggestsController',
                  action='index', conditions=dict(method=['GET']))

        # Create a Data Request
        m.connect('/%s/new' % constants.SUGGESTS_MAIN_PATH,
                  controller='ckanext.suggests.controllers.suggest_controller:SuggestsController',
                  action='new', conditions=dict(method=['GET', 'POST']))

        # Show a Data Request
        m.connect('suggest_show', '/%s/{id}' % constants.SUGGESTS_MAIN_PATH,
                  controller='ckanext.suggests.controllers.suggest_controller:SuggestsController',
                  action='show', conditions=dict(method=['GET']), ckan_icon='question-sign')

        # Update a Data Request
        m.connect('/%s/edit/{id}' % constants.SUGGESTS_MAIN_PATH,
                  controller='ckanext.suggests.controllers.suggest_controller:SuggestsController',
                  action='update', conditions=dict(method=['GET', 'POST']))

        # Delete a Data Request
        m.connect('/%s/delete/{id}' % constants.SUGGESTS_MAIN_PATH,
                  controller='ckanext.suggests.controllers.suggest_controller:SuggestsController',
                  action='delete', conditions=dict(method=['POST']))

        # Close a Data Request
        m.connect('/%s/close/{id}' % constants.SUGGESTS_MAIN_PATH,
                  controller='ckanext.suggests.controllers.suggest_controller:SuggestsController',
                  action='close', conditions=dict(method=['GET', 'POST']))


        # Comment, update and view comments (of) a Data Request
        m.connect('suggest_comment', '/%s/comment/{id}' % constants.SUGGESTS_MAIN_PATH,
                  controller='ckanext.suggests.controllers.suggest_controller:SuggestsController',
                  action='comment', conditions=dict(method=['GET', 'POST']), ckan_icon='comment')

        # Delete data request
        m.connect('/%s/comment/{suggest_id}/delete/{comment_id}' % constants.SUGGESTS_MAIN_PATH,
                  controller='ckanext.suggests.controllers.suggest_controller:SuggestsController',
                  action='delete_comment', conditions=dict(method=['GET', 'POST']))

        return m
