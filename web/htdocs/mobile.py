#!/usr/bin/python
#encoding: utf-8

#import config, defaults, livestatus, htmllib, time, os, re, pprint, time, copy
#import weblib, traceback
import re
from lib import *
import views, config, htmllib
#from pagefunctions import *

# These regexes are taken from the public domain code of Matt Sullivan
# http://sullerton.com/2011/03/django-mobile-browser-detection-middleware/
reg_b = re.compile(r"android.+mobile|avantgo|bada\\/|blackberry|blazer|compal|elaine|fennec|hiptop|iemobile|ip(hone|od)|iris|kindle|lge |maemo|midp|mmp|opera m(ob|in)i|palm( os)?|phone|p(ixi|re)\\/|plucker|pocket|psp|symbian|treo|up\\.(browser|link)|vodafone|wap|windows (ce|phone)|xda|xiino", re.I|re.M)
reg_v = re.compile(r"1207|6310|6590|3gso|4thp|50[1-6]i|770s|802s|a wa|abac|ac(er|oo|s\\-)|ai(ko|rn)|al(av|ca|co)|amoi|an(ex|ny|yw)|aptu|ar(ch|go)|as(te|us)|attw|au(di|\\-m|r |s )|avan|be(ck|ll|nq)|bi(lb|rd)|bl(ac|az)|br(e|v)w|bumb|bw\\-(n|u)|c55\\/|capi|ccwa|cdm\\-|cell|chtm|cldc|cmd\\-|co(mp|nd)|craw|da(it|ll|ng)|dbte|dc\\-s|devi|dica|dmob|do(c|p)o|ds(12|\\-d)|el(49|ai)|em(l2|ul)|er(ic|k0)|esl8|ez([4-7]0|os|wa|ze)|fetc|fly(\\-|_)|g1 u|g560|gene|gf\\-5|g\\-mo|go(\\.w|od)|gr(ad|un)|haie|hcit|hd\\-(m|p|t)|hei\\-|hi(pt|ta)|hp( i|ip)|hs\\-c|ht(c(\\-| |_|a|g|p|s|t)|tp)|hu(aw|tc)|i\\-(20|go|ma)|i230|iac( |\\-|\\/)|ibro|idea|ig01|ikom|im1k|inno|ipaq|iris|ja(t|v)a|jbro|jemu|jigs|kddi|keji|kgt( |\\/)|klon|kpt |kwc\\-|kyo(c|k)|le(no|xi)|lg( g|\\/(k|l|u)|50|54|e\\-|e\\/|\\-[a-w])|libw|lynx|m1\\-w|m3ga|m50\\/|ma(te|ui|xo)|mc(01|21|ca)|m\\-cr|me(di|rc|ri)|mi(o8|oa|ts)|mmef|mo(01|02|bi|de|do|t(\\-| |o|v)|zz)|mt(50|p1|v )|mwbp|mywa|n10[0-2]|n20[2-3]|n30(0|2)|n50(0|2|5)|n7(0(0|1)|10)|ne((c|m)\\-|on|tf|wf|wg|wt)|nok(6|i)|nzph|o2im|op(ti|wv)|oran|owg1|p800|pan(a|d|t)|pdxg|pg(13|\\-([1-8]|c))|phil|pire|pl(ay|uc)|pn\\-2|po(ck|rt|se)|prox|psio|pt\\-g|qa\\-a|qc(07|12|21|32|60|\\-[2-7]|i\\-)|qtek|r380|r600|raks|rim9|ro(ve|zo)|s55\\/|sa(ge|ma|mm|ms|ny|va)|sc(01|h\\-|oo|p\\-)|sdk\\/|se(c(\\-|0|1)|47|mc|nd|ri)|sgh\\-|shar|sie(\\-|m)|sk\\-0|sl(45|id)|sm(al|ar|b3|it|t5)|so(ft|ny)|sp(01|h\\-|v\\-|v )|sy(01|mb)|t2(18|50)|t6(00|10|18)|ta(gt|lk)|tcl\\-|tdg\\-|tel(i|m)|tim\\-|t\\-mo|to(pl|sh)|ts(70|m\\-|m3|m5)|tx\\-9|up(\\.b|g1|si)|utst|v400|v750|veri|vi(rg|te)|vk(40|5[0-3]|\\-v)|vm40|voda|vulc|vx(52|53|60|61|70|80|81|83|85|98)|w3c(\\-| )|webc|whit|wi(g |nc|nw)|wmlb|wonu|x700|xda(\\-|2|g)|yas\\-|your|zeto|zte\\-", re.I|re.M)

