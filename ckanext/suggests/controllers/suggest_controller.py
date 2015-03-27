import logging

import ckan.lib.base as base
import ckan.model as model
import ckan.plugins as plugins
import ckan.lib.helpers as helpers
import ckanext.suggests.constants as constants
import functools
import re

from ckan.common import request
from urllib import urlencode

##########################################################################################################
_link = re.compile(r'')
####  _link = re.compile(r'(?:(http://)|(www\.))(\S+\b/?)([!"#$%&\'()*+,\-./:;<=>?@[\\\]^_`{|}~]*)(\s|$)', re.I)
###########################################################################################################


log = logging.getLogger(__name__)
tk = plugins.toolkit
c = tk.c


def convert_links(text):
    def replace(match):
        groups = match.groups()
        protocol = groups[0] or ''  # may be None
        www_lead = groups[1] or ''  # may be None
        return '<a href="http://{1}{2}" target="_blank">{0}{1}{2}</a>{3}{4}'.format(
            protocol, www_lead, *groups[2:])
    return _link.sub(replace, text)


def _get_errors_summary(errors):
    errors_summary = {}

    for key, error in errors.items():
        errors_summary[key] = ', '.join(error)

    return errors_summary


def _encode_params(params):
    return [(k, v.encode('utf-8') if isinstance(v, basestring) else str(v))
            for k, v in params]


def url_with_params(url, params):
    params = _encode_params(params)
    return url + u'?' + urlencode(params)


def search_url(params):
    url = helpers.url_for(controller='ckanext.suggests.controllers.suggest_controller:SuggestsController',
                          action='index')
    return url_with_params(url, params)




