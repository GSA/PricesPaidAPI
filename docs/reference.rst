Reference
---------

.. module:: solr
   :synopsis: Convenient interface to Solr search services.

.. role:: var(emphasis)

   
Data representation
~~~~~~~~~~~~~~~~~~~

Solr documents are simple collections of named fields; the fields may be
multi-valued, depending on the Solr schema being used.

In Python, these documents are modeled as dictionaries with the field
names as keys and field values (or sets of values) as values.  When
multiple values are presented to Solr, the value in the dictionary must
be a list, tuple or set.  (A ``frozenset`` is not accepted.)

Values may be strings (``str`` or ``unicode``), dates, datetimes, bools,
or ``None``.  Field values of ``None`` are omitted from the values
submitted to Solr.

``datetime.datetime`` values are converted to UTC.

``datetime.date`` values are converted to ``datetime.datetime`` values
at 00:00:00 with an assumed timezone of UTC.

``bool`` values are converted to the string values ``'true'`` or
``'false'``.


Exceptions
~~~~~~~~~~

The :mod:`solr` module provides everything you'll need.  There's an
exception that might be raised by many operations:

.. autoexception:: solr.SolrException
   :members: httpcode, reason, body
   :show-inheritance:

These exceptions, along with others, can be raised by the connection
objects that are provided.


Connections
~~~~~~~~~~~

There are two flavors of connection objects; one is provided to support
older applications, and the other provides more rational (and powerful)
access to commit controls.

Both connection classes are designed to work with the 2.2 response
format generated by Solr 1.2 and newer, but will likely work with the
older 2.1 response format as well.

.. class:: Solr(url)

   Connect to the Solr instance at `url`.  If the Solr instance provides
   multiple cores, `url` should be to a specific core.
   Examples:

       | http://localhost:8080/solr
       | https://solr-server/solr

   Python must have SSL support installed for the ``https`` scheme to
   work.  (Most pre-packaged Python builds are.)

   Many keyword arguments can be specified to tailor instances for the
   needs of specific applications:

   `persistent`
       Keep a persistent connection open.
       Defaults to ``True``.

   `timeout`
       Timeout, in seconds, for the server to response.  By default, use
       the Python default timeout.

   `ssl_key`, `ssl_cert`
       If using client-side key files for SSL authentication, these
       should be, respectively, your PEM key file and certificate file.

   `http_user`, `http_pass`
       If given, include HTTP Basic authentication in all request
       headers.

   `post_headers`
       A dictionary of headers that should be included in all requests
       to Solr.  This is a good way to provide the User-Agent or other
       specialized headers.

   `max_retries`
       Maximum number of retries to perform automatically.  Re-tries are
       only attempted when socket errors or
       :exc:`httplib.ImproperConnectionState` or
       :exc:`httplib.BadStatusLine` exceptions are generated from calls
       into :mod:`httplib`.


Commit-control arguments
++++++++++++++++++++++++

Some methods support optional Boolean arguments to control commits that
may be made by the method.  These arguments are always optional, and no
commit will be performed if they are not given.

Methods that accept these arguments are identified as supporting
commit-control arguments, but the arguments are not listed or described
for the individual methods.

The following commit-control keyword arguments are defined:

`commit`
    Indicates whether a commit should be performed before the method
    returns.

`optimize`
    Indicates whether index optimization should be performed before the
    method returns.  If true, implies a `commit` value of ``True``.

`wait_flush`
    Indicates whether the request should block until the commit has been
    flushed to disk on the server.  If not specified, this defaults to
    ``True``.  (There's some question about whether this is honored in
    recent versions of Solr.)

`wait_searcher`
    Indicates whether the request should block until searcher objects
    have been warmed for use before returning.  If not specified, this
    defaults to ``True``.  If true, implies a `wait_flush` value of
    ``True`` (a false `wait_flush` value will be ignored).

If `wait_flush` or `wait_searcher` are specified when neither `commit`
nor `optimize` are true, a :exc:`TypeError` will be raised.

Whenever possible, the request to commit or optimize the index will be
collapsed into an update request being performed by the method being
called.  This avoids a separate HTTP round-trip to commit changes.


Methods common to connections
+++++++++++++++++++++++++++++

These methods are available on both connection classes.

.. The signatures on the delete* methods are required since those
   methods are wrapped by the ``committing`` decorator.