def is_mobile(user_agent):
    return reg_b.search(user_agent) or reg_v.search(user_agent[0:4])

def mobile_html_head(title, ready_code=""):
    html.mobile = True
    html.write("""<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html>
 <head>
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>%s</title>
  <link rel="stylesheet" type="text/css" href="jquery/jquery.mobile-1.0.css">
  <link rel="stylesheet" type="text/css" href="check_mk.css">
  <link rel="stylesheet" type="text/css" href="status.css">
  <link rel="stylesheet" type="text/css" href="mobile.css">
  <script type='text/javascript' src='jquery/jquery-1.6.4.min.js'></script>
  <script type='text/javascript' src='jquery/jquery.mobile-1.0.min.js'></script>
  <script type='text/javascript'>
      $(document).ready(function() { %s });
  </script>
  
</head>
<body class=mobile>
""" % (title, ready_code))

def mobile_html_foot():
    html.write("</body></html>\n")

def jqm_header_button(url, title, icon=""):
    html.write('<a href="%s" data-icon="%s" data-iconpos="left" '
               'data-transition="flip" data-direction="reverse">%s</a>\n' % (url, icon, title))

def jqm_page_header(title, id=None, left_button=None, right_button=None):
    idtxt = id and (' id="%s"' % id) or ''
    html.write(
        '<div data-role="page"%s>\n'
        '<div data-role="header">\n' % idtxt)
    if left_button:
        jqm_header_button(*left_button)
    html.write('<h1>%s</h1>\n' % title)
    if right_button:
        jqm_header_button(*right_button)
    html.write('</div>')
    html.write('<div data-role="content">\n')

def jqm_page_footer(content=""):
    html.write('</div>') # close content-div
    html.write(
        '</div>\n'
        '<div data-role="footer"><h4>%s</h4></div>\n' % content)
    html.write('</div>') # close page-div

def jqm_page_navfooter(items, current, page_id):
    html.write("</div>\n") # close content
    html.write(
        '<div data-role="footer" data-id="%s" data-position="fixed">\n'
        '<div data-role="navbar">\n'
        '<ul>\n' % page_id)
    data_direction = "reverse"
    for href, title, icon in items:
        if current == href:
            active = ' class="ui-state-persist ui-btn-active"'
            data_direction = ""
        else:
            active = ''
        html.write('<li><a data-transition="slide" data-direction="%s" '
                   'data-icon="%s" data-iconpos="bottom" '
                   'href="%s"%s>%s</a></li>\n' % 
                   (data_direction, icon, href, active, title))
    html.write(
        '</ul>\n'
        '</div>\n'
        '</div>\n')
    html.write('</div>') # close page-div


def jqm_page_index(title, items):
    html.write(
        '<ul data-role="listview" data-inset="true">\n')
    for href, title in items:
        html.write('<li><a data-ajax="false" data-transition="flip" href="%s">%s</a></li>\n' %
                (href, title))
    html.write("</ul>\n")

    # Link to non-mobile GUI
    html.write(
        '<ul data-role="listview" data-inset="true">\n')
    html.write('<li><a data-ajax="false" data-transition="fade" href="%s">%s</a></li>\n' %
                ("index.py?mobile=", _("Classical web GUI")))
    html.write('</ul>\n')

def jqm_page(title, content, foot, id=None):
    jqm_page_header(title, id)
    html.write(content)
    jqm_page_footer(foot)

def page_login():
    title = "Check_MK Mobile"
    mobile_html_head(title)
    jqm_page_header(title, id="login")
    html.write('<div id="loginhead">%s</div>' % 
      _("Welcome to Check_MK Multisite Mobile. Please Login."))

    html.begin_form("login", method = 'POST', add_transid = False)
    # Keep information about original target URL
    origtarget = html.var('_origtarget', '')
    if not origtarget and not html.req.myfile == 'login':
        origtarget = html.req.uri
    html.hidden_field('_origtarget', htmllib.attrencode(origtarget)) 

    html.text_input("_username", size = 50, label = _("Username:"))
    html.password_input("_password", size = 50, label = _("Password:"))
    html.write("<br>")
    html.button("_login", _('Login'))
    html.set_focus("_username")
    html.end_form()
    html.write('<div id="loginfoot">')
    html.write('<img class="logomk" src="images/logo_mk.png">')
    html.write('<div class="copyright">%s</div>' % _("Copyright Mathias Kettner 2012"))
    html.write('</div>')  
    jqm_page_footer()
    mobile_html_foot()
    return 0 # apache.OK

    