class SuggestsController(base.BaseController):

    def _get_context(self):
        return {'model': model, 'session': model.Session,
                'user': c.user, 'auth_user_obj': c.userobj}

    def _show_index(self, url_func, file_to_render):

        def pager_url(q=None, page=None):
            params = list()
            params.append(('page', page))
            return url_func(params)

        try:
            context = self._get_context()
            page = int(request.GET.get('page', 1))
            limit = constants.SUGGESTS_PER_PAGE
            offset = (page - 1) * constants.SUGGESTS_PER_PAGE
            data_dict = {'offset': offset, 'limit': limit}

            state = request.GET.get('state', None)
            if state:
                data_dict['closed'] = True if state == 'closed' else False


            tk.check_access(constants.SUGGEST_INDEX, context, data_dict)
            suggests_list = tk.get_action(constants.SUGGEST_INDEX)(context, data_dict)
            c.suggest_count = suggests_list['count']
            c.suggests = suggests_list['result']
            c.search_facets = suggests_list['facets']
            c.page = helpers.Page(
                collection=suggests_list['result'],
                page=page,
                url=pager_url,
                item_count=suggests_list['count'],
                items_per_page=limit
            )
            c.facet_titles = {
                'state': tk._('State'),
            }


            return tk.render(file_to_render)
        except ValueError as e:
            # This exception should only occur if the page value is not valid
            log.warn(e)
            tk.abort(400, tk._('"page" parameter must be an integer'))
        except tk.NotAuthorized as e:
            log.warn(e)
            tk.abort(403, tk._('Unauthorized to list Data Requests'))

    def index(self):
        return self._show_index( search_url, 'suggests/index.html')

    def _process_post(self, action, context):
        # If the user has submitted the form, the data request must be created
        if request.POST:
            data_dict = {}
            data_dict['title'] = request.POST.get('title', '')
            data_dict['description'] = request.POST.get('description', '')


            if action == constants.SUGGEST_UPDATE:
                data_dict['id'] = request.POST.get('id', '')

            try:
                result = tk.get_action(action)(context, data_dict)
                tk.response.status_int = 302
                tk.response.location = '/%s/%s' % (constants.SUGGESTS_MAIN_PATH,
                                                   result['id'])

            except tk.ValidationError as e:
                log.warn(e)
                # Fill the fields that will display some information in the page
                c.suggest = {
                    'id': data_dict.get('id', ''),
                    'title': data_dict.get('title', ''),
                    'description': data_dict.get('description', '')
                }
                c.errors = e.error_dict
                c.errors_summary = _get_errors_summary(c.errors)

    def new(self):
        context = self._get_context()

        # Basic intialization
        c.suggest = {}
        c.errors = {}
        c.errors_summary = {}

        # Check access
        try:
            tk.check_access(constants.SUGGEST_CREATE, context, None)
            self._process_post(constants.SUGGEST_CREATE, context)

            # The form is always rendered
            return tk.render('suggests/new.html')

        except tk.NotAuthorized as e:
            log.warn(e)
            tk.abort(403, tk._('Unauthorized to create a Data Request'))

    def show(self, id):
        data_dict = {'id': id}
        context = self._get_context()

        try:
            tk.check_access(constants.SUGGEST_SHOW, context, data_dict)
            c.suggest = tk.get_action(constants.SUGGEST_SHOW)(context, data_dict)

            context_ignore_auth = context.copy()
            context_ignore_auth['ignore_auth'] = True

            return tk.render('suggests/show.html')
        except tk.ObjectNotFound as e:
            tk.abort(404, tk._('Data Request %s not found') % id)
        except tk.NotAuthorized as e:
            log.warn(e)
            tk.abort(403, tk._('You are not authorized to view the Data Request %s'
                               % id))

    def update(self, id):
        data_dict = {'id': id}
        context = self._get_context()

        # Basic intialization
        c.suggest = {}
        c.errors = {}
        c.errors_summary = {}

        try:
            tk.check_access(constants.SUGGEST_UPDATE, context, data_dict)
            c.suggest = tk.get_action(constants.SUGGEST_SHOW)(context, data_dict)
            c.original_title = c.suggest.get('title')
            self._process_post(constants.SUGGEST_UPDATE, context)
            return tk.render('suggests/edit.html')
        except tk.ObjectNotFound as e:
            log.warn(e)
            tk.abort(404, tk._('Data Request %s not found') % id)
        except tk.NotAuthorized as e:
            log.warn(e)
            tk.abort(403, tk._('You are not authorized to update the Data Request %s'
                               % id))

    def delete(self, id):
        data_dict = {'id': id}
        context = self._get_context()

        try:
            tk.check_access(constants.SUGGEST_DELETE, context, data_dict)
            suggest = tk.get_action(constants.SUGGEST_DELETE)(context, data_dict)
            tk.response.status_int = 302
            tk.response.location = '/%s' % constants.SUGGESTS_MAIN_PATH
            helpers.flash_notice(tk._('Data Request %s deleted correctly') % suggest.get('title', ''))
        except tk.ObjectNotFound as e:
            log.warn(e)
            tk.abort(404, tk._('Data Request %s not found') % id)
        except tk.NotAuthorized as e:
            log.warn(e)
            tk.abort(403, tk._('You are not authorized to delete the Data Request %s'
                               % id))


    def close(self, id):
        data_dict = {'id': id}
        context = self._get_context()

        # Basic intialization
        c.suggest = {}

        def _return_page(errors={}, errors_summary={}):

            base_datasets = tk.get_action('package_search')({'ignore_auth': True}, {'rows': 500})['results']

            c.datasets = []
            c.errors = errors
            c.errors_summary = errors_summary
            for dataset in base_datasets:
                c.datasets.append({'name': dataset.get('name'), 'title': dataset.get('title')})

            return tk.render('suggests/close.html')

        try:
            tk.check_access(constants.SUGGEST_CLOSE, context, data_dict)
            c.suggest = tk.get_action(constants.SUGGEST_SHOW)(context, data_dict)

            if c.suggest.get('closed', False):
                tk.abort(403, tk._('This data request is already closed'))
            elif request.POST:
                data_dict = {}
                data_dict['id'] = id

                tk.get_action(constants.SUGGEST_CLOSE)(context, data_dict)
                tk.response.status_int = 302
                tk.response.location = '/%s/%s' % (constants.SUGGESTS_MAIN_PATH, data_dict['id'])
            else:   # GET
                return _return_page()

        except tk.ValidationError as e:     # Accepted Dataset is not valid
            log.warn(e)
            errors_summary = _get_errors_summary(e.error_dict)
            return _return_page(e.error_dict, errors_summary)
        except tk.ObjectNotFound as e:
            log.warn(e)
            tk.abort(404, tk._('Data Request %s not found') % id)
        except tk.NotAuthorized as e:
            log.warn(e)
            tk.abort(403, tk._('You are not authorized to close the Data Request %s'
                               % id))

    def comment(self, id):
        try:
            context = self._get_context()
            data_dict_comment_list = {'suggest_id': id}
            data_dict_dr_show = {'id': id}
            tk.check_access(constants.SUGGEST_COMMENT_LIST, context, data_dict_comment_list)

            comment = request.POST.get('comment', '')
            comment_id = request.POST.get('comment-id', '')

            if request.POST:
                try:
                    comment_data_dict = {'suggest_id': id, 'comment': comment, 'id': comment_id}
                    action = constants.SUGGEST_COMMENT if not comment_id else constants.SUGGEST_COMMENT_UPDATE
                    comment = tk.get_action(action)(context, comment_data_dict)
                except tk.NotAuthorized as e:
                    log.warn(e)
                    tk.abort(403, tk._('You are not authorized to create/edit the comment'))
                except tk.ValidationError as e:
                    log.warn(e)
                    c.errors = e.error_dict
                    c.errors_summary = _get_errors_summary(c.errors)
                    c.comment = comment
                except tk.ObjectNotFound as e:
                    log.warn(e)
                    tk.abort(404, tk._('Data Request %s not found') % id)

            # TODO: Fix me... this function is not called if an exception is risen when the comment is
            # being created
            # Comments should be retrieved once that the comment has been created
            get_comments_data_dict = {'suggest_id': id}
            c.comments = tk.get_action(constants.SUGGEST_COMMENT_LIST)(context, get_comments_data_dict)
            c.suggest = tk.get_action(constants.SUGGEST_SHOW)(context, data_dict_dr_show)

            # Replace URLs by links
            # Replace new lines by HTML line break
            for comment in c.comments:
                comment['comment'] = convert_links(comment['comment'])
                comment['comment'] = comment['comment'].replace('\n', '<br/>')

        except tk.ObjectNotFound as e:
            log.warn(e)
            tk.abort(404, tk._('Data Request %s not found' % id))

        except tk.NotAuthorized as e:
            log.warn(e)
            tk.abort(403, tk._('You are not authorized to comment the Data Request %s'
                               % id))

        return tk.render('suggests/comment.html')

    def delete_comment(self, suggest_id, comment_id):
        print 'that feeling is the best thing, alright'
        try:
            context = self._get_context()
            data_dict = {'id': comment_id}
            tk.get_action(constants.SUGGEST_COMMENT_DELETE)(context, data_dict)
            tk.response.status_int = 302
            tk.response.location = '/%s/comment/%s' % (constants.SUGGESTS_MAIN_PATH, suggest_id)
        except tk.ObjectNotFound as e:
            log.warn(e)
            tk.abort(404, tk._('Comment %s not found') % comment_id)
        except tk.NotAuthorized as e:
            log.warn(e)
            tk.abort(403, tk._('You are not authorized to delete this comment'))