.. automethod:: solr.Solr.delete(id=None, ids=None, queries=None)
.. automethod:: solr.Solr.delete_many(ids)
.. automethod:: solr.Solr.delete_query(query)
.. automethod:: solr.Solr.commit(wait_flush=True, wait_searcher=True)
.. automethod:: solr.Solr.optimize
.. automethod:: solr.Solr.close


Methods specific to :class:`Solr`
+++++++++++++++++++++++++++++++++

These methods are specific to the :class:`Solr` class; similarly-named
methods on :class:`SolrConnection` may exist with different signatures.

.. attribute:: Solr.select

   A :class:`SearchHandler` instance for the commonly-defined ``select``
   request handler on the server.

.. automethod:: solr.Solr.add(doc)
.. automethod:: solr.Solr.add_many(docs)


Compatibility support
~~~~~~~~~~~~~~~~~~~~~

.. class:: SolrConnection(url)

   This class is used by older applications of ``solrpy``; newer
   applications should use :class:`solr.Solr`.

   The constructor arguments and most methods are the same as for
   :class:`solr.Solr`; only these method signatures differ:


.. automethod:: solr.SolrConnection.add

   Unlike the same-named method of :class:`Solr`, this does *not*
   support commit-control arguments.


.. automethod:: solr.SolrConnection.add_many

   Unlike the same-named method of :class:`Solr`, this does *not*
   support commit-control arguments.


.. method:: SolrConnection.query(q, fields=None, highlight=None, score=True, sort=None, sort_order="asc", **params)

   Call the ``select`` search handler,
   returning the result of that call.


.. method:: SolrConnection.raw_query(**params)

   Call the ``raw`` method of the ``select`` search handler,
   returning the result of that call.


Search handlers
~~~~~~~~~~~~~~~

A `search handler` provides access to a named search on the Solr
server.  Most servers are configured with a search named ``select``, but
different searches may be defined that require different arguments or
different default parameters.

The :class:`SearchHandler` class provides access to a named search.
Handlers are constructed simply, and can be saved and used as many times
as needed.


.. class:: SearchHandler(connection, path)

   Construct a search handler for :var:`connection` with the relative
   path given by :var:`path`.  For example, to use the commonly-defined
   ``select`` search, construct a handler like this::

       import solr
       conn = solr.Solr("http://solr.example.net/solr")
       select = solr.SearchHandler(conn, "/select")

   This is exactly how the :attr:`select` attribute of :class:`Solr`
   instances is constructed.  An alternate request handler can be used
   by providing an alternate `path`::

       find_stuff = solr.SearchHandler(conn, "/find_stuff")

   The slash at the beginning of the `path` value is required if the URL
   given to the connection constructor does not end with a slash.


.. method:: SearchHandler.__call__(q=None, fields=None, highlight=None, score=True, sort=None, sort_order="asc", **params)

   :var:`q` is the query string in the format configured for the request
   handler in the Solr server.

   :var:`fields` is an optional list of fields to include.  It can be
   either a string in the format that Solr expects, or an iterable of
   field names.  Defaults to all fields (``'*'``).

   :var:`score` indicates whether score should be included in the field
   list.  Note that if you explicitly list "score" in your fields
   value, then score is effectively ignored.  Defaults to ``True``.

   :var:`highlight` indicates whether highlighting should be included.
   highlight can either be ``False``, indicating "No" (the default),
   a list of fields in the same format as :var:`fields` or True,
   indicating to highlight any fields included in :var:`fields`.  If
   ``True`` and no "fields" are given, raise a :exc:`ValueError`.

   :var:`sort` is a list of fields to sort by.  See :var:`fields` for
   formatting.  Each sort element can have be in the form "fieldname
   asc|desc" as specified by Solr specs.

   :var:`sort_order` is the backward-compatible way to add the same
   ordering to all the sort field when it is not specified.

   Optional parameters can also be passed in.  Many Solr parameters
   are in a dotted notation (for example, ``hl.simple.post``).  For
   such parameters, replace the dots with underscores when calling
   this method::

       r = conn.query('text:solrpy', hl_simple_post='</pre>')

   Returns a :class:`Response` instance.


.. method:: SearchHandler.raw(**params)

   Issue a query against a Solr server.  No logical interpretation of
   the parameters is performed, but encoding for transfer as form fields
   over HTTP is handled.

   Return the raw result as text.  No processing is performed on the
   response.
