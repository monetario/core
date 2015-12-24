import functools

from flask import jsonify as flask_jsonify
from flask import request
from flask import url_for


def jsonify(exclude=None):
    """
    This decorator generates a JSON response from a Python dictionary or
    a SQLAlchemy model.
    """
    def decorator(f):
        @functools.wraps(f)
        def wrapped(*args, **kwargs):
            rv = f(*args, **kwargs)
            status_or_headers = {}
            headers = None
            if isinstance(rv, tuple):
                rv, status_or_headers, headers = rv + (None,) * (3 - len(rv))
            if isinstance(status_or_headers, (dict, list)):
                headers, status_or_headers = status_or_headers, None
            if not isinstance(rv, dict):
                # assume it is a model, call its to_json() method
                rv = rv.to_json(exclude=exclude).data
            rv = flask_jsonify(rv)
            if status_or_headers is not None:
                rv.status_code = status_or_headers
            if headers is not None:
                rv.headers.extend(headers)
            return rv
        return wrapped
    return decorator


def _filter_query(model, query, filter_spec):
    filters = [f.split(',') for f in filter_spec.split(';')]

    for f in filters:
        if len(f) < 3 or (len(f) > 3 and f[1] != 'in'):
            continue
        if f[1] == 'in':
            f = [f[0], f[1], f[2:]]
        ops = {'eq': '__eq__', 'ne': '__ne__', 'lt': '__lt__', 'le': '__le__',
               'gt': '__gt__', 'ge': '__ge__', 'in': 'in_', 'like': 'like'}
        if hasattr(model, f[0]) and f[1] in ops.keys():
            column = getattr(model, f[0])
            op = ops[f[1]]
            query = query.filter(getattr(column, op)(f[2]))
    return query


def _sort_query(model, query, sort_spec):
    sort = [s.split(',') for s in sort_spec.split(';')]

    for s in sort:
        if hasattr(model, s[0]):
            column = getattr(model, s[0])
            if len(s) == 2 and s[1] in ['asc', 'desc']:
                query = query.order_by(getattr(column, s[1])())
            else:
                query = query.order_by(column.asc())
    return query


def collection(model, name=None, max_per_page=10, exclude=None):
    """
    This decorator implements pagination, filtering, sorting and expanding
    for collections. The expected response from the decorated route is a
    SQLAlchemy query.
    """
    if name is None:
        name = model.__tablename__

    def decorator(f):
        @functools.wraps(f)
        def wrapped(*args, **kwargs):
            query = f(*args, **kwargs)

            p, meta = get_pagination(model, query, max_per_page, **kwargs)

            expand = request.args.get('expand')

            if expand:
                items = [item.to_json(exclude=exclude).data for item in p.items]
            else:
                items = [item.resource_url for item in p.items]
            return {'objects': items, 'meta': meta}
            # return {name: items, 'meta': meta}
        return wrapped
    return decorator


def get_pagination(model, query, max_per_page=10, **kwargs):
    # filtering and sorting
    filter = request.args.get('filter')
    if filter:
        query = _filter_query(model, query, filter)
    sort = request.args.get('sort')
    if sort:
        query = _sort_query(model, query, sort)

    # pagination
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', max_per_page,
                                    type=int), max_per_page)
    expand = request.args.get('expand')

    p = query.paginate(page, per_page)
    pages = {'page': page, 'per_page': per_page,
             'total': p.total, 'pages': p.pages}
    if p.has_prev:
        pages['prev_url'] = url_for(request.endpoint, page=p.prev_num,
                                    per_page=per_page,
                                    expand=expand, _external=True,
                                    **kwargs)
    else:
        pages['prev_url'] = None
    if p.has_next:
        pages['next_url'] = url_for(request.endpoint, filter=filter,
                                    sort=sort, page=p.next_num,
                                    per_page=per_page,
                                    expand=expand, _external=True,
                                    **kwargs)
    else:
        pages['next_url'] = None
    pages['first_url'] = url_for(request.endpoint, filter=filter,
                                 sort=sort, page=1, per_page=per_page,
                                 expand=expand, _external=True,
                                 **kwargs)
    pages['last_url'] = url_for(request.endpoint, filter=filter,
                                sort=sort, page=p.pages or 1,
                                per_page=per_page, expand=expand,
                                _external=True, **kwargs)

    return p, pages