def page_index():
    title = "Check_MK Mobile"
    mobile_html_head(title)
    jqm_page_header(title, left_button=("logout.py", "Logout", "delete"))
    views.load_views()
    items = []
    for view_name, view in html.available_views.items():
        if view.get("mobile") and not view.get("hidden"):
            url = "mobile_view.py?view_name=%s" % view_name
            count = views.show_view(view, only_count = True)
            if view.get("mustsearch"):
                url += "#filter"
            items.append((url, '%s <span class="ui-li-count">%d</span>' % (view["title"], count)))
    jqm_page_index(_("Check_MK Mobile"), items)
    jqm_page_footer()
    mobile_html_foot()

def page_view():
    views.load_views()
    view_name = html.var("view_name")
    view = html.available_views.get(view_name)
    title = views.view_title(view)
    mobile_html_head(title)
    try:
        views.show_view(view, show_heading = False, show_buttons = False, 
                        show_footer = False, render_function = render_view)
        pass
    except Exception, e:
        if config.debug:
            raise
        html.write("ERROR showing view: %s" % e)
    mobile_html_foot()

def render_view(view, rows, datasource, group_painters, painters, 
                display_options, painter_options, show_heading, show_buttons,
                show_checkboxes, layout, num_columns, show_filters, show_footer, hide_filters,
                browser_reload):

    home=("mobile.py", "Home", "home")

    title = views.view_title(view)
    navbar = [
      ( "#data",     _("Results"), "grid"),
      ( "#commands", _("Commands"), "gear" ),
      ( "#filter",   _("Filter"),   "search" )]

    # Should we show a page with context links?
    context_links = [
        e for e in views.collect_context_links(view, hide_filters)
        if e[0].get("mobile") ]

    if context_links:
        navbar.append(( "#context", _("Context"), "arrow-r"))
    page_id = "view_" + view["name"]

    # Page: data rows of view
    jqm_page_header(title, left_button=home, right_button=("javascript:document.location.reload();", _("Reload"), "refresh"), id="data")
    if len(rows) == 0:
        html.write(_("No hosts/services found."))
    else:
        try:
            # TODO: special limit for mobile UI
            html.check_limit(rows, views.get_limit())
            layout["render"](rows, view, group_painters, painters, num_columns,
                            show_checkboxes and not html.do_actions())
        except Exception, e:
            html.write(_("Error showing view: %s" % e))
    jqm_page_navfooter(navbar, '#data', page_id)

    # Page: Commands
    jqm_page_header(_("Commands"), left_button=home, id="commands")
    html.write("Hier kommen die Commands")
    jqm_page_navfooter(navbar, '#commands', page_id)

    # Page: Filters
    jqm_page_header(_("Filter / Search"), left_button=home, id="filter")
    show_filter_form(show_filters)
    jqm_page_navfooter(navbar, '#filter', page_id)

    # Page: Context buttons
    if context_links:
        jqm_page_header(_("Context"), left_button=home, id="context")
        show_context_links(context_links)
        jqm_page_navfooter(navbar, '#context', page_id)
    

def show_filter_form(show_filters):
    # Sort filters
    s = [(f.sort_index, f.title, f) for f in show_filters if f.available()]
    s.sort()

    html.begin_form("filter")
    html.write('<ul data-inset="false" data-role="listview">\n')
    for sort_index, title, f in s:
        html.write('<li data-role="fieldcontain">\n')
        html.write('<fieldset data-role="controlgroup">\n')
        html.write('<div role="heading" class="ui-controlgroup-label">%s</div>' % title)
        html.write('<div class="ui-controlgroup-controls">')
        f.display()
        html.write('</div></fieldset></li>\n')
    html.write("</ul>\n")
    html.hidden_fields()
    html.end_form()
    # Make the tab 'Results' not simply switch to the results page
    # but submit the form and fetch new data. This is done by overriding
    # that buttons click function to submit the form. Note: We need to
    # remove the ancor in href. Otherwise jQuery will do some magic
    # itself and first switch to that page...
    html.javascript(
      "$('div#filter a[href=\"#data\"]')"
      ".attr('href', '').live('click', function(e) "
      "{ e.preventDefault(); $('div#filter form[name=\"filter\"]').submit();});")


def show_context_links(context_links):
    items = []
    for view, title, uri, icon, buttonid in context_links:
        items.append((uri, title))
    jqm_page_index(_("Related Views"), items)

