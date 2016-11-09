# Copyright 2008-2016 Luc Saffre
# License: BSD (see file COPYING for details)

"""Adds functionality for managing notifications.

.. autosummary::
   :toctree:

    models
    actions
    mixins
    utils

Templates used by this plugin
=============================

.. xfile:: notify/body.eml

    A Jinja template used for generating the body of the email when
    sending a notification per email to its recipient.

    Available context variables:

    - ``obj`` -- The :class:`Notification
      <lino.modlib.notify.models.Notification>` instance being sent.

    - ``E`` -- The html namespace :mod:`lino.utils.xmlgen.html`

    - ``rt`` -- The runtime API :mod:`lino.api.rt`

    - ``ar`` -- The action request which caused the notification. a
      :class:`BaseRequest <lino.core.requests.BaseRequest>` instance.

"""

from lino.api import ad, _


class Plugin(ad.Plugin):
    "See :class:`lino.core.plugin.Plugin`."

    use_websockets = True
    """Set this to False in order to deactivate use of websockets and
    channels.

    """

    verbose_name = _("Notifications")

    needs_plugins = ['lino.modlib.users', 'lino.modlib.gfks', 'channels']

    site_js_snippets = ['js/reconnecting-websocket.min.js']
    # media_base_url = "http://ext.ensible.com/deploy/1.0.2/"
    media_name = 'js'

    # email_subject_template = "Notification about {obj.owner}"
    # """The template used to build the subject lino of notification emails.

    # :obj: is the :class:`Notification
    #       <lino.modlib.notify.models.Notification>` object.

    # """

    def setup_main_menu(self, site, profile, m):
        p = site.plugins.office
        m = m.add_menu(p.app_label, p.verbose_name)
        m.add_action('notify.MyNotifications')

    def setup_explorer_menu(self, site, profile, m):
        p = site.plugins.system
        m = m.add_menu(p.app_label, p.verbose_name)
        m.add_action('notify.AllNotifications')

    def get_head_lines(self, site, request):
        if not self.use_websockets:
            return
        user_name = "anony"
        if request.user.authenticated:
            user_name = request.user.username

        js_to_add = """
    <script type="text/javascript">
    Ext.onReady(function() {
        // Note that the path doesn't matter for routing; any WebSocket
        // connection gets bumped over to WebSocket consumers
        var ws_scheme = window.location.protocol == "https:" ? "wss" : "ws";
        var ws_path = ws_scheme + '://' + window.location.host + "/websocket/";
        console.log("Connecting to " + ws_path);
        var socket = new ReconnectingWebSocket(ws_path);
        socket.onmessage = function(e) {
            alert(e.data);
            try {
                var json_data = JSON.parse(e.data);
                if ( Number.isInteger(JSON.parse(e.data)["id"])){
                    socket.send(JSON.stringify({
                                    "command": "seen",
                                    "notification_id": JSON.parse(e.data)["id"],
                                }));
                            }
                }
            catch(err) {
                console.log(err.message);
            }
        }
        if (false) {
        socket.onopen = function() {
            socket.send(JSON.stringify({
                            "command": "user_connect",
                            "username": "%s",
                        }));
        }
        // Call onopen directly if socket is already open
        if (socket.readyState == WebSocket.OPEN) socket.onopen();
        }
    }); // end of onReady()"
    </script>
        """ % (user_name)
        yield js_to_add
