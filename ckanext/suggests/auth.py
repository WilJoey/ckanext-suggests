import constants
from ckan.plugins import toolkit as tk


def suggest_create(context, data_dict):
    return {'success': True}


@tk.auth_allow_anonymous_access
def suggest_show(context, data_dict):
    return {'success': True}


def auth_if_creator(context, data_dict, show_function):
    # Sometimes data_dict only contains the 'id'
    if 'user_id' not in data_dict:
        function = tk.get_action(show_function)
        data_dict = function({'ignore_auth': True}, {'id': data_dict.get('id')})

    return {'success': data_dict['user_id'] == context.get('auth_user_obj').id}


def suggest_update(context, data_dict):
    #return auth_if_creator(context, data_dict, constants.SUGGEST_SHOW)
    ##JOE##
    return {'success': False}


@tk.auth_allow_anonymous_access
def suggest_index(context, data_dict):
    return {'success': True}


def suggest_delete(context, data_dict):
    #return auth_if_creator(context, data_dict, constants.SUGGEST_SHOW)
    ##JOE##
    return {'success': False}

def suggest_close(context, data_dict):
    #return auth_if_creator(context, data_dict, constants.SUGGEST_SHOW)
    ##JOE##
    return {'success': False}

def suggest_comment(context, data_dict):
    return {'success': True}


@tk.auth_allow_anonymous_access
def suggest_comment_list(context, data_dict):
    new_data_dict = {'id': data_dict['suggest_id']}
    return suggest_show(context, new_data_dict)


@tk.auth_allow_anonymous_access
def suggest_comment_show(context, data_dict):
    return {'success': True}


def suggest_comment_update(context, data_dict):
    return auth_if_creator(context, data_dict, constants.SUGGEST_COMMENT_SHOW)


def suggest_comment_delete(context, data_dict):
    return auth_if_creator(context, data_dict, constants.SUGGEST_COMMENT_SHOW)
